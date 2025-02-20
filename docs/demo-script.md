# Burner Agents — 90 second demo script

## The story (whitepaper)

1. **Problem:** Every site builds a profile of *you*.
2. **Burner Agents:** You **delegate**. The web sees a **swarm of strangers**, each born for one task, destroyed when done.
3. **You** never touch the site directly.

## Before you go on stage

```bash
make demo
# Opens http://127.0.0.1:8090/
```

Optional: open the demo product in a second window (`http://127.0.0.1:8088/`) if you want to flip stock for the restock sentinel beat later.

## Live flow

| Time | Say | Do |
|------|-----|-----|
| 0:00 | "This is Burner Agents. You delegate, the web sees strangers." | Show black console. |
| 0:15 | "I describe what I want. The swarm handles the web." | Type or use preset **Check demo product**. |
| 0:25 | "Three agents. Each a different stranger." | Set agents to **3**, click **LAUNCH SWARM**. |
| 0:35 | | Point at **SWARM** panel. Agents move to `running`. |
| 0:45 | | Point at **RUN.LOG**. Birth, fetch, stock result per agent. |
| 0:60 | "When the task ends, the identity is destroyed. Here is the proof." | Highlight `proof 0x…` lines. |
| 1:15 | "The site never saw me. It saw strangers." | Pause. |
| 1:30 | "Restock sentinel is one app on this platform." | Optional: **Watch drop** preset or Docker stack. |

## One-liners if asked

- **vs VPN:** VPN is one tunnel. Burner is **multiplicity**: many unrelated identities.
- **vs headless browser:** We **orchestrate** disposability and coordination, not just automation.
- **Whitepaper:** [docs/burner_whitepaper.pdf](burner_whitepaper.pdf)

## Troubleshooting

- Blank log after launch: ensure demo product is up (`curl http://127.0.0.1:8088/health`).
- `make smoke` must pass before presenting.
