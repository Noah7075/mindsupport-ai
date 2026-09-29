// MindSupport AI - Autonomous Support Copilot with Hindsight Persistent Memory, Behavioral Routing & Voice Call Dispatch

let currentUserId = "tony";
let isHindsightMode = true;
let usersData = {};
const userChatHistories = {
  tony: [],
  sarah: [],
  alex: [],
  marcus: [],
  elena: []
};

const userSuggestedPrompts = {
  tony: [
    "Why hasn't my 18k gold earrings refund reached my account?",
    "I'd like to speak with a human agent on the phone.",
    "What is the warranty policy on quantum processors?"
  ],
  sarah: [
    "Where is my Silk Slip Dress? It says delivered but nothing arrived!",
    "Can I talk with a live specialist on a voice call right now?",
    "Do you sell international airline tickets?"
  ],
  alex: [
    "Kafka consumer offset mismatch is causing payment webhooks to loop 500s.",
    "Connect me to an engineer on a voice call immediately.",
    "How do I bake sourdough bread from scratch?"
  ],
  marcus: [
    "I need an update on my Enterprise 42U Server Rack delivery.",
    "Can I get a phone call from my enterprise account lead?",
    "What is the population of Mars?"
  ],
  elena: [
    "We want to return our Dell UltraSharp 4K Monitor from March. Process the refund to our corporate account.",
    "I need an immediate tax invoice for my Dell UltraSharp 4K Monitor.",
    "Can someone call my phone to verify our enterprise contract details?"
  ]
};

document.addEventListener("DOMContentLoaded", () => {
  initApp();
});

async function initApp() {
  setupEventListeners();
  await loadUsers();
  switchUser("tony");
}

function setupEventListeners() {
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const dropdownBtn = document.getElementById("user-dropdown-btn");
  const dropdownMenu = document.getElementById("user-dropdown-menu");

  // User Dropdown Toggle
  dropdownBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    dropdownMenu.classList.toggle("open");
  });

  document.addEventListener("click", () => {
    dropdownMenu.classList.remove("open");
  });

  // Chat Form Submit
  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (!text) return;
    chatInput.value = "";
    submitMessage(text);
  });

  // Reset Session
  document.getElementById("btn-clear-chat").addEventListener("click", async () => {
    if (!confirm(`Reset chat session and clear local context for ${usersData[currentUserId]?.name || currentUserId}?`)) return;
    userChatHistories[currentUserId] = [];
    document.getElementById("chat-messages").innerHTML = "";
    try {
      await fetch("/api/clear_memory", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: currentUserId })
      });
      showToast("Session reset successfully.");
      loadWelcomeMessage(currentUserId);
    } catch (e) {
      showToast("Session reset.");
      loadWelcomeMessage(currentUserId);
    }
  });

  // Drawer Close
  document.getElementById("btn-close-drawer").addEventListener("click", closeDetailsDrawer);
  document.getElementById("drawer-overlay").addEventListener("click", closeDetailsDrawer);

  // Mode Toggle Listener (Hindsight Copilot vs Standard Chatbot)
  const btnMode = document.getElementById("btn-mode-toggle");
  if (btnMode) {
    btnMode.addEventListener("click", () => {
      isHindsightMode = !isHindsightMode;
      updateModeUI();
    });
  }
}

async function loadUsers() {
  try {
    const res = await fetch("/api/users");
    const data = await res.json();
    usersData = data.users || {};
    renderUserDropdown();
  } catch (err) {
    console.error("Failed to load users:", err);
  }
}

function renderUserDropdown() {
  const menu = document.getElementById("user-dropdown-menu");
  const userItems = Object.keys(usersData).map(uid => {
    const u = usersData[uid];
    return `
      <div class="user-dropdown-item ${uid === currentUserId ? 'active' : ''}" onclick="switchUser('${uid}')">
        <img src="${u.avatar}" class="user-dropdown-avatar" alt="${u.name}">
        <div class="user-dropdown-meta">
          <strong>${u.name}</strong>
          <span>${u.phone}</span>
        </div>
        <span class="user-dropdown-tag">${(u.plan || 'User').split(' ')[0]}</span>
      </div>
    `;
  }).join("");

  const addNewBtn = `
    <div style="border-top:1px solid var(--border); margin-top:4px; padding-top:4px;">
      <button onclick="promptAddNewUser()" style="width:100%; display:flex; align-items:center; justify-content:center; gap:6px; background:var(--primary-light); color:var(--primary); border:1px dashed var(--primary-border); border-radius:var(--radius-md); padding:8px; font-size:11px; font-weight:700; cursor:pointer;">
        <span>➕ Chat as New User / Custom Name</span>
      </button>
    </div>
  `;

  menu.innerHTML = userItems + addNewBtn;
}

window.promptAddNewUser = async function() {
  const name = prompt("Enter your Name:", "Thanuj");
  if (!name || !name.trim()) return;
  const phone = prompt("Enter your Phone Number:", "+1 (415) 888-1234") || "+1 (555) 019-9000";

  try {
    const res = await fetch("/api/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: name.trim(),
        phone: phone.trim()
      })
    });
    const data = await res.json();
    if (data.users) {
      usersData = data.users;
    }
    const uid = (data.user && data.user.id) || name.trim().toLowerCase().replace(/[^a-z0-9]/g, "_");
    userSuggestedPrompts[uid] = [
      `Hi, I am ${name.trim()} and my phone is ${phone.trim()}.`,
      "What details have you remembered about me so far?",
      "Can you connect me with a specialist on a voice call?"
    ];
    userChatHistories[uid] = [];
    switchUser(uid);
    renderUserDropdown();
    showToast(`Created & switched to new user: ${name.trim()}`);
  } catch (err) {
    console.error("Failed to create user on backend:", err);
  }
};

function switchUser(uid) {
  if (!usersData[uid]) return;
  currentUserId = uid;

  const u = usersData[uid];

  // Update Header Pill
  document.getElementById("header-user-avatar").src = u.avatar;
  document.getElementById("header-user-name").textContent = u.name;
  document.getElementById("header-user-phone").textContent = u.phone;

  // Update Info Strip
  document.getElementById("strip-name").textContent = u.name;
  document.getElementById("strip-plan").textContent = u.plan;
  document.getElementById("strip-phone").textContent = u.phone;
  document.getElementById("strip-address").textContent = u.address;
  const orderSummary = (u.orders || []).map(o => o.item).slice(0, 3).join(", ");
  document.getElementById("strip-orders").textContent = `${u.orders?.length || 0} Orders (${orderSummary}...)`;
  document.getElementById("strip-wallet").textContent = "$" + Number(u.wallet_balance || 0).toFixed(2);
  const ticketElem = document.getElementById("strip-tickets");
  if (ticketElem) ticketElem.textContent = u.total_tickets || 5;

  // Update Chips
  renderChips(uid);

  // Update Dropdown UI
  renderUserDropdown();
  document.getElementById("user-dropdown-menu").classList.remove("open");

  // Load chat history for this user
  const container = document.getElementById("chat-messages");
  container.innerHTML = "";

  if (!userChatHistories[uid] || userChatHistories[uid].length === 0) {
    loadWelcomeMessage(uid);
  } else {
    userChatHistories[uid].forEach((msg, idx) => {
      renderMessage(msg, idx);
    });
  }
}

function renderChips(uid) {
  const container = document.getElementById("chips-container");
  const prompts = userSuggestedPrompts[uid] || [
    "I'd like to speak with a human agent on the phone.",
    "What is the status of my recent order?"
  ];

  container.innerHTML = prompts.map(p => `
    <button class="quick-chip" onclick="sendSuggestedPrompt(this)">
      ${p}
    </button>
  `).join("");
}

function sendSuggestedPrompt(btn) {
  const text = btn.textContent.trim();
  document.getElementById("chat-input").value = text;
  document.getElementById("chat-form").dispatchEvent(new Event("submit"));
}

function loadWelcomeMessage(uid) {
  const u = usersData[uid] || { name: "there" };
  const welcome = {
    sender: "bot",
    text: `Hello ${u.name.split(' ')[0]}! What can I do for you today?`,
    time: formatTime(),
    recalled_memories: []
  };
  userChatHistories[uid] = [welcome];
  renderMessage(welcome, 0);
}

function renderMessage(msg, index) {
  const container = document.getElementById("chat-messages");
  const row = document.createElement("div");
  row.className = `message-row ${msg.sender}`;

  const u = usersData[currentUserId] || {};
  const avatar = msg.sender === "user" ? (u.avatar ? `<img src="${u.avatar}" style="width:100%;height:100%;border-radius:6px;object-fit:cover;">` : "👤") : "🧠";

  let howSolvedBtn = "";
  if (msg.sender === "bot" && index > 0) {
    howSolvedBtn = `
      <button class="btn-how-solved" onclick="openDetails(${index})">
        <span>🔍 How Agent Solved This</span>
      </button>
    `;
  }

  // Voice Call Card if requested
  let voiceCardHtml = "";
  if (msg.is_voice_call_request && msg.matched_specialist) {
    const spec = msg.matched_specialist;
    voiceCardHtml = `
      <div class="voice-call-card">
        <div class="voice-call-header">
          <div class="voice-call-title">
            <span>📞 Voice Call Dispatch Protocol</span>
          </div>
          <span style="font-size:10px; font-weight:700; background:#ecfdf5; color:#059669; padding:2px 8px; border-radius:9999px; border:1px solid #a7f3d0;">
            ✓ Phone Verified
          </span>
        </div>
        <div class="voice-call-body">
          <img src="${spec.avatar || 'https://api.dicebear.com/7.x/avataaars/svg?seed=SupportSpecialist'}" class="voice-agent-avatar" alt="${spec.name}">
          <div class="voice-agent-meta">
            <span class="voice-agent-name">${spec.name} (${spec.role})</span>
            <span class="voice-agent-role">${spec.superpower}</span>
            <span class="voice-agent-phone">Target Line: ${spec.phone} ➔ ${u.phone || 'Your Number'}</span>
          </div>
          <button class="btn-dial" id="dial-btn-${index}" onclick="simulateVoiceDial(${index}, '${spec.name}', '${u.phone}')">
            <span>📞 Initiate Call</span>
          </button>
        </div>
      </div>
    `;
  }

  // Interactive Counter-Offer Option Pills
  let counterOfferHtml = "";
  if (msg.sender === "bot" && (msg.text.includes("Option A") || msg.text.includes("Trade-In Credit") || msg.text.includes("70% Instant Store"))) {
    const activeCust = usersData[currentUserId] || {};
    const orders = activeCust.orders || [];
    let estVal = "$805.00";
    let targetOrder = orders.length > 0 ? orders[orders.length - 1] : null;
    if (orders.length > 0) {
      // Find matching or latest physical order
      for (const o of orders) {
        if (msg.text.toLowerCase().includes((o.item || "").toLowerCase().split(" ")[0])) {
          targetOrder = o;
          break;
        }
      }
      if (targetOrder) {
        try {
          const rawP = parseFloat(String(targetOrder.price).replace(/[^0-9.]/g, ''));
          if (!isNaN(rawP)) estVal = "$" + (rawP * 0.70).toFixed(2);
        } catch (e) {}
      }
    }

    counterOfferHtml = `
      <div class="action-options-container">
        <div class="action-option-pill" onclick="triggerDirectAction('ACCEPT_COUNTER_OFFER', 'option_a')">
          <div>
            <strong>💳 Option A: Instant 70% Trade-In Credit (${estVal})</strong>
            <span>Direct deposit to your wallet balance immediately. No return waiting.</span>
          </div>
          <button class="action-pill-btn">Accept Credit</button>
        </div>
        <div class="action-option-pill" onclick="triggerDirectAction('ACCEPT_COUNTER_OFFER', 'option_b')">
          <div>
            <strong>🛡️ Option B: 2-Year Hardware Care Plan + $100 Credit</strong>
            <span>Keep your item with full accidental protection + $100 wallet credit.</span>
          </div>
          <button class="action-pill-btn">Enroll Protection</button>
        </div>
        <div class="action-option-pill" onclick="triggerDirectAction('GENERATE_RMA', 'label')">
          <div>
            <strong>🏷️ Option C: Generate Official Prepaid FedEx Return Label (RMA)</strong>
            <span>Ship device to Austin depot for physical inspection & exception review.</span>
          </div>
          <button class="action-pill-btn" style="background:#0f172a;">Print RMA</button>
        </div>
      </div>
    `;
  }

  // Interactive RMA Label Card
  let rmaCardHtml = "";
  if (msg.action_result && (msg.action_result.action_type === "GENERATE_RMA_LABEL" || msg.action_result.rma_number)) {
    const r = msg.action_result;
    rmaCardHtml = `
      <div class="rma-label-card">
        <div class="rma-label-header">
          <div class="rma-carrier-logo">FedEx <span>Priority Return</span></div>
          <div class="rma-badge">✓ PREPAID BILLABLE STAMP</div>
        </div>
        <div class="rma-route-grid">
          <div>
            <span style="color:#64748b; font-size:10px; font-weight:700;">FROM (SENDER):</span><br>
            <strong>${r.sender?.name || u.name}</strong><br>
            <span style="color:#64748b;">${r.sender?.address || u.address}</span>
          </div>
          <div>
            <span style="color:#64748b; font-size:10px; font-weight:700;">TO (DESTINATION):</span><br>
            <strong>Central Depot #4 QA Bay</strong><br>
            <span style="color:#64748b;">4000 Tech Ridge, Austin TX</span>
          </div>
        </div>
        <div class="rma-barcode-box">
          <div class="barcode-lines"></div>
          <div>${r.tracking_number}</div>
          <div style="font-size:10px; color:#64748b; margin-top:4px;">RMA: ${r.rma_number} | Payout: ESCROW (Auto-release on scan)</div>
        </div>
        <button class="btn-download-label" onclick="showToast('Prepaid FedEx Label generated & ready to print. Tracking active.')">
          <span>📥 Download & Print Shipping Label (PDF)</span>
        </button>
      </div>
    `;
  }

  // Action Success Banner
  let actionSuccessHtml = "";
  if (msg.action_result && msg.action_result.action_type === "COUNTER_OFFER_ACCEPTED") {
    const r = msg.action_result;
    actionSuccessHtml = `
      <div class="action-success-card">
        <div class="action-success-title">
          <span>⚡ Autonomous Resolution Executed</span>
        </div>
        <div class="action-success-body">
          <strong>${r.display_name}</strong><br>
          ${r.execution_output}<br>
          <span style="color:#059669; font-weight:700; margin-top:4px; display:inline-block;">✓ Store Credit Deposited: ${r.credit_issued} | Active Wallet: ${r.updated_wallet_balance}</span>
        </div>
      </div>
    `;
  }

  // Official CRM Ticket Pill
  let ticketPillHtml = "";
  if (msg.ticket) {
    const t = msg.ticket;
    const isResolved = (t.status || "").includes("RESOLVED");
    ticketPillHtml = `
      <div class="message-ticket-pill">
        <span class="ticket-pill-id">🎫 Ticket #${t.ticket_id}</span>
        <span class="ticket-pill-status ${isResolved ? 'status-resolved' : 'status-escalated'}">${t.status_label || t.status}</span>
        <span class="ticket-pill-priority">${(t.priority || '').split(' ')[0]}</span>
      </div>
    `;
  }

  row.innerHTML = `
    <div class="message-avatar">${avatar}</div>
    <div class="message-content" style="max-width: 100%;">
      <div class="message-bubble">
        <div>${formatMarkdown(msg.text)}</div>
        ${counterOfferHtml}
        ${rmaCardHtml}
        ${actionSuccessHtml}
        ${voiceCardHtml}
        ${ticketPillHtml}
        <div class="message-footer">
          <span class="message-time">${msg.time}</span>
          ${howSolvedBtn}
        </div>
      </div>
    </div>
  `;

  container.appendChild(row);
  scrollToBottom();
}

window.triggerDirectAction = async function(actionType, choice) {
  showToast("Executing autonomous resolution...");
  try {
    const activeCust = usersData[currentUserId] || {};
    const orders = activeCust.orders || [];
    const targetOrder = orders.length > 0 ? orders[orders.length - 1] : { id: "ORD-1180", item: "Asset" };

    const res = await fetch("/api/action/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: currentUserId,
        action_type: actionType,
        order_id: targetOrder.id,
        item_name: targetOrder.item,
        offer_choice: choice
      })
    });
    const data = await res.json();
    if (data.wallet_balance !== undefined) {
      document.getElementById("strip-wallet").textContent = "$" + Number(data.wallet_balance).toFixed(2);
      if (usersData[currentUserId]) usersData[currentUserId].wallet_balance = data.wallet_balance;
    }
    if (data.total_tickets !== undefined) {
      const ticketElem = document.getElementById("strip-tickets");
      if (ticketElem) ticketElem.textContent = data.total_tickets;
      if (usersData[currentUserId]) usersData[currentUserId].total_tickets = data.total_tickets;
    }
    const history = userChatHistories[currentUserId];
    const prevTurn = history.slice().reverse().find(m => m.recalled_memories && m.recalled_memories.length > 0);
    const queryTitle = actionType === "GENERATE_RMA" 
      ? `Generate Official Prepaid FedEx Return Label (${targetOrder.item})` 
      : (choice === "option_a" ? `Accept 70% Trade-In Credit (${targetOrder.item})` : "Accept 2-Year Hardware Care Plan");

    const botMsg = {
      sender: "bot",
      text: data.action_result?.execution_output || "Action executed successfully.",
      time: formatTime(),
      action_result: data.action_result,
      user_query: `[Autonomous Action]: ${queryTitle}`,
      ticket: data.ticket,
      recalled_memories: prevTurn ? prevTurn.recalled_memories : []
    };
    history.push(botMsg);
    renderMessage(botMsg, history.length - 1);
    showToast("Autonomous action executed!");
  } catch (err) {
    showToast("Action execution failed.");
  }
};

window.simulateVoiceDial = function(idx, specialistName, customerPhone) {
  const btn = document.getElementById(`dial-btn-${idx}`);
  if (!btn) return;

  btn.classList.add("dialing");
  btn.innerHTML = `<span>⏳ Connecting...</span>`;

  setTimeout(() => {
    btn.classList.remove("dialing");
    btn.style.background = "#059669";
    btn.innerHTML = `<span>🟢 Call Connected</span>`;
    showToast(`Connecting ${specialistName} to ${customerPhone}... Call active.`);
  }, 1800);
};

async function submitMessage(text) {
  const history = userChatHistories[currentUserId];
  const userMsg = {
    sender: "user",
    text: text,
    time: formatTime()
  };
  history.push(userMsg);
  renderMessage(userMsg, history.length - 1);

  try {
    const currentUser = usersData[currentUserId] || {};
    const resp = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        user_id: currentUserId,
        user_name: currentUser.name,
        user_phone: currentUser.phone,
        user_address: currentUser.address,
        mode: isHindsightMode ? "hindsight" : "legacy"
      })
    });

    const data = await resp.json();

    if (data.total_tickets !== undefined) {
      const ticketElem = document.getElementById("strip-tickets");
      if (ticketElem) ticketElem.textContent = data.total_tickets;
      if (usersData[currentUserId]) usersData[currentUserId].total_tickets = data.total_tickets;
    }

    const botMsg = {
      sender: "bot",
      text: data.reply,
      time: formatTime(),
      recalled_memories: data.recalled_memories || [],
      action_result: data.action_result,
      logs_inspected: data.logs_inspected || [],
      behavioral_routing: data.behavioral_routing,
      is_voice_call_request: data.is_voice_call_request,
      matched_specialist: data.matched_specialist,
      user_query: text,
      ticket: data.ticket,
      mode: data.mode || (isHindsightMode ? "hindsight" : "legacy")
    };
    history.push(botMsg);
    renderMessage(botMsg, history.length - 1);

  } catch (err) {
    const errorMsg = {
      sender: "bot",
      text: "Sorry, I encountered an error connecting to the backend service.",
      time: formatTime(),
      recalled_memories: []
    };
    history.push(errorMsg);
    renderMessage(errorMsg, history.length - 1);
  }
}

window.openDetails = function(index) {
  const history = userChatHistories[currentUserId];
  const msg = history[index];
  if (!msg) return;

  const drawer = document.getElementById("details-drawer");
  const overlay = document.getElementById("drawer-overlay");
  const body = document.getElementById("drawer-body");

  if (msg.mode === "legacy") {
    body.innerHTML = `
      <div class="query-banner">
        <strong>User Query:</strong> "${msg.user_query || ''}"
      </div>
      <div class="section-box" style="border-color:#fecdd3; background:#fffafa;">
        <div class="section-box-title" style="color:#be123c;">
          <span>🔴 Standard Chatbot Mode (Stateless)</span>
          <span style="font-size:10px; background:#ffe4e6; color:#be123c; border:1px solid #fecdd3; padding:1px 6px; border-radius:9999px; margin-left:auto;">MEMORY DISABLED</span>
        </div>
        <div style="font-size:12px; line-height:1.6; color:#881337;">
          <div style="margin-bottom:6px;"><strong>• Hindsight Memory Recall:</strong> Bypassed (0 memories fetched). Bot treats customer as an unknown stranger.</div>
          <div style="margin-bottom:6px;"><strong>• Behavioral Sentiment:</strong> Disabled (No emotion trajectory or specialist match).</div>
          <div style="margin-bottom:6px;"><strong>• Autonomous Actions:</strong> Disabled (No RMA label or trade-in credit can be executed).</div>
          <div><strong>• Result:</strong> Bot asks customer to re-enter order details and directs them to a 2–3 business day email queue.</div>
        </div>
      </div>
    `;
    drawer.classList.add("open");
    overlay.classList.add("open");
    return;
  }

  // Official CRM Ticket Lifecycle Record
  let ticketRecordHtml = "";
  if (msg.ticket) {
    const t = msg.ticket;
    const isResolved = (t.status || "").includes("RESOLVED");
    ticketRecordHtml = `
      <div class="section-box" style="border-color:${isResolved ? '#a7f3d0' : '#fecdd3'}; background:${isResolved ? '#fcfdfd' : '#fffbfb'};">
        <div class="section-box-title" style="color:${isResolved ? '#059669' : '#e11d48'};">
          <span>🎫 Official CRM Ticket Lifecycle Record</span>
          <span style="font-size:10px; background:${isResolved ? '#ecfdf5' : '#fff1f2'}; color:${isResolved ? '#059669' : '#e11d48'}; border:1px solid ${isResolved ? '#a7f3d0' : '#fecdd3'}; padding:1px 6px; border-radius:9999px; margin-left:auto;">${t.status_label || t.status}</span>
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:11px; margin-bottom:8px;">
          <div><strong>Ticket ID:</strong> <code style="background:#f1f5f9; padding:2px 6px; border-radius:4px; font-weight:700;">#${t.ticket_id}</code></div>
          <div><strong>Priority:</strong> <span class="chip" style="font-weight:700;">${t.priority}</span></div>
          <div><strong>Customer:</strong> ${t.customer_name} (${t.customer_id})</div>
          <div><strong>Timestamp:</strong> ${t.created_at || 'Just now'}</div>
        </div>
        <div style="font-size:11px; color:#475569; background:#f8fafc; padding:8px 10px; border-radius:6px; border:1px solid #e2e8f0; line-height:1.5;">
          <strong>Ticket Resolution Summary:</strong><br>
          ${t.resolution_summary}<br>
          <div style="margin-top:6px; color:#059669; font-weight:600;">
            ✓ Synchronized to Vectorize Hindsight Cloud bank: <code>mindsupport_master_bank</code>
          </div>
        </div>
      </div>
    `;
  }

  // Behavioral Routing View
  let behaviorHtml = "";
  if (msg.behavioral_routing) {
    const b = msg.behavioral_routing;
    const spec = b.matched_specialist || b.assigned_specialist;
    const isCritical = (b.detected_temperament || '').includes("Hostile") || (b.volatility_index || '').includes("High") || (b.volatility_score || 0) >= 70;
    const chipStyle = isCritical 
      ? 'background:#fff1f2; color:#e11d48; border:1px solid #fecdd3; font-weight:700;' 
      : '';

    behaviorHtml = `
      <div class="section-box" style="${isCritical ? 'border-color:#fecdd3; background:#fffbfb;' : ''}">
        <div class="section-box-title" style="${isCritical ? 'color:#e11d48;' : ''}">
          <span>👤 Behavioral Sentiment & Specialist Routing</span>
          ${isCritical ? '<span style="font-size:10px; background:#e11d48; color:white; padding:1px 6px; border-radius:9999px; margin-left:auto;">⚠️ CRITICAL ESCALATION</span>' : ''}
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:11px; margin-bottom:8px;">
          <div><strong>Temperament:</strong> <span class="chip" style="${chipStyle}">${b.detected_temperament || b.temperament || 'Standard'}</span></div>
          <div><strong>Volatility:</strong> <span class="chip" style="${chipStyle}">${b.volatility_index || b.volatility_score || 'Low'}</span></div>
          <div><strong>VIP Level:</strong> <span class="chip">${b.vip_level || 'Tier 1 Priority'}</span></div>
          <div><strong>Action Speed:</strong> <span class="chip" style="${isCritical ? chipStyle : ''}">${b.response_urgency || b.escalation_level || 'Normal'}</span></div>
        </div>
        ${spec ? `
          <div style="background:white; border:1px solid ${isCritical ? '#fecdd3' : 'var(--border)'}; padding:8px 10px; border-radius:6px; font-size:11px;">
            <div style="display:flex; align-items:center; gap:6px;">
              <strong>Assigned Specialist:</strong> 
              <span style="font-weight:700; color:${isCritical ? '#e11d48' : 'var(--primary)'};">${spec.name}</span> 
              <span style="color:var(--text-muted); font-size:10px;">(${spec.role})</span>
            </div>
            <div style="color:var(--text-muted); margin-top:3px; line-height:1.4;">
              <strong>Rationale:</strong> ${b.routing_rationale || b.routing_reason || spec.superpower}
            </div>
          </div>
        ` : ''}
      </div>
    `;
  }

  // Format memories
  let memoryItemsHtml = "";
  if (msg.recalled_memories && msg.recalled_memories.length > 0) {
    memoryItemsHtml = msg.recalled_memories.map(m => `
      <div class="memory-item">
        <div>${m.text}</div>
        ${m.entities && m.entities.length > 0 ? `
          <div class="memory-chips">
            ${m.entities.map(e => `<span class="chip">#${e}</span>`).join("")}
          </div>
        ` : ""}
      </div>
    `).join("");
  } else {
    memoryItemsHtml = `<p style="font-size:12px; color:#94a3b8;">No prior memories were retrieved for this query.</p>`;
  }

  // Format Autonomous Action or Policy Decision Breakdown
  let actionHtml = "";
  if (msg.action_result) {
    const act = msg.action_result;
    let detailsSpecific = "";
    if (act.rma_number) {
      detailsSpecific = `
        <div style="font-size:12px; margin-bottom:4px;"><strong>RMA Code:</strong> <code style="background:#f1f5f9; padding:2px 6px; border-radius:4px; font-weight:700;">${act.rma_number}</code></div>
        <div style="font-size:12px; margin-bottom:4px;"><strong>Tracking ID:</strong> <code>${act.tracking_number}</code> (${act.carrier || 'FedEx Priority'})</div>
        <div style="font-size:12px; margin-bottom:4px;"><strong>Payout Protocol:</strong> <span class="chip" style="background:#fef3c7; color:#92400e;">${act.payout_status || 'ESCROW HOLD'}</span></div>
        <div style="font-size:11px; color:#475569; margin-top:8px; background:#f8fafc; padding:8px 10px; border-radius:6px; border:1px solid #e2e8f0; line-height:1.5;">
          <strong>🛡️ Risk Guardrails Verified:</strong><br>
          ✓ Financial Escrow: Funds hold locked until carrier intake scan.<br>
          ✓ Idempotency: Single-use RMA code registered in master ledger.<br>
          ✓ Inspection Checklist: iCloud sign-out & charger verification required.
        </div>
      `;
    } else if (act.credit_issued) {
      detailsSpecific = `
        <div style="font-size:12px; margin-bottom:4px;"><strong>Resolution Type:</strong> ${act.resolution_type}</div>
        <div style="font-size:12px; margin-bottom:4px; color:#059669;"><strong>Store Credit Deposited:</strong> <strong>${act.credit_issued}</strong></div>
        <div style="font-size:12px; margin-bottom:4px;"><strong>Updated Wallet Balance:</strong> ${act.updated_wallet_balance}</div>
        <div style="font-size:11px; color:#475569; margin-top:8px; background:#f8fafc; padding:8px 10px; border-radius:6px; border:1px solid #e2e8f0; line-height:1.5;">
          <strong>🛡️ Risk Guardrails Verified:</strong><br>
          ✓ Hard Financial Cap: Capped strictly at 70% of verified order value.<br>
          ✓ Anti-Bleed Idempotency: Duplicate credit attempts automatically rejected.<br>
          ✓ Ledger Entry: Synchronized to customer account balance.
        </div>
      `;
    } else if (act.diagnostic) {
      detailsSpecific = `
        <div style="font-size:12px; margin-bottom:6px;"><strong>Diagnostic Root-Cause:</strong> ${act.diagnostic}</div>
        <div style="font-size:12px; color:#059669;"><strong>Execution Result:</strong> ${act.execution_output}</div>
      `;
    }

    actionHtml = `
      <div class="section-box" style="border-color:#a7f3d0; background:#fcfdfd;">
        <div class="section-box-title" style="color:#059669;">
          <span>⚡ Autonomous Resolution Executed</span>
          <span style="font-size:10px; background:#ecfdf5; color:#059669; border:1px solid #a7f3d0; padding:1px 6px; border-radius:9999px; margin-left:auto;">COMPLETED</span>
        </div>
        <div style="font-size:12px; margin-bottom:6px; font-weight:700;">${act.display_name || 'Autonomous Action Execution'}</div>
        ${detailsSpecific}
      </div>
    `;
  } else if (msg.sender === "bot") {
    actionHtml = `
      <div class="section-box" style="border-color:#e0e7ff; background:#fbfcfe;">
        <div class="section-box-title" style="color:#4338ca;">
          <span>📋 Autonomous Policy & Decision Engine Audit</span>
          <span style="font-size:10px; background:#eef2ff; color:#4338ca; border:1px solid #c7d2fe; padding:1px 6px; border-radius:9999px; margin-left:auto;">VERIFIED</span>
        </div>
        <div style="font-size:12px; line-height:1.6; color:#334155;">
          <div style="margin-bottom:6px;"><strong>1. Account & Order Verification:</strong> Evaluated purchase date, item serial records, and account warranty ledger.</div>
          <div style="margin-bottom:6px;"><strong>2. Policy Engine Check:</strong> Standard 30-day window evaluated. Flagged high-value asset inspection requirement (prevents return fraud on assets &gt;$1,000).</div>
          <div style="margin-bottom:6px;"><strong>3. Risk & Financial Guardrails:</strong> Pre-authorized bounded concessions (strict 70% trade-in valuation ceiling, escrow hold on RMA returns, idempotency locks).</div>
          <div><strong>4. Autonomous Path Forward:</strong> Multi-option resolution matrix presented directly in UI without human employee bottleneck.</div>
        </div>
      </div>
    `;
  }

  // Format Logs
  let logsHtml = "";
  if (msg.logs_inspected && msg.logs_inspected.length > 0) {
    logsHtml = `
      <div class="section-box">
        <div class="section-box-title">📡 Live Warehouse & Gateway Logs Inspected (${msg.logs_inspected.length} lines)</div>
        <div class="log-terminal-mini">
          ${msg.logs_inspected.map(line => {
            let cls = "terminal-line";
            if (line.includes("422") || line.includes("expired") || line.includes("ERR") || line.includes("stalled") || line.includes("500") || line.includes("MISMATCH")) cls += " terminal-err";
            else if (line.includes("APPROVED") || line.includes("OK") || line.includes("verified") || line.includes("DELIVERED") || line.includes("ACTIVE")) cls += " terminal-success";
            return `<div class="${cls}">${line}</div>`;
          }).join("")}
        </div>
      </div>
    `;
  }

  body.innerHTML = `
    <div class="query-banner">
      <strong>User Query:</strong> "${msg.user_query || ''}"
    </div>

    ${ticketRecordHtml}
    ${behaviorHtml}
    ${actionHtml}
    ${logsHtml}

    <div class="section-box">
      <div class="section-box-title">🧠 Specific Hindsight Memories Recalled (${msg.recalled_memories ? msg.recalled_memories.length : 0})</div>
      ${memoryItemsHtml}
    </div>
  `;

  drawer.classList.add("open");
  overlay.classList.add("open");
};

function closeDetailsDrawer() {
  document.getElementById("details-drawer").classList.remove("open");
  document.getElementById("drawer-overlay").classList.remove("open");
}

function formatMarkdown(text) {
  if (!text) return "";
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code style="background:#f1f5f9; color:#0f172a; padding:2px 5px; border-radius:4px; font-family:var(--font-mono); font-size:12px;">$1</code>')
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n/g, '<br>');
}

function formatTime() {
  const now = new Date();
  return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function scrollToBottom() {
  const container = document.getElementById("chat-messages");
  container.scrollTop = container.scrollHeight;
}

function showToast(msg) {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 3000);
}

/* ==========================================================================
   MODE CONTROLLER: HINDSIGHT COPILOT VS STANDARD CHATBOT
   ========================================================================== */
function updateModeUI() {
  const btn = document.getElementById("btn-mode-toggle");
  const modeText = document.getElementById("mode-text");
  const modeBadge = document.getElementById("mode-badge");
  const legacyBanner = document.getElementById("legacy-banner");

  if (!btn) return;

  if (isHindsightMode) {
    btn.className = "btn-mode-toggle mode-hindsight";
    if (modeText) modeText.textContent = "Hindsight Active";
    if (modeBadge) modeBadge.textContent = "AI Copilot";
    if (legacyBanner) legacyBanner.style.display = "none";
    showToast("🟢 MindSupport AI Active: Vectorize Hindsight Persistent Memory & Autonomous Actions Enabled");
  } else {
    btn.className = "btn-mode-toggle mode-legacy";
    if (modeText) modeText.textContent = "Standard Bot";
    if (modeBadge) modeBadge.textContent = "No Memory";
    if (legacyBanner) legacyBanner.style.display = "flex";
    showToast("🔴 Standard Chatbot Mode Active: Stateless (No memory, asks for name/order ID every time)");
  }
}
