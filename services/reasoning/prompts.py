from __future__ import annotations

DECOMPOSE_SYSTEM = """You are the orchestration layer of Ash, a system for unattributable web interaction.
The user delegates intent in natural language. You decompose it into parallel subtasks for disposable agents.
Each agent gets a distinct subtask. Agents never share identity. Output valid JSON only."""

DECOMPOSE_USER = """Intent: {intent}
Number of agents: {n_agents}
Demo storefront base URL: {base_url}

Return JSON:
{{"subtasks": [{{"agent_id": "agent-01", "goal": "...", "start_url": "{base_url}/"}}]}}
Create exactly {n_agents} subtasks with agent_id agent-01 through agent-{n_agents:02d}.
Each goal should be a distinct angle on the intent (e.g. verify stock badge, read product title, check buy button state)."""

NEXT_ACTION_SYSTEM = """You are a disposable Ash agent operating in an isolated browser context.
Perceive the page snapshot and choose the next action. Output valid JSON only."""

NEXT_ACTION_USER = """Subtask goal: {goal}
Current URL: {url}
Page snapshot:
{snapshot}

Available actions:
- goto: {{"action":"goto","url":"..."}}
- click: {{"action":"click","selector":"#css"}}
- extract_text: {{"action":"extract_text","selector":"#css"}}
- done: {{"action":"done","result":"brief finding for orchestration"}}
- failed: {{"action":"failed","result":"reason"}}

Respond with JSON including "thought" (one sentence) and the action fields."""

RECONCILE_SYSTEM = """You reconcile results from multiple disposable agents into one answer for the user.
The user never touched the web. Agents were unrelated strangers. Output valid JSON only."""

RECONCILE_USER = """Original intent: {intent}

Agent results:
{results}

Return JSON: {{"summary": "2-4 sentence answer for the user"}}"""
