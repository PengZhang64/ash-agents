# Cursor Prompt — Burner Sentinel

Paste this into Cursor. Keep `Burner_Sentinel_Spec.md` in the project as the reference;
this prompt tells you how to execute it.

---

You are building a restock-monitoring product called Burner Sentinel. Read
`Burner_Sentinel_Spec.md` first — it is the design doc. This prompt is how we execute it.

## Read these before writing code
- `Burner_Sentinel_Spec.md` — architecture, stack, and the two hard gates.
- changedetection.io docs and its REST API spec (we integrate via the API, we do not fork it).

## Two hard rules that override everything
1. We run changedetection.io as a self-hosted service and drive it through its REST API.
   Do NOT fork, vendor, or modify its source into this repo. (There is a commercial-license
   question being resolved separately; keep our code cleanly separated from theirs.)
2. We build to ASSIST a user's own checkout, never autonomous mass-purchase. Do not write
   anything that buys at scale to resell.

## Build in this exact order. Stop and verify after each step before moving on.

### Step 1 — Demo backbone: a real alert fires
- Stand up changedetection.io via Docker (docker compose).
- Create a local TEST product page (simple static HTML) with a toggle between "out of stock"
  and "in stock".
- Add a watch on that test page in changedetection, enable restock detection, and configure
  a Discord OR Telegram webhook notification.
- Flip the test page to in-stock and CONFIRM the alert fires.
- Do not proceed until a real notification lands. This is the demo backbone.

### Step 2 — Disposable identity per check
- Put CloakBrowser behind changedetection's Playwright fetcher so each check uses a fresh
  fingerprint. First do a standalone spike: launch CloakBrowser, load a bot-detection test
  page, confirm a non-default fingerprint, and confirm it works as changedetection's fetcher.
- Use changedetection's per-watch proxy configuration so each check egresses from a
  different IP.
- PROVE via logs that two consecutive checks present different fingerprints and IPs.

### Step 3 — Buy-assist on the drop
- Build a small service (our code) that listens for the restock notification (via webhook
  from changedetection) and dispatches a buy-assist agent.
- The agent runs on a fresh CloakBrowser identity (browser-use optional for the reasoning),
  opens the product page, adds to cart / proceeds to the user's checkout, reports back, and
  its identity is destroyed.
- ASSIST only. Stop at the user's checkout handoff.

### Step 4 — Meter + thin UI
- Add a $BURNER meter (stub balance) that counts watches and buy-assists.
- Use changedetection's own dashboard for the prototype, or a thin wrapper UI. Don't build a
  full custom dashboard yet.

### Step 5 — Demo polish
- Make the test page toggle reliable, surface the rotating identities/IPs in the UI so
  disposability is visible, and make the flip -> alert -> buy-assist sequence fast and
  repeatable. Rehearse it.

## General rules
- Pin all dependencies to exact versions; audit the dependency tree.
- Keep our differentiated code (identity rotation, buy-assist dispatch, meter) clearly
  separated from the changedetection.io service we run.
- Report back after Step 1 with the working alert before building Step 2.

Start with Step 1. Get a real restock alert firing on the test page first.
```
