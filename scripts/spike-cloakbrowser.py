#!/usr/bin/env python3
"""Spike: launch disposable identity and report fingerprint config."""
from identity.rotation import IdentityFactory
from identity.launcher import launch_cloakbrowser

if __name__ == "__main__":
    ident = IdentityFactory(proxy_pool="http://proxy-a:8080,http://proxy-b:8080").next_identity()
    cfg = launch_cloakbrowser(ident)
    print("Identity spike:", cfg)
