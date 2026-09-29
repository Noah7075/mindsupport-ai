/**
 * WorkEase Guardian - Chat & Memory Controller
 * Connects natural conversation, overnight autonomy simulations,
 * and persistent Hindsight memory banking.
 */

// State
let chatHistory = [];
let voiceEnabled = false;
let synth = window.speechSynthesis;

// DOM Elements
const chatFeed = document.getElementById("chatFeed");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const simKnownBtn = document.getElementById("simKnownBtn");
const simNovelBtn = document.getElementById("simNovelBtn");
const hintChips = document.querySelectorAll(".hint-chip");

const safePlaybooksList = document.getElementById("safePlaybooksList");
const mistakesList = document.getElementById("mistakesList");
const policiesList = document.getElementById("policiesList");

// Modals
const openTeachModalBtn = document.getElementById("openTeachModalBtn");
const teachModal = document.getElementById("teachModal");
const closeTeachModalBtn = document.getElementById("closeTeachModalBtn");
const saveRuleBtn = document.getElementById("saveRuleBtn");
const ruleCategory = document.getElementById("ruleCategory");
const ruleText = document.getElementById("ruleText");

const settingsBtn = document.getElementById("settingsBtn");
const settingsModal = document.getElementById("settingsModal");
const closeSettingsModalBtn = document.getElementById("closeSettingsModalBtn");
const saveSettingsBtn = document.getElementById("saveSettingsBtn");
const geminiKey = document.getElementById("geminiKey");
const hindsightUrl = document.getElementById("hindsightUrl");
const hindsightKey = document.getElementById("hindsightKey");
const voiceToggleBtn = document.getElementById("voiceToggleBtn");


// Initialization
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  loadMemories();
});


function setupEventListeners() {
  // Simulations
  simKnownBtn.addEventListener("click", () => triggerOvernightSimulation("known_issue"));
  simNovelBtn.addEventListener("click", () => triggerOvernightSimulation("novel_issue"));

  // Chat Submission
  chatForm.addEventListener("submit", handleChatSubmit);

  // Quick hint chips
  hintChips.forEach(chip => {
    chip.addEventListener("click", () => {
      chatInput.value = chip.getAttribute("data-prompt");
      handleChatSubmit(new Event("submit"));
    });
  });

  // Voice toggle
  voiceToggleBtn.addEventListener("click", () => {
    voiceEnabled = !voiceEnabled;
    voiceToggleBtn.textContent = voiceEnabled ? "Voice: On" : "Voice: Off";
    if (voiceEnabled) {
      voiceToggleBtn.classList.add("active");
      speakText("Voice debrief activated.");
    } else {
      voiceToggleBtn.classList.remove("active");
      if (synth) synth.cancel();
    }
  });

  // Teach Rule Modal
  openTeachModalBtn.addEventListener("click", () => teachModal.classList.add("open"));
  closeTeachModalBtn.addEventListener("click", () => teachModal.classList.remove("open"));
  saveRuleBtn.addEventListener("click", handleSaveRule);

  // Settings Modal
  settingsBtn.addEventListener("click", () => settingsModal.classList.add("open"));
  closeSettingsModalBtn.addEventListener("click", () => settingsModal.classList.remove("open"));
  saveSettingsBtn.addEventListener("click", handleSaveSettings);
}


// Handle Overnight Simulation
async function triggerOvernightSimulation(scenarioType) {
  appendUserMessage(
    scenarioType === "known_issue" 
      ? "Simulate: What happened during the 2:14 AM checkout crash?" 
      : "Simulate: What happened during the 3:30 AM background worker crash?"
  );

  showTypingIndicator();

  try {
    const res = await fetch("/api/overnight", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario_type: scenarioType })
    });
    const data = await res.json();
    removeTypingIndicator();
    appendOvernightEventCard(data);

    if (voiceEnabled) {
      speakText(data.developer_summary);
    }
  } catch (err) {
    removeTypingIndicator();
    appendBotMessage(`Connection error: ${err.message}`);
  }
}


// Handle Normal Chat Message
async function handleChatSubmit(e) {
  if (e) e.preventDefault();
  const text = chatInput.value.trim();
  if (!text) return;

  appendUserMessage(text);
  chatInput.value = "";
  showTypingIndicator();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, history: chatHistory })
    });
    const data = await res.json();
    removeTypingIndicator();
    appendBotMessage(data.reply);

    if (data.memory_added) {
      loadMemories();
    }

    if (voiceEnabled) {
      speakText(data.reply);
    }
  } catch (err) {
    removeTypingIndicator();
    appendBotMessage(`Error communicating with Guardian: ${err.message}`);
  }
}


// Append User Message to Chat
function appendUserMessage(text) {
  const bubble = document.createElement("div");
  bubble.className = "chat-bubble user-bubble";
  bubble.innerHTML = `
    <div class="bubble-header">
      <span class="bubble-sender">You (Solo Developer)</span>
      <span class="bubble-time">Just now</span>
    </div>
    <div class="bubble-body">
      <p>${escapeHtml(text)}</p>
    </div>
  `;
  chatFeed.appendChild(bubble);
  chatFeed.scrollTop = chatFeed.scrollHeight;
  chatHistory.push({ role: "user", content: text });
}


// Append Bot Response
function appendBotMessage(text) {
  const bubble = document.createElement("div");
  bubble.className = "chat-bubble bot-bubble";
  bubble.innerHTML = `
    <div class="bubble-header">
      <span class="bubble-sender">Aegis Guardian</span>
      <span class="bubble-time">Just now</span>
    </div>
    <div class="bubble-body">
      <p>${escapeHtml(text)}</p>
    </div>
  `;
  chatFeed.appendChild(bubble);
  chatFeed.scrollTop = chatFeed.scrollHeight;
  chatHistory.push({ role: "assistant", content: text });
}


// Append Overnight Event Card to Chat
function appendOvernightEventCard(event) {
  const card = document.createElement("div");
  card.className = "incident-event-card";

  const isAutoFix = event.autonomy_decision === "AUTONOMOUS_FIX_APPLIED";
  const badgeClass = isAutoFix ? "badge-auto-fix" : "badge-containment";
  const badgeLabel = isAutoFix ? "Autonomous Safe Fix Applied" : "Safety Containment Only (Risk Blocked)";

  card.innerHTML = `
    <div class="event-card-header">
      <span class="event-time-code">${event.scenario_id} • ${event.timestamp}</span>
      <span class="event-decision-badge ${badgeClass}">${badgeLabel}</span>
    </div>

    <div class="event-summary-text">
      ${event.developer_summary}
    </div>

    <div class="event-details-grid">
      <div class="detail-item">
        <strong>Target Service</strong>
        <span>${event.service}</span>
      </div>
      <div class="detail-item">
        <strong>Error Caught</strong>
        <span>${event.error_code}</span>
      </div>
      <div class="detail-item">
        <strong>Hindsight Memory Match</strong>
        <span>${event.matched_memory_id ? `${event.matched_memory_id} (${event.confidence_score}% Confidence)` : '0% (Novel Issue)'}</span>
      </div>
      <div class="detail-item">
        <strong>Action Executed</strong>
        <span>${event.action_taken}</span>
      </div>
    </div>

    <div class="event-comparison-box">
      <strong>Why a Standard Dumb AI Would Have Failed:</strong>
      ${event.dumb_ai_comparison}
    </div>
  `;

  chatFeed.appendChild(card);
  chatFeed.scrollTop = chatFeed.scrollHeight;
}


// Typing Indicator
function showTypingIndicator() {
  const typing = document.createElement("div");
  typing.id = "typingIndicator";
  typing.className = "chat-bubble bot-bubble";
  typing.innerHTML = `
    <div class="bubble-body" style="padding: 10px 16px; color: #64748b; font-style: italic;">
      Guardian is querying Hindsight memory...
    </div>
  `;
  chatFeed.appendChild(typing);
  chatFeed.scrollTop = chatFeed.scrollHeight;
}

function removeTypingIndicator() {
  const el = document.getElementById("typingIndicator");
  if (el) el.remove();
}


// Load & Categorize Memories from Hindsight
async function loadMemories() {
  try {
    const res = await fetch("/api/memories");
    const data = await res.json();
    const memories = data.memories || [];
    renderMemoryCategories(memories);
  } catch (err) {
    console.error("Failed to load memories:", err);
  }
}

function renderMemoryCategories(memories) {
  safePlaybooksList.innerHTML = "";
  mistakesList.innerHTML = "";
  policiesList.innerHTML = "";

  memories.forEach(m => {
    // 1. Safe Playbooks
    if (m.runbook_command && !m.tags?.includes("policy")) {
      const card = document.createElement("div");
      card.className = "memory-card";
      card.innerHTML = `
        <div class="memory-card-top">
          <span class="memory-id">${m.incident_id}</span>
          <span class="memory-stage">Auto-Allowed</span>
        </div>
        <div class="memory-title">${m.title}</div>
        <div class="memory-body">${m.successful_resolution}</div>
        <div class="memory-runbook"><code>${m.runbook_command}</code></div>
      `;
      safePlaybooksList.appendChild(card);
    }

    // 2. Mistakes to Avoid
    if (m.failed_attempts && m.failed_attempts.length > 0) {
      m.failed_attempts.forEach(fail => {
        const card = document.createElement("div");
        card.className = "memory-card";
        card.style.borderLeft = "3px solid #ef4444";
        card.innerHTML = `
          <div class="memory-card-top">
            <span class="memory-id">Anti-Pattern</span>
            <span class="memory-stage" style="color: #ef4444;">Never Do This</span>
          </div>
          <div class="memory-body">${fail}</div>
        `;
        mistakesList.appendChild(card);
      });
    }

    // 3. Policies / Rules
    if (m.tags?.includes("policy") || m.tags?.includes("developer-rule")) {
      const card = document.createElement("div");
      card.className = "memory-card";
      card.style.borderLeft = "3px solid #2563eb";
      card.innerHTML = `
        <div class="memory-card-top">
          <span class="memory-id">${m.incident_id}</span>
          <span class="memory-stage" style="color: #2563eb;">Policy</span>
        </div>
        <div class="memory-title">${m.title}</div>
        <div class="memory-body">${m.root_cause}</div>
      `;
      policiesList.appendChild(card);
    }
  });

  // Default fallbacks if empty
  if (!safePlaybooksList.children.length) {
    safePlaybooksList.innerHTML = `<div style="font-size:12px; color:#94a3b8;">No playbooks recorded yet.</div>`;
  }
}


// Save New Rule
async function handleSaveRule() {
  const text = ruleText.value.trim();
  const cat = ruleCategory.value;
  if (!text) {
    alert("Please enter a rule description.");
    return;
  }

  try {
    const res = await fetch("/api/teach", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rule_text: text, category: cat })
    });
    const data = await res.json();
    teachModal.classList.remove("open");
    ruleText.value = "";
    appendBotMessage(`I have committed your new rule to Hindsight memory: "${text}". I will enforce this rule going forward.`);
    loadMemories();
  } catch (err) {
    alert("Error saving rule: " + err.message);
  }
}


// Save Settings
async function handleSaveSettings() {
  const payload = {
    gemini_api_key: geminiKey.value.trim() || null,
    hindsight_base_url: hindsightUrl.value.trim() || null,
    hindsight_api_key: hindsightKey.value.trim() || null
  };

  try {
    await fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    settingsModal.classList.remove("open");
    alert("Configuration updated successfully.");
  } catch (err) {
    alert("Settings error: " + err.message);
  }
}


// Speech Synthesis
function speakText(text) {
  if (!voiceEnabled || !synth) return;
  synth.cancel();

  const clean = text.replace(/[*#`_~]/g, "");
  const utterance = new SpeechSynthesisUtterance(clean);
  utterance.rate = 1.0;
  synth.speak(utterance);
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
