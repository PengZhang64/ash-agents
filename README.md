# Burner Agents

A swarm of disposable agents for unattributable web interaction. Each task runs under a fresh identity that is destroyed on completion, so you are represented online not by one persistent self but by a continuous supply of unrelated strangers, none of which leads back.

<img width="1915" height="821" alt="image" src="https://github.com/user-attachments/assets/37a62696-d1d5-4d86-bc1f-1237dcc90c68" />

## Why Burner

The modern web identifies you by default. Every site you touch fingerprints you, cookies you, and joins today's visit to everything you did before, until a detailed profile has assembled itself around a single durable identity you never see and cannot control. This is not the result of any wrongdoing. It is the cost of using the web as one consistent, observable self.

Existing tools treat the symptom, not the cause. A VPN hides where you connect from but not who you are once you arrive. Private browsing clears local state but does nothing about fingerprinting or behavioral correlation. Anti-tracking extensions cut some third-party collection and leave first-party identification fully intact. Each narrows the surface. None removes the thing that actually leaks, which is that you show up as the same person every time.

Burner removes the persistent identity instead of hiding it better. You never act on the web directly. You delegate, and what the web observes is never you.

## How it works

You express intent in plain language. The system delegates the work to one or more agents, each running in its own isolated browser context with its own fingerprint, device characteristics, and network egress. No two agents share a signature. Each does its task and is destroyed on completion, leaving no state behind for anyone to correlate. To any site, there is no single user to track, only a series of unrelated participants, each seen once and never again.

```
burner/
├── isolation/        # a fresh, separable browser context per agent
├── reasoning/        # turns intent into actions, reasoning over each page live
├── orchestration/    # decomposes a task, fans it across agents, reconciles results
└── identity/         # instantiate on task start, destroy on completion
```

- **Isolation** gives every agent a distinct browser environment. Separation is the structure of the environment, not a setting applied on top of it.
- **Reasoning** lets an agent perceive each page as it loads and decide the next action in context, so it adapts to the dynamic, inconsistent, often hostile pages of the real web rather than following a brittle script.
- **Orchestration** binds the agents to your single intent entirely within your trust boundary. It is never exposed to any site. The coordination is private; only the multiplicity is observable.
- **Identity** is scoped to the task, not to you and not to a durable session. Completion and erasure are a single event. No archive, no fallback copy, nothing kept against the possibility it might later be wanted.

<img width="1672" height="941" alt="unknown" src="https://github.com/user-attachments/assets/054422a5-e4dd-4a51-9e66-64feeb2f556b" />

## Design principles

Three ideas govern the system.

**Delegation over exposure.** The user's own identity, environment, and fingerprint never make contact with a service. The interface between you and the web is the agent, and the agent is disposable.

**Disposability over concealment.** The system does not try to hide a persistent identity more effectively. It declines to maintain one at all. There is no long-lived profile to conceal because none is ever permitted to form.

**Multiplicity over singularity.** You are represented not by one well-hidden identity but by many unrelated ones. To the web, there is no single entity to find. There is a crowd with no discernible center.

## What it provides

- **Non-attribution.** Because you never touch a service directly and every interaction runs under a disposable identity sharing nothing with your environment, no interaction can be bound to you.
- **Non-linkability.** Because each task runs under an identity that shares no fingerprint, state, or behavioral baseline with any other, an observer cannot determine that two interactions came from the same source, even aggregating across services and over time.
- **No persistent profile.** Because identities are destroyed and no state is retained, there is no durable record for a profile to attach to. The adversary's main instrument, accumulation of behavior over a stable identity, is denied its precondition.
- **No exposed center.** Because coordination lives only within your trust boundary, an observer of the swarm sees unrelated participants and no coordinating entity. There is no single identity whose discovery compromises the others.

<img width="1672" height="941" alt="unknown" src="https://github.com/user-attachments/assets/11fabb34-cfac-4596-af4b-c97b0345b2d7" />

## License

MIT. See [LICENSE](legal/LICENSE).

## Notice

This project is for privacy-preserving interaction with web services. It is a technical system, not an offer or inducement of any kind. You are responsible for ensuring any use complies with the terms of the services you interact with and with the law in your jurisdiction.
