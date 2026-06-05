from typing import Any


RESTART_WORKFLOW_INSTRUCTION = (
    "Restart the current workflow and collect all required information from the beginning."
)


def restart_requested(response_data: Any) -> bool:
    return isinstance(response_data, dict) and response_data.get("restart_workflow") is True


def add_restart_instruction(message: str, response_data: Any) -> str:
    if not restart_requested(response_data):
        return message
    return f"{message}\n<System instruction> {RESTART_WORKFLOW_INSTRUCTION}"


def reset_bot_state_if_requested(bot: Any, response_data: Any) -> bool:
    if not restart_requested(response_data):
        return False
    reset_workflow_state = getattr(bot, "reset_workflow_state", None)
    if callable(reset_workflow_state):
        reset_workflow_state()
    return True
