let currentMode = "fire_and_forget";
let currentGuideline = "normal";
let currentTarget = "";
let currentSettings = {};

async function sendPrompt() {
    const input = document.getElementById("prompt-input");
    const btn = document.getElementById("send-btn");
    const prompt = input.value.trim();

    if (!prompt) return;

    const messages = document.getElementById("messages");
    const welcome = messages.querySelector(".welcome");
    if (welcome) welcome.remove();

    const msgEl = appendPromptOnly(prompt, currentMode);

    showLoading(currentMode);

    input.disabled = true;
    btn.disabled = true;
    document.getElementById("guideline-btn").disabled = true;
    btn.textContent = "Reloading...";

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt }),
        });

        if (!res.ok) {
            const errData = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
            throw new Error(errData.error || `Request failed with status ${res.status}`);
        }

        const data = await res.json();

        clearLoading();
        completeMessage(msgEl, data.response_html);

        input.value = "";
        autoResize(input);
    } catch (err) {
        clearLoading();
        setErrorOnMessage(msgEl, err.message);
    } finally {
        input.disabled = false;
        btn.disabled = false;
        document.getElementById("guideline-btn").disabled = false;
        updateButtonText();
        input.focus();
    }
}

async function loadLastEntry() {
    try {
        const res = await fetch("/history");
        const entries = await res.json();
        if (entries.length > 0) {
            const messages = document.getElementById("messages");
            messages.innerHTML = "";
            appendMessage(entries[0].prompt, entries[0].response_html);
        }
    } catch (err) {
        console.error("Failed to load history:", err);
    }
}

function appendMessage(prompt, responseHtml, mode) {
    const messages = document.getElementById("messages");
    const div = document.createElement("div");
    div.className = "message";
    div.innerHTML = `
        ${modeBadge(mode)}
        <div class="prompt-label">Prompt</div>
        <div class="prompt-text">${escapeHtml(prompt)}</div>
        <div class="prompt-label">Response</div>
        <div class="response-text">${responseHtml}</div>
    `;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

function modeBadge(mode) {
    return mode === "aim_and_ask"
        ? '<span class="mode-badge aim">Aim & Ask</span>'
        : '<span class="mode-badge fire">Fire & Forget</span>';
}

function appendPromptOnly(prompt, mode) {
    const messages = document.getElementById("messages");
    const div = document.createElement("div");
    div.className = "message";
    div.innerHTML = `
        ${modeBadge(mode)}
        <div class="prompt-label">Prompt</div>
        <div class="prompt-text">${escapeHtml(prompt)}</div>
    `;
    messages.appendChild(div);
    div.scrollIntoView({ behavior: "smooth", block: "start" });
    return div;
}

function completeMessage(el, responseHtml) {
    el.innerHTML += `
        <div class="prompt-label">Response</div>
        <div class="response-text">${responseHtml}</div>
    `;
    el.scrollIntoView({ behavior: "smooth", block: "start" });
}

function setErrorOnMessage(el, message) {
    el.innerHTML += `
        <div class="response-text" style="color: #f44;">
            <strong>Error:</strong> ${escapeHtml(message)}
        </div>
    `;
    el.scrollIntoView({ behavior: "smooth", block: "start" });
}

function showLoading(mode) {
    const messages = document.getElementById("messages");
    const loading = document.createElement("div");
    loading.className = "message";
    loading.id = "loading-indicator";
    const color = mode === "aim_and_ask" ? "#0078d4" : "#d43030";
    loading.innerHTML = `
        <div class="loading-dots" style="--dot-color: ${color};">
            <span></span><span></span><span></span>
        </div>
    `;
    messages.appendChild(loading);
    messages.scrollTop = messages.scrollHeight;
}

function clearLoading() {
    const el = document.getElementById("loading-indicator");
    if (el) el.remove();
}

function autoResize(el) {
    el.style.height = "48px";
    const newHeight = Math.min(el.scrollHeight, 200);
    el.style.height = Math.max(newHeight, 48) + "px";
}

function handleKeydown(e) {
    if (e.key === "," && e.ctrlKey) {
        e.preventDefault();
        openSettingsModal();
    } else if (e.key === "Enter" && e.ctrlKey && e.shiftKey) {
        e.preventDefault();
        toggleGuideline();
    } else if (e.key === "Enter" && e.ctrlKey && e.altKey) {
        e.preventDefault();
        openTargetModal();
    } else if (e.key === "Enter" && e.ctrlKey) {
        e.preventDefault();
        toggleMode();
    } else if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendPrompt();
    }
}

function handleTargetKeydown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        saveTarget();
    } else if (e.key === "Escape") {
        e.preventDefault();
        closeTargetModal();
    }
}

function openTargetModal() {
    const overlay = document.getElementById("target-modal-overlay");
    const input = document.getElementById("target-input");
    overlay.style.display = "flex";
    input.value = currentTarget;
    setTimeout(() => input.focus(), 50);
}

function closeTargetModal(e) {
    if (e && e.target && e.target !== document.getElementById("target-modal-overlay")) return;
    const overlay = document.getElementById("target-modal-overlay");
    overlay.style.display = "none";
    refocusInput();
}

async function saveTarget() {
    const input = document.getElementById("target-input");
    const value = input.value.trim();
    try {
        const res = await fetch("/target", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ target: value }),
        });
        if (!res.ok) return;
        currentTarget = value;
        updateTargetBadge();
        closeTargetModal();
    } catch (err) {
        console.error("Failed to save target:", err);
    }
}

function openSettingsModal(tab = "settings") {
    const overlay = document.getElementById("settings-modal-overlay");
    overlay.style.display = "flex";
    if (tab === "guide") {
        switchSettingsTab("guide");
    } else {
        switchSettingsTab("settings");
        populateSettingsForm();
        setTimeout(() => document.getElementById("settings-api-key").focus(), 50);
    }

    const settingsKeyHandler = (e) => {
        if (e.key === "Enter" && !e.shiftKey && e.target.tagName !== "TEXTAREA") {
            e.preventDefault();
            saveSettings();
            document.removeEventListener("keydown", settingsKeyHandler);
        } else if (e.key === "Escape") {
            e.preventDefault();
            closeSettingsModal();
            document.removeEventListener("keydown", settingsKeyHandler);
        }
    };
    document.addEventListener("keydown", settingsKeyHandler);
}

function switchSettingsTab(tabName) {
    const tabs = document.querySelectorAll(".modal-tab");
    const settingsContent = document.getElementById("settings-tab");
    const guideContent = document.getElementById("guide-tab");

    tabs.forEach(tab => {
        if (tab.dataset.tab === tabName) {
            tab.classList.add("active");
        } else {
            tab.classList.remove("active");
        }
    });

    if (tabName === "settings") {
        settingsContent.classList.remove("hidden");
        guideContent.classList.add("hidden");
    } else {
        settingsContent.classList.add("hidden");
        guideContent.classList.remove("hidden");
    }
}

function closeSettingsModal(e) {
    if (e && e.target && e.target !== document.getElementById("settings-modal-overlay")) return;
    document.getElementById("settings-modal-overlay").style.display = "none";
    refocusInput();
}

function populateSettingsForm() {
    document.getElementById("settings-host").value = currentSettings.host || "";
    document.getElementById("settings-port").value = currentSettings.port || 443;
    document.getElementById("settings-api-key").value = currentSettings.api_key || "";
    document.getElementById("settings-model").value = currentSettings.model || "";
}

async function loadSettings() {
    try {
        const res = await fetch("/settings");
        if (!res.ok) return false;
        currentSettings = await res.json();
        return true;
    } catch (err) {
        console.error("Failed to load settings:", err);
        return false;
    }
}

async function saveSettings() {
    const settings = {
        host: document.getElementById("settings-host").value,
        port: parseInt(document.getElementById("settings-port").value) || 443,
        api_key: document.getElementById("settings-api-key").value,
        model: document.getElementById("settings-model").value,
    };

    try {
        const res = await fetch("/settings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(settings),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.error || "Failed to save settings");
        }
        currentSettings = settings;
        closeSettingsModal();
        document.getElementById("prompt-input").focus();
    } catch (err) {
        console.error("Failed to save settings:", err);
        alert("Failed to save settings: " + err.message);
    }
}

function updateTargetBadge() {
    const badge = document.getElementById("target-badge");
    if (currentTarget) {
        badge.textContent = "Target: " + currentTarget;
        badge.classList.remove("empty");
        badge.classList.add("set");
    } else {
        badge.textContent = "Target: None";
        badge.classList.remove("set");
        badge.classList.add("empty");
    }
}

async function loadTarget() {
    try {
        const res = await fetch("/target");
        if (!res.ok) return;
        const data = await res.json();
        currentTarget = data.target;
        updateTargetBadge();
    } catch (err) {
        console.error("Failed to load target:", err);
    }
}

function updateButtonText() {
    const sendBtn = document.getElementById("send-btn");
    const guidelineBtn = document.getElementById("guideline-btn");

    if (currentMode === "aim_and_ask") {
        sendBtn.textContent = "Aim & Ask";
        sendBtn.classList.remove("fire-mode");
        sendBtn.classList.add("aim-mode");
    } else {
        sendBtn.textContent = "Fire & Forget";
        sendBtn.classList.remove("aim-mode");
        sendBtn.classList.add("fire-mode");
    }

    guidelineBtn.textContent = currentGuideline === "concise" ? "Quick" : "Steady";
    guidelineBtn.classList.remove("quick", "steady");
    guidelineBtn.classList.add(currentGuideline === "concise" ? "quick" : "steady");
}

function toggleMode() {
    const next = currentMode === "fire_and_forget" ? "aim_and_ask" : "fire_and_forget";
    setMode(next);
}

async function setMode(mode) {
    if (mode === currentMode) return;

    try {
        const res = await fetch("/mode", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mode }),
        });

        if (!res.ok) return;

        currentMode = mode;
        updateButtonText();
    } catch (err) {
        console.error("Failed to set mode:", err);
    }
}

function toggleGuideline() {
    const next = currentGuideline === "normal" ? "concise" : "normal";
    setGuideline(next);
}

async function setGuideline(guideline) {
    if (guideline === currentGuideline) return;

    try {
        const res = await fetch("/guideline", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ guideline }),
        });

        if (!res.ok) return;

        currentGuideline = guideline;
        updateGuidelinePill();
    } catch (err) {
        console.error("Failed to set guideline:", err);
    }
}

function updateGuidelinePill() {
    updateButtonText();
}

function truncate(str, max) {
    return str.length > max ? str.slice(0, max) + "..." : str;
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

function refocusInput() {
    const input = document.getElementById("prompt-input");
    if (!input.disabled) {
        input.focus();
    }
}

let idleTimer = null;

function resetIdleTimer() {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(refocusInput, 10000);
}

document.addEventListener("DOMContentLoaded", async () => {
    await loadLastEntry();
    await loadTarget();
    const settingsLoaded = await loadSettings();

    if (!settingsLoaded || !currentSettings.api_key) {
        openSettingsModal();
    }

    updateButtonText();
    updateGuidelinePill();
    const input = document.getElementById("prompt-input");
    autoResize(input);
    input.focus();

    const messagesContainer = document.getElementById("messages");

    messagesContainer.addEventListener("keydown", (e) => {
        if (e.key === "ArrowDown" || e.key === "PageDown") {
            e.preventDefault();
            messagesContainer.scrollBy({ top: 100, behavior: "smooth" });
        } else if (e.key === "ArrowUp" || e.key === "PageUp") {
            e.preventDefault();
            messagesContainer.scrollBy({ top: -100, behavior: "smooth" });
        } else if (e.key === "Home") {
            e.preventDefault();
            messagesContainer.scrollTo({ top: 0, behavior: "smooth" });
        } else if (e.key === "End") {
            e.preventDefault();
            messagesContainer.scrollTo({ top: messagesContainer.scrollHeight, behavior: "smooth" });
        }
    });

    messagesContainer.setAttribute("tabindex", "0");

    document.addEventListener("keydown", (e) => {
        if (e.target === input && (e.key === "ArrowDown" || e.key === "ArrowUp") && e.ctrlKey) {
            e.preventDefault();
            if (e.key === "ArrowDown") {
                messagesContainer.scrollBy({ top: 100, behavior: "smooth" });
            } else if (e.key === "ArrowUp") {
                messagesContainer.scrollBy({ top: -100, behavior: "smooth" });
            }
        }
    });

    document.addEventListener("mousemove", resetIdleTimer);
    document.addEventListener("keydown", resetIdleTimer);

    window.addEventListener("focus", () => {
        refocusInput();
    });

    resetIdleTimer();
});
