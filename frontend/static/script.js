let currentThreadId = localStorage.getItem("travel_thread_id") || null;
let latestAnswerMarkdown = "";
let waitingForApproval = false;

console.log("✅ Script loaded - checkpoint 1");

const AGENT_LABELS = {
  flight_agent: "✈️ Flight Agent",
  hotel_agent: "🏨 Hotel Agent",
  weather_agent: "🌦️ Weather Agent",
  budget_agent: "💰 Budget Agent",
  itinerary_agent: "🗓️ Itinerary Agent"
};

function setPrompt(text) {
  document.getElementById("userInput").value = text;
}

function setLoading(isLoading, mode = "draft") {
  const sendBtn = document.getElementById("sendBtn");
  const btnText = document.getElementById("btnText");
  const btnLoader = document.getElementById("btnLoader");
  const approveBtn = document.getElementById("approveBtn");
  const reviseBtn = document.getElementById("reviseBtn");

  sendBtn.disabled = isLoading;
  approveBtn.disabled = isLoading;
  reviseBtn.disabled = isLoading;

  if (isLoading && mode === "draft") {
    btnText.classList.add("hidden");
    btnLoader.classList.remove("hidden");
  } else {
    btnText.classList.remove("hidden");
    btnLoader.classList.add("hidden");
  }
}

function showError(message) {
  const errorBox = document.getElementById("errorBox");
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
  errorBox.scrollIntoView({ behavior: "smooth", block: "center" });
}

function hideError() {
  const errorBox = document.getElementById("errorBox");
  errorBox.classList.add("hidden");
  errorBox.textContent = "";
}

function renderMarkdown(element, markdown) {
  if (typeof marked !== "undefined") {
    element.innerHTML = marked.parse(markdown || "");
  } else {
    element.innerText = markdown || "";
  }
}

function showWorkflow(data) {
  const section = document.getElementById("workflowSection");
  const reasoning = document.getElementById("supervisorReasoning");
  const chips = document.getElementById("agentChips");
  const guardrailBadge = document.getElementById("guardrailBadge");

  reasoning.textContent = data.supervisor_reasoning || "Supervisor routing completed.";
  chips.innerHTML = "";

  (data.selected_agents || []).forEach((agent) => {
    const chip = document.createElement("span");
    chip.className = "agent-chip";
    chip.textContent = AGENT_LABELS[agent] || agent;
    chips.appendChild(chip);
  });

  if (data.guardrail_allowed === false) {
    guardrailBadge.textContent = "Guardrail blocked";
    guardrailBadge.classList.add("blocked");
  } else {
    guardrailBadge.textContent = "Guardrail passed";
    guardrailBadge.classList.remove("blocked");
  }

  section.classList.remove("hidden");
}

function showResult(answer, threadId, isDraft = false) {
  latestAnswerMarkdown = answer || "";

  const resultSection = document.getElementById("resultSection");
  const resultBox = document.getElementById("resultBox");
  const threadInfo = document.getElementById("threadInfo");
  const resultTitle = document.getElementById("resultTitle");

  renderMarkdown(resultBox, latestAnswerMarkdown);
  threadInfo.textContent = `Thread ID: ${threadId}`;
  resultTitle.textContent = isDraft ? "Draft Travel Plan" : "Your Final AI Travel Plan";
  resultSection.classList.remove("hidden");

  resultSection.scrollIntoView({
    behavior: "smooth",
    block: "start"
  });
}

function showApproval(data) {
  console.log("🔍 showApproval() CALLED");
  console.log("Input data:", data);
  
  waitingForApproval = true;

  const section = document.getElementById("approvalSection");
  const approvalRequest = document.getElementById("approvalRequest");
  const approvalDraft = document.getElementById("approvalDraft");

  console.log("Elements found:", {
    section: !!section,
    approvalRequest: !!approvalRequest,
    approvalDraft: !!approvalDraft
  });

  const interrupt = data.interrupt || {};

  const request =
    data.approval_request ||
    interrupt.approval_request ||
    interrupt.question ||
    "Please review the draft itinerary before continuing.";

  const draft =
    data.draft_itinerary ||
    data.itinerary ||
    interrupt.draft_itinerary ||
    "";

  console.log("Setting approvalRequest text");
  approvalRequest.textContent = request;

  console.log("Rendering markdown for draft (length: " + draft.length + ")");
  renderMarkdown(approvalDraft, draft);

  console.log("Removing 'hidden' class from section");
  console.log("Before remove - classList:", section.className);
  section.classList.remove("hidden");
  console.log("After remove - classList:", section.className);

  section.scrollIntoView({
    behavior: "smooth",
    block: "center"
  });

  console.log("✅ showApproval() COMPLETED");
}

function hideApproval() {
  waitingForApproval = false;
  document.getElementById("approvalSection").classList.add("hidden");
  document.getElementById("approvalFeedback").value = "";
}

async function sendMessage() {
  console.log("📍 sendMessage() START");
  hideError();

  if (waitingForApproval) {
    showError("Please approve or revise the current draft before starting another plan.");
    return;
  }

  const input = document.getElementById("userInput");
  const message = input.value.trim();

  if (!message) {
    showError("Please enter your travel request first.");
    return;
  }

  setLoading(true, "draft");

  try {
    console.log("🚀 Sending request to /api/travel");
    
    const response = await fetch("/api/travel", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        message: message,
        thread_id: currentThreadId
      })
    });

    console.log("📡 Response received, status:", response.status);

    const data = await response.json();

    console.log("✅ JSON parsed");
    console.log("Full response object:", data);

    if (!response.ok || !data.success) {
      throw new Error(data.error || "Something went wrong.");
    }

    currentThreadId = data.thread_id;
    localStorage.setItem("travel_thread_id", currentThreadId);

    showWorkflow(data);

    console.log("\n📊 APPROVAL CHECK:");
    console.log("  - data.requires_approval:", data.requires_approval);
    console.log("  - data.interrupt:", data.interrupt);
    console.log("  - data.approval_request:", data.approval_request);

    const requiresApproval =
      data.requires_approval === true ||
      data.interrupt != null ||
      data.approval_request != null;

    console.log("🎯 Final requiresApproval result:", requiresApproval);

    if (requiresApproval) {
      console.log("✅ CONDITION TRUE - SHOWING APPROVAL SECTION");

      const draft =
        data.draft_itinerary ||
        data.itinerary ||
        data.interrupt?.draft_itinerary ||
        data.answer ||
        "";

      console.log("📄 Draft content length:", draft.length);

      showResult(draft, data.thread_id, true);
      console.log("🔔 About to call showApproval()...");
      showApproval(data);
      console.log("✅ showApproval() returned");

    } else {
      console.log("❌ CONDITION FALSE - NOT SHOWING APPROVAL, showing final result");

      hideApproval();
      showResult(data.answer, data.thread_id, false);
    }
  } catch (error) {
    console.error("❌ CAUGHT ERROR:", error);
    showError(error.message);
  } finally {
    setLoading(false, "draft");
    console.log("📍 sendMessage() END\n");
  }
}

async function submitApproval(approved) {
  hideError();

  if (!currentThreadId || !waitingForApproval) {
    showError("There is no draft waiting for approval.");
    return;
  }

  const feedbackInput = document.getElementById("approvalFeedback");
  const feedback = feedbackInput.value.trim();

  if (!approved && !feedback) {
    showError("Please enter revision feedback before requesting changes.");
    feedbackInput.focus();
    return;
  }

  setLoading(true, "approval");

  try {
    const response = await fetch("/api/travel/approve", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        thread_id: currentThreadId,
        approved: approved,
        feedback: feedback
      })
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      throw new Error(data.error || "Could not resume the travel workflow.");
    }

    showWorkflow(data);
    hideApproval();
    showResult(data.answer, data.thread_id, false);
  } catch (error) {
    showError(error.message);
  } finally {
    setLoading(false, "approval");
  }
}

function copyResult() {
  const resultBox = document.getElementById("resultBox");
  const text = resultBox.innerText;

  if (!text) {
    return;
  }

  navigator.clipboard.writeText(text)
    .then(() => {
      const copyBtn = document.querySelector(".copy-btn");
      const oldText = copyBtn.textContent;
      copyBtn.textContent = "Copied!";

      setTimeout(() => {
        copyBtn.textContent = oldText;
      }, 1400);
    })
    .catch(() => {
      showError("Could not copy result.");
    });
}

function downloadPDF() {
  const pdfContent = document.getElementById("pdfContent");

  if (!latestAnswerMarkdown || !pdfContent) {
    showError("No travel plan available to download.");
    return;
  }

  const downloadBtn = document.querySelector(".download-btn");
  const oldText = downloadBtn.textContent;
  downloadBtn.textContent = "Preparing PDF...";
  downloadBtn.disabled = true;

  const options = {
    margin: 0.5,
    filename: "ai-travel-plan.pdf",
    image: {
      type: "jpeg",
      quality: 0.98
    },
    html2canvas: {
      scale: 2,
      useCORS: true,
      backgroundColor: "#ffffff"
    },
    jsPDF: {
      unit: "in",
      format: "a4",
      orientation: "portrait"
    },
    pagebreak: {
      mode: ["avoid-all", "css", "legacy"]
    }
  };

  html2pdf()
    .set(options)
    .from(pdfContent)
    .save()
    .then(() => {
      downloadBtn.textContent = oldText;
      downloadBtn.disabled = false;
    })
    .catch(() => {
      downloadBtn.textContent = oldText;
      downloadBtn.disabled = false;
      showError("Could not download PDF.");
    });
}

document.addEventListener("keydown", function(event) {
  if (event.ctrlKey && event.key === "Enter") {
    sendMessage();
  }
});

console.log("✅✅✅ script.js FULLY LOADED ✅✅✅");