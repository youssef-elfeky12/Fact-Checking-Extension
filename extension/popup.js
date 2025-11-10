// Extension state management
let extensionEnabled = true;

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
        '<span class="indicator indicator-active"></span> Connected';
    } else {
      statusElement.innerHTML =
        '<span class="indicator indicator-inactive"></span> Error';
    }
  } catch (error) {
    statusElement.innerHTML =
      '<span class="indicator indicator-inactive"></span> Offline';
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

// Load extension state from storage
async function loadExtensionState() {
  try {
    const result = await browser.storage.local.get("extensionEnabled");
    console.log("Loaded from storage:", result);

    // If extensionEnabled exists in storage, use it; otherwise default to true
    extensionEnabled =
      result.extensionEnabled !== undefined ? result.extensionEnabled : true;

    console.log("Extension enabled:", extensionEnabled);
    updateToggleSwitch();
    updateExtensionStatus();
  } catch (error) {
    console.error("Error loading extension state:", error);
  }
}

// Update toggle switch appearance
function updateToggleSwitch() {
  const toggleSwitch = document.querySelector(
    "#toggle-extension .toggle-switch"
  );

  if (extensionEnabled) {
    toggleSwitch.classList.add("active");
  } else {
    toggleSwitch.classList.remove("active");
  }
}

// Update extension status display
function updateExtensionStatus() {
  const statusElement = document.getElementById("extension-status");

  if (extensionEnabled) {
    statusElement.innerHTML = `
      <span class="indicator indicator-active"></span>
      Enabled
    `;
  } else {
    statusElement.innerHTML = `
      <span class="indicator indicator-inactive"></span>
      Disabled
    `;
  }
}

// Toggle extension on/off
async function toggleExtension() {
  console.log("Toggle clicked! Current state:", extensionEnabled);

  extensionEnabled = !extensionEnabled;
  console.log("New state:", extensionEnabled);

  // Save to storage
  try {
    await browser.storage.local.set({ extensionEnabled });
    console.log("Saved to storage:", extensionEnabled);

    // Verify it was saved
    const verify = await browser.storage.local.get("extensionEnabled");
    console.log("Verified storage after save:", verify);
  } catch (error) {
    console.error("Error saving to storage:", error);
  }

  updateToggleSwitch();
  updateExtensionStatus();

  // Notify content scripts of the state change
  try {
    const [tab] = await browser.tabs.query({
      active: true,
      currentWindow: true,
    });

    if (tab && (tab.url.includes("twitter.com") || tab.url.includes("x.com"))) {
      await browser.tabs.sendMessage(tab.id, {
        type: "EXTENSION_STATE_CHANGED",
        enabled: extensionEnabled,
      });
      console.log("Notified content script");
    }
  } catch (error) {
    console.error("Error notifying content script:", error);
  }
}

// Initialize when popup opens
document.addEventListener("DOMContentLoaded", () => {
  console.log("Popup initialized");

  loadExtensionState();
  checkBackendStatus();
  checkPageStatus();

  // Set up toggle switch click handler
  const toggleElement = document.getElementById("toggle-extension");
  console.log("Toggle element found:", toggleElement);

  if (toggleElement) {
    toggleElement.addEventListener("click", toggleExtension);
    console.log("Click listener attached");
  } else {
    console.error("Toggle element not found!");
  }

  // Refresh backend status every 3 seconds
  setInterval(checkBackendStatus, 3000);
});
