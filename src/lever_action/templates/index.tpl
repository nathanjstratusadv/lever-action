<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lever Action</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <link rel="stylesheet" href="/static/css/pygments.css">
</head>
<body>
    <div class="app">
        <main class="chat-area">
            <div class="messages" id="messages">
                <div class="welcome">
                    <h1>Aim. Shoot. Reload.</h1>
                    <p>Type a prompt below to fire your first shot.</p>
                </div>
            </div>
            <div class="input-area">
                <button id="settings-btn" class="settings-btn" onclick="openSettingsModal()">
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
                    <button id="guideline-btn" class="guideline-btn steady" onclick="toggleGuideline()">Steady</button>
                    <button id="send-btn" class="fire-mode" onclick="toggleMode()">Fire & Forget</button>
                </div>
                <span id="target-badge" class="target-badge" onclick="openTargetModal()">Target: None</span>
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
    <div id="settings-modal-overlay" class="modal-overlay" onclick="closeSettingsModal(event)">
        <div class="modal-content settings-modal" onclick="event.stopPropagation()">
            <div class="modal-header">
                <span>Settings</span>
                <button class="modal-close" onclick="closeSettingsModal()">&times;</button>
            </div>
            <div class="settings-form" id="settings-form">
                <div class="form-group">
                    <label for="settings-provider">LLM Provider</label>
                    <select id="settings-provider" onchange="onProviderChange()">
                        <option value="openai">OpenAI</option>
                        <option value="anthropic">Anthropic</option>
                        <option value="google">Google</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="settings-api-key">API Key</label>
                    <input type="password" id="settings-api-key" placeholder="sk-..." autocomplete="off">
                </div>
                <div class="form-group">
                    <label for="settings-model">Model</label>
                    <input type="text" id="settings-model" placeholder="gpt-4o-mini">
                </div>
                <div class="form-group">
                    <label for="settings-base-url">Base URL <span class="optional">(optional)</span></label>
                    <input type="text" id="settings-base-url" placeholder="https://api.openai.com">
                </div>
                <div class="form-group">
                    <label for="settings-temperature">Temperature: <span id="temp-value">0.7</span></label>
                    <input type="range" id="settings-temperature" min="0" max="2" step="0.1" value="0.7" oninput="updateTempDisplay()">
                </div>
                <div class="form-group">
                    <label for="settings-max-tokens">Max Tokens</label>
                    <input type="number" id="settings-max-tokens" min="1" max="32000" value="4096">
                </div>
                <div class="form-group">
                    <label for="settings-system-prompt">System Prompt <span class="optional">(optional)</span></label>
                    <textarea id="settings-system-prompt" placeholder="You are a helpful assistant..."></textarea>
                </div>
            </div>
            <div class="modal-actions">
                <button class="modal-btn cancel" onclick="closeSettingsModal()">Cancel</button>
                <button class="modal-btn save" onclick="saveSettings()">Save</button>
            </div>
        </div>
    </div>
    <script src="/static/js/app.js"></script>
</body>
</html>