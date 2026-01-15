// Connect to Socket.IO server
document.addEventListener("DOMContentLoaded", function () {
  const socket = io();

  // DOM elements for workflow steps
  const githubTokenSection = document.getElementById("githubTokenSection");
  const repositorySelectionSection = document.getElementById("repositorySelectionSection");
  const issueSelectionSection = document.getElementById("issueSelectionSection");
  const configurationSection = document.getElementById("configurationSection");

  // Navigation buttons
  const prevStepBtn = document.getElementById("prevStepBtn");
  const nextStepBtn = document.getElementById("nextStepBtn");
  const startRunBtn = document.getElementById("startRunBtn");

  // Form elements
  const githubTokenInput = document.getElementById("githubToken");
  const validateTokenBtn = document.getElementById("validateTokenBtn");
  const tokenValidationStatus = document.getElementById("tokenValidationStatus");
  
  const githubRepoUrlInput = document.getElementById("github-repo-input");
  const branchSelectionGroup = document.getElementById("branchSelectionGroup");
  const githubBranchSelect = document.getElementById("githubBranch");
  const selectedRepoInfo = document.getElementById("selectedRepoInfo");
  const repoDisplayName = document.getElementById("repoDisplayName");
  const branchDisplayName = document.getElementById("branchDisplayName");

  const githubIssueInput = document.getElementById("githubIssueInput");
  const manualIssueText = document.getElementById("manualIssueText");

  // Configuration elements
  const modelSelect = document.getElementById("modelName");

  // Other UI elements
  const activeRunsContainer = document.getElementById("activeRuns");
  const chatMessagesContainer = document.getElementById("chatMessages");
  const timelineViewContainer = document.getElementById("timelineView");
  const runDetailsContainer = document.getElementById("runDetails");
  const runStatusElement = document.getElementById("runStatus");
  const exitStatusElement = document.getElementById("exitStatus");
  const stepCountElement = document.getElementById("stepCount");

  // Cost display elements
  const costDisplayContainer = document.getElementById("costDisplay");
  const costStatsContainer = document.getElementById("costStats");

  let currentStep = 1;
  let selectedRepository = null;
  let selectedBranch = null;
  let selectedIssueUrl = null;
  
  // Workflow steps
  const STEP_TOKEN = 1;
  const STEP_REPO = 2;
  const STEP_ISSUE = 3;
  const STEP_CONFIG = 4;

  // Initialize workflow
  function initWorkflow() {
    updateStepDisplay();
    setupEventListeners();
    fetchModels();
  }

  // Update which step is visible
  function updateStepDisplay() {
    // Hide all steps
    githubTokenSection.classList.add("hidden");
    repositorySelectionSection.classList.add("hidden");
    issueSelectionSection.classList.add("hidden");
    configurationSection.classList.add("hidden");

    // Show current step
    switch (currentStep) {
      case STEP_TOKEN:
        githubTokenSection.classList.remove("hidden");
        break;
      case STEP_REPO:
        repositorySelectionSection.classList.remove("hidden");
        break;
      case STEP_ISSUE:
        issueSelectionSection.classList.remove("hidden");
        // Show GitHub issues section if we have a repo
        if (selectedRepository) {
          document.getElementById("githubIssuesSection").classList.remove("hidden");
        }
        break;
      case STEP_CONFIG:
        configurationSection.classList.remove("hidden");
        break;
    }

    // Update navigation buttons
    prevStepBtn.classList.toggle("hidden", currentStep === 1);
    nextStepBtn.classList.toggle("hidden", currentStep === 4);
    startRunBtn.classList.toggle("hidden", currentStep !== 4);
  }

  // Setup event listeners for workflow navigation
  function setupEventListeners() {
    prevStepBtn.addEventListener("click", goToPreviousStep);
    nextStepBtn.addEventListener("click", goToNextStep);
    startRunBtn.addEventListener("click", startAgentRun);
    
    // GitHub token validation
    validateTokenBtn.addEventListener("click", async function() {
      const isValid = await validateGitHubToken();
      if (isValid) {
        // Auto-advance to next step after successful validation
        setTimeout(goToNextStep, 500);
      }
    });

    // Repository selection - use the auto-complete element's events
    githubRepoUrlInput.addEventListener("change", function() {
      if (this.value) {
        selectedRepository = this.value;
        updateSelectedRepoDisplay();
        
        // Fetch branches for this repository
        fetchGitHubBranches(this.value);
      }
    });
    const completer = document.getElementById("github-repo-auto-complete");
    const container = completer.parentElement;
    completer.addEventListener("loadstart", () =>
      container.classList.add("is-loading"),
    );
    completer.addEventListener("loadend", () =>
      container.classList.remove("is-loading"),
    );
    completer.addEventListener("load", () =>
      container.classList.add("is-success"),
    );
    completer.addEventListener("error", () =>
      container.classList.add("is-error"),
    );
    completer.fetchResult = async (url) => {
      response = await fetch(url);
      json = await response.json();

      // Enhanced HTML with professional GitHub-like styling
      html = json.repositories
        .map(
          (r) => `
              <li role="option" data-autocomplete-value="${r.full_name}" class="autocomplete-item">
                  <span class="autocomplete-repo-icon">🐙</span>
                  <div class="autocomplete-repo-info">
                      <div class="autocomplete-repo-name">${r.full_name}</div>
                      ${r.description ? `<div class="autocomplete-repo-description">${r.description}</div>` : ""}
                      <div class="autocomplete-repo-stats">
                          <span class="autocomplete-repo-stat autocomplete-star-icon">⭐ ${r.stargazers_count || 0}</span>
                          <span class="autocomplete-repo-stat autocomplete-fork-icon">🍴 ${r.forks_count || 0}</span>
                      </div>
                  </div>
              </li>
          `,
        )
        .join("");

      return html;
    };

    // Branch selection
    githubBranchSelect.addEventListener("change", function() {
      if (this.value) {
        selectedBranch = this.value;
        updateSelectedRepoDisplay();
      }
    });

    // Issue input - either from dropdown or manual entry
    let issueDebounceTimer;
    githubIssueInput.addEventListener("input", function() {
      clearTimeout(issueDebounceTimer);
      issueDebounceTimer = setTimeout(() => {
        fetchGitHubIssues();
      }, 300);
    });

    // Handle issue selection from dropdown
    githubIssueInput.addEventListener("change", function() {
      if (this.value) {
        selectedIssueUrl = this.value;
        manualIssueText.value = this.value; // Sync with manual field
      }
    });
  }

  // Go to previous step in workflow
  function goToPreviousStep() {
    if (currentStep > 1) {
      currentStep--;
      updateStepDisplay();
    }
  }

  // Go to next step in workflow
  function goToNextStep() {
    let canAdvance = true;
    
    // Validate current step before advancing
    switch (currentStep) {
      case STEP_TOKEN:
        if (!githubTokenInput.value.trim()) {
          alert("Please enter a GitHub token");
          canAdvance = false;
        }
        break;
      case STEP_REPO:
        if (!selectedRepository) {
          alert("Please select a repository");
          canAdvance = false;
        }
        break;
      case STEP_ISSUE:
        // Issue text is required
        const issueText = manualIssueText.value.trim();
        if (!issueText && !selectedIssueUrl) {
          alert("Please enter an issue description or select an issue from the list");
          canAdvance = false;
        }
        break;
    }

    if (canAdvance) {
      currentStep++;
      updateStepDisplay();
      
      // When moving to issue selection, fetch issues for the repo
      if (currentStep === STEP_ISSUE && selectedRepository) {
        fetchGitHubIssues();
      }
    }
  }

  // Update display of selected repository and branch
  function updateSelectedRepoDisplay() {
    if (selectedRepository) {
      selectedRepoInfo.classList.remove("hidden");
      repoDisplayName.textContent = `Repository: ${selectedRepository}`;
      
      if (selectedBranch) {
        branchDisplayName.textContent = `Branch: ${selectedBranch}`;
      } else {
        branchDisplayName.textContent = "Branch: main (default)";
      }
    } else {
      selectedRepoInfo.classList.add("hidden");
    }
  }

  // GitHub token validation function
  async function validateGitHubToken() {
    const token = githubTokenInput.value.trim();
    
    if (!token) {
      showTokenValidationStatus("error", "Please enter a GitHub token");
      return false;
    }
    
    try {
      const response = await fetch("/api/github/validate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ token: token }),
      });
      
      const data = await response.json();
      
      if (response.ok && data.valid) {
        showTokenValidationStatus("success", "GitHub token is valid!");
        return true;
      } else {
        showTokenValidationStatus("error", data.error || "Invalid GitHub token");
        return false;
      }
    } catch (error) {
      console.error("Error validating token:", error);
      showTokenValidationStatus("error", "Failed to validate token: " + error.message);
      return false;
    }
  }

  // Show token validation status
  function showTokenValidationStatus(type, message) {
    tokenValidationStatus.textContent = message;
    tokenValidationStatus.className = `validation-status ${type}`;
    tokenValidationStatus.classList.remove("hidden");
  }

  // Fetch available branches for a GitHub repository
  async function fetchGitHubBranches(repoUrl) {
    const token = githubTokenInput.value.trim();
    
    if (!repoUrl || !token) return;
    
    try {
      // Extract owner/repo from URL
      let repoName = repoUrl;
      if (repoUrl.startsWith("https://github.com/")) {
        const parts = repoUrl.split("/");
        if (parts.length >= 5) {
          repoName = `${parts[3]}/${parts[4]}`;
        }
      }

      const response = await fetch(`/api/github/branches?repo=${encodeURIComponent(repoName)}&github_token=${token}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        
        // Clear existing options except default
        while (githubBranchSelect.options.length > 1) {
          githubBranchSelect.remove(1);
        }

        // Add branch options
        (data.branches || []).forEach(branch => {
          const option = document.createElement("option");
          option.value = branch;
          option.textContent = branch;
          githubBranchSelect.appendChild(option);
        });

        // Show branch selection
        branchSelectionGroup.style.display = "block";
      }
    } catch (error) {
      console.error("Error fetching branches:", error);
    }
  }

  // Fetch GitHub issues from API based on current repository and search query
  async function fetchGitHubIssues() {
    const repoUrl = githubIssueInput.dataset.repoUrl || selectedRepository;
    
    if (!repoUrl) {
      document.getElementById("github-issue-results").innerHTML = "";
      return;
    }

    try {
      const response = await fetch(
        `/api/github/issues?repo=${encodeURIComponent(repoUrl)}`,
      );
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      displayGitHubIssues(data.issues || []);
    } catch (error) {
      console.error("Error fetching GitHub issues:", error);
      // Clear results on error
      document.getElementById("github-issue-results").innerHTML = "";
    }
  }

  // Display GitHub issues in the dropdown
  function displayGitHubIssues(issues) {
    const resultsContainer = document.getElementById("github-issue-results");
    if (!resultsContainer) return;

    if (issues.length === 0) {
      resultsContainer.innerHTML =
        '<li class="no-results">No open issues found</li>';
      return;
    }

    const html = issues
      .map(
        (issue) => `
            <li class="github-issue-result" data-url="${issue.url}">
                <div class="github-issue-number">#${issue.number}</div>
                <div class="github-issue-title">${escapeHtml(issue.title)}</div>
                ${issue.body ? `<div class="github-issue-body">${truncateText(escapeHtml(issue.body), 100)}</div>` : ""}
            </li>
        `,
      )
      .join("");

    resultsContainer.innerHTML = html;

    // Add click handlers to issue items
    const issueItems = resultsContainer.querySelectorAll(".github-issue-result");
    issueItems.forEach(item => {
      item.addEventListener("click", function() {
        selectedIssueUrl = this.dataset.url;
        manualIssueText.value = this.dataset.url;
        githubIssueInput.value = this.dataset.url || "";
      });
    });
  }

  // Start agent run with collected configuration
  async function startAgentRun() {
    const problemStatement = manualIssueText.value.trim();
    
    if (!problemStatement && !selectedIssueUrl) {
      alert("Please enter an issue description");
      return;
    }

    // Build the final problem statement
    let finalProblemStatement = problemStatement;
    
    if (selectedIssueUrl) {
      // Use GitHub issue URL format
      finalProblemStatement = {
        type: "github",
        github_url: selectedIssueUrl,
      };
    }

    // Build configuration from UI inputs
    const config = {};

    // Handle repository configuration if a GitHub repo was selected
    if (selectedRepository) {
      if (!config.env) config.env = {};
      if (!config.env.repo) config.env.repo = {};
      config.env.repo.type = "github";
      config.env.repo.github_url = selectedRepository;
      
      // Add branch if specified
      if (selectedBranch) {
        config.env.repo.branch = selectedBranch;
      }
    }

    // Handle agent configuration
    const modelTemperature = document.getElementById("modelTemperature").value;
    const modelName = document.getElementById("modelName").value;
    const costLimit = document.getElementById("costLimit").value;
    const enableBash = document.getElementById("enableBash").value;

    if (modelTemperature || modelName || costLimit || enableBash) {
      config.agent = {};

      if (modelTemperature || modelName || costLimit) {
        config.agent.model = {};

        if (modelTemperature) {
          config.agent.model.temperature = parseFloat(modelTemperature);
        }

        if (modelName) {
          config.agent.model.name = modelName;
        }

        if (costLimit) {
          config.agent.model.per_instance_cost_limit = parseFloat(costLimit);
        }
      }

      if (enableBash !== "") {
        if (!config.agent.tools) config.agent.tools = {};
        config.agent.tools.enable_bash_tool = enableBash === "true";
      }
    }

    try {
      // Create the run via API
      const response = await fetch("/api/runs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          problem_statement: finalProblemStatement,
          config: config,
          github_token: githubTokenInput.value.trim(),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        alert("Failed to start run: " + (errorData.error || "Unknown error"));
        return;
      }

      const data = await response.json();
      const runId = data.run_id;

      // Store current run ID for tracking
      window.currentRunId = runId;

      console.log("Started run:", runId);
      
      // You could navigate to a run monitoring view here
      // For now, just show success message
      refreshRunsList();
    } catch (error) {
      console.error("Error starting agent:", error);
      alert("Failed to start agent: " + error.message);
    }
  }

  // Fetch available models from API and populate dropdown
  async function fetchModels() {
    try {
      const response = await fetch("/api/models");
      if (!response.ok) throw new Error("Failed to load models");

      const data = await response.json();

      if (data.model_names && data.model_names.length > 0) {
        // Clear existing options except the default one
        while (modelSelect.options.length > 1) {
          modelSelect.remove(1);
        }

        // Add model options
        data.model_names.forEach((modelName) => {
          const option = document.createElement("option");
          option.value = modelName;
          option.textContent = modelName;
          modelSelect.appendChild(option);
        });
      }
    } catch (error) {
      console.error("Error loading models:", error);
    }
  }

  // Encode HTML for use in onclick handlers and attributes
  function encodeHTML(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  // Update cost display sidebar with model statistics
  function updateCostDisplay(stats) {
    let html = "";

    const formatStatKey = (key) => {
      const mappings = {
        total_tokens: "Total Tokens",
        input_tokens: "Input Tokens",
        output_tokens: "Output Tokens",
        cost_usd: "Cost ($)",
        execution_time: "Time (s)",
      };
      return (
        mappings[key] ||
        key
          .split("_")
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
          .join(" ")
      );
    };

    // Display all stats except cost
    Object.entries(stats).forEach(([key, value]) => {
      if (key !== "cost_usd") {
        const formattedValue =
          typeof value === "number" ? value.toFixed(2) : value;
        html += `<div class="cost-stat"><span class="cost-label">${formatStatKey(key)}:</span><span class="cost-value">${formattedValue}</span></div>`;
      }
    });

    // Display cost separately with emphasis
    if (stats.cost_usd) {
      const cost = typeof stats.cost_usd === "number" ? stats.cost_usd.toFixed(2) : stats.cost_usd;
      html += `<div class="cost-total">Total Cost: $${cost}</div>`;
    }

    costStatsContainer.innerHTML = html;
  }

  // Add model statistics as a chat message
  function addModelStats(stats) {
    const messageDiv = document.createElement("div");
    messageDiv.className = "chat-message message-system model-stats";

    let statsHtml = "<strong>Model Stats:</strong> ";
    statsHtml += Object.entries(stats)
      .map(([key, value]) => {
        const formattedValue =
          typeof value === "number" ? value.toFixed(2) : value;
        return `<span class="stat-item">${formatStatKey(key)}: ${formattedValue}</span>`;
      })
      .join(" | ");

    messageDiv.innerHTML = statsHtml;
    chatMessagesContainer.appendChild(messageDiv);
    smoothScrollToBottom(chatMessagesContainer);
  }

  // Format stat key for display (used by updateCostDisplay and addModelStats)
  function formatStatKey(key) {
    const mappings = {
      total_tokens: "Total Tokens",
      input_tokens: "Input Tokens",
      output_tokens: "Output Tokens",
      cost_usd: "Cost ($)",
      execution_time: "Time (s)",
    };
    return (
      mappings[key] ||
      key
        .split("_")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ")
    );
  }

  // Escape HTML to prevent XSS
  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  }

  // Format a component for the timeline view
  function formatComponent(label, content, type) {
    let contentClass = "component-content";
    if (type === "thought") contentClass += " thought-content";
    else if (type === "action") contentClass += " action-content";
    else if (type === "observation") contentClass += " observation-content";

    return `
            <div class="${contentClass}">
                <strong>${label}:</strong> ${content}
            </div>
        `;
  }

  // Add a step to the timeline view
  function addStepToTimeline(stepNum, stepData) {
    const stepCard = document.createElement("div");
    stepCard.className = "step-card";

    let thoughtContent = "";
    let actionContent = "";
    let observationContent = "";
    let responseContent = "";

    if (stepData.thought) {
      thoughtContent = formatComponent("Thought", stepData.thought, "thought");
    }

    if (stepData.action) {
      // Check if action is a bash command
      const bashRegex = /^bash: (.+)$/i;
      if (bashRegex.test(stepData.action)) {
        const bashCommand = stepData.action.replace(bashRegex, "$1");
        actionContent = formatComponent(
          "Action",
          `<pre>${escapeHtml(bashCommand)}</pre>`,
          "action"
        );
      } else {
        actionContent = formatComponent("Action", stepData.action, "action");
      }
    }

if (stepData.observation) {
      // title = observation up to and included the first colon : box the rest of the content
      const colonIndex = stepData.observation.indexOf(':');
      let title, content;
      if (colonIndex !== -1) {
        title = stepData.observation.substring(0, colonIndex + 1);
        content = stepData.observation.substring(colonIndex + 1).trim();
      } else {
        title = "👁️‍🗨️ Observation";
        content = stepData.observation;
      }
      observationContent = formatComponent(title, content, "observation");
    }
    if (stepData.response) {
      responseContent = formatComponent("Response", stepData.response, "response");
    }

    stepCard.innerHTML = `
            <div class="step-header">Step ${stepNum}</div>
            ${thoughtContent}
            ${actionContent}
            ${observationContent}
            ${responseContent}
        `;

    timelineViewContainer.appendChild(stepCard);
  }

  // Add a chat message to the chat interface
  function addChatMessage(role, content) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `chat-message message-${role}`;

    let formattedContent = content;

    // Detect bash commands
    const bashRegex = /^bash: (.+)$/i;
    const bashMatch = content.match(bashRegex);

    if (bashMatch) {
      formattedContent = `
                <div class="message-content">
                    <div class="code-header">
                        <span class="code-language">Bash</span>
                        <button class="copy-button" onclick="copyToClipboard('${encodeHTML(content)}')">Copy</button>
                    </div>
                    <pre class="code-block"><code>${escapeHtml(bashMatch[1])}</code></pre>
                </div>`;
    } else {
      formattedContent = `<div class="message-content">${content}</div>`;
    }

    messageDiv.innerHTML = formattedContent;
    chatMessagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    smoothScrollToBottom(chatMessagesContainer);
  }

  // Update run info display (status, exit code, steps)
  function updateRunInfo(data) {
    if (data.exit_status) {
      exitStatusElement.innerHTML = `<span class="info-item">Exit: ${data.exit_status}</span>`;
    }

    stepCountElement.innerHTML = `<span class="info-item">Steps: ${data.trajectory ? data.trajectory.length : 0}</span>`;

    if (data.model_stats && Object.keys(data.model_stats).length > 0) {
      // Update cost display sidebar
      updateCostDisplay(data.model_stats);
      costDisplayContainer.classList.remove("hidden");

      // Add model stats to the chat as well (for backward compatibility)
      addModelStats(data.model_stats);
    }
  }

  // Create a visual card for a run in the runs list
  function createRunCard(run) {
    const card = document.createElement("div");
    card.className = "run-card";
    card.dataset.runId = run.run_id;

    let statusClass = "status-started";
    if (run.completed) {
      statusClass = run.error ? "status-error" : "status-completed";
    }

    // Build problem statement display
    const problemStatement = run.problem_statement
      ? `<div class="run-problem">${escapeHtml(run.problem_statement)}</div>`
      : "";

    // Build current action display
    let currentActionDisplay = "";
    if (run.current_action) {
      const actionText =
        run.current_action.length > 100
          ? escapeHtml(run.current_action.substring(0, 100)) + "..."
          : escapeHtml(run.current_action);
      currentActionDisplay = `
                <div class="run-action">
                    <strong>Current Action:</strong> ${actionText}
                </div>`;
    }

    // Build model stats display
    let modelStatsDisplay = "";
    if (run.model_stats && Object.keys(run.model_stats).length > 0) {
      const cost = run.model_stats.cost_usd || 0;
      const tokens = run.model_stats.total_tokens || 0;
      modelStatsDisplay = `
                <div class="run-stats">
                    <strong>Cost:</strong> $${typeof cost === "number" ? cost.toFixed(2) : cost} |
                    <strong>Tokens:</strong> ${typeof tokens === "number" ? tokens.toFixed(0) : tokens}
                </div>`;
    }

    card.innerHTML = `
            <div class="run-header">
                <span class="run-id">Run ${run.run_id}</span>
                <span class="run-status ${statusClass}">
                    ${run.completed ? (run.error ? "Error" : "Completed") : "Running"}
                </span>
            </div>
            ${problemStatement}
            <div class="run-steps">Steps: ${run.steps || 0}</div>
            ${currentActionDisplay}
            ${modelStatsDisplay}
        `;

    card.addEventListener("click", function () {
      loadRunDetails(run.run_id);
    });

    return card;
  }

  // Load run details and display in the chat interface
  async function loadRunDetails(runId) {
    currentRunId = runId;

    try {
      const response = await fetch(`/api/runs/${runId}/trajectory`);
      if (!response.ok) throw new Error("Failed to load trajectory");

      const data = await response.json();

      // Clear previous content
      chatMessagesContainer.innerHTML = "";
      timelineViewContainer.innerHTML = "";
      runDetailsContainer.classList.remove("hidden");

      // Add problem statement to chat (for context)
      if (data.problem_statement?.type === "github")
      addChatMessage("user", data.problem_statement);

      // Use timeline view for trajectory steps
      if (data.trajectory && data.trajectory.length > 0) {
        // Switch to timeline view
        chatMessagesContainer.classList.add("hidden");
        timelineViewContainer.classList.remove("hidden");

        data.trajectory.forEach((step, index) => {
          const stepNum = index + 1;
          addStepToTimeline(stepNum, step);
        });
      }

      // Update run info
      updateRunInfo(data);
    } catch (error) {
      console.error("Error loading run details:", error);
      addChatMessage("system", `Error: ${error.message}`);
    }
  }

  // Refresh the list of active runs
  async function refreshRunsList() {
    try {
      const response = await fetch("/api/runs");
      if (!response.ok) throw new Error("Failed to load runs");

      const data = await response.json();
      activeRunsContainer.innerHTML = "";

      data.runs.forEach((run) => {
        activeRunsContainer.appendChild(createRunCard(run));
      });
    } catch (error) {
      console.error("Error refreshing runs list:", error);
    }
  }

  // Initialize the workflow when page loads
  initWorkflow();

  // Copy to clipboard functionality
  window.copyToClipboard = function (text) {
    navigator.clipboard.writeText(text).then(function () {
      alert("Copied to clipboard!");
    });
  };

  // Helper function for smooth scrolling (reduces forced reflows)
  function smoothScrollToBottom(element) {
    // Use requestAnimationFrame to batch with other operations
    requestAnimationFrame(() => {
      element.scrollTop = element.scrollHeight;
    });
  }

  // Socket.IO event handlers for real-time updates
  socket.on("connect", function () {
    console.log("Connected to server");
    refreshRunsList();
  });

  socket.on("update", function (data) {
    if (data.run_id !== currentRunId) return;

    const stepNumber = data.step_count || 1;
    const stepData = data.current_step || null;
    const message = data.message || "";

    // Group all messages under the current step or global
    const stepContainer = getStepContainer(stepNumber);

    // Clear previous content
    stepContainer.innerHTML = "";

    // Handle status
    if (data.status === "completed") {
      // Final message
      addFinalMessage(stepContainer, data.exit_status || "success", data.step_count);
      return;
    }

    // If no step data, just show message
    if (!stepData && !message) {
      addChatMessage(stepContainer, "system", "Agent is running...");
      return;
    }

    // === Step Flow: Thought → Action → Observation ===
    if (stepData) {
      // 1. Thought (if present)
      if (stepData.thought) {
        addThoughtMessage(stepContainer, stepData.thought);
      } else {
        // Implied action (no thought needed)
        addImpliedActionMessage(stepContainer, stepData.action);
      }

      // 2. Action (tool call)
      if (stepData.action) {
        const bashRegex = /^bash: (.+)$/i;
        if (bashRegex.test(stepData.action)) {
          addToolCallMessage(stepContainer, "Bash", stepData.action.replace(bashRegex, "$1"));
        } else {
          addToolCallMessage(stepContainer, "Action", stepData.action);
        }
      }

      // 3. Observation (result)
      if (stepData.observation) {
        addObservationMessage(stepContainer, stepData.observation);
      }
    }

    // Handle general messages (e.g., "Starting run", "Step 3 of 5")
    if (message) {
      message_text = message.split("Planning: ")
      if (message === message_text) {
        addChatMessage(stepContainer, "system", message);
      }
    }

    // Display model stats
    if (data.model_stats && Object.keys(data.model_stats).length > 0) {
      updateCostDisplay(data.model_stats);
      costDisplayContainer.classList.remove("hidden");
      addModelStats(data.model_stats);
    }

    refreshRunsList();
    // Auto-scroll to bottom
    smoothScrollToBottom(stepContainer);
  });

  // === Helper Functions ===

  function getStepContainer(stepNumber) {
    if (!stepMap.has(stepNumber)) {
      const container = document.createElement("div");
      container.className = "step-card";
      container.dataset.step = stepNumber;
      container.dataset.open = "false";

      const header = document.createElement("div");
      header.className = "step-header";
      header.innerHTML = `<span class="step-number">Step ${stepNumber}</span> <span class="step-icon">▶</span>`;
      container.appendChild(header);

      const content = document.createElement("div");
      content.className = "step-content";
      content.innerHTML = `<div class="step-details"></div>`;
      container.appendChild(content);

      // Add to container
      const containerEl = document.getElementById("chatMessages");
      containerEl.appendChild(container);

      stepMap.set(stepNumber, container);
    }
    return stepMap.get(stepNumber);
  }

  function addThoughtMessage(container, thought) {
    const msg = document.createElement("div");
    msg.className = "thought-message";
    msg.innerHTML = `<span class="icon">🧠</span> <strong>Thought:</strong> ${thought}`;
    container.appendChild(msg);
  }

  function addImpliedActionMessage(container, action) {
    const msg = document.createElement("div");
    msg.className = "implied-action";
    msg.innerHTML = `<span class="icon">➡️</span> <strong>Implied:</strong> ${action}`;
    container.appendChild(msg);
  }

  function addToolCallMessage(container, type, action) {
    const block = document.createElement("div");
    block.className = "tool-call";
    block.innerHTML = `
      <div class="tool-header">
        <span class="icon">⚙️</span>
        <span class="tool-type">${type}</span>
      </div>
      <div class="tool-content">
        <pre class="code-block"><code>${escapeHtml(action)}</code></pre>
        <button class="copy-button" onclick="copyToClipboard('${encodeHTML(action)}')">Copy</button>
      </div>
    `;
    container.appendChild(block);
  }

  function addObservationMessage(container, observation) {
    const msg = document.createElement("div");
    msg.className = "observation-message";
    msg.innerHTML = `<span class="icon">✅</span> <strong>Observation:</strong> ${observation}`;
    container.appendChild(msg);
  }

  function addFinalMessage(container, status, stepCount) {
    const msg = document.createElement("div");
    msg.className = "final-message";
    msg.innerHTML = `<strong>✅ Run completed!</strong> Exit status: ${status}. Total steps: ${stepCount}`;
    container.appendChild(msg);
  }

  function addChatMessage(container, role, content) {
    const msg = document.createElement("div");
    msg.className = `chat-message message-${role}`;
    msg.innerHTML = `<strong>${role}:</strong> ${content}`;
    container.appendChild(msg);
  }
});