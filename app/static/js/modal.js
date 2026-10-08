(function () {
  if (window.__spinflowModalInstalled) return;
  window.__spinflowModalInstalled = true;

  const ICONS = {
    success: "✓",
    error: "!",
    warning: "!",
    info: "i",
    question: "?",
    lock: "🔒",
    coin: "₱",
  };

  const COLORS = {
    success: "#4edea3",
    error: "#ffb4ab",
    warning: "#f5a524",
    info: "#4cd7f6",
    question: "#4cd7f6",
    lock: "#adc6ff",
    coin: "#4edea3",
  };

  function ensureHost() {
    let host = document.getElementById("__spinflowModalHost");
    if (host) return host;

    host = document.createElement("div");
    host.id = "__spinflowModalHost";
    host.style.cssText = "position:fixed;inset:0;z-index:9999;pointer-events:none;";
    host.innerHTML = `
      <div id="__spinflowModalBackdrop" style="
        position:absolute;inset:0;
        background:rgba(8,14,29,0.82);
        backdrop-filter:blur(8px);
        -webkit-backdrop-filter:blur(8px);
        display:none;
        align-items:center;justify-content:center;
        padding:1rem;
        pointer-events:auto;
        animation:sfFadeIn 0.18s ease-out;
      ">
        <div id="__spinflowModalCard" style="
          background:linear-gradient(180deg,#242a3a 0%,#191f2f 100%);
          border:1px solid rgba(76,215,246,0.18);
          border-radius:1rem;
          padding:1.75rem;
          max-width:26rem;width:100%;
          box-shadow:0 24px 72px rgba(0,0,0,0.65),0 0 0 1px rgba(76,215,246,0.08);
          animation:sfScaleIn 0.22s cubic-bezier(0.16,1,0.3,1);
          position:relative;
          font-family:Inter,system-ui,sans-serif;
          color:#dde2f8;
        ">
          <div id="__spinflowModalTopGlow" style="
            position:absolute;top:0;left:1.5rem;right:1.5rem;height:1px;
            background:linear-gradient(90deg,transparent,rgba(76,215,246,0.5),transparent);
            border-top-left-radius:1rem;border-top-right-radius:1rem;
          "></div>

          <div style="display:flex;align-items:flex-start;gap:1rem;">
            <div id="__spinflowModalIcon" style="
              width:3rem;height:3rem;border-radius:50%;
              display:flex;align-items:center;justify-content:center;
              font-size:1.5rem;font-weight:700;flex-shrink:0;
            "></div>
            <div style="flex:1;min-width:0;">
              <div id="__spinflowModalTitle" style="
                font-size:20px;font-weight:600;color:#dde2f8;
                letter-spacing:-0.01em;margin-bottom:0.5rem;
              "></div>
              <div id="__spinflowModalMessage" style="
                font-size:14px;line-height:1.6;color:#bcc9cd;
              "></div>
            </div>
          </div>

          <div id="__spinflowModalInputWrap" style="display:none;margin-top:1rem;">
            <input id="__spinflowModalInput" style="
              width:100%;background:#080e1d;border:1px solid rgba(148,163,184,0.2);
              border-radius:0.5rem;padding:0.75rem 1rem;color:#dde2f8;
              font-family:'JetBrains Mono',monospace;font-size:14px;outline:none;
            ">
          </div>

          <div id="__spinflowModalFooter" style="
            display:flex;gap:0.75rem;justify-content:flex-end;
            padding-top:1.25rem;margin-top:1.25rem;
            border-top:1px solid #3d494c;
          ">
            <button id="__spinflowModalCancel" type="button" style="
              min-width:6rem;justify-content:center;
              display:inline-flex;align-items:center;gap:0.5rem;
              padding:0.65rem 1.25rem;border-radius:0.5rem;
              border:1px solid #3d494c;background:#242a3a;color:#dde2f8;
              font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;
              text-transform:uppercase;letter-spacing:0.08em;cursor:pointer;
              transition:background 0.15s ease;
            ">Cancel</button>
            <button id="__spinflowModalConfirm" type="button" style="
              min-width:6rem;justify-content:center;
              display:inline-flex;align-items:center;gap:0.5rem;
              padding:0.65rem 1.25rem;border-radius:0.5rem;
              border:none;background:#06b6d4;color:#003640;
              font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;
              text-transform:uppercase;letter-spacing:0.08em;cursor:pointer;
              transition:background 0.15s ease, box-shadow 0.15s ease;
            ">OK</button>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(host);

    const style = document.createElement("style");
    style.textContent = `
      @keyframes sfFadeIn { from { opacity: 0; } to { opacity: 1; } }
      @keyframes sfScaleIn {
        from { opacity: 0; transform: scale(0.95) translateY(8px); }
        to { opacity: 1; transform: scale(1) translateY(0); }
      }
      #__spinflowModalConfirm:hover { filter: brightness(1.1); }
      #__spinflowModalCancel:hover { background: #2f3445; }
      #__spinflowModalInput:focus {
        border-color: #4cd7f6;
        box-shadow: 0 0 0 1px rgba(76,215,246,0.3);
      }
    `;
    document.head.appendChild(style);

    return host;
  }

  function showBubble(opts) {
    opts = opts || {};
    return new Promise((resolve) => {
      ensureHost();

      const backdrop = document.getElementById("__spinflowModalBackdrop");
      const card = document.getElementById("__spinflowModalCard");
      const iconEl = document.getElementById("__spinflowModalIcon");
      const titleEl = document.getElementById("__spinflowModalTitle");
      const messageEl = document.getElementById("__spinflowModalMessage");
      const inputWrap = document.getElementById("__spinflowModalInputWrap");
      const input = document.getElementById("__spinflowModalInput");
      const footer = document.getElementById("__spinflowModalFooter");
      const cancelBtn = document.getElementById("__spinflowModalCancel");
      const confirmBtn = document.getElementById("__spinflowModalConfirm");

      const type = opts.type || "info";
      const color = COLORS[type] || COLORS.info;
      const icon = opts.icon || ICONS[type] || "i";
      const mode = opts.mode || "alert";

      iconEl.textContent = icon;
      iconEl.style.background = color + "22";
      iconEl.style.border = "1px solid " + color + "55";
      iconEl.style.color = color;

      titleEl.textContent = opts.title || "Notice";
      messageEl.textContent = opts.message || "";

      confirmBtn.style.background = color;
      confirmBtn.style.color = (type === "error") ? "#690005" : "#003640";

      if (mode === "prompt") {
        inputWrap.style.display = "block";
        input.value = opts.defaultValue || "";
        input.placeholder = opts.placeholder || "";
        input.type = opts.inputType || "text";
        footer.style.display = "flex";
        cancelBtn.style.display = "inline-flex";
        confirmBtn.textContent = opts.confirmLabel || "Submit";
        setTimeout(() => input.focus(), 50);
      } else if (mode === "confirm") {
        inputWrap.style.display = "none";
        footer.style.display = "flex";
        cancelBtn.style.display = "inline-flex";
        confirmBtn.textContent = opts.confirmLabel || "Confirm";
      } else {
        inputWrap.style.display = "none";
        footer.style.display = "flex";
        cancelBtn.style.display = "none";
        confirmBtn.textContent = opts.confirmLabel || "OK";
      }

      backdrop.style.display = "flex";
      requestAnimationFrame(() => requestAnimationFrame(() => backdrop.style.opacity = "1"));

      function close(result) {
        backdrop.style.opacity = "0";
        setTimeout(() => {
          backdrop.style.display = "none";
          cleanup();
          resolve(result);
        }, 150);
      }

      function cleanup() {
        confirmBtn.onclick = null;
        cancelBtn.onclick = null;
        input.onkeydown = null;
        backdrop.onclick = null;
        document.removeEventListener("keydown", onKey);
      }

      function onKey(e) {
        if (e.key === "Escape") { e.preventDefault(); close(mode === "alert" ? true : null); }
        if (e.key === "Enter" && mode === "prompt") { e.preventDefault(); close(input.value); }
        if (e.key === "Enter" && mode === "confirm") { e.preventDefault(); close(true); }
      }

      document.addEventListener("keydown", onKey);

      confirmBtn.onclick = () => {
        if (mode === "prompt") close(input.value);
        else close(true);
      };
      cancelBtn.onclick = () => close(null);
      backdrop.onclick = (e) => {
        if (e.target === backdrop) close(mode === "alert" ? true : null);
      };
    });
  }

  window.notify = function (title, message, type) {
    return showBubble({ title, message, type: type || "success", mode: "alert" });
  };

  window.confirmDialog = function (title, message, confirmLabel) {
    return showBubble({
      title,
      message,
      type: "warning",
      mode: "confirm",
      confirmLabel: confirmLabel || "Confirm",
      icon: "!",
    });
  };

  window.promptDialog = function (title, message, defaultValue, inputType) {
    return showBubble({
      title,
      message,
      type: "info",
      mode: "prompt",
      defaultValue: defaultValue || "",
      inputType: inputType || "text",
    });
  };

  window.showBubble = showBubble;
  window.__spinflowIcons = ICONS;
  window.__spinflowColors = COLORS;
})();