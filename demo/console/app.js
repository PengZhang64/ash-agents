(function () {
  const intentEl = document.getElementById("intent");
  const agentCountEl = document.getElementById("agent-count");
  const launchBtn = document.getElementById("launch");
  const logEl = document.getElementById("log");
  const swarmListEl = document.getElementById("swarm-list");

  let eventSource = null;
  let running = false;

  function appendLog(line, className) {
    const span = document.createElement("span");
    span.className = className || "";
    span.textContent = line + "\n";
    logEl.appendChild(span);
    logEl.scrollTop = logEl.scrollHeight;
  }

  function clearLog() {
    logEl.textContent = "";
  }

  function renderSwarm(agents) {
    if (!agents || agents.length === 0) {
      swarmListEl.innerHTML =
        '<li class="agent-row idle"><span class="agent-id">—</span><span class="agent-state">idle</span></li>';
      return;
    }
    swarmListEl.innerHTML = agents
      .map(function (a) {
        const cls = "agent-row " + (a.state || "idle");
        return (
          '<li class="' +
          cls +
          '"><span class="agent-id">' +
          a.id +
          '</span><span class="agent-state">' +
          (a.state || "idle") +
          "</span></li>"
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

  function connectStream(taskId) {
    closeStream();
    const url = "/api/events/stream?task_id=" + encodeURIComponent(taskId);
    eventSource = new EventSource(url);

    eventSource.onmessage = function (ev) {
      try {
        const data = JSON.parse(ev.data);
        if (data.type === "log") {
          const cls = data.level === "proof" ? "line-proof" : data.level === "dim" ? "line-dim" : "";
          appendLog(data.message, cls);
        }
        if (data.type === "swarm" && data.agents) {
          renderSwarm(data.agents);
        }
        if (data.type === "done") {
          running = false;
          launchBtn.disabled = false;
          closeStream();
        }
      } catch (e) {
        console.error(e);
      }
    };

    eventSource.onerror = function () {
      if (running) {
        appendLog("[stream disconnected]", "line-dim");
      }
      running = false;
      launchBtn.disabled = false;
      closeStream();
    };
  }

  async function launch(body) {
    if (running) return;
    running = true;
    launchBtn.disabled = true;
    clearLog();
    renderSwarm([]);

    try {
      const res = await fetch("/api/delegate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const err = await res.json().catch(function () {
          return { detail: res.statusText };
        });
        appendLog("error: " + (err.detail || res.statusText));
        running = false;
        launchBtn.disabled = false;
        return;
      }
      const data = await res.json();
      if (data.agents) {
        renderSwarm(data.agents);
      }
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
      appendLog("enter a task or use a preset", "line-dim");
      return;
    }
    launch({
      intent: intent,
      agents: parseInt(agentCountEl.value, 10) || 3,
    });
  });

  document.querySelectorAll(".btn-preset").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const preset = btn.getAttribute("data-preset");
      launch({
        preset: preset,
        agents: parseInt(agentCountEl.value, 10) || 3,
      });
    });
  });

  fetch("/api/swarm")
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      if (data.agents && data.agents.length) {
        renderSwarm(data.agents);
      }
    })
    .catch(function () {});
})();
