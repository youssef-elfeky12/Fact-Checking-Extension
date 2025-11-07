// Check backend API status via background script
async function checkBackendStatus() {
  const statusElement = document.getElementById("backend-status");

  try {
    // Use background script to avoid CSP issues
    const response = await browser.runtime.sendMessage({
      type: "HEALTH_CHECK",
    });

    if (response.success) {
      statusElement.innerHTML =
        'Connected <span class="indicator indicator-active"></span>';
    } else {
      statusElement.innerHTML =
        'Error <span class="indicator indicator-inactive"></span>';
    }
  } catch (error) {
    statusElement.innerHTML =
      'Offline <span class="indicator indicator-inactive"></span>';
  }
}

// Check if we're on a supported page
async function checkPageStatus() {
  const pageStatusElement = document.getElementById("page-status");

  try {
    const [tab] = await browser.tabs.query({
      active: true,
      currentWindow: true,
    });

    if (tab && (tab.url.includes("twitter.com") || tab.url.includes("x.com"))) {
      pageStatusElement.textContent = "Twitter/X ✓";
    } else {
      pageStatusElement.textContent = "Other page";
    }
  } catch (error) {
    pageStatusElement.textContent = "Unknown";
  }
}

// Initialize when popup opens
document.addEventListener("DOMContentLoaded", () => {
  checkBackendStatus();
  checkPageStatus();

  // Refresh backend status every 3 seconds
  setInterval(checkBackendStatus, 3000);
});
