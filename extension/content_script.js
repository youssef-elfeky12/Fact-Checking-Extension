/**
 * Fact Checker - Content Script
 * Injects "Check Fact" buttons into tweets and displays verification results
 */

const API_URL = "http://127.0.0.1:8000/check";
const CHECK_BUTTON_CLASS = "fact-checker-button";
const RESULT_CONTAINER_CLASS = "fact-checker-result";
const PROCESSED_ATTRIBUTE = "data-fact-checker-processed";

// Cache for already checked tweets
const checkedTweets = new Map();

/**
 * Extract tweet text from a tweet element
 */
function extractTweetText(tweetElement) {
  // Try multiple selectors for tweet text (Twitter/X changes their DOM frequently)
  const textSelectors = [
    '[data-testid="tweetText"]',
    "[lang] > span",
    ".tweet-text",
    '[dir="auto"] > span',
  ];

  for (const selector of textSelectors) {
    const textElement = tweetElement.querySelector(selector);
    if (textElement && textElement.textContent.trim()) {
      // Get all text spans and join them
      const spans = textElement.querySelectorAll("span");
      const text = Array.from(spans)
        .map((span) => span.textContent)
        .join("")
        .trim();

      if (text.length > 10) {
        // Minimum viable tweet length
        return text;
      }
    }
  }

  return null;
}

/**
 * Create the "Check Fact" button
 */
function createCheckButton() {
  const button = document.createElement("button");
  button.className = CHECK_BUTTON_CLASS;
  button.textContent = "🔍 Check Fact";
  button.title = "Verify this tweet with AI fact-checking";

  return button;
}

/**
 * Create the result display container
 */
function createResultContainer() {
  const container = document.createElement("div");
  container.className = RESULT_CONTAINER_CLASS;
  container.style.display = "none";

  return container;
}

/**
 * Display the fact-check result
 */
function displayResult(container, result) {
  const { verdict, certainty, evidences, explanation } = result;

  // Convert verdict to display text
  let verdictText, color;
  if (verdict === "SUPPORTS") {
    verdictText = "True";
    color = "#10b981"; // green
  } else if (verdict === "REFUTES") {
    verdictText = "False";
    color = "#ef4444"; // red
  } else {
    verdictText = "Uncertain";
    color = "#f59e0b"; // orange
  }

  // Convert certainty to percentage (0.0-1.0 -> 0-100)
  const certaintyPercent = Math.round(certainty * 100);

  // Clean up explanation - remove the "VERDICT: ... | CERTAINTY: ..." prefix if present
  let cleanedExplanation = explanation;
  const verdictPattern = /^VERDICT:\s*\w+\s*\|\s*CERTAINTY:\s*\d+%\s*\|\s*/i;
  cleanedExplanation = cleanedExplanation.replace(verdictPattern, "");
  // Also try without the pipe format
  cleanedExplanation = cleanedExplanation.replace(
    /^VERDICT:\s*\w+\s*\|\s*CERTAINTY:\s*\d+%\s*/i,
    ""
  );
  cleanedExplanation = cleanedExplanation.replace(/^EXPLANATION:\s*/i, "");

  // Build HTML with new format: "True/False XX% certainty"
  let html = `
    <div class="fact-checker-header">
      <div class="fact-checker-score" style="color: ${color};">
        <span class="score-label">${verdictText} ${certaintyPercent}% certainty</span>
      </div>
    </div>
    
    <div class="fact-checker-explanation">
      ${cleanedExplanation}
    </div>
  `;

  // Add evidence if available
  if (evidences && evidences.length > 0) {
    html += `<div class="fact-checker-evidence">`;
    html += `<div class="evidence-header">Top ${evidences.length} Most Reliable Sources:</div>`;

    evidences.slice(0, 3).forEach((ev, idx) => {
      const stanceIcon =
        ev.stance === "support" ? "✓" : ev.stance === "contradict" ? "✗" : "○";
      const stanceClass = `stance-${ev.stance}`;

      // Make source clickable if URL is available
      const sourceHTML = ev.url
        ? `<a href="${ev.url}" target="_blank" rel="noopener noreferrer" class="evidence-source-link">${ev.source} 🔗</a>`
        : `<span>${ev.source}</span>`;

      html += `
        <div class="evidence-item ${stanceClass}">
          <span class="evidence-icon">${stanceIcon}</span>
          <div class="evidence-content">
            <div class="evidence-source">${sourceHTML}</div>
            <div class="evidence-snippet">${ev.snippet}</div>
          </div>
        </div>
      `;
    });

    html += `</div>`;
  }

  container.innerHTML = html;
  container.style.display = "block";
}

/**
 * Display loading state
 */
function displayLoading(container) {
  container.innerHTML = `
    <div class="fact-checker-loading">
      <span class="loading-spinner">⏳</span>
      <span>Checking facts...</span>
    </div>
  `;
  container.style.display = "block";
}

/**
 * Display error state
 */
function displayError(container, message) {
  container.innerHTML = `
    <div class="fact-checker-error">
      <span class="error-icon">⚠️</span>
      <span>${message}</span>
    </div>
  `;
  container.style.display = "block";
}

/**
 * Call the fact-checking API via background script (to bypass CSP)
 */
async function checkFact(tweetText) {
  // Check cache first
  if (checkedTweets.has(tweetText)) {
    return checkedTweets.get(tweetText);
  }

  try {
    console.log("Sending message to background script");
    console.log("Tweet text:", tweetText.substring(0, 100));

    // Send message to background script which will make the actual API call
    const response = await browser.runtime.sendMessage({
      type: "CHECK_FACT",
      tweetText: tweetText,
    });

    console.log("Response from background:", response);

    if (!response.success) {
      throw new Error(response.error || "Unknown error");
    }

    const result = response.data;
    console.log("Result received:", result);

    // Cache the result
    checkedTweets.set(tweetText, result);

    return result;
  } catch (error) {
    console.error("Fact-checking API error:", error);
    console.error("Error type:", error.constructor.name);
    console.error("Error message:", error.message);
    throw error;
  }
}

/**
 * Handle button click
 */
async function handleCheckButtonClick(button, tweetElement, resultContainer) {
  // Prevent double-clicking
  if (button.disabled) return;

  button.disabled = true;
  button.textContent = "⏳ Checking...";

  // Extract tweet text
  const tweetText = extractTweetText(tweetElement);

  if (!tweetText) {
    displayError(resultContainer, "Could not extract tweet text");
    button.disabled = false;
    button.textContent = "🔍 Check Fact";
    return;
  }

  // Show loading state
  displayLoading(resultContainer);

  try {
    // Call API
    const result = await checkFact(tweetText);

    // Display result
    displayResult(resultContainer, result);

    // Update button
    button.textContent = "✓ Checked";
  } catch (error) {
    console.error("Full error details:", error);

    // Show more specific error message
    let errorMessage = "Backend not available. ";
    if (error.message && error.message.includes("NetworkError")) {
      errorMessage +=
        "Firefox may be blocking localhost access. Check extension permissions.";
    } else if (error.message) {
      errorMessage += error.message;
    } else {
      errorMessage +=
        "Make sure the server is running on http://127.0.0.1:8000";
    }

    displayError(resultContainer, errorMessage);

    // Re-enable button
    button.disabled = false;
    button.textContent = "🔍 Check Fact";
  }
}

/**
 * Add fact-checker button to a tweet
 */
function addFactCheckerToTweet(tweetElement) {
  // Check if already processed
  if (tweetElement.getAttribute(PROCESSED_ATTRIBUTE)) {
    return;
  }

  // Mark as processed
  tweetElement.setAttribute(PROCESSED_ATTRIBUTE, "true");

  // Find the action bar (where like, retweet buttons are)
  const actionBar = tweetElement.querySelector('[role="group"]');

  if (!actionBar) {
    return; // Not a valid tweet element
  }

  // Create button and result container
  const button = createCheckButton();
  const resultContainer = createResultContainer();

  // Add click handler
  button.addEventListener("click", (e) => {
    e.stopPropagation(); // Prevent tweet click
    handleCheckButtonClick(button, tweetElement, resultContainer);
  });

  // Insert button into action bar
  const buttonWrapper = document.createElement("div");
  buttonWrapper.style.marginLeft = "8px";
  buttonWrapper.appendChild(button);
  actionBar.appendChild(buttonWrapper);

  // Insert result container after the tweet
  tweetElement.appendChild(resultContainer);
}

/**
 * Find all tweets on the page and add fact-checker buttons
 */
function processTweets() {
  // Twitter/X uses [data-testid="tweet"] for tweet containers
  const tweets = document.querySelectorAll('[data-testid="tweet"]');

  tweets.forEach((tweet) => {
    addFactCheckerToTweet(tweet);
  });
}

/**
 * Initialize the extension
 */
function init() {
  console.log("Fact Checker extension loaded");

  // Process initial tweets
  processTweets();

  // Watch for new tweets (infinite scroll)
  const observer = new MutationObserver((mutations) => {
    processTweets();
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });

  console.log("Fact Checker: Watching for tweets...");
}

// Wait for page to be ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
