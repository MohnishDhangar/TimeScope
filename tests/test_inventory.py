from scripts.prepare_from_inventory import contains

def test_convex_spherical_region_handles_wrap_and_reversed_order():
    region='POLYGON ICRS 359 -1 1 -1 1 1 359 1 359 -1'
    assert contains(region,0,0)
    assert not contains(region,180,0)
    assert not contains(region,4,0)
    assert contains('POLYGON ICRS 359 1 1 1 1 -1 359 -1',0,0)

def test_declination_and_unsupported_regions():
    assert contains('POLYGON ICRS 10 80 12 80 12 82 10 82',11,81)
    assert not contains('POLYGON ICRS 10 80 12 80 12 82 10 82',11,70)
    assert not contains('CIRCLE ICRS 10 20 1',10,20)
