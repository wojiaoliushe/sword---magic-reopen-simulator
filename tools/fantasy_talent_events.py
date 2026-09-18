# -*- coding: utf-8 -*-
"""Talent-gated flavor / forced events (9300–9305)."""
from __future__ import annotations


def apply_talent_events(events: list, add) -> None:
    existing = {int(ev["eventId"]) for ev in events}
    rows = [
        {
            "eventId": 9300,
            "type": "forced",
            "desc": "一百岁，匣子自己开了。里面不是财宝，是一张写给一百岁的你的字条：你还在。",
            "minAge": 100,
            "maxAge": 100,
            "baseWeight": 0,
            "requiredFlags": [{"talent_box": True}],
            "effects": {"wis": 2, "gold": 5, "cha": 1},
        },
        {
            "eventId": 9301,
            "type": "forced",
            "desc": "六十岁，那粒橙色的丸化在舌上。今年能抽到的事，气味都不一样了。",
            "minAge": 60,
            "maxAge": 60,
            "baseWeight": 0,
            "requiredFlags": [{"talent_orange_pill": True}],
            "effects": {"con": 1, "wis": 1},
        },
        {
            "eventId": 9302,
            "desc": "梦里有人把契约摊开。你没签字，墨却已经干了。",
            "minAge": 1,
            "maxAge": 90,
            "requiredFlags": [{"talent_pact": True}],
            "effects": {"cha": 1, "wis": 1},
            "cooldownGroups": ["talent_pact"],
            "cooldownMinInterval": 8,
            "baseWeight": 8,
        },
        {
            "eventId": 9303,
            "desc": "卫兵看了看你那张皱路条，犹豫片刻，还是让你进城了。",
            "minAge": 12,
            "maxAge": 80,
            "requiredFlags": [{"talent_city": True}],
            "effects": {"cha": 1, "gold": -1},
            "cooldownGroups": ["talent_city", "court"],
            "cooldownMinInterval": 6,
            "baseWeight": 8,
        },
        {
            "eventId": 9304,
            "desc": "路条在酒渍里还能认出火漆。有人请你上座，不问你从哪条巷子来。",
            "minAge": 16,
            "maxAge": 70,
            "requiredFlags": [{"talent_city": True}],
            "effects": {"cha": 1, "wis": 1},
            "cooldownGroups": ["talent_city", "court"],
            "cooldownMinInterval": 7,
            "baseWeight": 6,
        },
        {
            "eventId": 9305,
            "desc": "庇护者在耳边说：十六岁以前也可以先欠着。",
            "minAge": 8,
            "maxAge": 40,
            "requiredFlags": [{"talent_pact": True}],
            "effects": {"int": 1, "cha": 1},
            "cooldownGroups": ["talent_pact"],
            "cooldownMinInterval": 10,
            "baseWeight": 6,
        },
    ]
    for row in rows:
        if int(row["eventId"]) in existing:
            continue
        add(row)
