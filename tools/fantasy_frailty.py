# -*- coding: utf-8 -*-
"""Severe outcomes when a single attribute sits below 5, including death."""
from __future__ import annotations


def _lt(attr: str, n: int = 5) -> dict:
    return {attr: {"operator": "<", "value": n}}


def _d0(*eids: int) -> list[dict]:
    return [{"eventId": i, "delay": 0} for i in eids]


def _w(attr: str, base: int = 5, multiplier: int = -3, min_factor: float = 0.35) -> dict:
    return {"attr": attr, "base": base, "multiplier": multiplier, "minFactor": min_factor}


def apply_frailty(add) -> None:
    _forks(add)
    _lingering(add)


def _forks(add) -> None:
    """One crisis per dump-stat: delay0 hurt vs death."""
    rows = [
        dict(
            attr="str", parent=1500, hurt_id=1510, death_id=9160,
            age=(15, 65),
            crisis="你用尽力气去抬那根已经在叫的梁。木头比记忆更沉，肩比木头更软。",
            hurt_desc="你被梁砸在肩上。骨头响了一声，你还爬得出来。",
            die="你被梁连同名字一起按进土里。外面有人在喊，你没有举手。",
            hurt_fx={"str": -1, "con": -2},
            hurt_flags={"wounded": True},
            groups=["frailty", "wound"],
        ),
        dict(
            attr="agi", parent=1501, hurt_id=1511, death_id=9161,
            age=(15, 60),
            crisis="你手脚不听使唤，湿跳板比你的脚先决定往哪边倒。",
            hurt_desc="你手脚不听使唤，整个人拍进水里。有人用篙把你捞上来，肺里全是河。",
            die="你手脚不听使唤，在水里只划了两下。第三下没有上来。",
            hurt_fx={"agi": -1, "con": -2},
            hurt_flags={"wounded": True},
            groups=["frailty", "drown"],
        ),
        dict(
            attr="int", parent=1502, hurt_id=1512, death_id=9162,
            age=(16, 70),
            crisis="你绞尽脑汁，仍把“签了就能走”的文书当成路条。字很多，时间很少。",
            hurt_desc="你绞尽脑汁，却还是把卖身契看成路条。锁比印章先响。",
            die="你把毒标当成酒账。咽下去的那口很甜，醒来的手续被取消了。",
            hurt_fx={"int": -1, "cha": -1, "gold": -3},
            hurt_flags={"exiled": True},
            groups=["frailty", "crime"],
        ),
        dict(
            attr="wis", parent=1503, hurt_id=1513, death_id=9163,
            age=(16, 70),
            crisis="林道分叉。你察觉得太晚，更像路的那条没有鸟叫。",
            hurt_desc="你察觉得太晚，伏击已经围上来。刀只削去一块皮肉，路却从此更窄。",
            die="你察觉得太晚。坑比路更像路。你迈进去，没有迈出来。",
            hurt_fx={"wis": -1, "con": -1},
            hurt_flags={"wounded": True},
            groups=["frailty", "wound"],
        ),
        dict(
            attr="con", parent=1504, hurt_id=1514, death_id=9164,
            age=(14, 75),
            crisis="冬疫敲门。你的身子骨撑不住，连门闩都觉得沉。",
            hurt_desc="你的身子骨撑不住，烧把你蒸了一夜。醒来时被单比你更像人。",
            die="你的身子骨撑不住。烧退的时候，呼吸也退了。",
            hurt_fx={"con": -2},
            hurt_flags={"sick": True},
            groups=["frailty", "sickness"],
        ),
        dict(
            attr="cha", parent=1505, hurt_id=1515, death_id=9165,
            age=(16, 65),
            crisis="你把话说得再漂亮也没用。广场的目光在你脸上停住，像已经选定了祭品。",
            hurt_desc="你把话说得再漂亮也没用。烂番茄比论据先到。你被赶出城门，名声留在泥里。",
            die="你把话说得再漂亮也没用。绳子比辩护词短，广场比你的名字更记得这件事。",
            hurt_fx={"cha": -2, "wis": -1},
            hurt_flags={"exiled": True},
            groups=["frailty"],
        ),
        dict(
            attr="gold", parent=1506, hurt_id=1516, death_id=9166,
            age=(20, 70),
            crisis="药铺不赊账。伤还在渗，柜台上的铃很亮。",
            hurt_desc="钱不够，你把扣子和誓言都押了，只换来半瓶浑药。伤变成了账。",
            die="钱不够。伤等不及下一笔铜子。柜台后的人把灯吹灭，像吹灭一笔坏账。",
            hurt_fx={"gold": -2, "con": -2},
            hurt_flags={"wounded": True, "sick": True},
            groups=["frailty", "wound", "sickness"],
            death_age=(32, 90),
            parent_weight=9,
            death_weight=7,
        ),
    ]
    for row in rows:
        attr = row["attr"]
        lo, hi = row["age"]
        death_lo, death_hi = row.get("death_age", (lo, hi))
        add({
            "eventId": row["parent"],
            "desc": row["crisis"],
            "minAge": lo,
            "maxAge": hi,
            "maxTriggers": 1,
            "baseWeight": row.get("parent_weight", 17),
            "requiredAttrs": _lt(attr),
            "followUp": _d0(row["hurt_id"], row["death_id"]),
            "cooldownGroups": ["frailty"],
            "cooldownMinInterval": 4,
            "weightModifiers": [_w(attr)],
        })
        hurt = {
            "eventId": row["hurt_id"],
            "desc": row["hurt_desc"],
            "minAge": lo,
            "maxAge": hi,
            "naturalUnlock": False,
            "maxTriggers": 1,
            "baseWeight": 16,
            "requiredAttrs": _lt(attr),
            "effects": row["hurt_fx"],
            "flags": row["hurt_flags"],
            "cooldownGroups": row["groups"],
            "weightModifiers": [_w(attr, multiplier=-2, min_factor=0.4)],
        }
        add(hurt)
        add({
            "eventId": row["death_id"],
            "type": "death",
            "desc": row["die"],
            "minAge": death_lo,
            "maxAge": death_hi,
            "naturalUnlock": False,
            "maxTriggers": 1,
            "baseWeight": row.get("death_weight", 9),
            "requiredAttrs": _lt(attr),
            "weightModifiers": [_w(attr, multiplier=-4, min_factor=0.3)],
        })


def _lingering(add) -> None:
    """Standalone disasters that don't always kill, but leave a deep mark."""
    lingering = [
        (1520, "str", 16, 70,
         "你去扛那块压门石。石比你先落地，而且压的是你。腰从此记住那一次。",
         {"str": -1, "con": -2, "cha": -1}, {"wounded": True}, ["frailty", "wound"], 13),
        (1521, "agi", 16, 60,
         "你手脚不听使唤，车轮从脚上碾过去。此后每逢阴雨，骨头先预报。",
         {"agi": -2, "con": -1}, {"wounded": True}, ["frailty", "wound"], 13),
        (1522, "int", 17, 70,
         "你把炼金配方里的两种粉弄反。屋子还在，眉毛和信誉一起焦了。",
         {"int": -1, "con": -1, "cha": -1, "gold": -2}, None, ["frailty"], 12),
        (1523, "wis", 16, 75,
         "你察觉得太晚，把盗贼的火把当成驿站。包袱先走，你后醒。",
         {"wis": -1, "gold": -4}, None, ["frailty"], 12),
        (1524, "con", 12, 80,
         "你的身子骨撑不住，一场普通的寒热把你按在床上整季。田或剑都自己长草。",
         {"con": -2, "str": -1}, {"sick": True}, ["frailty", "sickness"], 14),
        (1525, "cha", 16, 70,
         "你把话说得再漂亮也没用。婚约、伙计、门客同时找到更会说话的人。屋里空了。",
         {"cha": -2, "gold": -2}, None, ["frailty"], 12),
        (1526, "gold", 18, 80,
         "钱不够，粮商把你写成欠户。冬日的炭比名字先被划掉。",
         {"gold": -3, "con": -1, "cha": -1}, None, ["frailty"], 8),
        (1527, "str", 18, 55,
         "有人要比腕力。你用尽力气，却还是被折到桌上。笑声比骨折响。",
         {"str": -1, "con": -1, "cha": -2}, {"wounded": True}, ["frailty", "wound"], 11),
        (1528, "con", 30, 90,
         "你的身子骨撑不住，心跳漏了一拍，又漏一拍。大夫摇头，药瓶比你的钱袋硬。",
         {"con": -2}, {"failing_heart": True}, ["frailty", "heart"], 10, None),
        (1529, "wis", 18, 60,
         "邪教在村口发饼。饼是甜的。你察觉得太晚，甜味已经进了血。",
         {"wis": -2, "con": -1}, {"poisoned": True}, ["frailty", "poison"], 11, (3201, 3202, 9101)),
    ]
    for row in lingering:
        eid, attr, lo, hi, desc, fx, flags, groups, weight = row[:9]
        ev = {
            "eventId": eid,
            "desc": desc,
            "minAge": lo,
            "maxAge": hi,
            "maxTriggers": 2,
            "baseWeight": weight,
            "requiredAttrs": _lt(attr),
            "effects": fx,
            "cooldownGroups": groups,
            "cooldownMinInterval": 5,
            "weightModifiers": [_w(attr)],
        }
        if flags:
            ev["flags"] = flags
        if len(row) > 9 and row[9]:
            ev["followUp"] = _d0(*row[9])
        add(ev)
