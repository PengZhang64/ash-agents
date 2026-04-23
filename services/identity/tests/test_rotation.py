from identity.rotation import IdentityFactory


def test_fingerprint_unique() -> None:
    f = IdentityFactory(proxy_pool="http://a:1,http://b:2")
    a = f.next_identity()
    b = f.next_identity()
    assert a.fingerprint_seed != b.fingerprint_seed
    assert a.proxy_url != b.proxy_url
