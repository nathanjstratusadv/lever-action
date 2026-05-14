from __future__ import annotations

from unittest.mock import MagicMock, patch

from lever_action.services.chat_service import (
    CODE_FORMAT_GUIDELINE,
    CONCISE_GUIDELINE,
    ChatMode,
    ChatService,
    GuidelineMode,
)


class TestChatService:
    def test_process_returns_intel_from_bot(self) -> None:
        mock_intel = MagicMock()
        mock_intel.text = "Test response"

        with patch("lever_action.services.chat_service.Bot") as mock_bot_cls:
            mock_bot = MagicMock()
            mock_bot.process.return_value = mock_intel
            mock_bot_cls.return_value = mock_bot

            service = ChatService()
            result = service.process("Hello")

            mock_bot.process.assert_called_once_with("Hello")
            assert result == mock_intel

    def test_process_creates_new_bot_instance_each_call(self) -> None:
        with patch("lever_action.services.chat_service.Bot") as mock_bot_cls:
            mock_bot = MagicMock()
            mock_bot.process.return_value = MagicMock(text="ok")
            mock_bot_cls.return_value = mock_bot

            service = ChatService()
            service.process("First")
            service.process("Second")

            assert mock_bot_cls.call_count == 2

    def test_default_mode_is_fire_and_forget(self) -> None:
        service = ChatService()
        assert service.mode == ChatMode.FIRE_AND_FORGET

    def test_set_mode_changes_mode(self) -> None:
        service = ChatService()
        service.set_mode(ChatMode.AIM_AND_ASK)
        assert service.mode == ChatMode.AIM_AND_ASK

    def test_set_mode_resets_aim_bot(self) -> None:
        service = ChatService()
        service.set_mode(ChatMode.AIM_AND_ASK)

        with patch("lever_action.services.chat_service.Bot") as mock_bot_cls:
            mock_bot = MagicMock()
            mock_bot.process.return_value = MagicMock(text="ok")
            mock_bot_cls.return_value = mock_bot

            service.process("First")
            assert mock_bot_cls.call_count == 1

            service.process("Second")
            assert mock_bot_cls.call_count == 1

    def test_aim_and_ask_reuses_bot_instance(self) -> None:
        with patch("lever_action.services.chat_service.Bot") as mock_bot_cls:
            mock_bot = MagicMock()
            mock_bot.process.return_value = MagicMock(text="ok")
            mock_bot_cls.return_value = mock_bot

            service = ChatService()
            service.set_mode(ChatMode.AIM_AND_ASK)

            service.process("First")
            first_bot = mock_bot_cls.return_value

            service.process("Second")
            second_bot = mock_bot_cls.return_value

            assert first_bot is second_bot
            assert mock_bot_cls.call_count == 1

    def test_switching_to_fire_and_forget_resets_bot(self) -> None:
        with patch("lever_action.services.chat_service.Bot") as mock_bot_cls:
            mock_bot = MagicMock()
            mock_bot.process.return_value = MagicMock(text="ok")
            mock_bot_cls.return_value = mock_bot

            service = ChatService()
            service.set_mode(ChatMode.AIM_AND_ASK)
            service.process("First")

            service.set_mode(ChatMode.FIRE_AND_FORGET)
            service.process("Second")

            assert mock_bot_cls.call_count == 2

    def test_switching_from_fire_to_aim_creates_new_bot(self) -> None:
        with patch("lever_action.services.chat_service.Bot") as mock_bot_cls:
            mock_bot = MagicMock()
            mock_bot.process.return_value = MagicMock(text="ok")
            mock_bot_cls.return_value = mock_bot

            service = ChatService()
            service.process("First")
            assert mock_bot_cls.call_count == 1

            service.set_mode(ChatMode.AIM_AND_ASK)
            service.process("Second")
            assert mock_bot_cls.call_count == 2

    def test_fire_and_forget_caches_last_exchange(self) -> None:
        with patch("lever_action.services.chat_service.Bot") as mock_bot_cls:
            mock_intel = MagicMock()
            mock_intel.text = "Cached response"
            mock_bot = MagicMock()
            mock_bot.process.return_value = mock_intel
            mock_bot_cls.return_value = mock_bot

            service = ChatService()
            service.process("Cached prompt")

            assert service._last_fire_prompt == "Cached prompt"
            assert service._last_fire_response == "Cached response"

    def test_switch_to_aim_seeds_bot_with_last_fire_exchange(self) -> None:
        with patch("lever_action.services.chat_service.Bot") as mock_bot_cls:
            mock_intel = MagicMock()
            mock_intel.text = "F&F response"
            mock_bot = MagicMock()
            mock_bot.process.return_value = mock_intel
            mock_bot_cls.return_value = mock_bot

            service = ChatService()
            service.process("F&F prompt")
            service.set_mode(ChatMode.AIM_AND_ASK)

            seeded_bot = mock_bot_cls.return_value
            seeded_bot.llm.messages.add_message.assert_any_call(
                role="user", text="F&F prompt"
            )
            seeded_bot.llm.messages.add_message.assert_any_call(
                role="assistant", text="F&F response"
            )
            assert service._last_fire_prompt is None
            assert service._last_fire_response is None

    def test_seed_only_happens_once(self) -> None:
        with patch("lever_action.services.chat_service.Bot") as mock_bot_cls:
            mock_intel = MagicMock()
            mock_intel.text = "Response"
            mock_bot = MagicMock()
            mock_bot.process.return_value = mock_intel
            mock_bot_cls.return_value = mock_bot

            service = ChatService()
            service.process("Prompt")
            service.set_mode(ChatMode.AIM_AND_ASK)
            first_seed_count = mock_bot_cls.call_count

            service.set_mode(ChatMode.FIRE_AND_FORGET)
            service.set_mode(ChatMode.AIM_AND_ASK)

            assert mock_bot_cls.call_count == first_seed_count

    def test_switch_to_aim_without_prior_fire_no_seed(self) -> None:
        with patch("lever_action.services.chat_service.Bot") as mock_bot_cls:
            mock_bot = MagicMock()
            mock_bot.process.return_value = MagicMock(text="ok")
            mock_bot_cls.return_value = mock_bot

            service = ChatService()
            service.set_mode(ChatMode.AIM_AND_ASK)

            assert mock_bot_cls.call_count == 0
            assert service._aim_bot is None

    def test_default_guideline_is_normal(self) -> None:
        service = ChatService()
        assert service.guideline_mode == GuidelineMode.NORMAL

    def test_set_guideline_mode_changes_mode(self) -> None:
        service = ChatService()
        service.set_guideline_mode(GuidelineMode.CONCISE)
        assert service.guideline_mode == GuidelineMode.CONCISE

    def test_concise_guideline_passed_to_bot_fire_and_forget(self) -> None:
        with patch("lever_action.services.chat_service.Bot") as mock_bot_cls:
            mock_bot = MagicMock()
            mock_bot.process.return_value = MagicMock(text="ok")
            mock_bot_cls.return_value = mock_bot

            service = ChatService()
            service.set_guideline_mode(GuidelineMode.CONCISE)
            service.process("Hello")

            mock_bot_cls.assert_called_once_with(
                guidelines=f"{CONCISE_GUIDELINE} {CODE_FORMAT_GUIDELINE}"
            )

    def test_normal_guideline_passes_none_to_bot(self) -> None:
        with patch("lever_action.services.chat_service.Bot") as mock_bot_cls:
            mock_bot = MagicMock()
            mock_bot.process.return_value = MagicMock(text="ok")
            mock_bot_cls.return_value = mock_bot

            service = ChatService()
            service.process("Hello")

            mock_bot_cls.assert_called_once_with(guidelines=CODE_FORMAT_GUIDELINE)

    def test_set_guideline_mode_updates_aim_bot_system_message(self) -> None:
        with patch("lever_action.services.chat_service.Bot") as mock_bot_cls:
            mock_bot = MagicMock()
            mock_bot.process.return_value = MagicMock(text="ok")
            mock_bot.role = "Assistant"
            mock_bot.task = "Provide a response based on the users request, context or instructions."
            mock_bot.system_override_prompt = None
            mock_bot_cls.return_value = mock_bot

            service = ChatService()
            service.set_mode(ChatMode.AIM_AND_ASK)
            service.process("First")

            service.set_guideline_mode(GuidelineMode.CONCISE)

            assert mock_bot.llm.messages.messages.__setitem__.called

    def test_default_target_is_empty(self) -> None:
        service = ChatService()
        assert service.target == ""

    def test_set_target_sets_value(self) -> None:
        service = ChatService()
        service.set_target("Python Django")
        assert service.target == "Python Django"

    def test_set_target_strips_whitespace(self) -> None:
        service = ChatService()
        service.set_target("  Python Django  ")
        assert service.target == "Python Django"

    def test_target_prepended_to_prompt_fire_and_forget(self) -> None:
        with patch("lever_action.services.chat_service.Bot") as mock_bot_cls:
            mock_bot = MagicMock()
            mock_bot.process.return_value = MagicMock(text="ok")
            mock_bot_cls.return_value = mock_bot

            service = ChatService()
            service.set_target("Python Django")
            service.process("How do I create a view?")

            mock_bot.process.assert_called_once_with(
                "[Context: Python Django]\n\nHow do I create a view?"
            )

    def test_target_prepended_to_prompt_aim_and_ask(self) -> None:
        with patch("lever_action.services.chat_service.Bot") as mock_bot_cls:
            mock_bot = MagicMock()
            mock_bot.process.return_value = MagicMock(text="ok")
            mock_bot_cls.return_value = mock_bot

            service = ChatService()
            service.set_mode(ChatMode.AIM_AND_ASK)
            service.set_target("Python Django")
            service.process("How do I create a view?")

            mock_bot.process.assert_called_once_with(
                "[Context: Python Django]\n\nHow do I create a view?"
            )

    def test_no_target_does_not_modify_prompt(self) -> None:
        with patch("lever_action.services.chat_service.Bot") as mock_bot_cls:
            mock_bot = MagicMock()
            mock_bot.process.return_value = MagicMock(text="ok")
            mock_bot_cls.return_value = mock_bot

            service = ChatService()
            service.process("Hello")

            mock_bot.process.assert_called_once_with("Hello")
