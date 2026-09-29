/**
 * Aegis Guardian - Frontend Controller
 * Features slide-out Hindsight Memory Bank drawer,
 * category filtering, custom category input, simulation modal, and chat clearing.
 */

// State
let chatHistory = [];
let voiceEnabled = false;
let synth = window.speechSynthesis;
let allCategorizedMemories = [];
let currentCategoryFilter = "all";

// DOM Elements - Chat & Controls
const chatFeed = document.getElementById("chatFeed");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const clearChatBtn = document.getElementById("clearChatBtn");
const hintChips = document.querySelectorAll(".hint-chip");

// Incident Lab & Real Outage Testing Elements
const openSimModalBtn = document.getElementById("openSimModalBtn");
const simModal = document.getElementById("simModal");
const closeSimModalBtn = document.getElementById("closeSimModalBtn");
const tabPresetLogs = document.getElementById("tabPresetLogs");
const tabCustomLogs = document.getElementById("tabCustomLogs");
const panelPresetLogs = document.getElementById("panelPresetLogs");
const panelCustomLogs = document.getElementById("panelCustomLogs");
const btnAnalyzeCustomLog = document.getElementById("btnAnalyzeCustomLog");
const customLogService = document.getElementById("customLogService");
const customLogText = document.getElementById("customLogText");

// Real Outage Stack Trace Presets
const PRESET_LOGS = {
  redis_oom: {
    service: "checkout-api",
    scenario_name: "Redis OOM: maxmemory Exceeded by Unbounded Cache",
    log_content: `[2026-09-29 03:14:22] redis-server[2819]: OOM command not allowed when used memory > 'maxmemory' (2097152000 bytes)
[2026-09-29 03:14:22] celery.worker.consumer[102]: celery.exceptions.OperationalError: Error 500: OOM command not allowed
Traceback (most recent call last):
  File "/app/services/checkout.py", line 88, in reserve_stock
    redis_client.setex(f"stock_lock:{sku}", 300, order_id)
redis.exceptions.ResponseError: OOM command not allowed when used memory > 'maxmemory'.`
  },
  postgres_disk: {
    service: "db-primary",
    scenario_name: "PostgreSQL Disk Volume Full: WAL Archiving Panic",
    log_content: `[2026-09-29 04:02:11] postgres[18221]: [3-1] PANIC: could not write to file "pg_wal/xlogtemp.18221": No space left on device
[2026-09-29 04:02:12] postgres[18221]: [3-2] HINT: Check free disk space on data partition (/var/lib/postgresql/data).
[2026-09-29 04:02:15] app.db.pool[901]: asyncpg.exceptions.DiskFullError: disk full: 99.8% volume capacity reached`
  },
  checkout_pool: {
    service: "checkout-api-gateway",
    scenario_name: "Checkout Connection Pool Exhaustion (504 Timeout)",
    log_content: `HTTP 504: Upstream DB connection pool exhausted. Active: 150/150, Waiting threads: 842.
Traceback (most recent call last):
  File "/app/routes/checkout.py", line 142, in process_payment
    async with db.pool.acquire(timeout=15.0) as conn:
asyncpg.exceptions.PoolTimeoutError: connection acquisition timeout: pool exhausted`
  }
};

// Drawer Elements
const memoryDrawerBtn = document.getElementById("memoryDrawerBtn");
const memoryDrawer = document.getElementById("memoryDrawer");
const drawerBackdrop = document.getElementById("drawerBackdrop");
const closeDrawerBtn = document.getElementById("closeDrawerBtn");
const drawerMemoryList = document.getElementById("drawerMemoryList");
const drawerSearchInput = document.getElementById("drawerSearchInput");
const catTabs = document.querySelectorAll(".cat-tab");
const memoryBadgeCount = document.getElementById("memoryBadgeCount");

// Counter Spans
const catCountAll = document.getElementById("catCountAll");
const catCountPlaybooks = document.getElementById("catCountPlaybooks");
const catCountMistakes = document.getElementById("catCountMistakes");
const catCountPolicies = document.getElementById("catCountPolicies");

// Teach Rule Modal Elements
const openTeachModalBtn = document.getElementById("openTeachModalBtn");
const teachModal = document.getElementById("teachModal");
const closeTeachModalBtn = document.getElementById("closeTeachModalBtn");
const saveRuleBtn = document.getElementById("saveRuleBtn");
const ruleCategory = document.getElementById("ruleCategory");
const customCategoryGroup = document.getElementById("customCategoryGroup");
const customCategoryInput = document.getElementById("customCategoryInput");
const ruleText = document.getElementById("ruleText");

const voiceToggleBtn = document.getElementById("voiceToggleBtn");


// Initialization
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  loadMemories();
});


function setupEventListeners() {
  // Drawer open / close
  memoryDrawerBtn.addEventListener("click", openDrawer);
  closeDrawerBtn.addEventListener("click", closeDrawer);
  drawerBackdrop.addEventListener("click", closeDrawer);

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeDrawer();
      teachModal.classList.remove("open");
      simModal.classList.remove("open");
    }
  });

  // Drawer Category Tabs
  catTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      catTabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      currentCategoryFilter = tab.getAttribute("data-category");
      renderFilteredDrawerCards();
    });
  });

  // Drawer Search & Clear All
  drawerSearchInput.addEventListener("input", renderFilteredDrawerCards);
  const clearAllMemoriesBtn = document.getElementById("clearAllMemoriesBtn");
  if (clearAllMemoriesBtn) {
    clearAllMemoriesBtn.addEventListener("click", handleClearAllMemories);
  }

  // Incident Lab Modal Open & Close
  openSimModalBtn.addEventListener("click", () => simModal.classList.add("open"));
  closeSimModalBtn.addEventListener("click", () => simModal.classList.remove("open"));

  // Incident Lab Tabs
  if (tabPresetLogs && tabCustomLogs) {
    tabPresetLogs.addEventListener("click", () => {
      tabPresetLogs.classList.add("active");
      tabCustomLogs.classList.remove("active");
      panelPresetLogs.style.display = "block";
      panelCustomLogs.style.display = "none";
    });

    tabCustomLogs.addEventListener("click", () => {
      tabCustomLogs.classList.add("active");
      tabPresetLogs.classList.remove("active");
      panelCustomLogs.style.display = "block";
      panelPresetLogs.style.display = "none";
    });
  }

  // Preset Buttons: Run & Retest
  document.querySelectorAll(".btn-run-preset").forEach(btn => {
    btn.addEventListener("click", () => {
      const key = btn.getAttribute("data-preset");
      const preset = PRESET_LOGS[key];
      if (preset) {
        simModal.classList.remove("open");
        executeLogAnalysis(preset.log_content, preset.service, preset.scenario_name);
      }
    });
  });

  document.querySelectorAll(".btn-retest-preset").forEach(btn => {
    btn.addEventListener("click", () => {
      const key = btn.getAttribute("data-preset");
      const preset = PRESET_LOGS[key];
      if (preset) {
        simModal.classList.remove("open");
        executeLogAnalysis(preset.log_content, preset.service, preset.scenario_name);
      }
    });
  });

  // Custom Log Analysis
  if (btnAnalyzeCustomLog) {
    btnAnalyzeCustomLog.addEventListener("click", () => {
      const logText = customLogText.value.trim();
      if (!logText) {
        alert("Please paste some error logs or a stack trace to analyze.");
        return;
      }
      const service = customLogService.value.trim() || "api.production.app";
      simModal.classList.remove("open");
      executeLogAnalysis(logText, service, "Custom Outage Ingestion");
      customLogText.value = "";
    });
  }

  // Clear Chat Button
  clearChatBtn.addEventListener("click", resetChatFeed);

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
  openTeachModalBtn.addEventListener("click", () => {
    teachModal.classList.add("open");
  });
  closeTeachModalBtn.addEventListener("click", () => teachModal.classList.remove("open"));
  
  // Custom Category Toggle ("Other")
  ruleCategory.addEventListener("change", () => {
    if (ruleCategory.value === "Other") {
      customCategoryGroup.style.display = "flex";
      customCategoryInput.focus();
    } else {
      customCategoryGroup.style.display = "none";
    }
  });

  saveRuleBtn.addEventListener("click", handleSaveRule);
}


// Reset & Clear Chat Feed
function resetChatFeed() {
  chatFeed.innerHTML = `
    <div class="chat-bubble bot-bubble">
      <div class="bubble-header">
        <span class="bubble-sender">Aegis Guardian</span>
        <span class="bubble-time">Just now</span>
      </div>
      <div class="bubble-body">
        <p>Chat cleared. I am monitoring your production services with <strong>Gemini 2.5 Flash</strong> and <strong>Hindsight Cloud</strong> (Bank: <code>production-app</code>).</p>
        <p>All services are healthy (latency: 38ms). Click <strong>Try Simulation</strong> above to test an outage scenario or ask a question below.</p>
      </div>
    </div>
  `;
  chatHistory = [];
}


// Drawer Open / Close
function openDrawer() {
  memoryDrawer.classList.add("open");
  drawerBackdrop.classList.add("open");
}

function closeDrawer() {
  memoryDrawer.classList.remove("open");
  drawerBackdrop.classList.remove("open");
}


// Execute Log Analysis (Novel diagnosis & learning or Hindsight autonomous match)
async function executeLogAnalysis(logContent, service, scenarioName) {
  const shortSnippet = logContent.split("\n").slice(0, 3).join("\n");
  appendUserMessage(`Analyzing Live Telemetry: ${scenarioName || service}\n\n${shortSnippet}`);

  showTypingIndicator();

  try {
    const res = await fetch("/api/incidents/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        log_content: logContent,
        service: service,
        scenario_name: scenarioName
      })
    });
    const data = await res.json();
    removeTypingIndicator();
    appendIncidentAnalysisCard(data, logContent);

    // If novel incident was learned & stored in Hindsight, reload memory bank!
    if (data.status === "NOVEL_RESOLVED_AND_STORED" || data.retained_memory) {
      loadMemories();
    }

    if (voiceEnabled) {
      speakText(data.developer_summary);
    }
  } catch (err) {
    removeTypingIndicator();
    appendBotMessage(`Incident Analysis Error: ${err.message}`);
  }
}

// Backward-compatible trigger for overnight sim
async function triggerOvernightSimulation(scenarioType) {
  const key = scenarioType === "known_issue" ? "checkout_pool" : "redis_oom";
  const preset = PRESET_LOGS[key];
  if (preset) {
    executeLogAnalysis(preset.log_content, preset.service, preset.scenario_name);
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
      <span class="bubble-sender">You (Developer)</span>
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


// Append Incident Analysis Card to Chat
function appendIncidentAnalysisCard(event, originalLog) {
  const card = document.createElement("div");
  card.className = "incident-event-card";

  const isAutoFix = event.status === "AUTONOMOUS_FIX_APPLIED" || event.is_match;
  const badgeClass = isAutoFix ? "badge-auto-fix" : "badge-learned";
  const badgeLabel = isAutoFix 
    ? `Autonomous Safe Fix Applied (${event.confidence_score}% Hindsight Match)` 
    : `Novel Incident Learned & Stored in Hindsight Cloud`;

  card.innerHTML = `
    <div class="event-card-header">
      <span class="event-time-code">${event.scenario_id || event.incident_id} &bull; Just now</span>
      <span class="event-decision-badge ${badgeClass}">${badgeLabel}</span>
    </div>

    <div class="event-summary-text">
      ${event.developer_summary}
    </div>

    <div class="event-details-grid">
      <div class="detail-item">
        <strong>Target Service</strong>
        <span>${event.service || 'Production Gateway'}</span>
      </div>
      <div class="detail-item">
        <strong>Hindsight Memory Match</strong>
        <span>${event.matched_memory_id ? `${event.matched_memory_id} (${event.confidence_score}%)` : '0% (Novel Precedent)'}</span>
      </div>
      <div class="detail-item">
        <strong>Root Cause</strong>
        <span>${event.root_cause}</span>
      </div>
      <div class="detail-item">
        <strong>Action Executed</strong>
        <span><code>${event.action_taken}</code></span>
      </div>
    </div>

    <div class="event-comparison-box">
      <strong>Why a Standard AI Without Hindsight Fails:</strong>
      ${event.dumb_ai_comparison}
    </div>

    ${!isAutoFix ? `
      <div style="margin-top: 12px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
        <span style="font-size: 12px; color: #047857; font-weight: 600;">Saved into Hindsight Cloud Bank 'production-app'</span>
        <button class="btn btn-secondary btn-sm btn-retest-inline">Trigger Same Bug Again (Test Recall)</button>
      </div>
    ` : ''}
  `;

  // Wire up the inline re-test button
  const retestBtn = card.querySelector(".btn-retest-inline");
  if (retestBtn) {
    retestBtn.addEventListener("click", () => {
      executeLogAnalysis(originalLog, event.service, `Recurring: ${event.title || event.incident_id}`);
    });
  }

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
      Guardian is querying Hindsight Cloud memory with Gemini 2.5 Flash...
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
    const rawMemories = data.memories || [];
    
    categorizeMemories(rawMemories);
    updateCategoryCounters();
    renderFilteredDrawerCards();
  } catch (err) {
    console.error("Failed to load memories:", err);
  }
}


function categorizeMemories(rawMemories) {
  allCategorizedMemories = [];

  rawMemories.forEach(m => {
    // 1. Safe Playbooks
    if (m.runbook_command && !m.tags?.includes("policy")) {
      allCategorizedMemories.push({
        id: m.incident_id || m.id,
        category: "playbook",
        categoryLabel: "Safe Playbook",
        tagClass: "tag-playbook",
        title: m.title,
        body: m.successful_resolution || m.symptoms,
        runbook: m.runbook_command,
        raw: m
      });
    }

    // 2. Mistakes to Avoid
    if (m.failed_attempts && m.failed_attempts.length > 0) {
      m.failed_attempts.forEach(fail => {
        allCategorizedMemories.push({
          id: `${m.incident_id || 'INC'}-Avoid`,
          category: "mistake",
          categoryLabel: "Avoid Mistake",
          tagClass: "tag-mistake",
          title: "Anti-Pattern Warning",
          body: fail,
          runbook: null,
          raw: m
        });
      });
    }

    // 3. Policies / Rules
    if (m.tags?.includes("policy") || m.tags?.includes("developer-rule")) {
      allCategorizedMemories.push({
        id: m.incident_id || m.id,
        category: "policy",
        categoryLabel: m.title.replace("Policy: ", "") || "Policy",
        tagClass: "tag-policy",
        title: m.title,
        body: m.root_cause || m.symptoms,
        runbook: null,
        raw: m
      });
    }
  });
}


function updateCategoryCounters() {
  const total = allCategorizedMemories.length;
  const playbooks = allCategorizedMemories.filter(m => m.category === "playbook").length;
  const mistakes = allCategorizedMemories.filter(m => m.category === "mistake").length;
  const policies = allCategorizedMemories.filter(m => m.category === "policy").length;

  catCountAll.textContent = total;
  catCountPlaybooks.textContent = playbooks;
  catCountMistakes.textContent = mistakes;
  catCountPolicies.textContent = policies;
  memoryBadgeCount.textContent = total;
}


function renderFilteredDrawerCards() {
  drawerMemoryList.innerHTML = "";
  const query = drawerSearchInput.value.toLowerCase().trim();

  const filtered = allCategorizedMemories.filter(item => {
    const matchesCat = currentCategoryFilter === "all" || item.category === currentCategoryFilter;
    const matchesQuery = !query || 
      item.title.toLowerCase().includes(query) || 
      item.body.toLowerCase().includes(query) ||
      (item.runbook && item.runbook.toLowerCase().includes(query));
    return matchesCat && matchesQuery;
  });

  if (!filtered.length) {
    drawerMemoryList.innerHTML = `
      <div style="text-align: center; color: #94a3b8; padding: 24px 12px; font-size: 13px;">
        No memory records found matching criteria.
      </div>
    `;
    return;
  }

  filtered.forEach(item => {
    const card = document.createElement("div");
    card.className = `drawer-memory-card type-${item.category}`;

    const memoryTargetId = item.raw.incident_id || item.raw.id;

    card.innerHTML = `
      <div class="card-meta-top">
        <div style="display:flex; align-items:center; gap:6px;">
          <span style="font-family: var(--font-mono); font-size: 11px; font-weight: 600; color: #64748b;">${item.id}</span>
          <span class="card-category-tag ${item.tagClass}">${item.categoryLabel}</span>
        </div>
        <button class="btn-card-delete" data-id="${memoryTargetId}" title="Delete this memory">&times;</button>
      </div>
      <div class="card-title-text">${item.title}</div>
      <div class="card-body-text">${item.body}</div>
      ${item.runbook ? `<div class="card-runbook-code"><code>${item.runbook}</code></div>` : ''}
    `;

    // Delete handler
    const deleteBtn = card.querySelector(".btn-card-delete");
    if (deleteBtn) {
      deleteBtn.addEventListener("click", async (e) => {
        e.stopPropagation();
        await deleteMemoryItem(memoryTargetId);
      });
    }

    drawerMemoryList.appendChild(card);
  });
}

// Delete single memory item
async function deleteMemoryItem(memoryId) {
  try {
    const res = await fetch("/api/memories/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ memory_id: memoryId })
    });
    await res.json();
    loadMemories();
  } catch (err) {
    console.error("Failed to delete memory:", err);
  }
}

// Clear all memories
async function handleClearAllMemories() {
  if (confirm("Are you sure you want to clear all memories from the bank?")) {
    try {
      await fetch("/api/memories/clear", { method: "POST" });
      loadMemories();
    } catch (err) {
      console.error("Failed to clear memories:", err);
    }
  }
}


// Save New Rule (Supports "Other" custom category)
async function handleSaveRule() {
  const text = ruleText.value.trim();
  let selectedCategory = ruleCategory.value;

  if (selectedCategory === "Other") {
    const customName = customCategoryInput.value.trim();
    if (!customName) {
      alert("Please enter a custom category name.");
      customCategoryInput.focus();
      return;
    }
    selectedCategory = customName;
  }

  if (!text) {
    alert("Please enter a rule description.");
    return;
  }

  try {
    const res = await fetch("/api/teach", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rule_text: text, category: selectedCategory })
    });
    const data = await res.json();
    teachModal.classList.remove("open");
    ruleText.value = "";
    customCategoryInput.value = "";
    customCategoryGroup.style.display = "none";
    ruleCategory.value = "Database Policy";

    appendBotMessage(`I have committed your new rule to Hindsight Cloud memory under "${selectedCategory}": "${text}". I will enforce this rule going forward.`);
    loadMemories();
  } catch (err) {
    alert("Error saving rule: " + err.message);
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
