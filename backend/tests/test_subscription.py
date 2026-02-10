from app.services.subscription import PLAN_POLICIES, get_plan_policy


def test_known_plan_policy():
    assert PLAN_POLICIES["free"].upload_limit == 10
    assert PLAN_POLICIES["enterprise"].upload_limit is None


def test_unknown_plan_defaults_to_free():
    assert get_plan_policy("unknown-tier").upload_limit == 10
