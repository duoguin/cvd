""" updated 240924
- [x] add pdl bot
    - [ ] check performance diff for JSON / React output
"""
import re, datetime, json
from typing import List, Tuple
from .base import BaseBot
from .role_outputs import BotOutput, BotOutputType
from controller.base_data import Message, Role
from controller.base_llm import init_client, LLM_CFG
from controller.log import LogUtils
from utils.jinja_templates import jinja_render
from utils.wrappers import retry_wrapper
from utils.context_optimizer import get_local_flowchart, get_recent_history, infer_current_node
from utils.easonsi.llm.openai_client import OpenAIClient, Formater

# ── Tuỳ chỉnh context window ─────────────────────────────────────────────────
CTX_DEPTH_FWD = 2   # số bước BFS về phía trước trong flowchart
CTX_DEPTH_BWD = 1   # số bước BFS về phía sau
CTX_K_TURNS   = 6   # số lượt user-bot gần nhất giữ trong history
# ─────────────────────────────────────────────────────────────────────────────

class DummyBot(BaseBot):
    names: List[str] = ["dummy_bot"]
    bot_template_fn: str = ""

    # def __init__(self, **args) -> None:
    #     super().__init__(**args)

    def process(self, *args, **kwargs) -> BotOutput:
        self.cnt_bot_actions += 1
        if (self.cnt_bot_actions % 2) == 0:
            bot_output = BotOutput(action="calling api!")
            self.conv.add_message(Message(role=Role.BOT, content="bot action..."))
        else:
            bot_output = BotOutput(response="bot response...")
            self.conv.add_message(Message(role=Role.BOT, content="bot response..."))
        return bot_output


class ReactBot(BaseBot):
    """ ReactBot
    prediction format:
        (Thought, Response) for response node
        (Thought, Action, Action Input) for call api node
    """
    llm: OpenAIClient = None
    bot_template_fn: str = "flowagent/bot_flowbench.jinja"
    names = ["ReactBot", "react_bot"]

    def __init__(self, **args) -> None:
        super().__init__(**args)
        self.llm = init_client(llm_cfg=LLM_CFG[self.cfg.bot_llm_name])

    def process(self, *args, **kwargs) -> BotOutput:
        prompt = self._gen_prompt()
        @retry_wrapper(retry=self.cfg.bot_retry_limit, step_name="bot_process", log_fn=print)
        def process_with_retry(prompt):
            llm_response, prediction = self._process(prompt)
            return llm_response, prediction
        llm_response, prediction = process_with_retry(prompt)

        if prediction.action_type == BotOutputType.RESPONSE:
            msg_content = prediction.response
        else:
            msg_content = f"<Call API> {prediction.action}({prediction.action_input})"
        msg = Message(
            Role.BOT, msg_content, prompt=prompt, llm_response=llm_response,
            conversation_id=self.conv.conversation_id, utterance_id=self.conv.current_utterance_id
        )
        self.conv.add_message(msg)
        self.cnt_bot_actions += 1
        return prediction

    def _gen_prompt(self) -> str:
        # ── TỐI ƯU: chỉ lấy subgraph + history gần nhất ──────────────────
        current_node = infer_current_node(None, self.workflow.workflow)
        local_flow   = get_local_flowchart(
            self.workflow.workflow, current_node,
            depth_fwd=CTX_DEPTH_FWD, depth_bwd=CTX_DEPTH_BWD,
        )
        recent_hist  = get_recent_history(self.conv, k_turns=CTX_K_TURNS)
        # ──────────────────────────────────────────────────────────────────
        prompt = jinja_render(
            self.bot_template_fn,
            task_description=self.workflow.task_description,
            workflow=local_flow,              # ← subgraph thay vì full flowchart
            toolbox=self.workflow.toolbox,
            current_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            history_conversation=recent_hist, # ← K turns thay vì toàn bộ
        )
        return prompt

    def _process(self, prompt: str = None) -> Tuple[str, BotOutput]:
        llm_response = self.llm.query_one(prompt)
        prediction = self.parse_react_output(llm_response)
        return llm_response, prediction

    @staticmethod
    def parse_react_output(s: str) -> BotOutput:
        if "```" in s:
            s = Formater.parse_codeblock(s, type="").strip()
        pattern = r"(?P<field>Thought|Action|Action Input|Response):\s*(?P<value>.*?)(?=\n(Thought|Action|Action Input|Response):|\Z)"
        matches = re.finditer(pattern, s, re.DOTALL)
        result = {match.group('field'): match.group('value').strip() for match in matches}

        thought = result.get(BotOutput.thought_str, "")
        if BotOutput.action_str in result:
            assert BotOutput.action_input_str in result, \
                f"Action Input not in prediction! LLM output:\n" + LogUtils.format_infos_basic(s)
            try:
                result[BotOutput.action_input_str] = json.loads(result[BotOutput.action_input_str])
            except Exception as e:
                raise RuntimeError(f"Action Input not in json format! LLM output:\n" + LogUtils.format_infos_basic(s))
            if result[BotOutput.action_str].startswith("API_"):
                result[BotOutput.action_str] = result[BotOutput.action_str][4:]
            output = BotOutput(action=result[BotOutput.action_str], action_input=result[BotOutput.action_input_str], thought=thought)
        else:
            assert BotOutput.response_str in result, \
                f"Response not in prediction! LLM output:\n" + LogUtils.format_infos_basic(s)
            output = BotOutput(response=result[BotOutput.response_str], thought=thought)
        return output



class StateReactBot(ReactBot):
    """
    A variant of ReactBot that forces the LLM to output its current State
    before generating Thoughts and Responses/Actions.
    """
    bot_template_fn: str = "baselines/state_flowbench.jinja"
    names = ["state_react_bot", "StateReactBot"]

    def __init__(self, **args) -> None:
        super().__init__(**args)
        self.current_state = "Starting phase / Initial step"

    def reset_workflow_state(self) -> None:
        self.current_state = "Starting phase / Initial step"
        
    def _gen_prompt(self) -> str:
        # ── TỐI ƯU: infer node từ state string LLM tự sinh ───────────────
        current_node = infer_current_node(self.current_state, self.workflow.workflow)
        local_flow   = get_local_flowchart(
            self.workflow.workflow, current_node,
            depth_fwd=CTX_DEPTH_FWD, depth_bwd=CTX_DEPTH_BWD,
        )
        recent_hist  = get_recent_history(self.conv, k_turns=CTX_K_TURNS)
        # ──────────────────────────────────────────────────────────────────
        prompt = jinja_render(
            self.bot_template_fn,
            task_description=self.workflow.task_description,
            workflow=local_flow,              # ← subgraph
            toolbox=self.workflow.toolbox,
            current_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            history_conversation=recent_hist, # ← K turns
            current_state=self.current_state,
        )
        return prompt

    def _process(self, prompt: str = None) -> Tuple[str, BotOutput]:
        llm_response = self.llm.query_one(prompt)
        prediction, new_state = self.parse_react_output(llm_response)
        if new_state:
            self.current_state = new_state
        return llm_response, prediction

    @staticmethod
    def parse_react_output(s: str) -> Tuple[BotOutput, str]:
        if "```" in s:
            s = Formater.parse_codeblock(s, type="").strip()
        pattern = r"(?P<field>State|Thought|Action|Action Input|Response):\s*(?P<value>.*?)(?=\n(State|Thought|Action|Action Input|Response):|\Z)"
        matches = re.finditer(pattern, s, re.DOTALL)
        result = {match.group('field'): match.group('value').strip() for match in matches}

        state  = result.get("State", "")
        thought = result.get(BotOutput.thought_str, "")
        if state:
            thought = f"[State Tracking: {state}]\n" + thought

        if BotOutput.action_str in result:
            assert BotOutput.action_input_str in result, \
                f"Action Input not in prediction! LLM output:\n" + LogUtils.format_infos_basic(s)
            try:
                result[BotOutput.action_input_str] = json.loads(result[BotOutput.action_input_str])
            except Exception as e:
                raise RuntimeError(f"Action Input not in json format! LLM output:\n" + LogUtils.format_infos_basic(s))
            if result[BotOutput.action_str].startswith("API_"):
                result[BotOutput.action_str] = result[BotOutput.action_str][4:]
            output = BotOutput(action=result[BotOutput.action_str], action_input=result[BotOutput.action_input_str], thought=thought)
        else:
            assert BotOutput.response_str in result, \
                f"Response not in prediction! LLM output:\n" + LogUtils.format_infos_basic(s)
            output = BotOutput(response=result[BotOutput.response_str], thought=thought)
        return output, state
