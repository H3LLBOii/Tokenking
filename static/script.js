document.addEventListener("DOMContentLoaded", () => {
  const startBtn = document.getElementById("startBtn");
  const statusDiv = document.getElementById("status");
  const tokenDiv = document.getElementById("token");

  let pollingInterval;

  function pollTokenStatus() {
    fetch("/token_status")
      .then((res) => res.json())
      .then((data) => {
        statusDiv.innerText = "Status: " + data.status;
        tokenDiv.innerText = "Token: " + (data.access_token || "None");

        if (data.access_token || data.status.startsWith("Error") || data.status.includes("Timeout")) {
          clearInterval(pollingInterval);
        }
      })
      .catch(() => {
        statusDiv.innerText = "Status: Error fetching token status";
        clearInterval(pollingInterval);
      });
  }

  startBtn.addEventListener("click", () => {
    fetch("/start_oauth")
      .then(() => {
        statusDiv.innerText = "Status: OAuth process started, please login in Selenium browser";
        tokenDiv.innerText = "Token: None";

        pollingInterval = setInterval(pollTokenStatus, 2000);
      })
      .catch(() => {
        statusDiv.innerText = "Status: Failed to start OAuth";
      });
  });
});
