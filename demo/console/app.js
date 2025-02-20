(function () {
  const intentEl = document.getElementById("intent");
  const agentCountEl = document.getElementById("agent-count");
  const launchBtn = document.getElementById("launch");
  const logEl = document.getElementById("log");
  const orchFeed = document.getElementById("orch-feed");
  const webFeed = document.getElementById("web-feed");
  const swarmListEl = document.getElementById("swarm-list");
  const reconcileText = document.getElementById("reconcile-text");
  const resultBox = document.getElementById("result-box");

  let eventSource = null;
  let running = false;

  function appendLog(line, className) {
    const span = document.createElement("span");
    if (className) span.className = className;
    span.textContent = line + "\n";
    logEl.appendChild(span);
    logEl.scrollTop = logEl.scrollHeight;
  }

  function appendFeed(el, line) {
    el.textContent += line + "\n";
    el.scrollTop = el.scrollHeight;
  }

  function clearAll() {
    logEl.textContent = "";
    orchFeed.textContent = "";
    webFeed.textContent = "";
    resultBox.classList.add("hidden");
    reconcileText.textContent = "";
  }

  function renderSwarm(agents) {
    if (!agents || !agents.length) {
      swarmListEl.innerHTML = '<li class="agent-row idle"><span>—</span></li>';
      return;
    }
    swarmListEl.innerHTML = agents
      .map(function (a) {
        const fp = a.fingerprint ? '<span class="agent-fp">' + a.fingerprint + "</span>" : "";
        return (
          '<li class="agent-row ' +
          (a.state || "idle") +
          '"><span>' +
          a.id +
          '</span><span>' +
          (a.state || "idle") +
          "</span>" +
          fp +
          "</li>"
        );
      })
      .join("");
  }

  function closeStream() {
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
  }

  function handleEvent(data) {
    if (data.type === "log") {
      const cls = data.level === "proof" ? "line-proof" : "";
      appendLog(data.message, cls);
      return;
    }
    if (data.type === "swarm" && data.agents) {
      renderSwarm(data.agents);
      return;
    }
    if (data.type === "layer" && data.layer === "orchestration") {
      appendFeed(orchFeed, data.message);
      return;
    }
    if (data.type === "reasoning") {
      appendFeed(
        orchFeed,
        "[" + (data.agent || "?") + "] " + (data.thought || "") + " → " + (data.action || "")
      );
      return;
    }
    if (data.type === "web_observed") {
      appendFeed(
        webFeed,
        "stranger " + data.fingerprint + " @ " + (data.url || "").replace(/^https?:\/\/[^/]+/, "")
      );
      return;
    }
    if (data.type === "lifecycle") {
      appendLog(data.agent + " " + data.phase + (data.proof ? " " + data.proof.slice(0, 14) + "…" : ""), "");
      return;
    }
    if (data.type === "reconcile") {
      reconcileText.textContent = data.summary || "";
      resultBox.classList.remove("hidden");
      appendFeed(orchFeed, "RECONCILED: " + (data.summary || ""));
      return;
    }
    if (data.type === "done") {
      running = false;
      launchBtn.disabled = false;
      closeStream();
    }
  }

  function connectStream(taskId) {
    closeStream();
    eventSource = new EventSource("/api/events/stream?task_id=" + encodeURIComponent(taskId));
    eventSource.onmessage = function (ev) {
      try {
        handleEvent(JSON.parse(ev.data));
      } catch (e) {
        console.error(e);
      }
    };
    eventSource.onerror = function () {
      if (running) appendLog("[stream disconnected]");
      running = false;
      launchBtn.disabled = false;
      closeStream();
    };
  }

  async function launch(body) {
    if (running) return;
    running = true;
    launchBtn.disabled = true;
    clearAll();

    try {
      const res = await fetch("/api/delegate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json().catch(function () {
        return { detail: res.statusText };
      });
      if (!res.ok) {
        appendLog("error: " + (data.detail || res.statusText));
        running = false;
        launchBtn.disabled = false;
        return;
      }
      if (data.agents) renderSwarm(data.agents);
      connectStream(data.task_id);
    } catch (e) {
      appendLog("error: " + e.message);
      running = false;
      launchBtn.disabled = false;
    }
  }

  launchBtn.addEventListener("click", function () {
    const intent = intentEl.value.trim();
    if (!intent) {
      appendLog("enter intent or use preset");
      return;
    }
    launch({ intent: intent, agents: parseInt(agentCountEl.value, 10) || 3 });
  });

  document.querySelectorAll(".btn-preset").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const preset = btn.getAttribute("data-preset");
      intentEl.value = "Check the demo storefront and report stock status.";
      launch({ preset: preset, agents: parseInt(agentCountEl.value, 10) || 3 });
    });
  });
})();
