from __future__ import annotations

from enum import StrEnum
from typing import Any

from dandy import Bot
from dandy.llm.intelligence.prompts import service_system_prompt
from dandy.llm.request.message import Message

CONCISE_GUIDELINE = "Be concise. Give short, direct answers."
CODE_FORMAT_GUIDELINE = (
    "Always format code using fenced code blocks with triple backticks and "
    "specify the language (e.g., ```python)."
)


class ChatMode(StrEnum):
    FIRE_AND_FORGET = "fire_and_forget"
    AIM_AND_ASK = "aim_and_ask"


class GuidelineMode(StrEnum):
    NORMAL = "normal"
    CONCISE = "concise"


class ChatService:
    def __init__(self) -> None:
        self._mode: ChatMode = ChatMode.FIRE_AND_FORGET
        self._guideline_mode: GuidelineMode = GuidelineMode.NORMAL
        self._target: str = ""
        self._aim_bot: Bot | None = None
        self._last_fire_prompt: str | None = None
        self._last_fire_response: str | None = None

    @property
    def mode(self) -> ChatMode:
        return self._mode

    @property
    def guideline_mode(self) -> GuidelineMode:
        return self._guideline_mode

    @property
    def target(self) -> str:
        return self._target

    def set_target(self, target: str) -> None:
        self._target = target.strip()

    def _get_guidelines(self) -> str:
        guidelines = CODE_FORMAT_GUIDELINE
        if self._guideline_mode == GuidelineMode.CONCISE:
            guidelines = f"{CONCISE_GUIDELINE} {CODE_FORMAT_GUIDELINE}"
        return guidelines

    def _build_system_message(self) -> Message:
        system_text = service_system_prompt(
            role=self._aim_bot.role,
            task=self._aim_bot.task,
            guidelines=self._get_guidelines(),
            system_override_prompt=self._aim_bot.system_override_prompt,
        ).to_str()
        msg = Message(role="system")
        msg.add_content_from_text(system_text)
        return msg

    def set_mode(self, mode: ChatMode) -> None:
        self._aim_bot = None
        self._mode = mode

        if mode == ChatMode.AIM_AND_ASK and self._last_fire_prompt is not None:
            self._aim_bot = Bot(guidelines=self._get_guidelines())
            self._aim_bot.llm.messages.add_message(
                role="user", text=self._last_fire_prompt
            )
            self._aim_bot.llm.messages.add_message(
                role="assistant", text=self._last_fire_response
            )
            self._last_fire_prompt = None
            self._last_fire_response = None

    def set_guideline_mode(self, guideline_mode: GuidelineMode) -> None:
        self._guideline_mode = guideline_mode
        if self._aim_bot is not None and self._mode == ChatMode.AIM_AND_ASK:
            self._aim_bot.llm.messages.messages[0] = self._build_system_message()

    def _build_prompt(self, prompt: str) -> str:
        if self._target:
            return f"[Context: {self._target}]\n\n{prompt}"
        return prompt

    def process(self, prompt: str) -> Any:  # ty: ignore
        guidelines = self._get_guidelines()
        full_prompt = self._build_prompt(prompt)

        if self._mode == ChatMode.AIM_AND_ASK:
            if self._aim_bot is None:
                self._aim_bot = Bot(guidelines=guidelines)
            return self._aim_bot.process(full_prompt)

        response_intel = Bot(guidelines=guidelines).process(full_prompt)
        self._last_fire_prompt = prompt
        self._last_fire_response = response_intel.text
        return response_intel
