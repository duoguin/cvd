"""
optimized_bots.py
=================
Drop-in replacement cho các Bot class trong roles/bot.py.
Thêm 2 tối ưu vào _gen_prompt():
  1. Chỉ truyền subgraph flowchart xung quanh node hiện tại
  2. Chỉ truyền K turns hội thoại gần nhất

Cách tích hợp – trong roles/__init__.py (hoặc flowagent/__init__.py), thay:
    from .bot import ReactBot, StateReactBot, PDLBot
bằng:
    from .optimized_bots import OptReactBot   as ReactBot
    from .optimized_bots import OptStateReactBot as StateReactBot
    # PDLBot không dùng flowchart nên giữ nguyên

Hoặc ghi đè trực tiếp BOT_NAME2CLASS:
    from .optimized_bots import patch_bot_registry
    patch_bot_registry()
"""

from __future__ import annotations

import datetime
from typing import Tuple, Optional

from .bot import ReactBot, StateReactBot, PDLBot, BotOutput
from ..data import Message, Role
from utils.jinja_templates import jinja_render
from utils.context_optimizer import (
    get_local_flowchart,
    get_recent_history,
    infer_current_node,
)


# ---------------------------------------------------------------------------
# Cấu hình mặc định – có thể override qua cfg hoặc kwargs
# ---------------------------------------------------------------------------
DEFAULT_DEPTH_FWD  = 2   # số bước BFS về phía trước trong flowchart
DEFAULT_DEPTH_BWD  = 1   # số bước BFS về phía sau
DEFAULT_K_TURNS    = 6   # số lượt user-bot giữ trong history


# ---------------------------------------------------------------------------
# Mixin: thêm helper methods, không thay đổi logic gốc
# ---------------------------------------------------------------------------
class ContextOptimizerMixin:
    """
    Mixin cho các Bot class.
    Cung cấp:
        _get_local_flowchart(current_node)  → str
        _get_recent_history()               → str
        _resolve_current_node()             → Optional[str]
    """

    # ---------- config helpers ----------
    @property
    def _depth_fwd(self) -> int:
        return getattr(self.cfg, "ctx_depth_fwd", DEFAULT_DEPTH_FWD)

    @property
    def _depth_bwd(self) -> int:
        return getattr(self.cfg, "ctx_depth_bwd", DEFAULT_DEPTH_BWD)

    @property
    def _k_turns(self) -> int:
        return getattr(self.cfg, "ctx_k_turns", DEFAULT_K_TURNS)

    # ---------- main helpers ----------
    def _get_local_flowchart(self, current_node: Optional[str]) -> str:
        """Trả về subgraph Mermaid xung quanh current_node."""
        full = self.workflow.workflow
        if not current_node:
            return full
        return get_local_flowchart(
            full,
            current_node,
            depth_fwd=self._depth_fwd,
            depth_bwd=self._depth_bwd,
        )

    def _get_recent_history(self) -> str:
        """Trả về K turns hội thoại gần nhất."""
        return get_recent_history(self.conv, k_turns=self._k_turns)

    def _resolve_current_node(self) -> Optional[str]:
        """
        Lấy node hiện tại.
        StateReactBot lưu trong self.current_state (có thể chứa "SK004").
        ReactBot không tự track → infer từ history gần nhất.
        """
        state_str = getattr(self, "current_state", None)
        return infer_current_node(state_str, self.workflow.workflow)


# ---------------------------------------------------------------------------
# OptReactBot: ReactBot + context optimizer
# ---------------------------------------------------------------------------
class OptReactBot(ContextOptimizerMixin, ReactBot):
    """ReactBot với flowchart và history đã được tối ưu."""

    names = ["opt_react_bot", "OptReactBot"]

    def _gen_prompt(self) -> str:
        current_node = self._resolve_current_node()
        local_flow   = self._get_local_flowchart(current_node)
        recent_hist  = self._get_recent_history()

        prompt = jinja_render(
            self.bot_template_fn,
            task_description=self.workflow.task_description,
            workflow=local_flow,                  # ← chỉ subgraph
            toolbox=self.workflow.toolbox,
            current_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            history_conversation=recent_hist,     # ← chỉ K turns
        )
        return prompt


# ---------------------------------------------------------------------------
# OptStateReactBot: StateReactBot + context optimizer
# ---------------------------------------------------------------------------
class OptStateReactBot(ContextOptimizerMixin, StateReactBot):
    """
    StateReactBot với flowchart và history đã được tối ưu.
    LLM tự ghi nhớ State, nên việc infer current_node chính xác hơn.
    """

    names = ["opt_state_react_bot", "OptStateReactBot"]

    def _gen_prompt(self) -> str:
        current_node = self._resolve_current_node()
        local_flow   = self._get_local_flowchart(current_node)
        recent_hist  = self._get_recent_history()

        prompt = jinja_render(
            self.bot_template_fn,
            task_description=self.workflow.task_description,
            workflow=local_flow,
            toolbox=self.workflow.toolbox,
            current_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            history_conversation=recent_hist,
            current_state=self.current_state,
        )
        return prompt


# ---------------------------------------------------------------------------
# Hàm tiện ích: patch BOT_NAME2CLASS để register các bot mới
# ---------------------------------------------------------------------------
def patch_bot_registry():
    """
    Gọi hàm này một lần (vd trong flowagent/__init__.py hoặc controller)
    để đăng ký các OptimizedBot vào registry chung.

    Sau khi gọi, dùng --bot-mode=opt_react_bot hoặc opt_state_react_bot
    trong run_cli.sh.
    """
    try:
        from flowagent.roles import BOT_NAME2CLASS
        for cls in [OptReactBot, OptStateReactBot]:
            for name in cls.names:
                BOT_NAME2CLASS[name] = cls
        print("[context_optimizer] Registered:", list(OptReactBot.names) + list(OptStateReactBot.names))
    except ImportError as e:
        print(f"[context_optimizer] Warning: could not patch registry – {e}")