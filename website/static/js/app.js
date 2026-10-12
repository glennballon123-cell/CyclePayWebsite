(function () {
  if (window.__laundryApp) return;
  window.__laundryApp = true;

  function host() {
    let node = document.getElementById("bubbleHost");
    if (node) return node;
    node = document.createElement("div");
    node.id = "bubbleHost";
    node.style.cssText = "position:fixed;top:1.25rem;right:1.25rem;z-index:9999;display:flex;flex-direction:column;gap:0.6rem;pointer-events:none;";
    document.body.appendChild(node);
    return node;
  }

  function bubble(title, message, tone) {
    const colors = {
      success: { border: "#4edea3", color: "#4edea3" },
      error: { border: "#ffb4ab", color: "#ffb4ab" },
      info: { border: "#4cd7f6", color: "#4cd7f6" },
      warning: { border: "#f5a524", color: "#f5a524" }
    };
    const picked = colors[tone] || colors.info;
    const card = document.createElement("div");
    card.style.cssText = "pointer-events:auto;min-width:16rem;max-width:24rem;background:#242a3a;border:1px solid " + picked.border + ";border-radius:0.75rem;padding:0.9rem 1rem;box-shadow:0 8px 24px rgba(0,0,0,0.45);font-family:Inter,system-ui,sans-serif;color:#dde2f8;opacity:0;transform:translateY(-8px);transition:opacity 0.2s ease,transform 0.2s ease;";
    const heading = document.createElement("div");
    heading.style.cssText = "font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:" + picked.color + ";margin-bottom:0.25rem;";
    heading.textContent = title;
    const body = document.createElement("div");
    body.style.cssText = "font-size:13px;line-height:1.5;color:#bcc9cd;";
    body.textContent = message || "";
    card.appendChild(heading);
    card.appendChild(body);
    host().appendChild(card);
    requestAnimationFrame(function () {
      card.style.opacity = "1";
      card.style.transform = "translateY(0)";
    });
    setTimeout(function () {
      card.style.opacity = "0";
      card.style.transform = "translateY(-8px)";
      setTimeout(function () { card.remove(); }, 250);
    }, 3200);
  }

  window.bubble = bubble;

  function toastFor(action) {
    if (action.indexOf("/seal") !== -1) return ["Door", "Lock state changed.", "info"];
    if (action.indexOf("/pulse") !== -1) return ["Pulse", "Coil pulse dispatched.", "success"];
    if (action.indexOf("/tare") !== -1) return ["Tare", "Scale zeroed.", "info"];
    if (action.indexOf("/state") !== -1) return ["State", "Station state updated.", "info"];
    if (action.indexOf("/delete") !== -1) return ["Deleted", "Record removed.", "warning"];
    if (action.indexOf("/issue") !== -1) return ["Voucher", "Signed voucher issued.", "success"];
    if (action.indexOf("/credit") !== -1) return ["Credit", "Balance updated.", "success"];
    if (action.indexOf("/balance") !== -1) return ["Balance", "Balance set.", "success"];
    if (action.indexOf("/progress/complete") !== -1) return ["Complete", "Cycle marked finished.", "success"];
    if (action.indexOf("/progress/release") !== -1) return ["Released", "Door unlocked.", "success"];
    if (action.indexOf("/progress/help") !== -1) return ["Help", "Attendant notified.", "info"];
    if (action.indexOf("/add") !== -1) return ["Station", "Station created.", "success"];
    return ["Done", "Action completed.", "success"];
  }

  document.addEventListener("submit", function (event) {
    const form = event.target;
    if (!form || form.tagName !== "FORM") return;
    const action = form.getAttribute("action") || "";
    if (!action || action.indexOf("/logout") !== -1) return;
    if (action === "/access" || action === "/register") return;
    if (action.indexOf("/kiosk/pay") !== -1) return;

    event.preventDefault();
    const data = new FormData(form);
    const result = toastFor(action);

    fetch(action, { method: "POST", body: data, redirect: "follow" })
      .then(function (response) {
        return response.text().then(function () { return response.ok; });
      })
      .then(function (ok) {
        if (ok) {
          bubble(result[0], result[1], result[2]);
          setTimeout(function () { window.location.reload(); }, 600);
        } else {
          bubble("Error", "The action failed.", "error");
        }
      })
      .catch(function () {
        bubble("Network", "Could not reach the server.", "error");
      });
  });

  function renderQR() {
    const holder = document.getElementById("qrHolder");
    const code = holder ? holder.dataset.code : "";
    if (!holder || !code || typeof QRCode === "undefined") return;
    holder.innerHTML = "";
    new QRCode(holder, {
      text: code,
      width: 180,
      height: 180,
      colorDark: "#000000",
      colorLight: "#ffffff",
      correctLevel: QRCode.CorrectLevel.M
    });
    holder.removeAttribute("title");
    const el = holder.querySelector("img,canvas,svg");
    if (el) el.removeAttribute("title");
  }

  function startTimer() {
    const node = document.getElementById("liveTimer");
    if (!node) return;
    let seconds = parseInt(node.dataset.seconds || "0", 10);
    if (!seconds || seconds <= 0) {
      node.textContent = "Ready";
      return;
    }
    node.textContent = pad(seconds);
    setInterval(function () {
      if (seconds <= 0) { node.textContent = "Done"; return; }
      seconds -= 1;
      node.textContent = pad(seconds);
    }, 1000);
  }

  function pad(total) {
    const m = Math.floor(total / 60);
    const s = total % 60;
    return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
  }

  function onReady() {
    renderQR();
    startTimer();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", onReady);
  } else {
    onReady();
  }
})();