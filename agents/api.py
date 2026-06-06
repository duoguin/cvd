""" updated @240906
- [ ] generate api response with given history calling infos
- [ ] integrate with FastAPI
"""
import json, os, re
from typing import List
import requests
from .base import BaseAPIHandler
from .role_outputs import APIOutput, BotOutput
from controller.base_data import Role, Message
from controller.base_llm import init_client, LLM_CFG
from utils.jinja_templates import jinja_render
from utils.workflow_restart import add_restart_instruction
from utils.easonsi.llm.openai_client import OpenAIClient, Formater

class DummyAPIHandler(BaseAPIHandler):
    """ 
    API structure: (see apis_v0/apis.json)
    """
    names: List[str] = ["dummy_api"]
    api_template_fn: str = ""
    
    def __init__(self, **args) -> None:
        super().__init__(**args)
        self.cnt_api_callings: int = 0
        
    def process(self, *args, **kwargs) -> APIOutput:
        """ 
        1. match and check the validity of API
        2. call the API (with retry?)
        3. parse the response
        """
        # raise NotImplementedError
        self.cnt_api_callings += 1
        
        self.conv.add_message(
            Message(role=Role.SYSTEM, content="api calling..."),
        )
        api_output = APIOutput()
        return api_output


class LLMSimulatedAPIHandler(BaseAPIHandler):
    llm: OpenAIClient = None
    api_template_fn: str = "flowagent/api_llm.jinja"
    names = ["llm", "LLMSimulatedAPIHandler"]
    
    def __init__(self, **args) -> None:
        super().__init__(**args)
        self.llm = init_client(llm_cfg=LLM_CFG[self.cfg.api_llm_name])
        
    def process(self, apicalling_info: BotOutput, *args, **kwargs) -> APIOutput:
        from controller.log import SystemLogger
        SystemLogger.log("api", "LLMSimulatedAPIHandler.process", f"Khởi chạy gọi API giả lập: '{apicalling_info.action}'", with_print=False)
        flag, m = self.check_validation(apicalling_info)
        if not flag:        # base check error!
            SystemLogger.log("api", "LLMSimulatedAPIHandler.process", f"Kiểm tra tính hợp lệ thất bại: {m}", with_print=False)
            msg = Message(
                Role.SYSTEM, m,
                conversation_id=self.conv.conversation_id, utterance_id=self.conv.current_utterance_id
            )
            prediction = APIOutput(apicalling_info.action, apicalling_info.action_input, m, 400)
        else:
            self.cnt_api_callings[apicalling_info.action] += 1  # stat
            
            prompt = self._gen_prompt(apicalling_info)
            SystemLogger.log("api", "LLMSimulatedAPIHandler.process", f"Gửi yêu cầu tới LLM API Simulator (Prompt size: {len(prompt)})", with_print=False)
            llm_response = self.llm.query_one(prompt)
            prediction = self.parse_react_output(llm_response, apicalling_info) # parse_json_output
            SystemLogger.log("api", "LLMSimulatedAPIHandler.process", f"LLM API Simulator trả về Code={prediction.response_status_code}", with_print=False)
            if prediction.response_status_code==200:
                msg_content = f"<API response> {prediction.response_data}"
            else:
                msg_content = f"<API response> {prediction.response_status_code} {prediction.response_data}"
            msg = Message(
                Role.SYSTEM, msg_content, prompt=prompt, llm_response=llm_response, 
                conversation_id=self.conv.conversation_id, utterance_id=self.conv.current_utterance_id
            )
        self.conv.add_message(msg)
        return prediction
    
    def check_validation(self, apicalling_info: BotOutput) -> bool:
        # ... match the api by name? check params? 
        api_names = [api["API"] for api in self.api_infos]
        if apicalling_info.action not in api_names: 
            return False, f"<Calling API Error> : {apicalling_info.action} not in {api_names}"
        return True, None

    def _gen_prompt(self, apicalling_info: BotOutput) -> str:
        prompt = jinja_render(
            self.api_template_fn,     # "flowagent/api_llm.jinja": api_infos, api_name, api_input
            api_infos=self.api_infos,
            api_name=apicalling_info.action,
            api_input=apicalling_info.action_input,
        )
        return prompt

    @staticmethod
    def parse_json_output(s:str, apicalling_info:BotOutput) -> APIOutput:
        """ 
        parse the output: status_code, data
        NOTE: can also output in the format of ReAct
        """
        if "```" in s:
            s = Formater.parse_codeblock(s, type="json")
        response = json.loads(s) # eval | NameError: name 'null' is not defined
        assert all(key in response for key in [APIOutput.response_status_str, APIOutput.response_data_str]), f"Response not in prediction: {s}"
        # parse the "data"?
        return APIOutput(
            name=apicalling_info.action,
            request=apicalling_info.action_input,
            response_data=response[APIOutput.response_data_str],
            response_status_code=int(response[APIOutput.response_status_str]),
        )
    
    @staticmethod
    def parse_react_output(s: str, apicalling_info:BotOutput) -> APIOutput:
        if "```" in s:
            s = Formater.parse_codeblock(s, type="").strip()
        pattern = r"(?P<field>Status Code|Data):\s*(?P<value>.*?)(?=\n(Status Code|Data):|\Z)"
        matches = re.finditer(pattern, s, re.DOTALL)
        result = {match.group('field'): match.group('value').strip() for match in matches}
        
        # validate result
        assert all(key in result for key in [APIOutput.response_status_str_react, APIOutput.response_data_str_react]), f"Data/Status Code not in prediction: {s}"
        return APIOutput(
            name=apicalling_info.action,
            request=apicalling_info.action_input,
            response_data=json.dumps(result[APIOutput.response_data_str_react], ensure_ascii=False),
            response_status_code=int(result[APIOutput.response_status_str_react]),
        )


class RealAPIHandler(BaseAPIHandler):
    names: List[str] = ["real_api", "RealAPIHandler"]
    backend_url: str = ""
    api_template_fn: str = ""
    supported_actions = {
        "book_apartment_viewing",
        "doctor_schedule",
    }

    def __init__(self, **args) -> None:
        super().__init__(**args)
        base_url = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")
        self.backend_url = f"{base_url.rstrip('/')}/api"

    def process(self, apicalling_info: BotOutput, *args, **kwargs) -> APIOutput:
        from controller.log import SystemLogger
        SystemLogger.log("api", "RealAPIHandler.process", f"Khởi chạy gọi API thực tế: '{apicalling_info.action}'", with_print=False)
        flag, m = self.check_validation(apicalling_info)
        if not flag:
            SystemLogger.log("api", "RealAPIHandler.process", f"Kiểm tra tính hợp lệ thất bại: {m}", with_print=False)
            msg = Message(
                Role.SYSTEM, m,
                conversation_id=self.conv.conversation_id, utterance_id=self.conv.current_utterance_id
            )
            prediction = APIOutput(
                name=apicalling_info.action,
                request=apicalling_info.action_input,
                response_data=m,
                response_status_code=400,
            )
        else:
            self.cnt_api_callings[apicalling_info.action] += 1  # stat

            action_name = apicalling_info.action
            action_input = apicalling_info.action_input

            if isinstance(action_input, str):
                try:
                    payload = json.loads(action_input)
                except json.JSONDecodeError:
                    payload = None
            else:
                payload = action_input

            if not isinstance(payload, dict):
                status_code = 400
                response_data = {
                    "success": False,
                    "error_code": "INVALID_ACTION_INPUT",
                    "message": "Action Input must be a JSON object.",
                    "restart_workflow": True,
                }
                SystemLogger.log("api", "RealAPIHandler.process", f"Dữ liệu Action Input không phải JSON: {action_input}", with_print=False)
            else:
                url = f"{self.backend_url}/{action_name}"
                SystemLogger.log("api", "RealAPIHandler.process", f"Gửi HTTP POST tới {url} với payload: {payload}", with_print=False)
                try:
                    res = requests.post(url, json=payload, timeout=5)
                    status_code = res.status_code
                    try:
                        res_json = res.json()
                    except ValueError:
                        res_json = {
                            "success": False,
                            "error_code": "INVALID_BACKEND_RESPONSE",
                            "message": "Backend returned a non-JSON response.",
                            "restart_workflow": False,
                        }
                    response_data = res_json.get("data", res_json)
                    SystemLogger.log("api", "RealAPIHandler.process", f"Nhận kết quả HTTP {status_code}: {response_data}", with_print=False)
                except requests.RequestException as exc:
                    status_code = 503
                    response_data = {
                        "success": False,
                        "error_code": "BACKEND_UNAVAILABLE",
                        "message": f"Backend request failed: {type(exc).__name__}.",
                        "restart_workflow": False,
                    }
                    SystemLogger.log("api", "RealAPIHandler.process", f"Gọi backend thất bại: {exc}", with_print=False)

            prediction = APIOutput(
                name=action_name,
                request=action_input,
                response_data=response_data,
                response_status_code=status_code
            )
            
            if prediction.response_status_code == 200:
                msg_content = f"<API response> {prediction.response_data}"
            else:
                msg_content = f"<API response> {prediction.response_status_code} {prediction.response_data}"
            msg_content = add_restart_instruction(msg_content, prediction.response_data)
                
            msg = Message(
                Role.SYSTEM, msg_content,
                conversation_id=self.conv.conversation_id, utterance_id=self.conv.current_utterance_id
            )
            
        self.conv.add_message(msg)
        return prediction
        
    def check_validation(self, apicalling_info: BotOutput) -> bool:
        api_names = [api["API"] for api in self.api_infos]
        if apicalling_info.action not in api_names:
            return False, f"<Calling API Error> : {apicalling_info.action} not in {api_names}"
        if apicalling_info.action not in self.supported_actions:
            return False, (
                f"<Calling API Error> : {apicalling_info.action} is not implemented "
                "by the real backend"
            )
        return True, None
