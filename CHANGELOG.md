# Changelog

## [0.3.0] - 2026-05-12

### Added
- Persistent settings storage with automatic version migration
- Windows Package Manager (winget) submission workflow
- Inno Setup MSI installer build support
- App version displayed in browser title bar

### Changed
- Settings modal opens automatically when no API key is configured
- Simplified settings form: removed provider selection, temperature, max tokens, and system prompt fields
- Settings now use host/port instead of base URL

### Removed
- Multi-provider support (OpenAI, Anthropic, Google) — single LLM provider
- Icon generation script and standalone icon assets

## [0.2.0] - 2026-05-12

### Fixed
- Text can now be highlighted and copied from chat messages
- Fire & Forget to Aim & Ask transition now properly carries the last message including target context
- Code blocks now render with proper containment to prevent styling overflow

### Added
- Up/Down arrow navigation through prompt history in the input field
- Ctrl+R hotkey to reset chat
- Ctrl+, hotkey to open settings
- Tooltips on hover for all buttons showing function and hotkey
- Guide tab in settings modal with modes, guidelines, hotkeys, and target context documentation
- Keyboard scrolling for messages container (Arrow keys, Page Up/Down, Home, End)
- Ctrl+Up/Down scrolling while focused on input field
- CHANGELOG.md for tracking version changes

### Changed
- Improved scrollbar styling with track background and inset thumb
- Larger settings modal with tabbed interface
- Input area and button heights aligned to 48px
- Smoother scroll behavior and overscroll containment on messages

## [0.1.0] - 2026-05-08

### Added
- Initial release: native Windows AI chat web app
- Bottle web framework hosted in pywebview window
- Dandy LLM integration with fire-and-forget and aim-and-ask modes
- Per-user JSON chat history storage
- In-memory session management with token-based auth
- Configurable chat modes, guidelines, and target context
- Dark theme UI with markdown and code highlighting support
- PyInstaller executable builds
