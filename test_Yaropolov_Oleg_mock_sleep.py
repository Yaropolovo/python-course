from unittest.mock import patch
import pytest
import sleepy
import time

@patch("sleepy.sleep")
def test_can_add(mock_sleep):
    assert 6 == sleepy.sleep_add(2, 4)

@patch("time.sleep")
def test_can_multiply(mock_sleep):
    assert 6 == sleepy.sleep_multiply(2,3)
