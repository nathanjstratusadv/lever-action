<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lever Action v{{ version }}</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <link rel="stylesheet" href="/static/css/pygments.css">
    <style>
        .welcome h1 {
            font-size: 28px;
            letter-spacing: 4px;
            text-transform: uppercase;
        }

        .welcome-star-container {
            display: flex;
            justify-content: center;
            margin: 16px 0;
            position: relative;
            height: 48px;
        }

        .welcome-star-back {
            position: absolute;
            color: #6a4020;
        }

        .welcome-star-front {
            position: relative;
            color: #b87333;
        }
    </style>
</head>
<body>
    <div class="app">
        <main class="chat-area">
            <div class="messages" id="messages">
                <div class="welcome">
                    <h1>AIM • SHOOT • RELOAD</h1>
                    <div class="welcome-star-container">
                        <svg class="welcome-star-back" width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
                            <polygon points="12,2 15,9 22,9 16,14 18,21 12,17 6,21 8,14 2,9 9,9"/>
                        </svg>
                        <svg class="welcome-star-front" width="40" height="40" viewBox="0 0 24 24" fill="currentColor">
                            <polygon points="12,2 15,9 22,9 16,14 18,21 12,17 6,21 8,14 2,9 9,9"/>
                        </svg>
                    </div>
                    <p>Type a prompt below to fire your first shot.</p>
                </div>
            </div>
            <div class="input-area">
                <button id="settings-btn" class="settings-btn" onclick="openSettingsModal()" tooltip="Settings (Ctrl+,)">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="3"></circle>
                        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                    </svg>
                </button>
                <div class="input-wrapper">
                    <textarea
                        id="prompt-input"
                        placeholder="Aim your prompt..."
                        onkeydown="handleKeydown(event)"
                        oninput="autoResize(this)"
                    ></textarea>
                </div>
                <div class="send-buttons">
                    <button id="guideline-btn" class="guideline-btn steady" onclick="toggleGuideline()" tooltip="Toggle guideline (Ctrl+Shift+Enter)">Steady</button>
                    <button id="send-btn" class="fire-mode" onclick="toggleMode()" tooltip="Toggle mode (Ctrl+Enter)">Fire & Forget</button>
                </div>
                <span id="target-badge" class="target-badge" onclick="openTargetModal()" tooltip="Target context (Ctrl+Alt+Enter)">Target: None</span>
            </div>
        </main>
    </div>
    <div id="target-modal-overlay" class="modal-overlay" onclick="closeTargetModal(event)">
        <div class="modal-content" onclick="event.stopPropagation()">
            <div class="modal-header">
                <span>Target Context</span>
                <button class="modal-close" onclick="closeTargetModal()">&times;</button>
            </div>
            <p class="modal-description">Add fixed context to every message. Press Enter to save, Escape to cancel.</p>
            <textarea
                id="target-input"
                placeholder="e.g. Python Django REST framework..."
                onkeydown="handleTargetKeydown(event)"
            ></textarea>
            <div class="modal-actions">
                <button class="modal-btn cancel" onclick="closeTargetModal()">Cancel</button>
                <button class="modal-btn save" onclick="saveTarget()">Save</button>
            </div>
        </div>
    </div>
    <div id="settings-modal-overlay" class="modal-overlay" onclick="closeSettingsModal(event)" tabindex="-1">
        <div class="modal-content settings-modal" onclick="event.stopPropagation()" tabindex="-1">
            <div class="modal-tabs">
                <button class="modal-tab active" data-tab="settings" onclick="switchSettingsTab('settings')">Settings</button>
                <button class="modal-tab" data-tab="guide" onclick="switchSettingsTab('guide')">Guide</button>
                <button class="modal-close" onclick="closeSettingsModal()">&times;</button>
            </div>
            <div class="tab-content" id="settings-tab">
                <div class="settings-form" id="settings-form">
                    <div class="form-group">
                        <label for="settings-host">Host</label>
                        <input type="text" id="settings-host" placeholder="https://api.openai.com">
                    </div>
                    <div class="form-group">
                        <label for="settings-port">Port</label>
                        <input type="number" id="settings-port" min="1" max="65535" value="443">
                    </div>
                    <div class="form-group">
                        <label for="settings-api-key">API Key</label>
                        <input type="password" id="settings-api-key" placeholder="sk-..." autocomplete="off">
                    </div>
                    <div class="form-group">
                        <label for="settings-model">Model</label>
                        <input type="text" id="settings-model" placeholder="gpt-4o-mini">
                    </div>
                </div>
                <div class="modal-actions">
                    <button class="modal-btn cancel" onclick="closeSettingsModal()">Cancel</button>
                    <button class="modal-btn save" onclick="saveSettings()">Save</button>
                </div>
            </div>
            <div class="tab-content hidden" id="guide-tab">
                <div class="guide-content">
                    <h3>Modes</h3>
                    <div class="guide-section">
                        <div class="guide-item">
                            <span class="guide-label">Fire & Forget</span>
                            <span class="guide-desc">Each message starts fresh. Great for quick, independent queries.</span>
                        </div>
                        <div class="guide-item">
                            <span class="guide-label">Aim & Ask</span>
                            <span class="guide-desc">Maintains conversation context. Best for iterative work and follow-ups.</span>
                        </div>
                    </div>
                    <h3>Guideline</h3>
                    <div class="guide-section">
                        <div class="guide-item">
                            <span class="guide-label">Steady</span>
                            <span class="guide-desc">Normal response length. Balanced detail.</span>
                        </div>
                        <div class="guide-item">
                            <span class="guide-label">Quick</span>
                            <span class="guide-desc">Concise responses. Shorter, to-the-point answers.</span>
                        </div>
                    </div>
                    <h3>Target Context</h3>
                    <div class="guide-section">
                        <p class="guide-desc">Add persistent context that prepends to every prompt. Click the Target badge to set.</p>
                    </div>
                    <h3>Hot Keys</h3>
                    <div class="guide-section">
                        <div class="guide-item">
                            <kbd>Enter</kbd>
                            <span class="guide-desc">Send prompt</span>
                        </div>
                        <div class="guide-item">
                            <kbd>Shift + Enter</kbd>
                            <span class="guide-desc">New line in prompt</span>
                        </div>
                        <div class="guide-item">
                            <kbd>Ctrl + Enter</kbd>
                            <span class="guide-desc">Toggle mode (Fire &amp; Forget / Aim &amp; Ask)</span>
                        </div>
                        <div class="guide-item">
                            <kbd>Ctrl + Shift + Enter</kbd>
                            <span class="guide-desc">Toggle guideline (Steady / Quick)</span>
                        </div>
                        <div class="guide-item">
                            <kbd>Ctrl + Alt + Enter</kbd>
                            <span class="guide-desc">Open target modal</span>
                        </div>
                        <div class="guide-item">
                            <kbd>Ctrl + Shift + C</kbd>
                            <span class="guide-desc">Copy last response to clipboard</span>
                        </div>
                        <div class="guide-item">
                            <kbd>Ctrl + ,</kbd>
                            <span class="guide-desc">Open settings</span>
                        </div>
                        <div class="guide-item">
                            <kbd>Ctrl + R</kbd>
                            <span class="guide-desc">Reset chat</span>
                        </div>
                        <div class="guide-item">
                            <kbd>Escape</kbd>
                            <span class="guide-desc">Close modals</span>
                        </div>
                        <div class="guide-item">
                            <kbd>Ctrl + Up</kbd>
                            <span class="guide-desc">Scroll messages up (while typing)</span>
                        </div>
                        <div class="guide-item">
                            <kbd>Ctrl + Down</kbd>
                            <span class="guide-desc">Scroll messages down (while typing)</span>
                        </div>
                        <div class="guide-item">
                            <kbd>Arrow Up/Down</kbd>
                            <span class="guide-desc">Navigate prompt history (when typing)</span>
                        </div>
                        <div class="guide-item">
                            <kbd>Arrow Up/Down</kbd>
                            <span class="guide-desc">Scroll messages (when focused)</span>
                        </div>
                        <div class="guide-item">
                            <kbd>Page Up/Down</kbd>
                            <span class="guide-desc">Scroll messages by page (when focused)</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script src="/static/js/app.js"></script>
</body>
</html>