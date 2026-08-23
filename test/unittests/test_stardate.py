from skill_easter_eggs.stardate import StarDate


def test_stardate_returns_float():
    result = StarDate().getStardate()
    assert isinstance(result, float)


def test_stardate_current_is_past_tng_origin():
    # Origin is 1987-07-15 (TNG premiere). Any date today is well past it.
    result = StarDate().getStardate()
    assert result > 41000


def test_stardate_deterministic():
    date = "2024-06-15T12:00:00"
    assert StarDate(date=date).getStardate() == StarDate(date=date).getStardate()


def test_stardate_monotonic():
    earlier = StarDate(date="2020-01-01T00:00:00").getStardate()
    later = StarDate(date="2025-01-01T00:00:00").getStardate()
    assert later > earlier


def test_stardate_set_date():
    sd = StarDate()
    sd.setDate("2024-01-01T00:00:00")
    assert sd.date == "2024-01-01T00:00:00"
    result = sd.getStardate()
    assert isinstance(result, float)
