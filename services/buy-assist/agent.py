from __future__ import annotations

from typing import Any

from identity.rotation import IdentityFactory


def run_buy_assist(product_url: str, *, max_quantity: int = 1) -> dict[str, Any]:
    if max_quantity > 1:
        raise ValueError("Assist-only: max_quantity must be 1")

    identity = IdentityFactory().next_identity()
    # Prototype: simulate add-to-cart + checkout handoff under fresh identity.
    # Production: browser-use + CloakBrowser on identity, stop at user checkout.
    return {
        "status": "assist_complete",
        "product_url": product_url,
        "quantity": max_quantity,
        "identity_seed": identity.fingerprint_seed,
        "proxy_url": identity.proxy_url,
        "checkout_handoff": True,
        "message": "Added to cart under disposable identity; user completes payment.",
    }
