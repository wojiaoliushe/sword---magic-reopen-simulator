# -*- coding: utf-8 -*-
"""Thirty hard achievement spines: netted chains, multiple wins, closed failures."""
from __future__ import annotations


def ge(attr: str, n: int = 9) -> dict:
    return {attr: {"operator": ">=", "value": n}}


def lt_map(**attrs: int) -> dict:
    return {a: {"operator": "<", "value": n} for a, n in attrs.items()}


def d0(*eids: int) -> list[dict]:
    return [{"eventId": i, "delay": 0} for i in eids]


def later(eid: int, years: int) -> dict:
    return {"eventId": eid, "delay": years}


def w_attr(attr: str, base: int = 8, multiplier: int = 3, min_factor: float | None = 0.15) -> dict:
    item: dict = {"attr": attr, "base": base, "multiplier": multiplier}
    if min_factor is not None:
        item["minFactor"] = min_factor
    return item


def apply_achievements(add, events: list[dict], job_req, origin_req, race_req) -> None:
    _patch_tickets(events)
    ctx = dict(job_req=job_req, origin_req=origin_req, race_req=race_req, add=add)
    _crown(ctx)
    _free_city(ctx)
    _racial_pact(ctx)
    _win_war(ctx)
    _feud(ctx)
    _mercenary(ctx)
    _hold_pass(ctx)
    _dragon(ctx)
    _dragon_flight(ctx)
    _sea_serpent(ctx)
    _phoenix(ctx)
    _new_world(ctx)
    _world_map(ctx)
    _well_lord(ctx)
    _close_gate(ctx)
    _lich(ctx)
    _meet_god(ctx)
    _high_priest(ctx)
    _name_from_death(ctx)
    _philosopher_stone(ctx)
    _buy_peace(ctx)
    _return_relic(ctx)
    _correct_epic(ctx)
    _apprentice(ctx)
    _stop_plague(ctx)
    _feast(ctx)
    _refuse_godhood(ctx)
    _true_name_burial(ctx)
    _echoes(ctx)


def _patch_tickets(events: list[dict]) -> None:
    by = {int(ev["eventId"]): ev for ev in events}

    def flag(eid: int, **patch) -> None:
        ev = by.get(eid)
        if not ev:
            return
        flags = ev.setdefault("flags", {})
        flags.update(patch)

    flag(3211, dragon_scar=True)
    for eid in (4431, 4432, 4433, 4434, 4435):
        flag(eid, map_under=True)
    flag(4103, spared_foe=True, true_name_known=True)
    flag(4111, true_name_known=True)
    flag(4513, spared_foe=True)
    flag(4611, spared_foe=True, true_name_known=True)
    flag(4612, spared_foe=True)
    for eid in (4761, 4762, 4763):
        flag(eid, spared_foe=True)
    flag(3819, false_name=True)
    for eid in (4323, 4328, 4333, 4334):
        flag(eid, false_name=True)
    flag(4223, false_name=True)
    flag(3971, true_name_known=True)
    flag(4330, true_name_known=True)


def _nat(add, eid, desc, kids, min_age, max_age, *, weight=3, group="ach_entry", extra=None, interval=18, need=None):
    ev = {
        "eventId": eid, "desc": desc, "minAge": min_age, "maxAge": max_age,
        "maxTriggers": 1, "baseWeight": weight,
        "cooldownGroups": [group, "ach_entry"], "cooldownMinInterval": interval,
        "followUp": d0(*kids),
        "ageModifiers": {"peak": min(42, min_age + 8), "decay": 0.92},
    }
    if need:
        ev["requiredFlags"] = need
    if extra:
        ev.update(extra)
    add(ev)


def _gate(add, eid, desc, kids, need, min_age=22, max_age=90, set=None, fx=None):
    ev = {
        "eventId": eid, "desc": desc, "minAge": min_age, "maxAge": max_age,
        "naturalUnlock": False, "maxTriggers": 1,
        "requiredFlags": need, "followUp": d0(*kids),
    }
    if set:
        ev["flags"] = set
    if fx:
        ev["effects"] = fx
    add(ev)


def _leaf(add, eid, desc, *, attrs=None, need=None, set=None, fx=None, follow=None,
          weight=13, min_age=20, max_age=90, death=False, mutex=None, mt=None, wmod=None):
    ev = {
        "eventId": eid, "desc": desc, "minAge": min_age, "maxAge": max_age,
        "naturalUnlock": False, "baseWeight": weight,
    }
    if mt is not None:
        ev["maxTriggers"] = mt
    if death:
        ev["type"] = "death"
    if attrs:
        ev["requiredAttrs"] = attrs
    if need:
        ev["requiredFlags"] = need
    if set:
        ev["flags"] = set
    if fx:
        ev["effects"] = fx
    if follow:
        ev["followUp"] = follow
    if mutex:
        ev["mutexEvents"] = list(mutex)
    if wmod:
        ev["weightModifiers"] = wmod
    elif attrs:
        keys = list(attrs.keys())
        if len(keys) == 1:
            spec = attrs[keys[0]]
            if isinstance(spec, dict) and spec.get("operator") == ">=":
                ev["weightModifiers"] = [w_attr(keys[0], int(spec.get("value") or 8), 3)]
    add(ev)


def _win(add, eid, desc, ach, *, attrs=None, need=None, set=None, fx=None, follow=None,
         weight=16, min_age=24, mutex=None, wmod=None):
    flags = {ach: True}
    if set:
        flags.update(set)
    _leaf(
        add, eid, desc, attrs=attrs, need=need, set=flags, fx=fx or {"wis": 1, "cha": 1},
        follow=follow, weight=weight, min_age=min_age, mutex=mutex, mt=1, wmod=wmod,
    )


def _fail(add, eid, desc, *, attrs=None, need=None, set=None, fx=None, follow=None,
          weight=9, min_age=20):
    _leaf(
        add, eid, desc, attrs=attrs, need=need, set=set,
        fx=fx or {"cha": -1, "wis": 1}, follow=follow, weight=weight, min_age=min_age, mt=1,
    )


def _die(add, eid, desc, *, attrs=None, need=None, min_age=20, weight=11):
    _leaf(add, eid, desc, attrs=attrs, need=need, death=True, weight=weight, min_age=min_age, mt=1)


# -----------------------------------------------------------------------------
# 1 / 2 / 5  王冠脊：加冕、摄政、审王
# -----------------------------------------------------------------------------
KING_WINS = (6121, 6122, 6123, 6124)
REGENT_WINS = (6141, 6142, 6143)
TRIAL_WINS = (6171, 6172, 6173)


def _crown(ctx) -> None:
    add, origin_req = ctx["add"], ctx["origin_req"]
    _nat(add, 6100, "王室的信比丧报更轻：幼主、空座、以及一把还没人敢坐的椅子。",
         (6101, 6102, 6103, 6104, 6105), 22, 52, weight=3, group="ach_crown")
    _leaf(add, 6101, "你翻出一份发黄的荐信。墨水把你的姓写成王室旁支的影子。",
          attrs=ge("int", 8), need=origin_req("noble") + [{"royal_favor": True}, {"plot_courtier": True}],
          set={"crown_blood": True, "crown_ticket": True}, fx={"int": 1, "cha": 1},
          follow=[later(6110, 2)], min_age=22)
    _leaf(add, 6102, "军营里有人把你的旧番号喊成号令。旗帜转向你，像转向一口井。",
          attrs=ge("str", 8),
          need=[{"war_veteran": True}, {"home_held": True}, {"gladiator_fame": True}, {"enlisted": True}],
          set={"crown_army": True, "crown_ticket": True}, fx={"str": 1, "cha": 1},
          follow=[later(6110, 2)], min_age=22)
    _leaf(add, 6103, "联姻的酒比血甜。对方要的不是你，是你能挡住的那些刀。",
          attrs=ge("cha", 9), set={"crown_marriage": True, "crown_ticket": True},
          fx={"cha": 1, "gold": -4}, follow=[later(6110, 2)], min_age=22)
    _leaf(add, 6104, "神殿抽签抽到你的名字。神父说那是神谕。你说那是纸。纸仍被宣读。",
          attrs=ge("wis", 9), need=[{"faith": True}, {"cult_broken": True}, {"patron_god": "sun"}, {"patron_god": "fate"}],
          set={"crown_omen": True, "crown_ticket": True}, fx={"wis": 1, "cha": 1},
          follow=[later(6110, 2)], min_age=22)
    _fail(add, 6105, "你把信退回去。空座很快被别人坐热。你的名字没有进入那把椅子的阴影。",
          set={"crown_refused": True}, fx={"wis": 1, "cha": -1}, follow=[later(6106, 8)], min_age=22)
    _leaf(add, 6106, "多年后加冕礼的烟火照进你的窗。你关窗。烟火仍在别人的城里亮。",
          need=[{"crown_refused": True}], fx={"wis": 1}, min_age=30)

    _gate(add, 6110, "摄政会议、军头和神殿把三把钥匙放在桌上。钥匙比话锋利。",
          (6111, 6112, 6113, 6114), [{"crown_ticket": True}], min_age=24)
    _leaf(add, 6111, "你伸手去碰王冠。房间里的呼吸一齐停住。",
          attrs=ge("cha", 8), set={"king_path": True}, fx={"cha": 1},
          follow=[later(6120, 3)], min_age=24)
    _leaf(add, 6112, "你把王冠推向幼主，自己站到椅后。影子比座位长。",
          attrs=ge("wis", 8), set={"regent_path": True}, fx={"wis": 1},
          follow=[later(6140, 3)], min_age=24)
    _leaf(add, 6113, "你把王冠翻过来，当惊堂木。被告席是空的，很快会有人来坐。",
          attrs=ge("int", 8), set={"trial_path": True}, fx={"int": 1},
          follow=[later(6170, 3)], min_age=24)
    _fail(add, 6114, "你退出会场。钥匙仍在桌上。有人说你胆小，有人说你活着。",
          set={"crown_walked": True}, fx={"wis": 1, "gold": 2}, follow=[later(6115, 6)], min_age=24)
    _leaf(add, 6115, "新王的税吏来问你当年为什么不坐。你请他喝茶。茶比答案便宜。",
          need=[{"crown_walked": True}], fx={"cha": 1, "wis": 1}, min_age=30)

    _gate(add, 6120, "加冕日。城门反锁。钟声把刀也喊醒了。",
          (6121, 6122, 6123, 6124, 6125, 9200), [{"king_path": True}], min_age=27)
    _win(add, 6121, "荐信、血脉和你此刻的站姿叠在一起。冠落下。它比想象中重，也比刀轻。",
         "ach_king", attrs=ge("cha", 10),
         need=[{"crown_blood": True}, {"royal_favor": True}, {"origin": "noble"}, {"plot_courtier": True}],
         set={"crowned": True}, fx={"cha": 2, "gold": 6}, mutex=REGENT_WINS + TRIAL_WINS,
         follow=[later(6130, 6)], min_age=27)
    _win(add, 6122, "兵谏没有宣读。旗帜进殿。幼主让座，你没有解释。历史会替你解释错。",
         "ach_king", attrs=ge("str", 10),
         need=[{"crown_army": True}, {"war_veteran": True}, {"home_held": True}],
         set={"crowned": True}, fx={"str": 1, "cha": 1, "gold": 4}, mutex=REGENT_WINS + TRIAL_WINS,
         follow=[later(6130, 6)], min_age=27)
    _win(add, 6123, "选王会议上你把金币和承诺堆成一座临时的山。山够高，人就点头。",
         "ach_king", attrs=ge("gold", 12),
         set={"crowned": True}, fx={"gold": -10, "cha": 2}, mutex=REGENT_WINS + TRIAL_WINS,
         follow=[later(6130, 6)], min_age=27, wmod=[w_attr("gold", 12, 2, 0.2)])
    _win(add, 6124, "龙在城墙上低头。冠不必人手。鳞片的影子比绒面更像加冕。",
         "ach_king", attrs=ge("cha", 9), need=[{"dragon_allied": True}, {"dragon_pact": True}],
         set={"crowned": True}, fx={"cha": 2, "wis": 1}, mutex=REGENT_WINS + TRIAL_WINS,
         follow=[later(6130, 6)], min_age=27)
    _fail(add, 6125, "冠没有落下。你被请出殿，从侧门。侧门通向流放的路，路很直。",
          set={"plot_exiled": True, "false_name": True, "king_path": None},
          fx={"cha": -2, "gold": -3, "wis": 1}, follow=[later(6126, 5)], min_age=27)
    _die(add, 9200, "有人需要一个尸体来证明空座仍神圣。你的名字够短，够填进讣告。",
         attrs=lt_map(cha=9, str=9, gold=8), min_age=27)
    _leaf(add, 6126, "流亡路上有人仍称你为王。你让他们改口。改口比复辟安全。",
          need=[{"plot_exiled": True}], fx={"wis": 1, "con": 1}, min_age=32)
    _leaf(add, 6130, "有小孩把你的加冕画成童话。你把最像你的那一笔涂掉。",
          need=[{"ach_king": True}], fx={"wis": 1}, min_age=33)

    _gate(add, 6140, "幼主咳嗽。摄政印在你手里发烫。殿外有人教他叫你父王。",
          (6141, 6142, 6143, 6144), [{"regent_path": True, "crowned": False}], min_age=27)
    _win(add, 6141, "你把幼主养到能握住剑。你把印还他。他还你一个不必称王的余生。",
         "ach_regent", attrs=ge("wis", 10), set={"regent_done": True},
         fx={"wis": 2, "cha": 1}, mutex=KING_WINS + TRIAL_WINS, follow=[later(6145, 6)], min_age=27)
    _win(add, 6142, "你与教会共治。祭坛和印章各管一半城。你的名字不进颂歌，进账本。",
         "ach_regent", attrs=ge("cha", 9), need=[{"faith": True}, {"crown_omen": True}, {"cult_broken": True}],
         set={"regent_done": True}, fx={"wis": 1, "cha": 1, "gold": 3}, mutex=KING_WINS + TRIAL_WINS,
         follow=[later(6145, 6)], min_age=27)
    _win(add, 6143, "你把兵权分给三个互相讨厌的人。他们忙着讨厌彼此，幼主得以长大。",
         "ach_regent", attrs=ge("int", 10), set={"regent_done": True},
         fx={"int": 1, "wis": 1}, mutex=KING_WINS + TRIAL_WINS, follow=[later(6145, 6)], min_age=27)
    _fail(add, 6144, "你没忍住。你去碰冠。冠拒绝你，军头也拒绝你。你两头不着。",
          set={"regent_path": None, "plot_exiled": True}, fx={"cha": -2, "wis": 1, "gold": -2},
          follow=[later(6126, 4)], min_age=27)
    _leaf(add, 6145, "新王在诏书里称你为师。你把诏书叠进箱底，像叠进一场没有加冕的胜利。",
          need=[{"ach_regent": True}], fx={"wis": 1, "cha": 1}, min_age=33)

    _gate(add, 6170, "王被带上被告席。冠还在他头上。你要它先落地，或先认罪。",
          (6171, 6172, 6173, 6174, 9201), [{"trial_path": True, "crowned": False}], min_age=28)
    _win(add, 6171, "你用文书、账册和一封他自己签过的密令把他按进法律。法律第一次比剑响。",
         "ach_try_king", attrs=ge("int", 10),
         need=[{"plot_foiled": True}, {"plot_reported": True}, {"knows_old_tongue": True}],
         set={"king_tried": True}, fx={"int": 2, "wis": 1}, mutex=KING_WINS + REGENT_WINS,
         follow=[later(6175, 5)], min_age=28)
    _win(add, 6172, "兵围王宫。你不许斩首，只许公审。广场上的人第一次看见王冠也可以低头。",
         "ach_try_king", attrs=ge("str", 10),
         need=[{"crown_army": True}, {"war_veteran": True}, {"home_held": True}],
         set={"king_tried": True}, fx={"str": 1, "cha": 1, "wis": 1}, mutex=KING_WINS + REGENT_WINS,
         follow=[later(6175, 5)], min_age=28)
    _win(add, 6173, "神明入梦，王自己跪下。你只负责把梦记录成判词。墨比雷轻。",
         "ach_try_king", attrs=ge("wis", 10), need=[{"god_seen": True}, {"crown_omen": True}, {"faith": True}],
         set={"king_tried": True}, fx={"wis": 2, "cha": 1}, mutex=KING_WINS + REGENT_WINS,
         follow=[later(6175, 5)], min_age=28)
    _fail(add, 6174, "审到一半，赦免令从后门进来。你活着，判词变成笑话。笑话比绞索长。",
          set={"trial_path": None, "cha_debt": True}, fx={"cha": -2, "int": 1, "wis": 1},
          follow=[later(6176, 4)], min_age=28)
    _die(add, 9201, "叛逆的定义在这一天被写短。短到只容得下你的脖子。",
         attrs=lt_map(int=10, str=10, wis=10), min_age=28)
    _leaf(add, 6175, "有人请你当下一任王。你指着空席：它刚当过被告。",
          need=[{"ach_try_king": True}], fx={"wis": 1}, min_age=33)
    _leaf(add, 6176, "你在酒馆听见自己的审王被唱成闹剧。你没有纠正。纠正需要一座还听你的广场。",
          need=[{"cha_debt": True}], fx={"wis": 1, "con": 1}, min_age=32)


def _free_city(ctx) -> None:
    add = ctx["add"]
    _nat(add, 6200, "故乡的缺口补上了，法还没有。有人要你写第一句：谁说了算。",
         (6201, 6202, 6203, 6204), 24, 60, weight=3, group="ach_city",
         need=[{"home_held": True}, {"home_evacuated": True}, {"guild_trusted": True}, {"dungeon_cleared": True}])
    _leaf(add, 6201, "你把城墙当纸，把军令当第一行法。有人不喜欢，墙喜欢。",
          attrs=ge("str", 8), set={"city_iron": True}, fx={"str": 1, "cha": 1},
          follow=[later(6210, 3)], min_age=24)
    _leaf(add, 6202, "你用钱向旧王买自治特许。印章很贵，比再打一仗便宜。",
          attrs=ge("gold", 11), set={"city_charter": True}, fx={"gold": -8, "int": 1},
          follow=[later(6210, 3)], min_age=24, wmod=[w_attr("gold", 11, 2, 0.2)])
    _leaf(add, 6203, "你把城献给神，留下市民议会。神管天，人管井。",
          attrs=ge("wis", 9), need=[{"faith": True}, {"cult_broken": True}],
          set={"city_temple": True}, fx={"wis": 1, "cha": 1}, follow=[later(6210, 3)], min_age=24)
    _fail(add, 6204, "第一句你没写出来。有人替你写了税。税比法快，也比法短命。",
          fx={"wis": 1, "cha": -1}, follow=[later(6205, 6)], min_age=24)
    _leaf(add, 6205, "你在别人的法下交税。税单角落有一句像你起草的。像，不是。",
          fx={"wis": 1}, min_age=30)
    _gate(add, 6210, "外敌再来。这一次他们要试验你的法能不能活过第二夜。",
          (6211, 6212, 6213, 6214, 9219),
          [{"city_iron": True}, {"city_charter": True}, {"city_temple": True}], min_age=27)
    _win(add, 6211, "你守住缺口，并把今夜写进宪章：墙可以倒，表决不行。城在你死后仍按这句走。",
         "ach_free_city", attrs=ge("str", 10), need=[{"city_iron": True}, {"home_held": True}],
         set={"free_city": True}, fx={"str": 1, "wis": 1, "cha": 1}, follow=[later(6215, 7)], min_age=27)
    _win(add, 6212, "你把特许状摊在敌帅眼前。他笑，然后发现笑不掉印章。兵退了。法留下。",
         "ach_free_city", attrs=ge("int", 10), need=[{"city_charter": True}],
         set={"free_city": True}, fx={"int": 1, "gold": 2}, follow=[later(6215, 7)], min_age=27)
    _win(add, 6213, "神殿担保：攻此城即攻神。敌帅改去攻别的城。议会连夜把这句话抄成十条。",
         "ach_free_city", attrs=ge("wis", 10), need=[{"city_temple": True}, {"faith": True}],
         set={"free_city": True}, fx={"wis": 2, "cha": 1}, follow=[later(6215, 7)], min_age=27)
    _fail(add, 6214, "法在第二夜裂了。城还在，按别人的法走。你的第一句被涂成税。",
          set={"city_lost": True}, fx={"cha": -2, "wis": 1, "gold": -3}, follow=[later(6216, 5)], min_age=27)
    _die(add, 9219, "缺口认出你。它把你当成还没砌上的那块砖。",
         attrs=lt_map(str=10, int=10, wis=10), min_age=27)
    _leaf(add, 6215, "有外邦人来抄你的宪章。抄错了两句。你让他们抄错的那两句更像人话。",
          need=[{"ach_free_city": True}], fx={"wis": 1, "int": 1}, min_age=34)
    _leaf(add, 6216, "你在别人的城里看见自己起草的句子。句子还在，署名换成了胜利者。",
          need=[{"city_lost": True}], fx={"wis": 1, "con": 1}, min_age=32)


def _racial_pact(ctx) -> None:
    add, race_req = ctx["add"], ctx["race_req"]
    _nat(add, 6240, "两族在桥上对峙。桥比仇恨窄，仇恨比河深。",
         (6241, 6242, 6243, 6244), 20, 55, weight=3, group="ach_pact")
    _leaf(add, 6241, "你先把伤者从对岸背回来。他们恨你的血，暂不恨你的背。",
          attrs=ge("con", 8), set={"pact_debt": True}, fx={"con": 1, "cha": 1},
          follow=[later(6250, 2)], min_age=20)
    _leaf(add, 6242, "你用两边都能骂懂的话把刀按下。骂比血便宜。",
          attrs=ge("cha", 9), set={"pact_debt": True}, fx={"cha": 1, "wis": 1},
          follow=[later(6250, 2)], min_age=20)
    _leaf(add, 6243, "你的耳朵、角或鳞让两边都无法立刻把你归类。你把这尴尬用成通行证。",
          need=race_req("half_elf", "tiefling", "dragonborn", "half_orc"),
          set={"pact_debt": True}, fx={"cha": 1}, follow=[later(6250, 2)], min_age=20, weight=14)
    _fail(add, 6244, "你没有上桥。桥在夜里烧掉。两边都说是对方烧的。你成了唯一没资格解释的人。",
          set={"pact_failed": True}, fx={"wis": 1, "cha": -1}, follow=[later(6245, 6)], min_age=20)
    _leaf(add, 6245, "多年后渡口改了名字。旧名仍在仇恨的口头流传。你没有纠正。",
          need=[{"pact_failed": True}], fx={"wis": 1}, min_age=26)

    _gate(add, 6250, "有人在签字前一夜把你的翻译换成假的。永约差一寸就会变成宣战。",
          (6251, 6252, 6253, 6254, 9220), [{"pact_debt": True}], min_age=22)
    _win(add, 6251, "战场停火。你让胜利的一方把刀收进鞘，把粮食推向失败的一方。两边都恨，都签。",
         "ach_racial_pact", attrs=ge("wis", 10),
         need=[{"war_veteran": True}, {"war_letter_ok": True}, {"ach_win_war": True}],
         set={"pact_done": True, "spared_foe": True}, fx={"wis": 2, "cha": 1},
         follow=[later(6255, 6)], min_age=22)
    _win(add, 6252, "联姻在桥上完成。誓词用两种语言各说一遍。河第一次肯当证人。",
         "ach_racial_pact", attrs=ge("cha", 10), set={"pact_done": True, "spared_foe": True},
         fx={"cha": 2, "wis": 1}, follow=[later(6255, 6)], min_age=22)
    _win(add, 6253, "龙的影子压过桥。两边忽然发现彼此都是较小的敌人。约在鳞下签署。",
         "ach_racial_pact", attrs=ge("int", 9),
         need=[{"dragon_scar": True}, {"dragon_allied": True}, {"dragon_slain": True}, {"dragon_lair": True}],
         set={"pact_done": True, "spared_foe": True}, fx={"int": 1, "wis": 1},
         follow=[later(6255, 6)], min_age=22)
    _fail(add, 6254, "假翻译生效。第一滴血落在未干的墨上。约撕了。你被两边同时点名。",
          set={"pact_failed": True, "has_enemy_name": True}, fx={"cha": -2, "con": -1, "wis": 1},
          follow=[later(6245, 4)], min_age=22)
    _die(add, 9220, "桥塌的时候两边都松了手。你在中间。",
         attrs=lt_map(wis=10, cha=10, int=9), min_age=22)
    _leaf(add, 6255, "边境集市第一次同时说两种脏话。脏话听起来像和平。",
          need=[{"ach_racial_pact": True}], fx={"cha": 1, "gold": 1}, min_age=28)


def _win_war(ctx) -> None:
    add = ctx["add"]
    _nat(add, 6300, "战争要有人赢，不只是有人活。参谋部把地图翻到你面前，问你站哪一侧。",
         (6301, 6302, 6303, 6304, 6305), 23, 50, weight=3, group="ach_war")
    _leaf(add, 6301, "你把旧袍上的泥拍掉，重新走进编制。这一次你要的不是活命，是结局。",
          need=[{"war_veteran": True}, {"enlisted": True}, {"at_war": True}, {"war_night_survived": True}],
          set={"war_bid": True, "war_front": True}, fx={"str": 1, "con": 1},
          follow=[later(6310, 2)], min_age=23)
    _leaf(add, 6302, "你把当年那封改过边界的信摊开：还可以再改一寸，朝胜利的方向。",
          need=[{"war_letter_ok": True}, {"war_courier": True}],
          set={"war_bid": True, "war_intel": True}, fx={"int": 1, "agi": 1},
          follow=[later(6310, 2)], min_age=23)
    _leaf(add, 6303, "你以粮为刀。开过仓的人知道：饿比冲锋更快结束一场战争。",
          need=[{"war_gave_grain": True}, {"war_profiteer": True}],
          set={"war_bid": True, "war_starve": True}, fx={"int": 1, "gold": 2},
          follow=[later(6310, 2)], min_age=23)
    _leaf(add, 6304, "光荣榜上你的名字被划过。你改去组私军、当密使。路更长，仍通向同一张和约。",
          need=[{"war_draft_dodger": True}], set={"war_bid": True, "war_shadow": True},
          fx={"agi": 1, "wis": 1}, follow=[later(6330, 3)], min_age=23)
    _fail(add, 6305, "你站在墙头看别人赢。烟很远。你的手很干净，也没有资格去握和约。",
          set={"war_watched": True}, fx={"wis": 1, "cha": -1}, follow=[later(6306, 7)], min_age=23)
    _leaf(add, 6306, "凯旋式经过你的窗。你把窗关到旗帜走完。关窗也是一种参战。",
          need=[{"war_watched": True}], fx={"wis": 1}, min_age=30)

    _gate(add, 6310, "前线要一个决定：破城、逼和、断粮，或把敌帅的名字从世上抹掉。",
          (6311, 6312, 6313, 6314, 6315, 9202), [{"war_bid": True}], min_age=25)
    _win(add, 6311, "城破。你把旗帜插上敌楼，又下令不准屠城。胜利因此又脏又干净。",
         "ach_win_war", attrs=ge("str", 10), need=[{"war_front": True}, {"war_veteran": True}, {"home_held": True}],
         set={"war_won": True}, fx={"str": 1, "cha": 1, "gold": 5}, follow=[later(6320, 6)], min_age=25)
    _win(add, 6312, "你把和约写得像退路。敌帅签了，因为他看见你真的准备破城。",
         "ach_win_war", attrs=ge("cha", 10), need=[{"war_intel": True}, {"war_letter_ok": True}, {"war_front": True}],
         set={"war_won": True}, fx={"cha": 2, "int": 1}, follow=[later(6320, 6)], min_age=25)
    _win(add, 6313, "粮道断了。敌营先投降，后咒骂。咒骂里有你的名字，和约上也有。",
         "ach_win_war", attrs=ge("int", 10), need=[{"war_starve": True}, {"war_gave_grain": True}],
         set={"war_won": True, "war_dirty": True}, fx={"int": 1, "wis": 1, "cha": -1, "gold": 4},
         follow=[later(6320, 6)], min_age=25)
    _win(add, 6314, "敌帅在帐中倒下。战争少了一张嘴，多了一页空白。空白被你的人填成胜利。",
         "ach_win_war", attrs=ge("agi", 10), set={"war_won": True}, fx={"agi": 1, "wis": 1},
         follow=[later(6320, 6)], min_age=25)
    _fail(add, 6315, "进攻停在壕上。你活着下令撤退。这一场没有赢家，只有还活着的人互相避免对视。",
          set={"war_lost": True}, fx={"con": -1, "cha": -1, "wis": 1}, follow=[later(6321, 5)], min_age=25)
    _die(add, 9202, "号角比你的命令先到。你成为名册上最后一个被墨水吞掉的番号。",
         attrs=lt_map(str=10, cha=10, int=10, agi=10), min_age=25)
    _leaf(add, 6320, "有人把胜利写成你一个人的。你让他们把炊事兵的名字也写上。他们写了半个。",
          need=[{"ach_win_war": True}], fx={"wis": 1, "cha": 1}, min_age=31)
    _leaf(add, 6321, "停战碑背面没有字。有人说那一面是留给下一次的。你把青苔刮掉，没刻新的。",
          need=[{"war_lost": True}], fx={"wis": 1, "con": 1}, min_age=30)

    _gate(add, 6330, "私军和密使都准备好了。你要在编制外赢一场编制内的战争。",
          (6311, 6312, 6314, 6315, 9202), [{"war_shadow": True}], min_age=26)


def _feud(ctx) -> None:
    add = ctx["add"]
    _nat(add, 6340, "仇家的名再次出现，这一次带着一只空杯子和一把未出鞘的刀。",
         (6341, 6342, 6343), 22, 55, weight=3, group="ach_feud",
         need=[{"has_enemy_name": True}, {"plot_exiled": True}, {"war_draft_dodger": True}, {"caravan_fled": True}])
    _leaf(add, 6341, "你应了决斗。杯子空着。刀开始说话。",
          attrs=ge("str", 8), set={"feud_open": True, "feud_steel": True}, fx={"str": 1},
          follow=[later(6350, 2)], min_age=22)
    _leaf(add, 6342, "你把杯子斟满。酒比刀先到桌上。对方没有立刻打翻。",
          attrs=ge("cha", 8), set={"feud_open": True, "feud_wine": True}, fx={"cha": 1, "wis": 1},
          follow=[later(6350, 2)], min_age=22)
    _fail(add, 6343, "你躲开。仇在街上自己长大，长成与你无关的传说。传说仍咬人，只是不咬你。",
          set={"feud_avoided": True}, fx={"agi": 1, "cha": -1}, follow=[later(6344, 6)], min_age=22)
    _leaf(add, 6344, "仇家的孩子长大了，问你父亲为什么恨一个没有脸的人。你没有给脸。",
          need=[{"feud_avoided": True}], fx={"wis": 1}, min_age=28)

    _gate(add, 6350, "双方各死过一个近人。第三次可以是刀，也可以是酒。不能再是误会。",
          (6351, 6352, 6353, 6354, 9217), [{"feud_open": True}], min_age=24)
    _win(add, 6351, "决斗结束。仇尽了。你把刀擦净，发现擦不掉的是自己动手前的那一口痰。",
         "ach_end_feud", attrs=ge("str", 10), need=[{"feud_steel": True}],
         fx={"str": 1, "wis": 1, "cha": -1}, follow=[later(6355, 6)], min_age=24)
    _win(add, 6352, "你赔偿、公开道歉、把旧旗烧了。对方把杯子喝干。血仇改成难看的亲戚。",
         "ach_end_feud", attrs=ge("cha", 10), need=[{"feud_wine": True}, {"feud_steel": False}],
         set={"spared_foe": True}, fx={"cha": 2, "gold": -6, "wis": 1}, follow=[later(6355, 6)], min_age=24)
    _win(add, 6353, "你把仇家的孩子收作徒弟。妒忌以后再算。今天先教他活过你的姓。",
         "ach_end_feud", attrs=ge("wis", 10), set={"spared_foe": True, "has_apprentice": True, "true_name_known": True},
         fx={"wis": 2, "cha": 1}, follow=[later(6355, 6)], min_age=24)
    _fail(add, 6354, "第三次你又开了刃。酒洒了。仇改名换姓，传给下一辈。你赢了今晚，输了姓氏。",
          set={"feud_eternal": True, "feud_wine": None}, fx={"str": 1, "cha": -2, "wis": -1},
          follow=[later(6356, 5)], min_age=24)
    _die(add, 9217, "第三次仍是刀。刀比你记得更清楚谁先欠谁。",
         attrs=lt_map(str=10, cha=10, wis=10), min_age=24)
    _leaf(add, 6355, "有人问仇还在不在。你指指空杯子：在，只是不再喝人。",
          need=[{"ach_end_feud": True}], fx={"wis": 1}, min_age=30)
    _leaf(add, 6356, "下一辈的挑战书送到。字很嫩。你把它当柴烧。烟比血淡，仇不淡。",
          need=[{"feud_eternal": True}], fx={"con": 1, "wis": 1}, min_age=29)


def _mercenary(ctx) -> None:
    add = ctx["add"]
    _nat(add, 6370, "有人愿跟你吃饭、跟你死，暂不愿跟你的名字分开。佣兵团要一面旗。",
         (6371, 6372, 6373, 6374), 24, 50, weight=3, group="ach_merc")
    _leaf(add, 6371, "你用战歌把散兵收成一行。歌走调，人没有。",
          attrs=ge("cha", 9), set={"company_flag": True}, fx={"cha": 1, "str": 1},
          follow=[later(6380, 2)], min_age=24)
    _leaf(add, 6372, "你用金币把旗钉在桌上。钉很浅，钱很深。",
          attrs=ge("gold", 11), set={"company_flag": True}, fx={"gold": -8, "int": 1},
          follow=[later(6380, 2)], min_age=24, wmod=[w_attr("gold", 11, 2, 0.2)])
    _leaf(add, 6373, "角斗场和战场把你的名字借给旗帜。人跟着名字来，像跟着一口有水的井。",
          need=[{"gladiator_fame": True}, {"war_veteran": True}, {"guild_trusted": True}],
          set={"company_flag": True}, fx={"cha": 1}, follow=[later(6380, 2)], min_age=24)
    _fail(add, 6374, "没人跟你。你把旗叠起来当垫子。垫子比军团老实。",
          fx={"wis": 1, "cha": -1}, follow=[later(6375, 5)], min_age=24)
    _leaf(add, 6375, "路上遇见别人的佣兵。他们的旗很新。你的垫子很旧。你把路让开。",
          fx={"wis": 1}, min_age=29)

    _gate(add, 6380, "第一场胜了。内讧比敌人快。你要交不交出指挥权。",
          (6381, 6382, 6383, 6384), [{"company_flag": True}], min_age=26)
    _leaf(add, 6381, "你仍当团长，把内讧按进土里。土里会再长出来，只是今晚不长。",
          attrs=ge("str", 9), set={"company_yours": True}, fx={"str": 1, "cha": 1},
          follow=[later(6386, 2)], min_age=26)
    _leaf(add, 6382, "你改当军师。指挥权交给一个比你更不怕死的人。你怕地图。",
          attrs=ge("int", 9), set={"company_yours": True, "company_advisor": True}, fx={"int": 1, "wis": 1},
          follow=[later(6386, 2)], min_age=26)
    _leaf(add, 6383, "你把团献给国王，换成正规军的番号。旗还在，你的名字改成脚注。",
          attrs=ge("cha", 9), need=[{"royal_favor": True}, {"crowned": True}, {"regent_done": True}, {"crown_ticket": True}],
          set={"company_yours": True, "company_royal": True}, fx={"cha": 1, "gold": 4},
          follow=[later(6386, 2)], min_age=26)
    _fail(add, 6384, "内讧把旗撕成两半。两半都去给别人卖命。你成了没有团的团长。",
          set={"company_broke": True}, fx={"cha": -2, "gold": -3, "wis": 1}, follow=[later(6385, 5)], min_age=26)
    _leaf(add, 6385, "酒店里有人唱你们的第一场胜仗。唱到内讧时改口唱天气。",
          need=[{"company_broke": True}], fx={"wis": 1}, min_age=31)

    _gate(add, 6386, "你交出日常指挥。两年后有人来报：他们在你不在的战场上赢了。",
          (6387, 6388, 6389), [{"company_yours": True}], min_age=28)
    _win(add, 6387, "捷报上没有你的名字。你把酒洒在旗角：这才叫团还活着。",
         "ach_mercenary", need=[{"company_yours": True}], fx={"wis": 2, "cha": 1},
         follow=[later(6390, 5)], min_age=28)
    _win(add, 6388, "他们用你留的阵图赢的。你当军师的那一页被汗浸透，仍能读。",
         "ach_mercenary", need=[{"company_advisor": True}], fx={"int": 1, "wis": 1},
         follow=[later(6390, 5)], min_age=28)
    _win(add, 6389, "正规军打着你的旧旗号赢了边境。国王寄来一枚没有你肖像的奖章。你收了。",
         "ach_mercenary", need=[{"company_royal": True}], fx={"cha": 1, "gold": 3},
         follow=[later(6390, 5)], min_age=28)
    _leaf(add, 6390, "老兵来找你喝酒，叫你队长。你纠正：现在该叫他们队长。",
          need=[{"ach_mercenary": True}], fx={"cha": 1, "wis": 1}, min_age=33)


def _hold_pass(ctx) -> None:
    add = ctx["add"]
    _nat(add, 6392, "关隘的粮只够三天。地图上这关标着：不可守。有人仍把钥匙交给你。",
         (6393, 6394, 6395, 6396), 24, 48, weight=3, group="ach_pass")
    _leaf(add, 6393, "你下令死守。钥匙进你袖里，像进一口没有退路的井。",
          attrs=ge("con", 8), set={"pass_key": True, "pass_hold": True}, fx={"con": 1, "wis": 1},
          follow=[later(6397, 1)], min_age=24)
    _leaf(add, 6394, "你去找粮：开仓的旧账、无尽的袋，或踏水把河变成路。",
          attrs=ge("int", 8),
          need=[{"war_gave_grain": True}, {"item_endless_sack": True}, {"skill_water_walk": True}, {"guild_trusted": True}],
          set={"pass_key": True, "pass_supply": True}, fx={"int": 1},
          follow=[later(6397, 1)], min_age=24)
    _leaf(add, 6395, "你准备把关变成诱饵。假死、影藏、把敌帅请进来。",
          attrs=ge("agi", 8), set={"pass_key": True, "pass_trap": True}, fx={"agi": 1},
          follow=[later(6397, 1)], min_age=24)
    _fail(add, 6396, "你把钥匙还回去。不可守就是不可守。撤退的人活着，关的名字死了。",
          fx={"wis": 1, "cha": -1}, follow=[later(6391, 5)], min_age=24)
    _leaf(add, 6391, "新地图把那关涂成空白。空白比失败干净，也比你干净。",
          fx={"wis": 1}, min_age=29)

    _gate(add, 6397, "第三夜。粮尽。不可守的关还在问你一遍。",
          (6398, 6399, 6368, 6369, 9203), [{"pass_key": True}], min_age=25)
    _win(add, 6398, "你把关守到援军自己都不敢相信。不可守被改成一个笑话，笑话里有你的肩。",
         "ach_hold_pass", attrs=ge("con", 11), need=[{"pass_hold": True}],
         fx={"con": 2, "str": 1, "cha": 1}, follow=[later(6367, 6)], min_age=25)
    _win(add, 6399, "你放水淹关。关没了，敌帅的路也没了。活人从屋顶离开，地图从此多一条湖。",
         "ach_hold_pass", attrs=ge("int", 10), need=[{"pass_supply": True}, {"pass_hold": True}],
         fx={"int": 1, "wis": 1}, follow=[later(6367, 6)], min_age=25)
    _win(add, 6368, "敌帅进关来取你的尸体。尸体是假的。活的是你的刀。关还在。",
         "ach_hold_pass", attrs=ge("agi", 10), need=[{"pass_trap": True}],
         fx={"agi": 2, "int": 1}, follow=[later(6367, 6)], min_age=25)
    _fail(add, 6369, "你在第四夜下令弃关。人走了。关如它所愿，不可守被证实。",
          fx={"con": -1, "cha": -1, "wis": 1}, follow=[later(6391, 4)], min_age=25)
    _die(add, 9203, "粮尽之后是名尽。关把你留下，当最后一块不肯走的砖。",
         attrs=lt_map(con=11, int=10, agi=10), min_age=25)
    _leaf(add, 6367, "有参谋把‘不可守’从手册里划掉。他划得很用力，像怕字自己长回来。",
          need=[{"ach_hold_pass": True}], fx={"int": 1, "wis": 1}, min_age=31)


DRAGON_SLAY = (6421,)
DRAGON_ALLY = (6422, 6423)


def _dragon(ctx) -> None:
    add = ctx["add"]
    _nat(add, 6400, "有人把一片还热的龙鳞放上你的桌。桌开始出汗。传说要求你决定怕还是去。",
         (6401, 6402, 6403, 6404), 22, 55, weight=3, group="ach_dragon")
    _leaf(add, 6401, "你循焦土走。焦土比地图诚实，也比地图肯咬人。",
          attrs=ge("con", 8), set={"dragon_hunt": True, "dragon_scar": True}, fx={"con": 1, "wis": 1},
          follow=[later(6410, 2)], min_age=22)
    _leaf(add, 6402, "你把鳞片读成句子。句子指向一座没有鸟的山。",
          attrs=ge("int", 9), set={"dragon_hunt": True}, fx={"int": 1},
          follow=[later(6410, 2)], min_age=22)
    _leaf(add, 6403, "你向龙的旧债主买路：一张不平等的草约，墨还没干。",
          attrs=ge("cha", 9), set={"dragon_hunt": True}, fx={"cha": 1, "gold": -3},
          follow=[later(6410, 2)], min_age=22)
    _fail(add, 6404, "你把鳞片扔进井。井水响了一夜。你没有上山。山上的东西也没有下来——这一年。",
          fx={"wis": 1, "cha": -1}, follow=[later(6405, 8)], min_age=22)
    _leaf(add, 6405, "邻乡被烧过一回。有人说那是龙，有人说那是你扔掉的决定。",
          fx={"wis": 1, "con": 1}, min_age=30)

    _gate(add, 6410, "巢在眼前。空气像铁水。你可以谈、可以打、可以偷一枚还在跳的蛋。",
          (6411, 6412, 6413, 6414), [{"dragon_hunt": True}], min_age=24, set={"dragon_lair": True})
    _leaf(add, 6411, "你拔剑。龙睁眼，像睁开一座窑。",
          attrs=ge("str", 9), set={"dragon_duel": True}, fx={"str": 1, "con": -1},
          follow=[later(6420, 1)], min_age=24)
    _leaf(add, 6412, "你把剑放下。用喉咙里不是人的声音说话。龙的瞳孔缩成一条可谈判的缝。",
          attrs=ge("cha", 9), need=[{"skill_beast_speech": True}, {"job": "druid"}, {"job": "bard"}, {"dragon_scar": True}],
          set={"dragon_talk": True}, fx={"cha": 1, "wis": 1}, follow=[later(6420, 1)], min_age=24)
    _leaf(add, 6413, "你摸向那枚蛋。蛋的心跳比你的鼓。",
          attrs=ge("agi", 9), set={"dragon_egg": True}, fx={"agi": 1},
          follow=[later(6420, 1)], min_age=24)
    _fail(add, 6414, "你在窑口转身。龙没有追。它追的是以后那些更饿的人。你活着，传说停在山脚。",
          fx={"wis": 1, "cha": -1, "con": 1}, follow=[later(6415, 5)], min_age=24)
    _leaf(add, 6415, "有猎龙的人来问路。你指了相反的方向，又为这指法喝了一夜。",
          fx={"wis": 1}, min_age=29)

    _gate(add, 6420, "龙把翅膀张开。天黑了一半。这一次必须有结局。",
          (6421, 6422, 6423, 6424, 6425, 9204), [{"dragon_lair": True}], min_age=25)
    _win(add, 6421, "你斩下它。头落地的声音像一座庙倒塌。征服写在血里，也写在你从此睡不着的夜里。",
         "ach_dragon", attrs=ge("str", 11), need=[{"dragon_duel": True}],
         set={"dragon_slain": True, "map_under": True}, fx={"str": 2, "cha": 1, "gold": 12},
         mutex=DRAGON_ALLY, follow=[later(6426, 6), later(6450, 5)], min_age=25)
    _win(add, 6422, "它答应当你的坐骑、或你的债主。不平等条约上，人的名字比较小，人还活着。",
         "ach_dragon", attrs=ge("cha", 11), need=[{"dragon_talk": True}],
         set={"dragon_allied": True, "spared_foe": True, "true_name_known": True},
         fx={"cha": 2, "wis": 1}, mutex=DRAGON_SLAY, follow=[later(6426, 6), later(6450, 4)], min_age=25)
    _win(add, 6423, "你用金币买来百年不犯乡。龙把钱吞下去，像吞一句脏话。乡还在。",
         "ach_dragon", attrs=ge("gold", 14),
         set={"dragon_bought": True, "dragon_pact": True, "spared_foe": True},
         fx={"gold": -12, "wis": 1, "cha": 1}, mutex=DRAGON_SLAY,
         follow=[later(6426, 6)], min_age=25, wmod=[w_attr("gold", 14, 2, 0.2)])
    _win(add, 6424, "蛋在你怀里冷却成契约。龙用一句话认你：小偷，也是监护人。",
         "ach_dragon", attrs=ge("agi", 11), need=[{"dragon_egg": True}],
         set={"dragon_pact": True, "spared_foe": True}, fx={"agi": 1, "wis": 1, "cha": 1},
         mutex=DRAGON_SLAY, follow=[later(6426, 6), later(6450, 5)], min_age=25)
    _fail(add, 6425, "你败了，却被吐出来。龙息在你身上留下一张永不褪的伤疤。伤疤是通行证，也是拒绝。",
          set={"dragon_scar": True, "dragon_failed": True}, fx={"con": -2, "cha": -1, "wis": 1, "str": 1},
          follow=[later(6427, 5)], min_age=25)
    _die(add, 9204, "火焰覆盖巢和你。鳞片那一桌汗，原来是提前举行的葬礼。",
         attrs=lt_map(str=11, cha=11, gold=14, agi=11), min_age=25)
    _leaf(add, 6426, "有人问龙是否真的。你把伤疤或契约或金库的空位给他们看。他们改问别的。",
          need=[{"ach_dragon": True}], fx={"cha": 1, "wis": 1}, min_age=31)
    _leaf(add, 6427, "雨落在伤疤上会响。响声提醒你：有些山你还可以再上，只是腿先不同意。",
          need=[{"dragon_failed": True}], fx={"con": 1, "wis": 1}, min_age=30)


def _dragon_flight(ctx) -> None:
    add = ctx["add"]
    _nat(add, 6450, "王都在翼下像一盘没冷却的棋。箭塔抬头。龙问你：飞过去，还是绕。",
         (6451, 6452, 6453, 6454, 6455), 26, 60, weight=4, group="ach_dragon",
         extra={"naturalUnlock": False})
    _leaf(add, 6451, "你公然从王城上空过。箭雨像倒开的酒。酒没有碰到鳞。",
          attrs=ge("cha", 10), need=[{"dragon_allied": True}, {"dragon_pact": True}],
          set={"flight_open": True}, fx={"cha": 1, "agi": 1}, follow=[later(6460, 0)], min_age=26)
    _leaf(add, 6452, "你夜飞，只留下一片鳞在宫檐。清晨有人把它当成神谕，有人当成挑衅。",
          attrs=ge("agi", 10), need=[{"dragon_allied": True}, {"skill_shadow_hide": True}, {"item_shadow_cloak": True}],
          set={"flight_open": True}, fx={"agi": 1, "wis": 1}, follow=[later(6460, 0)], min_age=26)
    _leaf(add, 6453, "国王下请帖。请帖比箭软。你从正门的天空进去。",
          attrs=ge("cha", 9), need=[{"royal_favor": True}, {"crowned": True}, {"ach_king": True}, {"ach_regent": True}],
          set={"flight_open": True}, fx={"cha": 1, "gold": 2}, follow=[later(6460, 0)], min_age=26)
    _leaf(add, 6454, "你没有龙可骑。你用龙骨和帆布造了一具滑翔的骨架。智者说那是疯。风说可以试试。",
          attrs=ge("int", 11), need=[{"dragon_slain": True}],
          set={"flight_open": True, "flight_bone": True}, fx={"int": 1, "con": -1},
          follow=[later(6460, 0)], min_age=26)
    _fail(add, 6455, "箭塔把你赶下云。飞没有完成。王都仍只相信马。",
          fx={"cha": -1, "wis": 1, "con": 1}, follow=[later(6456, 5)], min_age=26)
    _leaf(add, 6456, "有人把你的没飞成写成谨慎。谨慎比箭轻，比传说假。",
          fx={"wis": 1}, min_age=31)

    _gate(add, 6460, "箭雨最密的那段天空只有一息。一息决定你是传说还是靶子。",
          (6461, 6462, 6463, 6465, 9205), [{"flight_open": True}], min_age=26)
    _win(add, 6461, "你飞过王都，没有被射下来。城在底下改口：那不是入侵，那是天气。",
         "ach_dragon_flight", attrs=ge("agi", 10), fx={"agi": 1, "cha": 2},
         follow=[later(6464, 6)], min_age=26)
    _win(add, 6462, "你把翅膀收成一次鞠躬。箭手放下弦。鞠躬比盔甲硬。",
         "ach_dragon_flight", attrs=ge("cha", 11), fx={"cha": 2, "wis": 1},
         follow=[later(6464, 6)], min_age=26)
    _win(add, 6463, "骨架在箭雨里叫。你让它叫完，仍落在宫门外，像一封不会燃烧的信。",
         "ach_dragon_flight", attrs=ge("int", 11), need=[{"flight_bone": True}],
         fx={"int": 1, "con": 1, "cha": 1}, follow=[later(6464, 6)], min_age=26)
    _fail(add, 6465, "箭擦过翼。你改高度，改成绕城。绕城不是飞过。王都仍只看见云。",
          fx={"con": -1, "cha": -1, "wis": 1}, follow=[later(6456, 4)], min_age=26)
    _die(add, 9205, "箭比传说快。王都第一次射落了一阵风。风里有你。",
         attrs=lt_map(agi=10, cha=11, int=11), min_age=26)
    _leaf(add, 6464, "有小孩用木板绑胳膊学飞。你没有阻止。阻止比摔跤更伤。",
          need=[{"ach_dragon_flight": True}], fx={"wis": 1}, min_age=32)


def _sea_serpent(ctx) -> None:
    add = ctx["add"]
    _nat(add, 6500, "真正的航线要船，不是折叠的玩具。海图在空白处画了一圈牙印。",
         (6501, 6502, 6503, 6504), 20, 50, weight=3, group="ach_sea")
    _leaf(add, 6501, "你募来一艘会挨咬的船。船名又长又硬，像一句不肯沉的咒。",
          attrs=ge("gold", 10),           set={"sea_route": True, "map_sea": True}, fx={"gold": -8, "con": 1},
          follow=[later(6510, 2), later(6560, 8)], min_age=20, wmod=[w_attr("gold", 10, 2, 0.2)])
    _leaf(add, 6502, "星盘把牙印读成航向。星星不保证回来，只保证去。",
          attrs=ge("int", 9), need=[{"item_star_astrolabe": True}, {"job": "ranger"}, {"job": "wizard"}],
          set={"sea_route": True, "map_sea": True}, fx={"int": 1}, follow=[later(6510, 2), later(6560, 8)], min_age=20)
    _leaf(add, 6503, "海神的名在你舌上发咸。浪让开一尺。一尺够龙骨。",
          attrs=ge("wis", 9), need=[{"patron_god": "sea"}, {"faith": True}, {"skill_water_walk": True}],
          set={"sea_route": True, "map_sea": True}, fx={"wis": 1, "con": 1},
          follow=[later(6510, 2), later(6560, 8)], min_age=20)
    _fail(add, 6504, "你没有出海。牙印在图上自己淡了。淡不是平安，是你被海忘了。",
          fx={"wis": 1}, follow=[later(6505, 6)], min_age=20)
    _leaf(add, 6505, "港口的人把巨蛇讲成儿歌。儿歌里没有你。你把儿歌听完。",
          fx={"wis": 1}, min_age=26)

    _gate(add, 6510, "风暴年。蛇从浪里露出比船更旧的一节。",
          (6511, 6512, 6513, 6514, 9206), [{"sea_route": True}], min_age=22)
    _win(add, 6511, "你把标枪送进它的眼。海在那一刻安静，像给猎人让路。蛇沉下去，航路浮上来。",
         "ach_sea_serpent", attrs=ge("str", 10), fx={"str": 1, "cha": 1, "gold": 6},
         follow=[later(6515, 6), later(6560, 3)], min_age=22)
    _win(add, 6512, "你用亡者的硬币买路。蛇把硬币含走，把船留下。深海的税吏比国王好说话。",
         "ach_sea_serpent", attrs=ge("wis", 10), need=[{"item_dead_coin": True}, {"patron_god": "death"}, {"job": "warlock"}],
         set={"spared_foe": True}, fx={"wis": 2, "gold": -2}, follow=[later(6515, 6), later(6560, 3)], min_age=22)
    _win(add, 6513, "你唱安眠曲。它沉回深海。你在那一处立灯塔：让后来的人怕，也让他们看见。",
         "ach_sea_serpent", attrs=ge("cha", 10), need=[{"skill_lullaby": True}, {"job": "bard"}, {"skill_beast_speech": True}],
         set={"spared_foe": True, "serpent_sleep": True}, fx={"cha": 2, "wis": 1},
         follow=[later(6515, 6), later(6560, 3)], min_age=22)
    _fail(add, 6514, "船裂了。你被别的船捞起。蛇还在。航线变成别人的牙印。",
          set={"sea_route": None}, fx={"con": -2, "gold": -4, "wis": 1}, follow=[later(6516, 5)], min_age=22)
    _die(add, 9206, "海把你连同船名一起收走。牙印在图上合拢。",
         attrs=lt_map(str=10, wis=10, cha=10), min_age=22)
    _leaf(add, 6515, "灯塔或鳞骨被画进海图。画师问蛇的眼睛什么颜色。你说：像欠债。",
          need=[{"ach_sea_serpent": True}], fx={"wis": 1, "cha": 1}, min_age=28)
    _leaf(add, 6516, "你怕水。洗澡时也怕。怕是一种还活着的航线。",
          fx={"con": 1, "wis": 1}, min_age=27)


def _phoenix(ctx) -> None:
    add, job_req = ctx["add"], ctx["job_req"]
    _nat(add, 6530, "凤凰羽毛在匣中自己发热。真凤凰要你先死一回，或装死一回。",
         (6531, 6532), 22, 55, weight=3, group="ach_phoenix",
         need=[{"item_phoenix_feather": True}, {"patron_god": "sun"}, {"patron_god": "fire"}])
    _leaf(add, 6531, "你收下热。热进到骨头里，像一封无法退回的请柬。",
          set={"phoenix_ash": True}, fx={"con": -1, "wis": 1}, follow=[later(6540, 2)], min_age=22)
    _fail(add, 6532, "你把匣子送回神殿。羽毛冷了。有些重生不邀请胆小鬼，也不邀请聪明人。",
          fx={"wis": 1, "gold": 2}, follow=[later(6533, 6)], min_age=22)
    _leaf(add, 6533, "神殿把羽毛陈列起来。说明牌写：未使用。未使用有时比使用更像结局。",
          fx={"wis": 1}, min_age=28)

    _gate(add, 6540, "火要验你。验过的人要么托着一只雏鸟，要么自己变成灰。",
          (6541, 6542, 6543, 6544, 9207), [{"phoenix_ash": True}], min_age=24)
    _win(add, 6541, "你用肉身挨过火。掌心裂开，裂开处有一只湿的、骂人的雏鸟。",
         "ach_phoenix", attrs=ge("con", 11), fx={"con": 2, "cha": 1, "wis": 1},
         follow=[later(6545, 7)], min_age=24)
    _win(add, 6542, "你装死。火焰以为验完了。你在灰里睁眼，把雏鸟从死亡的表格上偷走。",
         "ach_phoenix", attrs=ge("int", 10),
         need=[{"skill_feign_death": True}, {"item_upside_glass": True}] + job_req("rogue", "monk", "warlock", "bard"),
         fx={"int": 1, "agi": 1, "wis": 1}, follow=[later(6545, 7)], min_age=24)
    _win(add, 6543, "你用疗伤的光接住掉下来的那一团火。火在光里变成鸟。鸟在你掌心骂你多事。",
         "ach_phoenix", attrs=ge("wis", 10),
         need=[{"skill_heal": True}, {"skill_holy_light": True}] + job_req("cleric", "paladin", "druid"),
         fx={"wis": 2, "cha": 1}, follow=[later(6545, 7)], min_age=24)
    _fail(add, 6544, "你在最后一步跳出火圈。眉毛没了，凤凰也没了。热还在骨头里，找不到出口。",
          set={"phoenix_ash": None}, fx={"con": -1, "cha": -1, "wis": 1}, follow=[later(6546, 5)], min_age=24)
    _die(add, 9207, "火把你当成合格的燃料。雏鸟没有来。合格有时就是结束。",
         attrs=lt_map(con=11, int=10, wis=10), min_age=24)
    _leaf(add, 6545, "雏鸟长大后不再骂你。它只在你发烧时回来，像来收一笔它自己欠的热。",
          need=[{"ach_phoenix": True}], fx={"con": 1, "wis": 1}, min_age=31)
    _leaf(add, 6546, "你怕炉火。有人笑。你让他们笑。笑比复述那一夜便宜。",
          fx={"wis": 1}, min_age=29)


def _new_world(ctx) -> None:
    add = ctx["add"]
    _nat(add, 6560, "海的牙印西边还有空白。空白不是没有，是还没有人活着回来讲述。",
         (6561, 6562, 6563), 24, 55, weight=4, group="ach_sea", extra={"naturalUnlock": False})
    _leaf(add, 6561, "你下令继续西。水手骂你。骂声被风吹成号子。",
          attrs=ge("cha", 8), set={"new_world_sail": True}, fx={"cha": 1, "con": 1},
          follow=[later(6570, 2)], min_age=24)
    _leaf(add, 6562, "你把无尽粮袋和星盘钉在同一张桌上。桌不保证陆地，只保证晚饭。",
          need=[{"item_endless_sack": True}, {"item_star_astrolabe": True}, {"item_path_compass": True}],
          set={"new_world_sail": True}, fx={"int": 1}, follow=[later(6570, 2)], min_age=24)
    _fail(add, 6563, "你在蛇的残骸边下令返航。新大陆继续当空白。空白很安全。",
          fx={"wis": 1, "gold": 2}, follow=[later(6564, 5)], min_age=24)
    _leaf(add, 6564, "有年轻船长来问西边。你给他一张只画到牙印的图。图的边缘写：够了。",
          fx={"wis": 1}, min_age=29)

    _gate(add, 6570, "登陆。土是红的。返航的风暴已经在东边排队。",
          (6571, 6572, 6573, 6574, 9208), [{"new_world_sail": True}], min_age=26)
    _win(add, 6571, "你把能用的图画回来。王都的人骂你撒谎，直到第一棵异种种子发芽。",
         "ach_new_world", attrs=ge("int", 10), set={"map_new": True}, fx={"int": 2, "wis": 1, "cha": 1},
         follow=[later(6575, 6)], min_age=26)
    _win(add, 6572, "你带回一株还活着的植物。它在船上喝淡水像喝诗。诗比金币难养。",
         "ach_new_world", attrs=ge("wis", 10), set={"map_new": True}, fx={"wis": 2, "con": 1},
         follow=[later(6575, 6)], min_age=26)
    _win(add, 6573, "你把一位愿意来的使者活着带到王都。使者不会你们的话，会你们的沉默。",
         "ach_new_world", attrs=ge("cha", 10), set={"map_new": True, "spared_foe": True, "true_name_known": True},
         fx={"cha": 2, "wis": 1}, follow=[later(6575, 6)], min_age=26)
    _fail(add, 6574, "返航风暴把图、植物和使者都拿走。你被冲回旧港口。嘴里有新土的味道，手里什么都没有。",
          set={"map_new": True}, fx={"con": -2, "cha": -1, "wis": 1}, follow=[later(6576, 5)], min_age=26)
    _die(add, 9208, "空白把讲述者留下。新大陆有了第一座没有碑的坟。",
         attrs=lt_map(int=10, wis=10, cha=10), min_age=26)
    _leaf(add, 6575, "有人把你的航行写成发现。你改成相遇。出版社把相遇改回发现。",
          need=[{"ach_new_world": True}], fx={"wis": 1, "int": 1}, min_age=32)
    _leaf(add, 6576, "你在梦里还在画那张丢了的图。醒来时枕头是湿的，不是海水。",
          fx={"wis": 1}, min_age=31)


def _world_map(ctx) -> None:
    add = ctx["add"]
    _nat(add, 6580, "你把半生的图铺开。有些空白被涂成未知，有些仍被偷懒写成没有。",
         (6581, 6589, 6590, 6583), 28, 70, weight=4, group="ach_map", extra={"maxTriggers": 3, "cooldownMinInterval": 10})
    _nat(add, 6586, "鲸骨路通向没有名字的冰。指南针在这里只负责发抖。",
         (6587, 6588), 22, 50, weight=3, group="ach_map")
    _leaf(add, 6587, "你把极地画成一圈拒绝融化的问号。问号是一种诚实。",
          attrs=ge("con", 9), set={"map_north": True}, fx={"con": 1, "int": 1}, min_age=22)
    _fail(add, 6588, "你在冻伤前掉头。南风欢迎你。北极继续当没有。",
          fx={"wis": 1, "con": 1}, min_age=22)
    _win(add, 6581, "你把完成的世界图献给王室。空白被涂成未知，挂在比墙更难看的那面墙上。",
         "ach_world_map",
         need=[{"map_north": True, "map_under": True, "map_sea": True, "map_new": True}],
         fx={"int": 2, "wis": 1, "cha": 1, "gold": 4}, follow=[later(6584, 5)], min_age=28, weight=18)
    _win(add, 6589, "知识神殿借走抄本。他们把未知描金，你让他们改回铅笔。铅笔是一种虔诚。",
         "ach_world_map",
         need=[{"map_north": True, "map_under": True, "map_sea": True, "map_new": True, "faith": True},
               {"map_north": True, "map_under": True, "map_sea": True, "map_new": True, "patron_god": "knowledge"}],
         fx={"int": 2, "wis": 2}, follow=[later(6584, 5)], min_age=28, weight=16)
    _win(add, 6590, "你把图刻在故乡墙上。墙比王室近。小孩用手指描未知，像描一条还没走的路。",
         "ach_world_map",
         need=[{"map_north": True, "map_under": True, "map_sea": True, "map_new": True, "home_held": True},
               {"map_north": True, "map_under": True, "map_sea": True, "map_new": True, "free_city": True}],
         fx={"int": 1, "wis": 1, "cha": 1}, follow=[later(6584, 5)], min_age=28, weight=16)
    _fail(add, 6583, "还缺一域。你是旅行家，不是把世界画完的人。你把缺角朝外，免得自己骗自己。",
          fx={"wis": 1, "int": 1}, follow=[later(6585, 8)], min_age=28)
    _leaf(add, 6584, "知识神殿来借抄本。他们把未知描得更金。你让他们把金改回铅笔。",
          need=[{"ach_world_map": True}], fx={"int": 1, "wis": 1}, min_age=33)
    _leaf(add, 6585, "缺角那一域后来被别人填了。署名不是你。你请填的人喝酒，酒里没有醋。",
          fx={"wis": 1, "cha": 1}, min_age=36)


def _well_lord(ctx) -> None:
    add = ctx["add"]
    _nat(add, 6600, "黑井还认得你的鞋。这一次你不是来活着出去，是来让它听你的。",
         (6601, 6602, 6603), 28, 60, weight=3, group="ach_well",
         need=[{"dungeon_cleared": True}])
    _leaf(add, 6601, "你再下去。把规矩刻在第三层的门上：先敲门，再流血。",
          attrs=ge("int", 9), set={"well_return": True}, fx={"int": 1, "wis": 1},
          follow=[later(6610, 2)], min_age=28)
    _leaf(add, 6602, "你把守门的东西叫醒，问它想不想换一份工。它考虑得很慢，像地质。",
          attrs=ge("cha", 9), set={"well_return": True}, fx={"cha": 1},
          follow=[later(6610, 2)], min_age=28)
    _fail(add, 6603, "你在井口停住。活着出来已经够贵。做主人更贵。你把鞋上的泥磕掉。",
          fx={"wis": 1, "gold": 2}, follow=[later(6604, 6)], min_age=28)
    _leaf(add, 6604, "有人拿着你的旧地图问第四页。你仍说：别走。说的人自己也没有再走。",
          fx={"wis": 1}, min_age=34)

    _gate(add, 6610, "底厅的东西睁眼。钥匙在它枕头下，王冠在你的口气里。",
          (6611, 6612, 6613, 6614, 9209), [{"well_return": True}], min_age=30)
    _win(add, 6611, "你杀掉守门者。井承认新的主人。灰尘当你的旗帜，旗帜当灰尘。",
         "ach_well_lord", attrs=ge("str", 10), set={"well_claimed": True, "map_under": True},
         fx={"str": 1, "int": 1, "gold": 8}, follow=[later(6615, 7)], min_age=30)
    _win(add, 6612, "你对睡着的东西说话。它把钥匙和规矩一起交给你。井开始用你的声音回答回声。",
         "ach_well_lord", attrs=ge("cha", 10), set={"well_claimed": True, "spared_foe": True, "map_under": True},
         fx={"cha": 2, "wis": 1}, follow=[later(6615, 7)], min_age=30)
    _win(add, 6613, "你把井租给公会。租金是每年少死三个学徒。合同比王冠俗，也比王冠长。",
         "ach_well_lord", attrs=ge("int", 10), need=[{"in_guild": True}, {"guild_settled": True}, {"guild_trusted": True}],
         set={"well_claimed": True, "map_under": True}, fx={"int": 1, "gold": 6, "wis": 1},
         follow=[later(6615, 7)], min_age=30)
    _fail(add, 6614, "井把你吐回第一层。规矩没刻上。你仍是那个活着出来过的人，不是主人。",
          fx={"con": -1, "cha": -1, "wis": 1}, follow=[later(6616, 5)], min_age=30)
    _die(add, 9209, "底厅需要一个新枕头。这一次它选了你的名字。",
         attrs=lt_map(str=10, cha=10, int=10), min_age=30)
    _leaf(add, 6615, "有学徒在井口喊你的封号。封号回声回来时多了几个你没准的字。",
          need=[{"ach_well_lord": True}], fx={"cha": 1, "wis": 1}, min_age=37)
    _leaf(add, 6616, "你路过井盖。井盖上有别人的新刻痕。你没有蹲下去读。",
          fx={"wis": 1}, min_age=35)


def _close_gate(ctx) -> None:
    add = ctx["add"]
    _nat(add, 6630, "传送门不再只开三秒。缝里有风，风里有不该有的语法。门要人决定：关上，或成为铰链。",
         (6631, 6632, 6633, 6634), 26, 60, weight=3, group="ach_gate")
    _leaf(add, 6631, "你认出这是裂开。你留下记号，准备法阵。",
          attrs=ge("int", 9), set={"abyss_open": True}, fx={"int": 1},
          follow=[later(6640, 2)], min_age=26)
    _leaf(add, 6632, "你把无名骨灰洒在缝上。骨灰自己站成一行字：还不够。",
          need=[{"item_nameless_ash": True}, {"item_black_candle": True}],
          set={"abyss_open": True}, fx={"wis": 1}, follow=[later(6640, 2)], min_age=26)
    _leaf(add, 6633, "龙的尸体或活口都可以塞门。你开始计算尺寸。",
          need=[{"dragon_slain": True}, {"dragon_allied": True}],
          set={"abyss_open": True, "gate_dragon": True}, fx={"str": 1}, follow=[later(6640, 2)], min_age=26)
    _fail(add, 6634, "你叫人用木板钉上。木板在夜里变成芽。你改去睡得远一点。门继续开。",
          fx={"wis": 1, "con": -1}, follow=[later(6635, 6)], min_age=26)
    _leaf(add, 6635, "有村庄从地图上滑走。滑走的方式像被一句话删掉。你没有追上那句话。",
          fx={"wis": 1, "int": 1}, min_age=32)

    _gate(add, 6640, "门完全裂开。另一侧有东西在学你的名字发音。",
          (6641, 6642, 6643, 6644, 9210), [{"abyss_open": True}], min_age=28)
    _win(add, 6641, "法阵封闭。门缝变成一条普通的疤。疤会痒，不再说话。",
         "ach_close_gate", attrs=ge("int", 11), set={"gate_closed": True},
         fx={"int": 2, "wis": 1}, mutex=(6642,), follow=[later(6645, 7)], min_age=28)
    _win(add, 6642, "你用自己当铰链。门合上，你还站在边上。加冕与远航从此对你关着，门对世界关着。",
         "ach_close_gate", attrs=ge("con", 11),
         set={"abyss_hinge": True, "crowned": False}, fx={"con": 2, "wis": 1, "cha": -1, "gold": -5},
         mutex=(6641, 6643), follow=[later(6646, 4)], min_age=28)
    _win(add, 6643, "你把龙塞进门里。门满意地噎住。龙是否满意，门没有翻译。",
         "ach_close_gate", attrs=ge("str", 10), need=[{"gate_dragon": True}],
         set={"gate_closed": True}, fx={"str": 1, "wis": 1, "cha": 1}, mutex=(6642,),
         follow=[later(6645, 7)], min_age=28)
    _fail(add, 6644, "门没有关。你跑了。名字的发音在另一侧越来越像你。你开始少应人。",
          set={"false_name": True}, fx={"cha": -2, "wis": 1, "int": 1}, follow=[later(6647, 5)], min_age=28)
    _die(add, 9210, "另一侧先学会了你的全名。全名被叫走的人，这边只剩下衣服。",
         attrs=lt_map(int=11, con=11, str=10), min_age=28)
    _leaf(add, 6645, "有法师来量那条疤。量完说：普通。普通是你听过最昂贵的赞美。",
          need=[{"ach_close_gate": True, "abyss_hinge": False}], fx={"int": 1, "wis": 1}, min_age=35)
    _leaf(add, 6646, "你不能远航，不能加冕。你能站。站着的人把世界的门按住。风从你袖口走过。",
          need=[{"abyss_hinge": True}], fx={"con": 1, "wis": 2}, min_age=32)
    _leaf(add, 6647, "有人喊你的旧名。你回头慢了半拍。半拍里你确认自己还在这边。",
          need=[{"false_name": True}], fx={"wis": 1, "con": 1}, min_age=33)


def _lich(ctx) -> None:
    add, job_req = ctx["add"], ctx["job_req"]
    _nat(add, 6660, "亡灵低语说：把心放进盒子，名字可以留下。也可以都不留。",
         (6661, 6662, 6663), 30, 70, weight=3, group="ach_lich")
    _leaf(add, 6661, "你开始自愿转化。镜子先反对，骨灰后赞成。",
          attrs=ge("int", 9),
          need=job_req("warlock", "wizard", "cleric") + [{"item_nameless_ash": True}, {"skill_dead_whisper": True}],
          set={"lich_path": True}, fx={"int": 1, "con": -1}, follow=[later(6670, 3)], min_age=30)
    _leaf(add, 6662, "诅咒替你决定。你抢记忆水晶，准备在名字被删前把它抄下来。",
          need=[{"cursed_ring": True}, {"cursed_moon": True}, {"item_memory_crystal": True}],
          set={"lich_path": True, "lich_curse": True}, fx={"wis": 1, "int": 1},
          follow=[later(6670, 3)], min_age=30)
    _fail(add, 6663, "你把盒子砸了。低语改去找别人。你的心跳暂时仍是自己的。",
          fx={"wis": 1, "con": 1}, follow=[later(6664, 6)], min_age=30)
    _leaf(add, 6664, "墓园的土还认识你的体温。你把这当成恭维，也当成警告。",
          fx={"wis": 1}, min_age=36)

    _gate(add, 6670, "名字考验：在彻底冷掉之前，你要念出自己，且不能念成别人。",
          (6671, 6672, 6673, 9211), [{"lich_path": True}], min_age=33)
    _win(add, 6671, "你念对了。巫妖的壳里仍是那个会洗碗、会害怕的人。死亡神也许会因此多看一眼。",
         "ach_lich_named", attrs=ge("int", 11), set={"lich_named": True, "true_name_known": True},
         fx={"int": 2, "wis": 1, "con": -2, "cha": -1}, follow=[later(6674, 8)], min_age=33)
    _win(add, 6672, "水晶把你的乳名、骂名和假名一并灌回来。你挑选一个最像人的留下。",
         "ach_lich_named", attrs=ge("wis", 10), need=[{"lich_curse": True}, {"item_memory_crystal": True}],
         set={"lich_named": True, "true_name_known": True}, fx={"wis": 2, "int": 1, "con": -1},
         follow=[later(6674, 8)], min_age=33)
    _fail(add, 6673, "你念成了盒子上的编号。编号活着。人没有。有人把编号当成你，你无法反对。",
          set={"false_name": True, "lich_path": None}, fx={"cha": -3, "int": 1, "wis": -1},
          follow=[later(6675, 4)], min_age=33)
    _die(add, 9211, "名字先走。剩下的东西不记得该如何停下来，于是被圣武士停下来。",
         attrs=lt_map(int=11, wis=10), min_age=33)
    _leaf(add, 6674, "你在阳光下不融化。小孩问你是不是故事。你说：故事会结束，我还在洗碗。",
          need=[{"ach_lich_named": True}], fx={"wis": 1, "cha": 1}, min_age=41)
    _leaf(add, 6675, "有人按编号叫你。你应了。应完才发现自己把唯一的真名又让出去一寸。",
          need=[{"false_name": True}], fx={"wis": 1, "con": 1}, min_age=37)


def _meet_god(ctx) -> None:
    add, job_req = ctx["add"], ctx["job_req"]
    _nat(add, 6700, "祭坛后面的空气比前面厚。有东西把头转过来——还没有，只是准备转。",
         (6701, 6702, 6703, 6704, 6705), 24, 65, weight=3, group="ach_god")
    _leaf(add, 6701, "你把祭典做到没有一句错字。错字通常是人留下的门。你把门焊上。",
          attrs=ge("wis", 9), need=[{"faith": True}] + job_req("cleric", "paladin"),
          set={"god_rite": True}, fx={"wis": 1, "cha": 1}, follow=[later(6710, 3)], min_age=24)
    _leaf(add, 6702, "战神只要一场真胜。你把还在滴血的旗放上祭坛。旗比祷词诚实。",
          attrs=ge("str", 9), need=[{"ach_win_war": True}, {"war_won": True}, {"patron_god": "war"}, {"home_held": True}],
          set={"god_rite": True}, fx={"str": 1, "wis": 1}, follow=[later(6710, 3)], min_age=24)
    _leaf(add, 6703, "知识神要记忆水晶和一本不该打开的书。你都带来了。书在路上咬过你一口。",
          attrs=ge("int", 9),
          need=[{"item_memory_crystal": True}, {"patron_god": "knowledge"}, {"knows_old_tongue": True}],
          set={"god_rite": True}, fx={"int": 1}, follow=[later(6710, 3)], min_age=24)
    _leaf(add, 6704, "无信仰者走血祭和耳语面具。路更近，神更厌。",
          attrs=ge("con", 9), need=[{"item_whisper_mask": True}, {"skill_blood_rite": True}, {"item_dead_coin": True}],
          set={"god_rite": True, "god_wild": True}, fx={"con": 1, "wis": 1}, follow=[later(6710, 3)], min_age=24)
    _fail(add, 6705, "你在祭坛前跪下，又站起来。头没有转过来。香灰凉了。",
          fx={"wis": 1, "cha": -1}, follow=[later(6706, 6)], min_age=24)
    _leaf(add, 6706, "此后你仍祷告。祷告像对井说话。井有回声，没有脸。",
          fx={"wis": 1}, min_age=30)

    _gate(add, 6710, "神把头转过来。光或暗把你的影子按在地上，像按一枚印章。",
          (6711, 6712, 6713, 6714, 9212), [{"god_rite": True}], min_age=27)
    _win(add, 6711, "日、命运或自然从祭典里走出来，看了你一眼。一眼比一生的祷告响。",
         "ach_meet_god", attrs=ge("wis", 11), need=[{"god_wild": False, "faith": True}],
         set={"god_seen": True, "true_name_known": True}, fx={"wis": 2, "cha": 1},
         follow=[later(6715, 6)], min_age=27)
    _win(add, 6712, "死亡神收了你带来的硬币，又把硬币还给你：上面多了一张你尚未使用的脸。",
         "ach_meet_god", attrs=ge("int", 10),
         need=[{"patron_god": "death"}, {"item_dead_coin": True}, {"ach_lich_named": True}],
         set={"god_seen": True, "true_name_known": True}, fx={"int": 1, "wis": 2},
         follow=[later(6715, 6)], min_age=27)
    _win(add, 6713, "野神从血里抬头。它认得你，也厌你。觐见完成。教会的门从此对你关一寸。",
         "ach_meet_god", attrs=ge("con", 10), need=[{"god_wild": True}],
         set={"god_seen": True, "god_hated": True}, fx={"con": 1, "wis": 1, "cha": -2},
         follow=[later(6716, 5)], min_age=27)
    _fail(add, 6714, "神把脸转回去。你看见的只是自己的热望。热望冷却时像一次没有对象的失恋。",
          fx={"wis": 1, "cha": -1, "con": -1}, follow=[later(6717, 5)], min_age=27)
    _die(add, 9212, "凡人不该被完整地看见。你被看见了。看见结束了你。",
         attrs=lt_map(wis=11, int=10, con=10), min_age=27)
    _leaf(add, 6715, "此后祷告有回音。回音不一定答应，只是证明对面有耳朵。",
          need=[{"ach_meet_god": True, "god_hated": False}], fx={"wis": 1, "cha": 1}, min_age=33)
    _leaf(add, 6716, "神殿正门对你关得更严。侧门的香火仍收钱。你把钱放在侧门，像放在伤口上。",
          need=[{"god_hated": True}], fx={"wis": 1, "gold": -1}, min_age=32)
    _leaf(add, 6717, "你少看祭坛。祭坛并不因此少看你。只是双方都装作在看别处。",
          fx={"wis": 1}, min_age=32)


def _high_priest(ctx) -> None:
    add, job_req = ctx["add"], ctx["job_req"]
    _nat(add, 6730, "旧祭司的座位空了。空位发出和神殿一样的回声，问谁来坐。",
         (6731, 6732, 6733, 6734), 28, 65, weight=3, group="ach_faith",
         need=[{"faith": True, "god_hated": False}])
    _leaf(add, 6731, "你按律法走选举。票比香火臭，也比香火有效。",
          attrs=ge("cha", 9), set={"priest_run": True}, fx={"cha": 1, "wis": 1},
          follow=[later(6740, 3)], min_age=28)
    _leaf(add, 6732, "觐见过的人被神点名。点名不经过投票。投票的人改去投票给点名。",
          need=[{"god_seen": True}, {"ach_meet_god": True}],
          set={"priest_run": True, "priest_named": True}, fx={"wis": 1, "cha": 1},
          follow=[later(6740, 3)], min_age=28)
    _leaf(add, 6733, "你揭穿旧祭司的龙影教底子。柜子里的传单比圣物先被烧掉。",
          need=[{"cult_broken": True}, {"cult_reported": True}] + job_req("cleric", "paladin"),
          set={"priest_run": True}, fx={"int": 1, "wis": 1}, follow=[later(6740, 3)], min_age=28)
    _fail(add, 6734, "你没有去争。新祭司是别人。香火照旧。你的膝盖照旧。掌权与你无关。",
          fx={"wis": 1}, follow=[later(6735, 6)], min_age=28)
    _leaf(add, 6735, "新祭司请你讲一次旧规矩。你讲了。讲完你仍坐在侧殿。",
          fx={"wis": 1, "cha": 1}, min_age=34)

    _gate(add, 6740, "继任礼。权杖比你的胳膊沉。沉的是人，不是金子。",
          (6741, 6742, 6743, 6744), [{"priest_run": True, "god_hated": False}], min_age=31)
    _win(add, 6741, "正统选举把权杖交给你。你把它放在门边：先进来的人先摸到规矩。",
         "ach_high_priest", attrs=ge("cha", 10), set={"high_priest": True},
         fx={"cha": 2, "wis": 1, "gold": 3}, follow=[later(6745, 6)], min_age=31)
    _win(add, 6742, "神的点名被刻进石板。石板不认票数。你开始为点名负责。",
         "ach_high_priest", attrs=ge("wis", 11), need=[{"priest_named": True}],
         set={"high_priest": True}, fx={"wis": 2, "cha": 1}, follow=[later(6745, 6)], min_age=31)
    _win(add, 6743, "魔契师走渗透。你把旧教的根挖出来，自己坐上去。坐着的人脏，根没有了。",
         "ach_high_priest", attrs=ge("int", 10), need=[{"job": "warlock"}, {"cult_broken": True}],
         set={"high_priest": True, "war_dirty": True}, fx={"int": 1, "wis": 1, "cha": -1},
         follow=[later(6745, 6)], min_age=31)
    _fail(add, 6744, "继任被否。否决写得很礼貌。礼貌把你送回侧殿，侧殿把你送回膝盖。",
          fx={"cha": -1, "wis": 1}, follow=[later(6735, 4)], min_age=31)
    _leaf(add, 6745, "有人把你写成教会的实际掌权者。你改成：把门的人。门仍比你大。",
          need=[{"ach_high_priest": True}], fx={"wis": 1, "cha": 1}, min_age=37)


def _name_from_death(ctx) -> None:
    add = ctx["add"]
    _nat(add, 6760, "心跳漏拍之后，黑蜡烛自己燃了。有人在账本上找你的名字，准备划掉。",
         (6761, 6762, 6763, 6764), 40, 110, weight=4, group="ach_death",
         need=[{"failing_heart": True}, {"skill_feign_death": True}, {"item_black_candle": True}])
    _leaf(add, 6761, "你去找死神下棋。棋盘是你的肋骨。",
          attrs=ge("int", 9), set={"death_claim": True}, fx={"int": 1, "con": -1},
          follow=[later(6770, 1)], min_age=40)
    _leaf(add, 6762, "你把倒吊沙漏拧紧，想偷一年。沙子往上走，像不同意。",
          need=[{"item_upside_glass": True}], set={"death_claim": True}, fx={"wis": 1},
          follow=[later(6770, 1)], min_age=40)
    _leaf(add, 6763, "你装死。死神若填错表，冬天就还你。",
          need=[{"skill_feign_death": True}], set={"death_claim": True}, fx={"agi": 1, "int": 1},
          follow=[later(6770, 1)], min_age=40)
    _fail(add, 6764, "你把蜡烛掐灭。账本那一页暂时不划，只是更皱。皱不是赦免。",
          fx={"con": -1, "wis": 1}, follow=[later(6765, 4)], min_age=40)
    _leaf(add, 6765, "漏拍还在。你学会在漏拍里数数。数到后来，数本身也像祷告。",
          fx={"con": 1, "wis": 1}, min_age=44)

    _gate(add, 6770, "死神用笔尖点着你的名字。点着的地方发冷。",
          (6771, 6772, 6773, 6774, 9213), [{"death_claim": True}], min_age=40)
    _win(add, 6771, "你赢了那盘棋。死神把名字从即将一栏挪回暂缓。冬天因此多了一个还喘气的人。",
         "ach_name_from_death", attrs=ge("int", 11), fx={"int": 2, "con": 1, "wis": 1},
         follow=[later(6775, 5)], min_age=40)
    _win(add, 6772, "沙漏偷来一年。一年很短，短得像一份写明日期的缓刑。",
         "ach_name_from_death", attrs=ge("wis", 10), need=[{"item_upside_glass": True}],
         fx={"wis": 2, "con": 1}, follow=[later(6775, 5)], min_age=40)
    _win(add, 6773, "表填错了。错把你写成已葬。你在葬礼上咳嗽。咳嗽把名字要了回来。",
         "ach_name_from_death", attrs=ge("agi", 10), need=[{"skill_feign_death": True}],
         set={"true_name_known": True}, fx={"agi": 1, "cha": 1, "wis": 1},
         follow=[later(6775, 5)], min_age=40)
    _fail(add, 6774, "死神摇头。你仍活过这个下午，没有活过这个约定。账本暂时不划，只折角。",
          fx={"con": -1, "wis": 1, "cha": -1}, follow=[later(6776, 3)], min_age=40)
    _die(add, 9213, "名字被划掉。划痕比心跳直。",
         attrs=lt_map(int=11, wis=10, agi=10), min_age=40)
    _leaf(add, 6775, "你多活的那个冬天特别长。长到你开始给别人的名字求情。求情很少成功。",
          need=[{"ach_name_from_death": True}], fx={"wis": 1, "cha": 1}, min_age=45)
    _leaf(add, 6776, "折角的账本在梦里打开。你把梦喝成凉水。凉水比墨诚实。",
          fx={"con": 1, "wis": 1}, min_age=43)


def _philosopher_stone(ctx) -> None:
    add = ctx["add"]
    _nat(add, 6780, "蒸馏器、炼金、水晶，再加一片龙鳞或一根凤凰毛。桌子开始像一座可能爆炸的神坛。",
         (6781, 6782, 6783), 28, 60, weight=3, group="ach_stone")
    _leaf(add, 6781, "你把材料配齐。配齐的声音像把锁舌推到位。",
          need=[{"item_alembic": True, "skill_alchemy": True}],
          set={"stone_ready": True}, fx={"int": 1}, follow=[later(6785, 2)], min_age=28)
    _leaf(add, 6782, "缺的那一味用龙鳞或凤凰毛补上。补上之后桌子更烫。",
          need=[{"item_dragon_scale": True}, {"item_phoenix_feather": True}, {"dragon_slain": True}, {"ach_phoenix": True}],
          set={"stone_ready": True}, fx={"wis": 1}, follow=[later(6785, 2)], min_age=28)
    _fail(add, 6783, "你把桌子拆了。可能爆炸的神坛变回普通的厨房。厨房里仍可以活。",
          fx={"wis": 1, "gold": 1}, follow=[later(6784, 5)], min_age=28)
    _leaf(add, 6784, "有炼金学徒来问配方。你给他一张做汤的方子。汤很鲜。",
          fx={"wis": 1, "cha": 1}, min_age=33)

    _gate(add, 6785, "三次失败的爆炸之后，第四次，石头成了。它在掌心像一颗不肯冷却的星。",
          (6786, 6787, 6788, 6789, 6791, 9214), [{"stone_ready": True}], min_age=30)
    _win(add, 6786, "你把贤者之石砸碎。碎光像一场拒绝举行的加冕。拒绝比炼成更难。",
         "ach_refuse_stone", attrs=ge("wis", 11), set={"stone_smashed": True},
         fx={"wis": 2, "int": 1, "cha": 1}, mutex=(6789,), follow=[later(6792, 6)], min_age=30)
    _win(add, 6787, "你把石头交给教会封存。封条比你的锁心更结实。你睡得着。",
         "ach_refuse_stone", attrs=ge("cha", 10), need=[{"faith": True}, {"ach_high_priest": True}, {"god_seen": True}],
         set={"stone_sealed": True}, fx={"wis": 1, "cha": 1}, mutex=(6789,),
         follow=[later(6792, 6)], min_age=30)
    _win(add, 6788, "你把石头换成全城的粮。粮车走了三天。有人骂你傻。傻让人活过冬天。",
         "ach_refuse_stone", attrs=ge("int", 10), fx={"gold": -2, "cha": 2, "wis": 1, "con": 1},
         mutex=(6789,), follow=[later(6792, 6)], min_age=30)
    _leaf(add, 6789, "你吞下石头。长生在舌上发苦。苦的是你不再需要冬天，冬天仍需要别人。",
          attrs=ge("con", 10), set={"stone_swallowed": True, "lich_path": True},
          fx={"con": 2, "int": 1, "wis": -1, "cha": -1}, mutex=(6786, 6787, 6788),
          follow=[later(6793, 4), later(6670, 6)], min_age=30)
    _fail(add, 6791, "第四次仍爆炸。桌子没了。你的眉毛没了。石头没有。你还在。",
          fx={"con": -2, "int": 1, "wis": 1}, follow=[later(6794, 5)], min_age=30)
    _die(add, 9214, "爆炸把炼金术士写进配方。配方不需要署名。",
         attrs=lt_map(wis=11, cha=10, int=10, con=10), min_age=30)
    _leaf(add, 6792, "有人问石头的味道。你说：像没做成的王。他们以为你在比喻。",
          need=[{"ach_refuse_stone": True}], fx={"wis": 1}, min_age=36)
    _leaf(add, 6793, "你不再饿。不饿的人很难和还饿的人坐在同一张桌边。你仍坐下。坐下很费力。",
          need=[{"stone_swallowed": True}], fx={"con": 1, "cha": -1, "wis": 1}, min_age=34)
    _leaf(add, 6794, "你改去煮汤。汤不会爆炸。有学徒因此活过了学徒期。",
          fx={"wis": 1, "con": 1}, min_age=35)


def _buy_peace(ctx) -> None:
    add = ctx["add"]
    _nat(add, 6800, "账房说：以你现在的钱，买下一场战争或买下它的停火，只差一个签字。",
         (6801, 6802, 6803, 6804), 28, 60, weight=3, group="ach_gold",
         extra={"requiredAttrs": ge("gold", 12)})
    _leaf(add, 6801, "你把粮和雇佣兵一起买成和约。和约上的墨比血贵，也比血少。",
          attrs=ge("gold", 14), set={"peace_gold": True}, fx={"gold": -10, "cha": 1},
          follow=[later(6810, 2)], min_age=28, wmod=[w_attr("gold", 14, 2, 0.2)])
    _leaf(add, 6802, "你把钱堆在敌王面前。他丢脸地接受。丢脸有时比战败便宜。",
          attrs=ge("cha", 10), set={"peace_gold": True}, fx={"gold": -8, "cha": 1},
          follow=[later(6810, 2)], min_age=28)
    _leaf(add, 6803, "你用钱去买战争的胜利。胜利很响。响声里没有和平这两个字。",
          attrs=ge("str", 8), set={"war_bought_victory": True}, fx={"gold": -10, "str": 1, "cha": 1},
          follow=[later(6815, 3)], min_age=28)
    _fail(add, 6804, "你没有签字。钱还在。战争按原价进行。原价是别人的命。",
          fx={"wis": 1, "gold": 1}, follow=[later(6805, 6)], min_age=28)
    _leaf(add, 6805, "账单上战争一项被划掉，改成丧葬。你把账本合上，合上比签字轻。",
          fx={"wis": 1}, min_age=34)

    _gate(add, 6810, "和约要在双方刀还没入鞘时生效。钱在桌上，刀在手边。",
          (6811, 6812, 6813, 6814), [{"peace_gold": True, "war_bought_victory": False, "ach_win_war": False}], min_age=30)
    _win(add, 6811, "粮车和佣兵的合同同时生效。战场空了。空是你买来的。",
         "ach_buy_peace", attrs=ge("gold", 12), fx={"gold": -4, "wis": 1, "cha": 2},
         follow=[later(6816, 6)], min_age=30, wmod=[w_attr("gold", 12, 2, 0.2)])
    _win(add, 6812, "敌王在金币面前低头。低头被画进史书的边栏，正文仍写他英明。你不争正文。",
         "ach_buy_peace", attrs=ge("cha", 11), fx={"cha": 2, "wis": 1}, follow=[later(6816, 6)], min_age=30)
    _win(add, 6813, "你把战俘全部赎回。赎回的名单比和约长。长名单是一种胜利。",
         "ach_buy_peace", attrs=ge("wis", 10), fx={"gold": -6, "wis": 2, "cha": 1},
         follow=[later(6816, 6)], min_age=30)
    _fail(add, 6814, "签字前有人把桌子掀了。钱撒了一地。刀先说话。和平没有买成，战争打了折。",
          set={"peace_gold": None}, fx={"gold": -5, "cha": -1, "con": -1, "wis": 1},
          follow=[later(6817, 4)], min_age=30)
    _leaf(add, 6815, "你买来的胜利被写成赢得战争。史官不问钱。钱不问你后悔。你没有点亮另一盏灯。",
          need=[{"war_bought_victory": True}],
          set={"ach_win_war": True, "war_won": True}, fx={"cha": 1, "wis": 1, "gold": 2}, min_age=31)
    _leaf(add, 6816, "有将军骂你用钱侮辱战争。你请他吃饭。饭桌上没有刀。没有刀是你买到的东西。",
          need=[{"ach_buy_peace": True}], fx={"wis": 1, "cha": 1}, min_age=36)
    _leaf(add, 6817, "折扣战争仍死人。你去收尸。收尸比签字脏，也比签字真。",
          fx={"con": 1, "wis": 1}, min_age=34)


def _return_relic(ctx) -> None:
    add, job_req = ctx["add"], ctx["job_req"]
    _nat(add, 6830, "神器在玻璃后面呼吸。盗是巅峰。还是把黑路烧掉。",
         (6831, 6832, 6833, 6834), 22, 50, weight=3, group="ach_thief")
    _leaf(add, 6831, "你用开锁与影藏把神器请出玻璃。玻璃没有叫。叫的是你的心跳。",
          attrs=ge("agi", 9),
          need=[{"skill_lockpick": True}, {"skill_shadow_hide": True}] + job_req("rogue"),
          set={"relic_stolen": True}, fx={"agi": 1}, follow=[later(6840, 1)], min_age=22)
    _leaf(add, 6832, "你用假身份走进正门。正门相信证件。证件是假的。神器是真的。",
          attrs=ge("int", 9), need=[{"item_fake_papers": True}, {"skill_disguise": True}, {"item_pardon": True}],
          set={"relic_stolen": True}, fx={"int": 1, "cha": 1}, follow=[later(6840, 1)], min_age=22)
    _leaf(add, 6833, "沙漏、圣徽或龙蛋，你选了最会叫的那一件。它在怀里像一只告密的心脏。",
          need=[{"item_upside_glass": True}, {"item_holy_water": True}, {"dragon_egg": True}],
          set={"relic_stolen": True}, fx={"wis": 1}, follow=[later(6840, 1)], min_age=22)
    _fail(add, 6834, "你在玻璃前停手。巅峰与你无关。你去喝汤。汤不会报警。",
          fx={"wis": 1, "gold": 1}, follow=[later(6835, 5)], min_age=22)
    _leaf(add, 6835, "神器仍在玻璃后面呼吸。你偶尔去看。看不是偷。看也很贵。",
          fx={"wis": 1}, min_age=27)

    _gate(add, 6840, "全城追缉。神器在你手里发烫。烫的是还，还是留下。",
          (6841, 6842, 6843, 6844, 6845, 9215), [{"relic_stolen": True}], min_age=23)
    _win(add, 6841, "你把神器还神殿。神父假装没看见你的夜行衣。神殿看见了你的手是空的。",
         "ach_return_relic", attrs=ge("wis", 10), set={"relic_stolen": None},
         fx={"wis": 2, "cha": 1}, follow=[later(6846, 6)], min_age=23)
    _win(add, 6842, "你把蛋还给龙。龙没有谢。龙把追缉的人吓退。吓退也是一种收据。",
         "ach_return_relic", attrs=ge("cha", 10), need=[{"dragon_lair": True}, {"dragon_allied": True}, {"dragon_egg": True}],
         set={"relic_stolen": None, "spared_foe": True}, fx={"cha": 1, "wis": 1},
         follow=[later(6846, 6)], min_age=23)
    _win(add, 6843, "你把神器还王。王的赦免比神的轻，比绞索重。你接了。",
         "ach_return_relic", attrs=ge("cha", 9),
         need=[{"royal_favor": True}, {"crowned": True}, {"item_pardon": True}],
         set={"relic_stolen": None}, fx={"cha": 1, "gold": 3, "wis": 1},
         follow=[later(6846, 6)], min_age=23)
    _fail(add, 6844, "你留下私用。能力涨了。神厌或龙仇也涨了。巅峰变成诅咒的另一种叫法。",
          set={"god_hated": True, "has_enemy_name": True}, fx={"int": 1, "str": 1, "cha": -2, "wis": -1},
          follow=[later(6847, 4)], min_age=23)
    _fail(add, 6845, "追缉把你按在街上。神器被夺回。你的手空了，黑路还在，只是没有巅峰。",
          set={"relic_stolen": None, "exiled": True, "false_name": True},
          fx={"agi": -1, "cha": -2, "wis": 1}, follow=[later(6848, 4)], min_age=23)
    _die(add, 9215, "守卫的箭比还快。神器滚回玻璃。玻璃重新呼吸。你没有。",
         attrs=lt_map(wis=10, cha=9, agi=8), min_age=23)
    _leaf(add, 6846, "黑路的人不再给你口令。你说谢谢。谢谢把路烧掉。",
          need=[{"ach_return_relic": True}], fx={"wis": 1, "cha": 1}, min_age=29)
    _leaf(add, 6847, "神器在私用里越来越像主人。你越来越像抽屉。抽屉会响。",
          need=[{"god_hated": True}], fx={"con": -1, "wis": 1}, min_age=27)
    _leaf(add, 6848, "流放路上你的手仍记得那件东西的温度。温度不是它，是你没还出去的那一下。",
          need=[{"exiled": True}], fx={"wis": 1, "con": 1}, min_age=27)


def _correct_epic(ctx) -> None:
    add = ctx["add"]
    _nat(add, 6900, "酒馆里有人把你的事唱成别人的，或把别人的事唱成你的。诗人在场。酒是见证。",
         (6901, 6902, 6903, 6904), 26, 70, weight=4, group="ach_epic")
    _win(add, 6901, "你亲口把唱错的句子改对。诗人当场改弦。史诗在你活着时第一次说人话。",
         "ach_correct_epic", attrs=ge("cha", 9),
         need=[{"ach_dragon": True}, {"ach_win_war": True}, {"ach_king": True}, {"ach_meet_god": True}, {"ach_hold_pass": True}],
         set={"true_name_known": True}, fx={"cha": 2, "wis": 1}, follow=[later(6905, 6)], min_age=26)
    _win(add, 6902, "徒弟站起来纠正。他的声音比你的硬。你没有拦。拦会把史诗再唱错。",
         "ach_correct_epic", need=[{"has_apprentice": True}, {"ach_apprentice_surpass": True}],
         set={"true_name_known": True}, fx={"wis": 2, "cha": 1}, follow=[later(6905, 6)], min_age=26)
    _win(add, 6903, "你把会说话的骷髅或龙或井的回声请来作证。证人没有心跳，有记忆。",
         "ach_correct_epic", attrs=ge("int", 9),
         need=[{"item_talking_skull": True}, {"dragon_allied": True}, {"well_claimed": True}],
         set={"true_name_known": True}, fx={"int": 1, "cha": 1, "wis": 1},
         follow=[later(6905, 6)], min_age=26)
    _fail(add, 6904, "你想骗一首史诗。诗人当场拆穿。酒馆笑你。笑比刀轻，比刀长久。",
          fx={"cha": -3, "wis": 1}, follow=[later(6906, 4)], min_age=26, weight=8)
    _leaf(add, 6905, "此后有人按你改过的版本唱。版本仍会走样。走样里至少有一次被你按住过。",
          need=[{"ach_correct_epic": True}], fx={"cha": 1, "wis": 1}, min_age=32)
    _leaf(add, 6906, "你再进酒馆时诗人换了题目。题目里没有你。没有你是一种仁慈。",
          fx={"wis": 1, "con": 1}, min_age=30)


def _apprentice(ctx) -> None:
    add = ctx["add"]
    _nat(add, 6920, "徒弟立了一功。功把你的名字盖住一寸。妒忌在夜里醒来，比功早。",
         (6921, 6922, 6923, 6924), 32, 70, weight=4, group="ach_master",
         need=[{"has_apprentice": True}])
    _leaf(add, 6921, "你公开祝贺，把主位让出半寸。半寸比剑难。",
          attrs=ge("wis", 9), set={"apprentice_blessed": True, "true_name_known": True},
          fx={"wis": 1, "cha": 1}, follow=[later(6930, 2)], min_age=32)
    _leaf(add, 6922, "你把佣兵团或权柄的钥匙递给他。钥匙烫手。烫的是你还想握住。",
          need=[{"company_yours": True}, {"ach_mercenary": True}, {"regent_done": True}, {"crowned": True}],
          set={"apprentice_blessed": True}, fx={"cha": 1, "wis": 1}, follow=[later(6930, 2)], min_age=32)
    _leaf(add, 6923, "妒忌让你想下令逐他，或更坏。你把这念头咬住，咬出血。",
          attrs=ge("con", 8), set={"apprentice_tempted": True}, fx={"con": 1, "wis": 1},
          follow=[later(6930, 2)], min_age=32)
    _fail(add, 6924, "你下手了，或把人放逐了。功还在世上。人不在你身边。妒忌饱了，名声裂了。",
          set={"has_apprentice": None, "apprentice_ruined": True}, fx={"cha": -2, "wis": -1, "str": 1},
          follow=[later(6925, 5)], min_age=32)
    _leaf(add, 6925, "有人按他的功来问你。你说：那是我教过的人。教过，不等于还在。",
          need=[{"apprentice_ruined": True}], fx={"wis": 1, "con": 1}, min_age=37)

    _gate(add, 6930, "妒忌年正式到来。他站在你面前，比你更像故事。你还可以选。",
          (6931, 6932, 6933, 6934),
          [{"apprentice_blessed": True}, {"apprentice_tempted": True}], min_age=34)
    _win(add, 6931, "你祝贺到底，让位到底。他超过你。你还活着，妒忌没有活过这一夜。",
         "ach_apprentice_surpass", attrs=ge("wis", 11), set={"true_name_known": True},
         fx={"wis": 2, "cha": 1}, follow=[later(6935, 6)], min_age=34)
    _win(add, 6932, "你在加冕或摄政的席上指定他为继承人。冠可以不给你，路可以给他。",
         "ach_apprentice_surpass", attrs=ge("cha", 10),
         need=[{"crowned": True}, {"regent_done": True}, {"ach_king": True}, {"ach_regent": True}],
         set={"true_name_known": True}, fx={"cha": 2, "wis": 1}, follow=[later(6935, 6)], min_age=34)
    _win(add, 6933, "你把兵团交给他。两年后他们还在赢。赢的人叫他队长，叫你老师。",
         "ach_apprentice_surpass", need=[{"ach_mercenary": True}, {"company_yours": True}],
         set={"true_name_known": True}, fx={"wis": 1, "cha": 1}, follow=[later(6935, 6)], min_age=34)
    _fail(add, 6934, "你还是在最后一刻把人赶走了。赶走比下手干净，脏的是你自己知道差在哪一刻。",
          set={"has_apprentice": None, "apprentice_ruined": True}, fx={"cha": -2, "wis": 1},
          follow=[later(6925, 4)], min_age=34)
    _leaf(add, 6935, "他回来看你时把功劳讲成运气。你让他讲。讲成运气是一种孝。",
          need=[{"ach_apprentice_surpass": True}], fx={"wis": 1, "cha": 1}, min_age=40)


def _stop_plague(ctx) -> None:
    add, job_req = ctx["add"], ctx["job_req"]
    _nat(add, 6940, "黑死斑从一家走到一城。这一次要停的不是你的腕，是城门里的呼吸。",
         (6941, 6942, 6943, 6944), 20, 70, weight=4, group="ach_plague",
         need=[{"plague": True}, {"sick": True}])
    _leaf(add, 6941, "你按智识隔离：井、巷、名单。名单比药苦。",
          attrs=ge("int", 9), set={"plague_plan": True}, fx={"int": 1, "wis": 1},
          follow=[later(6950, 2)], min_age=20)
    _leaf(add, 6942, "你用抗毒剂、疗伤术、德鲁伊的种子和开过的仓把城撑过第一波。",
          need=[{"item_antitoxin": True}, {"skill_heal": True}, {"item_druid_seed": True}, {"war_gave_grain": True}]
          + job_req("cleric", "druid"),
          set={"plague_plan": True}, fx={"wis": 1, "con": 1}, follow=[later(6950, 2)], min_age=20)
    _leaf(add, 6943, "你准备在第二波烧掉一区，保住三区。准备本身已经脏。",
          attrs=ge("wis", 8), set={"plague_plan": True, "plague_fire": True}, fx={"wis": 1, "cha": -1},
          follow=[later(6950, 2)], min_age=20)
    _fail(add, 6944, "你只顾自己的腕。城按它的节奏去死。你若还活着，活在一座记住你袖手的城里。",
          fx={"cha": -2, "wis": 1, "con": 1}, follow=[later(6945, 5)], min_age=20)
    _leaf(add, 6945, "有人把那一年叫袖手年。你走过井盖时井盖不响。不响也是指控。",
          fx={"wis": 1, "con": 1}, min_age=25)

    _gate(add, 6950, "第二次爆发。正确的旗还在不在，此刻见分晓。",
          (6951, 6952, 6953, 6954, 9216), [{"plague_plan": True}], min_age=22)
    _win(add, 6951, "隔离线守住了。斑点停在线外。线内的人开始骂你，然后活过冬天。",
         "ach_stop_plague", attrs=ge("int", 10), fx={"int": 1, "wis": 1, "cha": 1},
         follow=[later(6955, 6)], min_age=22)
    _win(add, 6952, "神迹或大祭司的权杖把第二波按回去。有人跪。你让他们先洗手。",
         "ach_stop_plague", attrs=ge("wis", 11),
         need=[{"ach_meet_god": True}, {"ach_high_priest": True}, {"god_seen": True}],
         fx={"wis": 2, "cha": 1}, follow=[later(6955, 6)], min_age=22)
    _win(add, 6953, "你烧掉一区。三区还在。声望脏到能种地。地里明年仍长麦。",
         "ach_stop_plague", attrs=ge("wis", 9), need=[{"plague_fire": True}],
         set={"war_dirty": True}, fx={"wis": 1, "cha": -2, "con": 1, "str": 1},
         follow=[later(6955, 6)], min_age=22)
    _fail(add, 6954, "第二波比旗快。城没有停住。你若没死在斑里，就死在别人的眼睛里。",
          fx={"con": -2, "cha": -2, "wis": 1}, follow=[later(6956, 4)], min_age=22)
    _die(add, 9216, "斑点从腕走到心。城还在咳。你先停。",
         attrs=lt_map(int=10, wis=9, con=8), min_age=22)
    _leaf(add, 6955, "有孩子问那一年为什么少了一条街。你说：为了另外三条。孩子把这当成算术。",
          need=[{"ach_stop_plague": True}], fx={"wis": 1, "cha": 1}, min_age=28)
    _leaf(add, 6956, "你离开那座城。城的咳嗽跟了一程，然后放弃。放弃听起来像痊愈，不是。",
          fx={"con": 1, "wis": 1}, min_age=26)


def _feast(ctx) -> None:
    add = ctx["add"]
    _nat(add, 6962, "昔日魔头来赴宴。桌上有刀。对方是你亲自放过或感化过的那一个。",
         (6963, 6964, 6965, 6966), 28, 70, weight=3, group="ach_feast",
         need=[{"spared_foe": True}])
    _leaf(add, 6963, "你把刀推到桌子中间。两边都看得见，都暂时不拿。",
          attrs=ge("wis", 9), set={"feast_set": True}, fx={"wis": 1, "cha": 1},
          follow=[later(6970, 0)], min_age=28)
    _leaf(add, 6964, "你先动筷子。动筷子比动刀难，因为嘴还记得疼。",
          attrs=ge("cha", 9), set={"feast_set": True}, fx={"cha": 1},
          follow=[later(6970, 0)], min_age=28)
    _leaf(add, 6965, "你把对方介绍给在场的王或祭司。介绍词很短：这是我没有杀死的人。",
          need=[{"crowned": True}, {"royal_favor": True}, {"ach_high_priest": True}, {"ach_king": True}],
          set={"feast_set": True}, fx={"cha": 1, "wis": 1}, follow=[later(6970, 0)], min_age=28)
    _fail(add, 6966, "你拔剑。宴席变成旧业。放过的人重新成为仇。酒洒在刀上。",
          set={"spared_foe": None, "has_enemy_name": True}, fx={"str": 1, "cha": -2, "wis": -1},
          follow=[later(6967, 5)], min_age=28)
    _leaf(add, 6967, "有人把那次宴席写成你终于醒了。醒了是赞美，也是伪造。",
          fx={"wis": 1, "con": 1}, min_age=33)

    _gate(add, 6970, "刀在桌中央。汤还热。这一顿必须吃完，或必须有人先倒。",
          (6971, 6972, 6973, 6974), [{"feast_set": True}], min_age=28)
    _win(add, 6971, "你把这顿吃完。对方也是。刀直到残羹才被收走，像一件没被使用的证据。",
         "ach_feast_villain", attrs=ge("con", 9), fx={"con": 1, "wis": 1, "cha": 1},
         follow=[later(6975, 6)], min_age=28)
    _win(add, 6972, "你让国王看见你们同席。国王的手抖了一下。抖完仍举杯。举杯是一种国策。",
         "ach_feast_villain", attrs=ge("cha", 10),
         need=[{"crowned": True}, {"royal_favor": True}, {"ach_king": True}],
         fx={"cha": 2, "wis": 1}, follow=[later(6975, 6)], min_age=28)
    _win(add, 6973, "龙、教众或仇家在席间把旧事讲成笑话。笑话很冷。冷过之后仍是同席。",
         "ach_feast_villain", attrs=ge("wis", 10),
         need=[{"dragon_allied": True}, {"cult_broken": True}, {"ach_end_feud": True}],
         fx={"wis": 2, "cha": 1}, follow=[later(6975, 6)], min_age=28)
    _fail(add, 6974, "汤冷了。有人先拿刀。你挡开，宴席散了。放过仍在，同席没有完成。",
          fx={"con": -1, "cha": -1, "wis": 1}, follow=[later(6976, 4)], min_age=28)
    _leaf(add, 6975, "此后有人骂你与魔同席。你把骂写进菜单，当开胃。",
          need=[{"ach_feast_villain": True}], fx={"cha": 1, "wis": 1}, min_age=34)
    _leaf(add, 6976, "那把没被使用的刀后来砍了别人。你去看伤。伤不认识你的宴席。",
          fx={"wis": 1, "con": 1}, min_age=32)


def _refuse_godhood(ctx) -> None:
    add = ctx["add"]
    _nat(add, 6980, "神、门或石头把最后一次加冕递过来。递过来的不是冠，是不再做凡人的许可。",
         (6981, 6982, 6983, 6984), 36, 90, weight=3, group="ach_god", extra={"naturalUnlock": False})
    _win(add, 6981, "你拒绝，走回人间。人间有灰尘、欠债和还没洗的碗。碗比神位真实。",
         "ach_refuse_godhood", attrs=ge("wis", 11), set={"true_name_known": True},
         fx={"wis": 2, "cha": 1, "con": 1}, follow=[later(6985, 6)], min_age=36)
    _win(add, 6982, "你把神位让给徒弟。让出去的那只手抖。抖完仍空着，空着才能拥抱。",
         "ach_refuse_godhood", attrs=ge("cha", 10), need=[{"has_apprentice": True}, {"ach_apprentice_surpass": True}],
         set={"true_name_known": True}, fx={"cha": 2, "wis": 1}, follow=[later(6985, 6)], min_age=36)
    _win(add, 6983, "你把神位砸了。知识神因此另眼看你：有人把答案摔回题面。",
         "ach_refuse_godhood", attrs=ge("int", 11), need=[{"patron_god": "knowledge"}, {"god_seen": True}],
         fx={"int": 2, "wis": 1}, follow=[later(6985, 6)], min_age=36)
    _leaf(add, 6984, "你接受。从此雨不再落到你身上。雨落到别人身上时，你开始忘记湿是什么感觉。",
          set={"became_god": True}, fx={"int": 2, "wis": 2, "cha": 2, "con": 2},
          follow=[later(6986, 4)], min_age=36, weight=8)
    _leaf(add, 6985, "有神来问你后不后悔。你把洗碗的水指给他看。水里有菜叶。菜叶没有神性。",
          need=[{"ach_refuse_godhood": True}], fx={"wis": 1}, min_age=42)
    _leaf(add, 6986, "凡人来求你。你答应得很完整，完整得不像曾经洗过碗。这不是本成就。",
          need=[{"became_god": True}], fx={"cha": 1, "wis": 1}, min_age=40)


def _hook_refuse_godhood(ctx) -> None:
    """Schedule 6980 only from the last step of qualifying spines."""
    # Wired via later() on god_seen / hinge / king / lich wins below? 
    # 6711/6712 already later 6715; add 6980 there in _meet_god would fizzle without other flags.
    # Keep 6980 as a checker with delay0: qualifying wins OR fail "还不够格".
    pass


def _true_name_burial(ctx) -> None:
    add = ctx["add"]
    _nat(add, 6990, "临终的房间很静。静到能听见有没有人记得你的真名。",
         (6991, 6992, 6993, 6994), 55, 120, weight=5, group="ach_death", extra={"maxTriggers": 1})
    _leaf(add, 6991, "朋友在场，把真名说给送葬的人听。全城按这个名字下葬。假身份终于下班。",
          need=[{"true_name_known": True, "has_friend": True}],
          set={"ach_true_name_burial": True}, fx={"cha": 1, "wis": 1},
          death=True, min_age=55, weight=16, mt=1)
    _leaf(add, 6992, "史诗已经改对。唱诗的人把真名填进最后一段。棺木比假名宽。",
          need=[{"true_name_known": True, "ach_correct_epic": True}],
          set={"ach_true_name_burial": True}, fx={"cha": 1, "wis": 1},
          death=True, min_age=55, weight=15, mt=1)
    _leaf(add, 6993, "神殿按真名诵。徒弟或龙或神都点头。点头比碑文短，比碑文准。",
          need=[{"true_name_known": True, "has_apprentice": True}, {"true_name_known": True, "god_seen": True},
                {"true_name_known": True, "dragon_allied": True}],
          set={"ach_true_name_burial": True}, fx={"wis": 2},
          death=True, min_age=55, weight=15, mt=1)
    _die(add, 6994, "到死仍只剩假名，或根本没有人在场。讣告写得漂亮，写的不是你。一次普通的死亡。",
         min_age=55, weight=8)


def _echoes(ctx) -> None:
    add = ctx["add"]
    rows = [
        (7000, "ach_king", "有戏班把你的加冕演成喜剧。你让他们演。喜剧比史书肯承认手抖。"),
        (7001, "ach_regent", "幼主——已是王——在诏书边栏写：师。墨淡，字真。"),
        (7002, "ach_free_city", "外邦人按你的法纳税，骂你的法，仍按你的法。"),
        (7003, "ach_racial_pact", "桥上的两种脏话对唱。对唱比盟约响，也比盟约勤。"),
        (7004, "ach_try_king", "有王路过被告席，下意识低头。低头与你无关，与先例有关。"),
        (7005, "ach_win_war", "旧袍上的泥被当成勋章。你让他们去洗锅。锅比勋章有用。"),
        (7006, "ach_end_feud", "仇家那边来人借盐。盐很咸。咸比血淡。"),
        (7007, "ach_mercenary", "有人把你的旧旗当旅馆招牌。住宿费不含你的名字，包含你的规矩。"),
        (7008, "ach_hold_pass", "地图上那关被改成可守。改的人没见过你的肩。"),
        (7009, "ach_dragon", "有人问龙的味道。你说：像铁，像雨，像一句没有说完的话。"),
        (7010, "ach_dragon_flight", "王都的箭手此后见鸟也先看翼展。翼展成了一种礼貌。"),
        (7011, "ach_sea_serpent", "水手把你的灯塔当北。北有时是怕，有时是活。"),
        (7012, "ach_phoenix", "发烧的人来摸你的掌心。掌心早已不热。热在故事里。"),
        (7013, "ach_well_lord", "黑井的回声会先问：有没有敲门。问完才咬人。"),
        (7014, "ach_meet_god", "你走路时影子有时比你先拐弯。你让它。它见过更大的光。"),
        (7015, "ach_high_priest", "香火账问你签哪个名。你签把门的人。账房抗议。你仍签。"),
        (7016, "ach_name_from_death", "冬天来时你数自己的脉搏，像数一份不该属于你的工资。"),
        (7017, "ach_close_gate", "有法师来拍门疤。疤不回答。不回答是工作。"),
        (7018, "ach_refuse_stone", "炼金学徒把你的拒绝写成最后一章。最后一章比配方难抄。"),
        (7019, "ach_lich_named", "你在名单上同时出现在活人栏与死人栏。书记官来问。你说：洗碗栏。"),
        (7020, "ach_new_world", "有人把你的种子种死了。你又给一粒。给不是发现，是继续相遇。"),
        (7021, "ach_world_map", "有人把未知涂成金色。你把金刮掉，露出铅笔。铅笔还在发抖。"),
        (7022, "ach_buy_peace", "将军仍骂你。骂完把刀卖掉。卖掉的刀买了一头牛。"),
        (7023, "ach_return_relic", "盗贼公会把你的画像反过来挂。反过来是一种敬意。"),
        (7024, "ach_correct_epic", "走调的版本仍在乡下流传。乡下流传里你更像人。"),
        (7025, "ach_apprentice_surpass", "他的名声比你远。远的人回来时先脱鞋。脱鞋比跪有用。"),
        (7026, "ach_stop_plague", "城里少一条街。街上的风仍绕开你，像绕开一种算术。"),
        (7027, "ach_feast_villain", "有人把那次宴席写成软弱。你把菜单寄给他。菜单上没有刀。"),
        (7028, "ach_refuse_godhood", "神位的空缺被当成你的传说。传说里你在洗碗。洗碗没有传说。"),
        (7029, "ach_true_name_burial", "有人在坟前念对你的名字。念对的人自己也老了。老了仍念对。"),
    ]
    for eid, flag, desc in rows:
        add({
            "eventId": eid, "desc": desc,
            "minAge": 30, "maxAge": 120, "baseWeight": 4, "maxTriggers": 2,
            "requiredFlags": [{flag: True}],
            "effects": {"wis": 1},
            "cooldownGroups": ["ach_echo", "flag_echo"],
            "cooldownMinInterval": 8,
        })

    # Late invitation to refuse godhood: only if already on a qualifying peak.
    add({
        "eventId": 6988, "desc": "风把许可又送回来一次。这一次没有仪式，只有一句：还要不要。",
        "minAge": 40, "maxAge": 95, "maxTriggers": 1, "baseWeight": 3,
        "cooldownGroups": ["ach_god", "ach_entry"], "cooldownMinInterval": 20,
        "requiredFlags": [
            {"god_seen": True, "crowned": True},
            {"god_seen": True, "dragon_allied": True},
            {"god_seen": True, "ach_lich_named": True},
            {"god_seen": True, "abyss_hinge": True},
            {"god_seen": True, "ach_king": True},
            {"god_seen": True, "ach_well_lord": True},
        ],
        "followUp": d0(6981, 6982, 6983, 6984, 6987),
    })
    _fail(add, 6987, "你把许可又推回去，推得很累。累不是拒绝的成就，是凡人的下午。",
          fx={"wis": 1, "con": 1}, min_age=40)

    # 6980 remains a sealed beat from 6988.


