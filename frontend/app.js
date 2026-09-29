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

// Simulation Modal Elements
const openSimModalBtn = document.getElementById("openSimModalBtn");
const simModal = document.getElementById("simModal");
const closeSimModalBtn = document.getElementById("closeSimModalBtn");
const runKnownSimBtn = document.getElementById("runKnownSimBtn");
const runNovelSimBtn = document.getElementById("runNovelSimBtn");

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

  // Simulations Modal
  openSimModalBtn.addEventListener("click", () => simModal.classList.add("open"));
  closeSimModalBtn.addEventListener("click", () => simModal.classList.remove("open"));

  runKnownSimBtn.addEventListener("click", () => {
    simModal.classList.remove("open");
    triggerOvernightSimulation("known_issue");
  });

  runNovelSimBtn.addEventListener("click", () => {
    simModal.classList.remove("open");
    triggerOvernightSimulation("novel_issue");
  });

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
