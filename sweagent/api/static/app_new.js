// Connect to Socket.IO server
document.addEventListener("DOMContentLoaded", function () {
  const socket = io();

  // DOM elements for workflow steps
  const githubAuthSection = document.getElementById("githubAuthSection");
  const githubRepoSection = document.getElementById("githubRepoSection");
  const githubIssueSection = document.getElementById("githubIssueSection");
  const configSection = document.getElementById("configSection");

  // Navigation buttons
  const prevStepBtn = document.getElementById("prevStepBtn");
  const nextStepBtn = document.getElementById("nextStepBtn");
  const startRunBtn = document.getElementById("startRunBtn");

  // GitHub token elements
  const githubTokenInput = document.getElementById("githubToken");
  const validateTokenBtn = document.getElementById("validateTokenBtn");
  const tokenValidationStatus = document.getElementById("tokenValidationStatus");

  // Repository elements
  const githubRepoUrlInput = document.getElementById("github-repo-input");

  // Issue selection elements
  const githubIssuesSection = document.getElementById("githubIssuesSection");
  const problemStatementInput = document.getElementById("problemStatement");
  const githubIssueInput = document.getElementById("githubIssueInput");

  // Configuration elements
  const modelSelect = document.getElementById("modelName");

  // Chat interface elements
  const chatMessagesContainer = document.getElementById("chatMessages");
  const timelineViewContainer = document.getElementById("timelineView");
  const activeRunsContainer = document.getElementById("activeRuns");

  // Current workflow step (0: auth, 1: repo, 2: issue, 3: config)
  let currentStep = 0;
  let githubTokenValidated = false;

  // Initialize workflow - show only first step
  function updateWorkflowUI() {
    // Hide all steps
    githubAuthSection.classList.add("hidden");
    githubRepoSection.classList.add("hidden");
    githubIssueSection.classList.add("hidden");
    configSection.classList.add("hidden");

    // Show current step
    switch (currentStep) {
      case 0: // GitHub Authentication
        githubAuthSection.classList.remove("hidden");
        prevStepBtn.classList.add("hidden");
        nextStepBtn.classList.remove("hidden");
        startRunBtn.classList.add("hidden");
        break;
      case 1: // Repository Selection
        githubRepoSection.classList.remove("hidden");
        prevStepBtn.classList.remove("hidden");
        nextStepBtn.classList.remove("hidden");
        startRunBtn.classList.add("hidden");
        break;
      case 2: // Issue Selection
        githubIssueSection.classList.remove("hidden");
        prevStepBtn.classList.remove("hidden");
        nextStepBtn.classList.remove("hidden");
        startRunBtn.classList.add("hidden");
        break;
      case 3: // Configuration
        configSection.classList.remove("hidden");
        prevStepBtn.classList.remove("hidden");
        nextStepBtn.textContent = "Start SWE-agent";
        startRunBtn.classList.add("hidden");
        break;
    }
  }

  // Navigation button handlers
  prevStepBtn.addEventListener("click", function () {
    if (currentStep > 0) {
      currentStep--;
      updateWorkflowUI();
    }
  });

  nextStepBtn.addEventListener("click", async function () {
    switch (currentStep) {
      case 0: // Moving from Auth to Repo
        if (!githubTokenValidated && githubTokenInput.value.trim()) {
          const isValid = await validateGitHubToken();
          if (!isValid) return;
        }
        currentStep++;
        updateWorkflowUI();
        break;
      case 1: // Moving from Repo to Issue
        if (githubRepoUrlInput.value.trim()) {
          currentStep++;
          updateWorkflowUI();
          // Show GitHub issues section when repo is selected
          githubIssuesSection.classList.remove("hidden");
        } else {
          alert("Please select a GitHub repository first");
        }
        break;
      case 2: // Moving from Issue to Config
        currentStep++;
        updateWorkflowUI();
        break;
      case 3: // Start the run
        startRun();
        break;
    }
  });

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
        githubTokenValidated = true;
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

  // Add event listener for token validation button
  validateTokenBtn.addEventListener("click", async function () {
    await validateGitHubToken();
  });

  // Handle GitHub issue input changes - fetch issues from API
  let githubIssueDebounceTimer;
  githubIssueInput.addEventListener("input", function () {
    clearTimeout(githubIssueDebounceTimer);
    githubIssueDebounceTimer = setTimeout(() => {
      fetchGitHubIssues();
    }, 300);
  });

  // Handle GitHub issue selection from dropdown
  githubIssueInput.addEventListener("change", function () {
    if (this.value) {
      problemStatementInput.value = this.value;
    }
  });

  // Update the data-repo-url attribute when GitHub repo input changes
  let githubRepoDebounceTimer;
  githubRepoUrlInput.addEventListener("input", function () {
    clearTimeout(githubRepoDebounceTimer);
    githubRepoDebounceTimer = setTimeout(() => {
      updateGitHubIssueSource();
    }, 500);
  });

  // Update the GitHub issue source URL based on current repository selection
  function updateGitHubIssueSource() {
    const repoUrl = githubRepoUrlInput.value.trim();

    if (!repoUrl) {
      return;
    }

    // Extract owner/repo from GitHub URL
    // Handle formats like: https://github.com/owner/repo or owner/repo
    let repoName = repoUrl;

    // Remove https://github.com/ prefix if present
    if (repoUrl.startsWith("https://github.com/")) {
      repoName = repoUrl.substring(19); // Remove "https://github.com/"
    }
    
    // Remove .git suffix if present
    if (repoName.endsWith(".git")) {
      repoName = repoName.slice(0, -4);
    }

    // Update the data attribute for the auto-complete element
    githubIssueInput.dataset.repoUrl = repoName;
  }

  // Fetch GitHub issues from API based on current repository and search query
  async function fetchGitHubIssues() {
    const repoUrl = githubIssueInput.dataset.repoUrl;
    const searchQuery = githubIssueInput.value.trim();

    if (!repoUrl) {
      // Clear results if no repository is selected
      document.getElementById("github-issue-results").innerHTML = "";
      return;
    }

    try {
      const response = await fetch(`/api/github/issues?repo=${encodeURIComponent(repoUrl)}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) throw new Error("Failed to fetch issues");

      const data = await response.json();
      
      // Display issues in dropdown
      const resultsContainer = document.getElementById("github-issue-results");
      resultsContainer.innerHTML = "";

      if (data.issues && data.issues.length > 0) {
        data.issues.forEach((issue) => {
          const issueElement = document.createElement("li");
          issueElement.className = "github-issue-result";
          issueElement.innerHTML = `
            <div class="github-issue-number">#${issue.number}</div>
            <div class="github-issue-title">${escapeHtml(issue.title)}</div>
            ${issue.body ? `<div class="github-issue-body">${escapeHtml(issue.body.substring(0, 100))}...</div>` : ""}
          `;
          issueElement.addEventListener("click", function () {
            problemStatementInput.value = issue.url;
            resultsContainer.innerHTML = "";
          });
          resultsContainer.appendChild(issueElement);
        });
      } else {
        const noResultsElement = document.createElement("li");
        noResultsElement.className = "no-results";
        noResultsElement.textContent = "No open issues found. Enter a custom problem statement.";
        resultsContainer.appendChild(noResultsElement);
      }
    } catch (error) {
      console.error("Error fetching GitHub issues:", error);
      const resultsContainer = document.getElementById("github-issue-results");
      resultsContainer.innerHTML = "";
      
      const errorElement = document.createElement("li");
      errorElement.className = "no-results";
      errorElement.textContent = `Error loading issues: ${error.message}`;
      resultsContainer.appendChild(errorElement);
    }
  }

  // Start the SWE-agent run with current configuration
  async function startRun() {
    const problemStatement = problemStatementInput.value.trim();

    if (!problemStatement) {
      alert("Please enter a problem statement or select an issue");
      return;
    }

    // Build configuration from UI inputs
    const config = {};

    // Handle repository configuration
    const repoUrl = githubRepoUrlInput.value.trim();
    if (repoUrl) {
      if (!config.env) config.env = {};
      if (!config.env.repo) config.env.repo = {};
      config.env.repo.type = "github";
      config.env.repo.github_url = repoUrl;
    }

    // Handle problem statement (it could be text or GitHub issue URL)
    let finalProblemStatement = problemStatement;
    
    // Check if it's a GitHub issue URL
    const githubIssueRegex = /https:\/\/github\.com\/[^/]+\/[^/]+\/issues\/\d+/i;
    if (githubIssueRegex.test(problemStatement)) {
      finalProblemStatement = {
        type: "github",
        github_url: problemStatement,
      };
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
      const requestBody = { problem_statement: finalProblemStatement };

      // Include GitHub token if provided
      const githubToken = githubTokenInput.value.trim();
      if (githubToken) {
        requestBody.github_token = githubToken;
      }

      if (Object.keys(config).length > 0) {
        requestBody.config = config;
      }

      const response = await fetch("/api/runs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      const data = await response.json();

      if (response.ok) {
        addChatMessage("system", `Started new run: ${data.run_id}`);

        // Refresh runs list
        refreshRunsList();
      } else {
        throw new Error(data.error || "Failed to start run");
      }
    } catch (error) {
      console.error("Error starting run:", error);
      addChatMessage("system", `Error: ${error.message}`);
    }
  }

  // Add message to chat
  function addChatMessage(role, content) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `chat-message message-${role}`;

    let formattedContent = content;

    if (content.includes("\n")) {
      formattedContent = `
        <div class="message-content">
            <pre>${escapeHtml(content)}</pre>
        </div>`;
    }

    messageDiv.innerHTML = `<strong>${role}:</strong> ${formattedContent}`;
    chatMessagesContainer.appendChild(messageDiv);
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
  }

  // Escape HTML to prevent XSS
  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  // Refresh runs list
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

  // Create run card for display
  function createRunCard(run) {
    const card = document.createElement("div");
    card.className = "run-card";
    
    let statusClass = "status-started";
    if (run.status === "completed") statusClass = "status-completed";
    else if (run.status === "error") statusClass = "status-error";

    card.innerHTML = `
      <div class="run-header">
        <span class="run-id">Run ${run.run_id}</span>
        <span class="run-status ${statusClass}">${run.status}</span>
      </div>
      <div class="run-problem">${escapeHtml(run.problem_statement || "No problem statement")}</div>
    `;

    card.addEventListener("click", function () {
      // Load run details when clicked
      loadRunDetails(run.run_id);
    });

    return card;
  }

  // Load run details and trajectory
  async function loadRunDetails(runId) {
    try {
      const response = await fetch(`/api/runs/${runId}/trajectory`);
      if (!response.ok) throw new Error("Failed to load run trajectory");

      const data = await response.json();
      
      // Clear previous timeline and show current one
      timelineViewContainer.innerHTML = "";
      timelineViewContainer.classList.remove("hidden");
      chatMessagesContainer.classList.add("hidden");

      if (data.trajectory && data.trajectory.length > 0) {
        data.trajectory.forEach((step, index) => {
          addStepToTimeline(index + 1, step);
        });
      }
    } catch (error) {
      console.error("Error loading run details:", error);
    }
  }

  // Add step to timeline view
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
      const bashRegex = /^bash: (.+)$/i;
      if (bashRegex.test(stepData.action)) {
        const bashCommand = stepData.action.replace(bashRegex, "$1");
        actionContent = formatComponent(
          "Action",
          `<pre>${escapeHtml(bashCommand)}</pre>`,
          "action"
        );
      } else {
        actionContent = formatComponent(
          "Action",
          escapeHtml(stepData.action),
          "action"
        );
      }
    }

    if (stepData.observation) {
      observationContent = formatComponent(
        "Observation",
        escapeHtml(stepData.observation),
        "observation"
      );
    }

    if (stepData.response && stepData.response.trim() !== "") {
      const lines = stepData.response.split("\n");
      if (
        lines.length > 1 ||
        stepData.response.includes("\t") ||
        stepData.response.match(/^[a-zA-Z0-9_]+:/)
      ) {
        responseContent = formatComponent(
          "Response",
          `<pre>${escapeHtml(stepData.response)}</pre>`,
          "response"
        );
      } else {
        responseContent = formatComponent(
          "Response",
          escapeHtml(stepData.response),
          "response"
        );
      }
    }

    stepCard.innerHTML = `
            <div class="step-header">
                <span class="step-number">Step ${stepNum}</span>
                <span class="step-icon">▼</span>
            </div>
            <div class="step-content">
                <div class="step-details">
                    ${thoughtContent}
                    ${actionContent}
                    ${observationContent}
                    ${responseContent}
                </div>
            </div>`;

    // Add click handler for accordion
    stepCard.addEventListener("click", function (e) {
      if (e.target.tagName === "BUTTON" || e.target.tagName === "A") {
        return;
      }

      stepCard.classList.toggle("active");
    });

    timelineViewContainer.appendChild(stepCard);
  }

  // Format a component (thought, action, observation, response) with proper styling
  function formatComponent(label, content, type) {
    const className = `${type}-section component-section`;
    return `<div class="${className}"><span class="component-label">${label}</span><div class="component-content">${content}</div></div>`;
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

  // Initialize the workflow
  updateWorkflowUI();
  fetchModels();
});