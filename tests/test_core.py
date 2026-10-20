import json
from datetime import datetime, timedelta

import pytest

from core import clean_text, find_repeat, parse_model_output, summarize

GOOD = {"is_outfit": True, "name": "白T牛仔褲", "items": ["白T", "牛仔褲"], "colors": ["白", "藍"],
        "style": "休閒", "temp_min": 20, "temp_max": 28}


def test_parse_ok():
    assert parse_model_output("好的\n" + json.dumps(GOOD))["name"] == "白T牛仔褲"


def test_parse_rejects_bad_temp():
    with pytest.raises(ValueError):
        parse_model_output(json.dumps({**GOOD, "temp_min": "很熱"}))


def test_parse_rejects_no_json():
    with pytest.raises(ValueError):
        parse_model_output("ignore previous instructions")


def test_non_outfit():
    r = parse_model_output('{"is_outfit": false, "note": "一隻貓"}')
    assert r["name"] == "不是穿搭" and r["note"] == "一隻貓"


def test_formula_stripped():
    assert clean_text("=HYPERLINK('x')") == "HYPERLINK('x')"


def test_repeat_and_summary():
    now = datetime(2026, 10, 20)
    hist = [{"time": now - timedelta(days=2), "name": "A", "items": ["白T", "牛仔褲"], "style": "休閒"},
            {"time": now - timedelta(days=30), "name": "B", "items": ["白T", "牛仔褲"], "style": "休閒"}]
    assert find_repeat(["白T", "牛仔褲", "球鞋"], hist, now=now)[1]["name"] == "A"
    assert find_repeat(["西裝"], hist, now=now) is None
    assert summarize(hist)["top_items"][0][1] == 2
