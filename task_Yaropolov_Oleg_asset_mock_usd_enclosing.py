def side_effect():
    nonlocal iteration
    return 76.32 + 0.1 * iteration
mock_get_usd_course.side_effect = side_effect
