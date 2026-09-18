# -*- coding: utf-8 -*-
"""Coverage events: every flag value is read, and different values fork to different results."""
from __future__ import annotations


def _d0(*eids: int) -> list[dict]:
    return [{"eventId": i, "delay": 0} for i in eids]


def _leaf(
    add,
    eid: int,
    desc: str,
    flags_need: list[dict],
    effects: dict,
    *,
    min_age: int = 16,
    max_age: int = 90,
    weight: int = 12,
    flags_set: dict | None = None,
    natural: bool = False,
    groups: list[str] | None = None,
    interval: int = 6,
) -> None:
    ev = {
        "eventId": eid,
        "desc": desc,
        "minAge": min_age,
        "maxAge": max_age,
        "baseWeight": weight,
        "requiredFlags": flags_need,
        "effects": effects,
    }
    if not natural:
        ev["naturalUnlock"] = False
    else:
        ev["cooldownGroups"] = groups or ["flag_echo"]
        ev["cooldownMinInterval"] = interval
        ev["maxTriggers"] = 4
    if flags_set:
        ev["flags"] = flags_set
    add(ev)


def _scene(add, eid: int, desc: str, kids: tuple[int, ...], *, min_age=16, max_age=70, weight=5, extra=None):
    ev = {
        "eventId": eid,
        "desc": desc,
        "minAge": min_age,
        "maxAge": max_age,
        "maxTriggers": 3,
        "baseWeight": weight,
        "cooldownGroups": ["flag_fork"],
        "cooldownMinInterval": 8,
        "followUp": _d0(*kids),
    }
    if extra:
        ev.update(extra)
    add(ev)


def apply_flag_reads(add, events: list[dict], job_req) -> None:
    _patch_existing(events)
    _patrons(add)
    _styles(add)
    _unread_echoes(add)
    _forks(add)
    _race_origin_adult(add)


def _patch_existing(events: list[dict]) -> None:
    by = {int(ev["eventId"]): ev for ev in events}
    # Ordinary fever vs plague: different recoveries.
    for eid in (1902, 1903):
        if eid in by:
            req = by[eid].setdefault("requiredFlags", [{}])
            if req and isinstance(req[0], dict):
                req[0]["plague"] = False
    if 3884 in by:
        fu = by[3884].setdefault("followUp", [])
        if not any(int(x.get("eventId") or 0) == 5180 for x in fu):
            fu.insert(0, {"eventId": 5180, "delay": 0})
    # Hungry ring is the actual gate, not just "still wearing it".
    if 4560 in by:
        by[4560]["requiredFlags"] = [{"cursed_ring": True, "ring_hungry": True}]
    if 4561 in by:
        by[4561]["requiredFlags"] = [{"ring_hungry": True}]
    if 4562 in by:
        by[4562]["requiredFlags"] = [{"ring_hungry": True}]
    if 4563 in by:
        by[4563]["requiredFlags"] = [{"ring_hungry": True}]


def _patrons(add) -> None:
    # One echo per god. Effects are the "different result".
    rows = [
        (5000, "sun", "日神节你把脸晒脱了一层皮。有人说那是印记，你说那是欠债。",
         {"cha": 1, "con": 1}),
        (5001, "death", "亡者名册在你经过时自己翻了一页。没有你的名字。你走得更轻，别人离得更远。",
         {"wis": 1, "cha": -1}),
        (5002, "knowledge", "知识神殿允许你问一个真正愚蠢的问题。答案比问题更蠢，也更有用。",
         {"int": 2}),
        (5003, "war", "战神祭坛只要血不要祷词。你割破拇指，换来今晚不必先拔剑。",
         {"str": 1, "con": 1}),
        (5004, "nature", "林中神龛要你放下铁器。你空手走完一圈，蘑菇自己滚进袋里。",
         {"wis": 1, "gold": 1}),
        (5005, "fate", "命运纺线在你指间打了个结。你没有拆。后来那条路少死一个人。",
         {"wis": 1, "int": 1}),
        (5006, "sea", "你把不该捡的金币扔回浪里。浪回你一条活鱼，够吃两顿。",
         {"agi": 1, "con": 1}),
        (5007, "fire", "火神只要你保证：今晚的火只取暖。炉子听话，眉毛少了一截。",
         {"str": 1, "con": -1}),
    ]
    for eid, god, desc, fx in rows:
        add({
            "eventId": eid, "desc": desc,
            "minAge": 14, "maxAge": 80, "baseWeight": 7, "maxTriggers": 3,
            "requiredFlags": [{"patron_god": god}],
            "effects": fx,
            "cooldownGroups": ["patron_god", "flag_echo"],
            "cooldownMinInterval": 6,
        })


def _styles(add) -> None:
    rows = [
        (5020, "defense", "盾墙缺口轮到你去补。你没有前进，缺口也没有扩大。",
         {"con": 1, "str": 1}),
        (5021, "offense", "号角未落你已经在第一排。线破了，你的肩也破了一点。",
         {"str": 1, "con": -1, "cha": 1}),
        (5022, "archery", "你在四十步外结束战斗。近处的人还在找你的影子。",
         {"agi": 1, "int": 1}),
    ]
    for eid, style, desc, fx in rows:
        add({
            "eventId": eid, "desc": desc,
            "minAge": 18, "maxAge": 55, "baseWeight": 7, "maxTriggers": 4,
            "requiredFlags": [{"style": style}],
            "effects": fx,
            "cooldownGroups": ["fighting_style", "flag_echo"],
            "cooldownMinInterval": 5,
        })
    _scene(add, 5023, "伏击从两侧灌进来。你下意识去摸自己最熟的那一下。",
           (5024, 5025, 5026, 5027), min_age=18, max_age=50, weight=6,
           extra={"cooldownGroups": ["flag_fork", "combat"]})
    _leaf(add, 5024, "你把身体侧成盾。箭雨打在你而不是后排。",
          [{"style": "defense"}], {"con": 1})
    _leaf(add, 5025, "你迎着刀锋往前。伏击变成了对斩。",
          [{"style": "offense"}], {"str": 1, "con": -1})
    _leaf(add, 5026, "你先射倒喊口令的那一个。剩下的人不会喊了。",
          [{"style": "archery"}], {"agi": 1})
    _leaf(add, 5027, "你没有专精。你只会趴下、滚、再爬起来。这一次够用。",
          [{"style": False}, {"style": ""}], {"agi": 1, "con": -1}, weight=8)


def _unread_echoes(add) -> None:
    rows = [
        (5030, [{"in_school": True}], 7, 16,
         "学堂抽背到你。你把错的句子说成对的，先生没有拆穿。",
         {"int": 1, "cha": 1}, ["childhood", "flag_echo"]),
        (5031, [{"has_friend": True}], 16, 80,
         "撤退时有人喊你的名字。你回头，路还在。",
         {"cha": 1, "con": 1}, ["social", "flag_echo"]),
        (5032, [{"has_pet": True}], 12, 85,
         "你的兽在夜里先醒。盗贼只偷到一声吼，没偷到包。",
         {"wis": 1, "gold": 1}, ["flag_echo"]),
        (5033, [{"has_mount": True}], 16, 70,
         "黄昏前必须赶到下个镇子。马比你更讨厌这句话，仍把你送进门。",
         {"con": 1, "cha": 1}, ["flag_echo"]),
        (5034, [{"has_masterwork": True}], 20, 70,
         "武器商要买你那柄不起眼的剑。你报了个天价。他认真考虑了一息。",
         {"gold": 4, "cha": 1}, ["flag_echo"]),
        (5035, [{"guild_settled": True}], 20, 70,
         "公会账本允许你签字，不必再按手印。酒还是自己买，活却像样了。",
         {"gold": 3, "cha": 1}, ["money", "flag_echo"]),
        (5036, [{"map_partner": True}], 22, 70,
         "分赃时对方把大头推给你。他说地图是你先缝进衬里的。",
         {"gold": 4, "cha": 1}, ["flag_echo"]),
        (5037, [{"exiled": True}], 18, 80,
         "关卡认出你袖口的流放印。你走长路。长路没有印。",
         {"con": 1, "wis": 1, "cha": -1}, ["crime", "flag_echo"]),
        (5038, [{"plot_exiled": True}], 22, 85,
         "旧都商队把你错认成死讯。你买了他们的酒，把死讯喝成玩笑。",
         {"cha": 1, "int": 1}, ["court", "flag_echo"]),
        (5039, [{"war_gave_grain": True}], 22, 80,
         "饥年有人按那年开仓的记忆给你留了一袋麦。麦很潮，人情很干。",
         {"cha": 2, "con": 1}, ["war_echo", "flag_echo"]),
        (5040, [{"war_night_survived": True}], 20, 85,
         "营火边有人把那夜讲错。你纠正了一个名字，没有纠正自己当时的害怕。",
         {"wis": 1, "con": 1}, ["war_echo", "flag_echo"]),
        (5041, [{"plague": True}], 12, 80,
         "隔离线不认你的脸，只认腕上的斑。你在棚外过了一夜，星星比人近。",
         {"con": -1, "wis": 1}, ["sickness", "flag_echo"]),
        (5042, [{"ring_hungry": True}], 18, 70,
         "戒指在神坛前发烫。你没有献祭，它替你从盘子里卷走一枚金币。",
         {"gold": 2, "wis": -1}, ["artifact", "flag_echo"]),
        (5043, [{"knows_old_tongue": True}], 20, 90,
         "残碑上的骂人话只有你会读。你把它译成祝福，石头没有抗议。",
         {"int": 1, "cha": 1}, ["flag_echo"]),
    ]
    for eid, need, lo, hi, desc, fx, groups in rows:
        add({
            "eventId": eid, "desc": desc,
            "minAge": lo, "maxAge": hi, "baseWeight": 6, "maxTriggers": 3,
            "requiredFlags": need, "effects": fx,
            "cooldownGroups": groups, "cooldownMinInterval": 6,
        })
    # Plague recovery: different from ordinary fever (1902/1903).
    add({
        "eventId": 5180,
        "desc": "隔离棚里有人把醋泼在你脸上。斑点退了，气味留下，门才肯开。",
        "minAge": 12, "maxAge": 90, "naturalUnlock": False, "baseWeight": 14,
        "requiredFlags": [{"plague": True}],
        "flags": {"sick": None, "plague": None},
        "effects": {"con": 1, "cha": -1},
        "weightModifiers": [{"attr": "con", "base": 6, "multiplier": 2, "minFactor": 0.2}],
    })


def _forks(add) -> None:
    # School inspection: in_school vs not.
    _scene(add, 5050, "督学来抽查。没在册的孩子会被抓去搬砖，在册的要当场背书。",
           (5051, 5052), min_age=7, max_age=15, weight=7,
           extra={"cooldownGroups": ["flag_fork", "childhood"]})
    _leaf(add, 5051, "你把课文背成了顺口溜。督学记下你的名字，先生记下你的错字。",
          [{"in_school": True}], {"int": 1, "cha": 1}, min_age=7, max_age=16)
    _leaf(add, 5052, "你不在名册上。你去搬砖，砖比课文沉，也比课文诚实。",
          [{"in_school": False}], {"con": 1, "str": 1}, min_age=7, max_age=16, weight=9)

    # Friend vs alone when someone shouts your name.
    _scene(add, 5053, "背后有人喊你的旧名，像讨债，又像救命。",
           (5054, 5055), min_age=16, max_age=70)
    _leaf(add, 5054, "是你的朋友。他扔来一把刀，也扔来一句：别回头看我有多狼狈。",
          [{"has_friend": True}], {"cha": 1, "str": 1})
    _leaf(add, 5055, "没有朋友会这么喊。你跑。喊声变成别人的事。",
          [{"has_friend": False}], {"agi": 1, "con": -1}, weight=9)

    # Pet vs none at night camp.
    _scene(add, 5056, "营地夜里有细响，像刀，又像老鼠。",
           (5057, 5058), min_age=14, max_age=75)
    _leaf(add, 5057, "你的兽先扑出去。细响变成逃命。包还在。",
          [{"has_pet": True}], {"wis": 1, "gold": 1})
    _leaf(add, 5058, "你睡了过去。早晨少了一只鞋和半袋干粮。",
          [{"has_pet": False}], {"gold": -2, "con": -1}, weight=9)

    # Mount vs walk.
    _scene(add, 5059, "城门在黄昏关闭。你还有十里。",
           (5060, 5061), min_age=16, max_age=65)
    _leaf(add, 5060, "坐骑讨厌冲刺，更讨厌你走路。你们赶在门闩落下前挤进去。",
          [{"has_mount": True}], {"cha": 1, "con": 1})
    _leaf(add, 5061, "你跑完十里。门关了。你在壕里过了一夜，星比床硬。",
          [{"has_mount": False}], {"con": 1, "gold": -1}, weight=9)

    # Masterwork vs ordinary blade.
    _scene(add, 5062, "比武官要验刀。钝的去木人，快的去真人。",
           (5063, 5064), min_age=18, max_age=50,
           extra={"cooldownGroups": ["flag_fork", "arena"]})
    _leaf(add, 5063, "你那柄朴素的好剑通过了。对手看见刃口，先输了一寸气。",
          [{"has_masterwork": True}], {"str": 1, "cha": 1, "gold": 2})
    _leaf(add, 5064, "你的刀被编去打木人。木人倒了。观众仍觉得不过瘾。",
          [{"has_masterwork": False}], {"str": 1, "con": 1}, weight=9)

    # Guild settled vs still apprentice (must be in guild).
    _scene(add, 5065, "公会分派一份脏活：下水道里的东西在吃账本。",
           (5066, 5067), min_age=18, max_age=55,
           extra={"requiredFlags": [{"in_guild": True}], "cooldownGroups": ["flag_fork", "money"]})
    _leaf(add, 5066, "你已经能签字。你把脏活转成合同，合同比污水值钱。",
          [{"guild_settled": True}], {"gold": 3, "int": 1})
    _leaf(add, 5067, "见习栏的人没有签字权。你下了水道。账本救回来一半。",
          [{"guild_settled": False}], {"con": 1, "gold": 1}, weight=10)

    # Map partner vs solo treasure.
    _scene(add, 5068, "空城的灯还亮着一盏。有人问：这算几个人的份。",
           (5069, 5070), min_age=22, max_age=70,
           extra={"requiredFlags": [{"has_map_full": True}], "cooldownGroups": ["flag_fork", "artifact"]})
    _leaf(add, 5069, "合伙人把大袋推给你，自己拿走地图当纪念。纪念比金币轻。",
          [{"map_partner": True}], {"gold": 3, "cha": 1})
    _leaf(add, 5070, "只有你。你把灯也装进包。包很亮，路很黑。",
          [{"map_partner": False}], {"gold": 5, "con": -1}, weight=10)

    # Faith vs none at the donation box.
    _scene(add, 5071, "神殿门口摆着两个箱子：左边写神，右边写人。",
           (5072, 5073), min_age=12, max_age=80,
           extra={"cooldownGroups": ["flag_fork", "church"]})
    _leaf(add, 5072, "你把钱放进神那边，又留下来把蜡油刮掉。手黏，心不黏。",
          [{"faith": True}], {"wis": 1, "gold": -1})
    _leaf(add, 5073, "你把钱放进人那边。神父看了你一眼，没有阻止。",
          [{"faith": False}], {"cha": 1, "gold": -1}, weight=9)

    # Relationship: dating / engaged / married / none — mutually exclusive reads.
    _scene(add, 5074, "有人盯着你无名指上的白印，问那是不是戒痕。",
           (5075, 5076, 5077, 5078), min_age=18, max_age=60,
           extra={"cooldownGroups": ["flag_fork", "social"]})
    _leaf(add, 5075, "你还没到戒指。你说那是剑茧。对方笑了，你也笑了。",
          [{"dating": True, "engaged": False, "married": False}], {"cha": 1})
    _leaf(add, 5076, "你把婚期说漏了。对方祝贺，像祝贺一场即将开始的围城。",
          [{"engaged": True, "married": False}], {"cha": 1, "wis": 1})
    _leaf(add, 5077, "你亮出真正的戒指。问话的人退开一寸，像退开一把出鞘的剑。",
          [{"married": True}], {"cha": 1, "con": 1})
    _leaf(add, 5078, "那就是剑茧。你把茧展示给他们看。他们改问你刀法。",
          [{"dating": False, "engaged": False, "married": False}], {"str": 1, "cha": 1}, weight=8)

    # House vs none when soldiers requisition lodging.
    _scene(add, 5079, "过路军队要征用民房。没有房子的人去睡马厩。",
           (5080, 5081), min_age=20, max_age=70,
           extra={"cooldownGroups": ["flag_fork", "war"]})
    _leaf(add, 5080, "你用一顿饭把征用谈成借宿。他们睡地板，你睡自己的床沿。",
          [{"has_house": True}], {"cha": 1, "gold": -1})
    _leaf(add, 5081, "你本来就没有房子。马厩的草比他们的靴子香。",
          [{"has_house": False}], {"con": 1}, weight=9)

    # Child vs none when the gate is about to close for plague.
    _scene(add, 5082, "城门要为隔离关闭。里面有人在哭，外面有人在数钱。",
           (5083, 5084), min_age=20, max_age=70,
           extra={"cooldownGroups": ["flag_fork", "family"]})
    _leaf(add, 5083, "你把孩子从门缝里送进去。自己留在外面。门比誓言重。",
          [{"has_child": True}], {"wis": 1, "con": -1, "cha": 1})
    _leaf(add, 5084, "你去帮着关门。门关严了。哭声变成墙的事。",
          [{"has_child": False}], {"str": 1, "con": 1}, weight=9)

    # Apprentice vs none in a fight.
    _scene(add, 5085, "背后有刀。你来得及喊一声，来不及回头。",
           (5086, 5087), min_age=22, max_age=65)
    _leaf(add, 5086, "徒弟把那一刀接在木盾上。木盾废了。人没有。",
          [{"has_apprentice": True}], {"con": 1, "cha": 1})
    _leaf(add, 5087, "没有人替你接。你侧身，刀割开披风。披风比背便宜。",
          [{"has_apprentice": False}], {"agi": 1, "con": -1}, weight=9)

    # Sword vs none.
    _scene(add, 5088, "卫兵要验武器。没有剑的人交税，有剑的人交证明。",
           (5089, 5090), min_age=16, max_age=60,
           extra={"cooldownGroups": ["flag_fork", "town"]})
    _leaf(add, 5089, "你把剑横过来给人看刃。证明比税快。",
          [{"has_sword": True}], {"cha": 1, "str": 1})
    _leaf(add, 5090, "你没有剑。你交税。税吏说你看起来比有剑的人安分。",
          [{"has_sword": False}], {"gold": -1, "cha": 1}, weight=9)

    # War stance: enlisted / courier / profiteer / dodger / civilian.
    _scene(add, 5091, "征粮官按名册点人。点到的去前线，没点到的交粮，逃过的被多看一眼。",
           (5092, 5093, 5094, 5095, 5096), min_age=17, max_age=50,
           extra={"cooldownGroups": ["flag_fork", "war"]})
    _leaf(add, 5092, "你的番号比名字先被念出。粮不用你交，命已经交过。",
          [{"enlisted": True}], {"cha": 1, "con": 1})
    _leaf(add, 5093, "传令兵不在征粮册上。你把文书摊开，粮官改向别人要。",
          [{"war_courier": True}], {"int": 1, "agi": 1})
    _leaf(add, 5094, "有人记得你开过仓。粮官没敢在你面前把秤做假。",
          [{"war_gave_grain": True}], {"cha": 1, "gold": 1})
    _leaf(add, 5095, "光荣榜上你的名字被划过。粮官把你的份额写成两份。",
          [{"war_draft_dodger": True}], {"gold": -2, "cha": -1})
    _leaf(add, 5096, "你不在任何名册上。你交了一份普通的粮，领回一份普通的收据。",
          [{"enlisted": False, "war_courier": False, "war_draft_dodger": False, "war_gave_grain": False}],
          {"gold": -1}, weight=8)

    # Exile vs not at the border.
    _scene(add, 5097, "边境要看手心。流放印在阳光下像一枚不肯褪的章。",
           (5098, 5099), min_age=18, max_age=75,
           extra={"cooldownGroups": ["flag_fork", "crime"]})
    _leaf(add, 5098, "印还在。你被打发去绕山。山不认得印，只认得腿。",
          [{"exiled": True}], {"con": 1, "wis": 1})
    _leaf(add, 5099, "手心干净。卫兵收了一枚小钱，放你过去。",
          [{"exiled": False}], {"gold": -1}, weight=9)

    # Lion fame vs not at the inn.
    _scene(add, 5108, "旅店只剩马厩。老板看人下菜，也看传说下床。",
           (5109, 5110), min_age=18, max_age=70,
           extra={"cooldownGroups": ["flag_fork", "arena"]})
    _leaf(add, 5109, "老板说狮口余生的人应当睡得着。他把最好的床给你，自己去睡板凳。",
          [{"gladiator_fame": True}], {"con": 1, "cha": 1})
    _leaf(add, 5110, "你没有传说。你有马厩。草比某些床诚实。",
          [{"gladiator_fame": False}], {"con": 1}, weight=9)

    # Old tongue vs not at the inscription.
    _scene(add, 5111, "井盖上有一行没人肯读的字。村长说那是诅咒，小孩说那是笑话。",
           (5112, 5113), min_age=16, max_age=80)
    _leaf(add, 5112, "你读出来了：那是‘此井有人，请先敲门’。村里此后少掉了两个人。",
          [{"knows_old_tongue": True}], {"int": 1, "wis": 1, "cha": 1})
    _leaf(add, 5113, "你不认得。你把井盖盖好。诅咒如果存在，至少被你压住了一年。",
          [{"knows_old_tongue": False}], {"con": 1}, weight=9)


def _race_origin_adult(add) -> None:
    races = [
        (5120, "human", "旅店把你当成任何地方的人。账单也按任何地方的人来。你少解释一句，多喝一口。",
         {"cha": 1, "gold": -1}),
        (5121, "elf", "掌柜按‘长寿的钱包’给你开价。你按今晚的胃口还价。双方都觉得自己吃亏。",
         {"wis": 1, "gold": -1}),
        (5122, "dwarf", "酒窖请你品一口。你说浅。他们免费倒到你说深。",
         {"con": 1, "cha": 1}),
        (5123, "halfling", "有人试探你的口袋。你把试探送回他们口袋，并多放一粒石子。",
         {"agi": 1, "gold": 1}),
        (5124, "gnome", "磨坊的齿轮咬死了。你用一把餐刀和三句脏话让它重新唱歌。",
         {"int": 1, "gold": 1}),
        (5125, "half_orc", "有人先动手，为了证明自己不怕。你结束得比证明更快。",
         {"str": 1, "cha": -1}),
        (5126, "half_elf", "两张桌子同时向你招手。你各坐半席，把酒钱付成一份。",
         {"cha": 1, "wis": 1}),
        (5127, "dragonborn", "炉火对别人太旺，对你刚好。你睡在最热的角落，谁也没敢叫你让开。",
         {"con": 1}),
        (5128, "tiefling", "神殿正门对你关着。侧门的香火没问角的形状。你把钱放在侧门。",
         {"wis": 1, "cha": 1, "gold": -1}),
    ]
    for eid, race, desc, fx in races:
        add({
            "eventId": eid, "desc": desc,
            "minAge": 16, "maxAge": 80, "baseWeight": 5, "maxTriggers": 3,
            "requiredFlags": [{"race": race}],
            "effects": fx,
            "cooldownGroups": ["race_echo", "flag_echo"],
            "cooldownMinInterval": 7,
        })
    origins = [
        (5140, "priest", "商队请你给货箱祝福。你念了半句正经的，半句‘别发霉’。他们仍付钱。",
         {"wis": 1, "gold": 1}),
        (5141, "soldier", "民兵要你示范步法。你把他们走成一行，而不是一群鹅。",
         {"str": 1, "cha": 1}),
        (5142, "mage", "有人请你鉴定一把‘会说话的勺’。勺不会说话。你收了鉴定费。",
         {"int": 1, "gold": 2}),
        (5143, "merchant", "你把同样的货讲成两种故事，卖出两种价格。良心只出一份。",
         {"gold": 3, "int": 1}),
        (5144, "farmer", "田里生了陌生斑。你让他们把病株烧掉，把种子换垄。今年少饿一旬。",
         {"wis": 1, "con": 1, "cha": 1}),
        (5145, "artisan", "城门铰链咬死。你修到天亮，城门重新会鞠躬。",
         {"str": 1, "gold": 2}),
        (5146, "street", "你比卫兵更早看见那个伸口袋的手。卫兵看见的是你抬起的下巴。",
         {"agi": 1, "wis": 1}),
        (5147, "noble", "有人按你的旧姓要一份礼。你送出礼貌，没送出钱。礼貌很贵。",
         {"cha": 1, "gold": -1}),
        (5148, "tribe", "风转向了。你让营地挪开干河床。夜里河床重新变成河。",
         {"wis": 1, "con": 1}),
        (5149, "temple_order", "有人要你见证一句誓言。你让他们把‘永远’改成‘今晚’。今晚有效。",
         {"wis": 1, "cha": 1}),
    ]
    for eid, origin, desc, fx in origins:
        add({
            "eventId": eid, "desc": desc,
            "minAge": 16, "maxAge": 80, "baseWeight": 5, "maxTriggers": 3,
            "requiredFlags": [{"origin": origin}],
            "effects": fx,
            "cooldownGroups": ["origin_echo", "flag_echo"],
            "cooldownMinInterval": 7,
        })
