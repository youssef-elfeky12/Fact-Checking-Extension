/**
 * Background Script - Handles API calls without CSP restrictions
 * Content scripts can't make localhost requests due to Twitter's CSP,
 * so we proxy requests through the background script.
 */

const API_BASE = "http://127.0.0.1:8000";

// Listen for messages from content script
browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "CHECK_FACT") {
    // Handle fact-checking request
    checkFactAPI(message.tweetText)
      .then((result) => sendResponse({ success: true, data: result }))
      .catch((error) =>
        sendResponse({
          success: false,
          error: error.message || "Unknown error",
        })
      );

    // Return true to indicate we'll send response asynchronously
    return true;
  }

  if (message.type === "HEALTH_CHECK") {
    // Handle health check request
    healthCheckAPI()
      .then((result) => sendResponse({ success: true, data: result }))
      .catch((error) =>
        sendResponse({
          success: false,
          error: error.message || "Unknown error",
        })
      );

    return true;
  }
});

/**
 * Call the fact-checking API
 */
async function checkFactAPI(tweetText) {
  try {
    console.log("Background: Calling API:", `${API_BASE}/check`);
    console.log("Background: Tweet text:", tweetText.substring(0, 100));

    const response = await fetch(`${API_BASE}/check`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        tweet_text: tweetText,
      }),
    });

    console.log("Background: Response status:", response.status);
    console.log("Background: Response ok:", response.ok);

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const result = await response.json();
    console.log("Background: Result received:", result);

    return result;
  } catch (error) {
    console.error("Background: API error:", error);
    throw error;
  }
}

/**
 * Check backend health
 */
async function healthCheckAPI() {
  try {
    const response = await fetch(`${API_BASE}/health`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Background: Health check error:", error);
    throw error;
  }
}

console.log("Fact Checker background script loaded");
