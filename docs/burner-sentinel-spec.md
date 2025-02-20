# Burner Sentinel — Build Specification

A restock monitor that watches as a disposable stranger and assists checkout on the drop.
Hand this to Cursor as the project brief.

---

## What we are building

A product that watches a item's product page for a restock, checking repeatedly under a
fresh disposable identity each time (so the site never sees a single persistent watcher),
fires an instant alert when it comes back in stock, and optionally assists the user's
checkout under a clean identity. The disposability is the differentiator: ordinary
monitors check from one IP/fingerprint and get rate-limited or blocked; ours does not.

This is the "sentinel" wedge of the Burner idea: the watcher that was never there.

$BURNER meters the work: number of watches and buy-assist actions.

---

## TWO HARD GATES — resolve before shipping anything commercial

These are not code. They can sink the product. Do not skip.

1. **Commercial license.** changedetection.io is Apache-2.0 PLUS a separate
   COMMERCIAL_LICENCE.md. The README states: reselling the software in part or full as a
   commercial arrangement requires the commercial licence. We intend a paid product on top.
   Email dgtlmoon@gmail.com and contact@changedetection.io and get written clarity on
   whether our use (self-hosted engine behind our own product, driven via its REST API)
   needs the commercial licence and on what terms. Until resolved, this is a prototype only,
   not a launched paid product.

2. **Buy-automation legal line.** Automated purchasing of limited drops violates most
   retail terms and is legally contested in some regions. The defensible product is
   MONITOR + ALERT + ASSIST THE USER'S OWN CHECKOUT. Not mass-buying to resell. The demo
   and the product stay on the alert-and-assist side. Do not build autonomous mass-cop.

---

## The stack (verified)

- **changedetection.io** (self-hosted) — the monitoring engine, dashboard, restock/price
  detection, and notifications. Apache-2.0 core (see gate 1). ~30k stars, mature, actively
  maintained. We drive it through its REST API; we do NOT fork or modify its internals.
- **CloakBrowser** — stealth Chromium, drop-in Playwright replacement, per-launch
  fingerprint seed, BYO proxy. Slots in behind changedetection's Playwright fetcher so each
  check runs as a disposable identity.
- **Burner orchestrator** (from the existing skeleton) — the thin layer we own: rotates a
  fresh identity per check, and on a restock alert, dispatches the buy-assist agent.
- **browser-use** (optional, for the buy-assist agent) — drives the add-to-cart/checkout
  step under a fresh identity when a drop fires.
- **$BURNER meter** (from skeleton) — meters watches and buy-assists. Stub now, chain later.

---

## Architecture

```
                 BURNER SENTINEL (our product + API)
                          |
        +-----------------+------------------+
        |                                    |
  changedetection.io                   Burner orchestrator (ours)
  (self-hosted engine)                 - rotates identity per check
  - watches product page               - on alert -> buy-assist
  - restock/price detection            - meters via $BURNER
  - dashboard + notifications                  |
  - REST API  <------ we drive it -------------+
        |                                    |
  Playwright fetcher                   buy-assist agent (browser-use)
        |                                    |
  CloakBrowser  <-- disposable identity per check / per buy
        |
   THE WEB (sees unrelated strangers, never one watcher)
```

---

## Build order (gets to a working demo fastest)

### Step 1 — Stand up the engine, prove an alert fires
Run changedetection.io self-hosted (Docker is simplest). Add a watch on a TEST product
page you control (a simple local HTML page with an "out of stock" / "in stock" toggle).
Enable restock detection. Configure a notification (Discord or Telegram webhook). Flip the
test page to in-stock and confirm the alert fires. THIS IS THE DEMO BACKBONE. Get it
working before anything else.

### Step 2 — Disposable identity per check (the Burner layer)
Put CloakBrowser behind changedetection's Playwright fetcher so each check uses a fresh
fingerprint, and use changedetection's per-watch proxy config so each check egresses from a
different IP. Prove via logs that two consecutive checks present different fingerprints/IPs.
This is what makes it Burner and not just another monitor.

### Step 3 — Buy-assist on the drop
When the restock alert fires, the orchestrator dispatches a buy-assist agent (browser-use
on a fresh CloakBrowser identity) that opens the product page and adds to cart / proceeds to
the user's checkout. ASSIST, not autonomous mass-buy (see gate 2). The agent reports back
and its identity is destroyed.

### Step 4 — Meter + thin product UI
Wire the $BURNER meter to count watches and buy-assists (stub balance for now). Put a thin
dashboard or use changedetection's own UI for the prototype.

### Step 5 — Demo polish
Make the test page reliable, the identity rotation visible in the UI, and the alert + buy
beat fast and repeatable. Rehearse the flip-to-instock -> alert -> buy-assist sequence.

---

## What to tell Cursor explicitly

- Drive changedetection.io through its REST API. Do NOT fork or modify its internals; run it
  as a self-hosted service. (Licensing: see gate 1.)
- The differentiated code we own is the identity-rotation layer and the buy-assist dispatch.
  Keep changedetection as infrastructure, keep our value in our code.
- Each check and each buy-assist runs under a fresh CloakBrowser identity, destroyed after.
- Build to ASSIST the user's checkout, never autonomous mass-purchase (gate 2).
- Pin all dependencies; audit the tree (supply-chain caution).
- Start at Step 1 and get a real alert firing before building anything else.

---

## Demo script (what it looks like live)

1. Dashboard shows a product, marked out of stock, being watched. Say: "checked every few
   seconds, each time by a different disposable identity. the site never sees one watcher."
2. Flip the test page to in-stock.
3. Within seconds, the alert lands on screen (Discord/Telegram).
4. The buy-assist agent opens the page under a brand-new identity, adds to cart, reports back.
5. Close: "it watched as a stranger, caught the drop instantly, moved on it as someone the
   site had never seen, and vanished."

Demo uses a TEST page you control so the drop happens on cue. This proves the mechanism. It
does NOT prove you beat a specific real retailer's bot defenses — that's a separate claim
that needs real-world testing against that site. Don't conflate the two when presenting.

---

## Honest assessment

- Technically low-risk: changedetection.io is proven; we integrate via documented REST API.
  The only real engineering is the disposability layer, which attaches at existing seams
  (Playwright fetcher, per-watch proxy).
- Demo: strong. Real payoff, controllable, visual, on-thesis.
- Payable: yes, with a real wedge (disposability + buy-assist) over the base tool's $8.99
  hosted monitor — but ONLY if disposability genuinely delivers something the base can't,
  which depends on CloakBrowser performing against real anti-bot defenses (unverified).
- Two gates (license, buy-automation) are the real risks. Both clearable, neither is code.
```
