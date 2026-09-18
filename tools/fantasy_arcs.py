# -*- coding: utf-8 -*-
"""Long arcs: delayed follow-ups plus attr/flag forks (including death)."""
from __future__ import annotations


def ge(attr: str, n: int = 8) -> dict:
    return {attr: {"operator": ">=", "value": n}}


def lt_all(n: int, *attrs: str) -> dict:
    return {a: {"operator": "<", "value": n} for a in attrs}


def lt_map(**attrs: int) -> dict:
    return {a: {"operator": "<", "value": n} for a, n in attrs.items()}


def d0(*eids: int) -> list[dict]:
    return [{"eventId": i, "delay": 0} for i in eids]


def later(eid: int, years: int) -> dict:
    return {"eventId": eid, "delay": years}


def w_attr(attr: str, base: int = 5, multiplier: int = 2, min_factor: float | None = None) -> dict:
    item: dict = {"attr": attr, "base": base, "multiplier": multiplier}
    if min_factor is not None:
        item["minFactor"] = min_factor
    return item


def apply_arcs(add, job_req) -> None:
    _arena_lion(add)
    _war(add, job_req)
    _plot(add)
    _black_well(add)
    _caravan(add)
    _curse_ring(add)
    _outlaw(add)
    _treasure_map(add)
    _hometown_siege(add)
    _cult(add, job_req)
    _echoes(add)


def _fork(add, eid, desc, min_age, max_age, outcomes, weight=8, group="story_fork", extra=None):
    ev = {
        "eventId": eid, "desc": desc, "minAge": min_age, "maxAge": max_age,
        "maxTriggers": 1, "baseWeight": weight,
        "cooldownGroups": [group, "story_fork"], "cooldownMinInterval": 12,
        "followUp": d0(*outcomes),
    }
    if extra:
        ev.update(extra)
    add(ev)


def _res(add, eid, desc, attrs=None, flags_need=None, flags_set=None, effects=None,
         weight=13, wmod=None, follow=None, death=False, min_age=16, max_age=90):
    ev = {
        "eventId": eid, "desc": desc, "minAge": min_age, "maxAge": max_age,
        "naturalUnlock": False, "baseWeight": weight,
    }
    if death:
        ev["type"] = "death"
    if attrs:
        ev["requiredAttrs"] = attrs
    if flags_need:
        ev["requiredFlags"] = flags_need
    if flags_set:
        ev["flags"] = flags_set
    if effects:
        ev["effects"] = effects
    if wmod:
        ev["weightModifiers"] = wmod
    if follow:
        ev["followUp"] = follow
    add(ev)


def _must(add, eid, desc, flags_need, follow, min_age=18, max_age=90, flags_set=None, effects=None):
    ev = {
        "eventId": eid, "desc": desc, "minAge": min_age, "maxAge": max_age,
        "naturalUnlock": False, "maxTriggers": 1,
        "requiredFlags": flags_need, "followUp": follow,
    }
    if flags_set:
        ev["flags"] = flags_set
    if effects:
        ev["effects"] = effects
    add(ev)


def _arena_lion(add) -> None:
    add({
        "eventId": 4100,
        "desc": "你被推进角斗场。闸门对面是一头饿狮。沙很热，观众更热。",
        "minAge": 16, "maxAge": 50, "maxTriggers": 2, "baseWeight": 8,
        "cooldownGroups": ["arena", "story_fork"], "cooldownMinInterval": 10,
        "followUp": d0(4101, 4102, 4103, 4104, 4105, 9140),
        "ageModifiers": {"peak": 28, "decay": 0.94},
    })
    _res(add, 4101, "你用力量砸开它。狮子倒了，你的名字被喊成铁。",
         attrs=ge("str", 8), effects={"str": 1, "cha": 1, "gold": 3},
         flags_set={"arena_lion_slain": True, "gladiator_fame": True},
         wmod=[w_attr("str", 8, 3)], follow=[later(4110, 0), later(4120, 3), later(4128, 8)], weight=14)
    _res(add, 4102, "你不硬碰。绕圈、闪、再绕，狮子先趴下喘气。观众嫌不够血，驯兽师已经在收闸。",
         attrs=ge("agi", 8), effects={"agi": 1, "wis": 1, "gold": 2},
         flags_set={"arena_lion_tired": True, "gladiator_fame": True},
         wmod=[w_attr("agi", 8, 3)], follow=[later(4110, 0), later(4121, 4), later(4128, 8)], weight=14)
    _res(add, 4103, "你蹲下，用喉咙里不是人的声音说话。狮子坐了。观众骂假赛，它的耳朵只朝你转。",
         attrs=ge("wis", 8), effects={"wis": 2, "cha": 1},
         flags_set={"arena_lion_friend": True, "has_pet": True, "gladiator_fame": True},
         wmod=[w_attr("wis", 8, 3)], follow=[later(4111, 0), later(4122, 3), later(4128, 8)])
    _res(add, 4104, "你把观众变成你的盾：起哄、起哄、再起哄。嘘声乱了，闸门重新打开，狮子被收回去。",
         attrs=ge("cha", 8), effects={"cha": 2, "gold": 1},
         flags_set={"arena_lion_spared": True, "gladiator_fame": True},
         wmod=[w_attr("cha", 8, 3)], follow=[later(4110, 0), later(4123, 5), later(4128, 8)], weight=12)
    _res(add, 4105, "你看穿闸门的插销。狮子还没扑到，笼子自己回去了一半。驯兽师恨你拆台，你还活着。",
         attrs=ge("int", 8), effects={"int": 1, "agi": 1},
         flags_set={"arena_lion_trick": True, "gladiator_fame": True},
         wmod=[w_attr("int", 8, 3)], follow=[later(4110, 0), later(4124, 4), later(4128, 8)], weight=12)
    _res(add, 9140, "什么都不够。狮子比规则快。沙子进了嘴里，天黑了。",
         attrs=lt_all(8, "str", "agi", "wis", "cha", "int"), death=True, weight=11)
    _res(add, 4110, "你走出沙地。血或汗把名字写在木板上，写错了两个字，没人改。",
         effects={"cha": 1}, weight=10)
    _res(add, 4111, "你走出沙地。狮子在闸门后看你。有人说那是驯养，你说那是对话。",
         flags_need=[{"arena_lion_friend": True}], effects={"wis": 1, "cha": 1}, weight=10)
    _res(add, 4120, "三年后，有人把狮皮送到你门上。里面藏着一封仇家的名，墨还没干。",
         flags_need=[{"arena_lion_slain": True}], effects={"wis": 1},
         flags_set={"has_enemy_name": True}, follow=[later(4125, 2)], weight=10, min_age=19)
    _res(add, 4121, "四年后，角斗场请你再来“逗狮”。你拒绝。他们把奖金改成两倍，你仍拒绝。",
         flags_need=[{"arena_lion_tired": True}], effects={"wis": 1, "gold": 1}, weight=10, min_age=20)
    _res(add, 4122, "那头狮在市郊等你。它老了，仍认你的气味。你坐下来，像坐在一个沉默的老朋友旁边。",
         flags_need=[{"arena_lion_friend": True}], effects={"wis": 2, "cha": 1},
         follow=[later(4126, 6)], weight=10, min_age=19)
    _res(add, 4123, "有人把你当年鼓动观众的事写成话本。你在里面更帅，也更不像你。",
         flags_need=[{"arena_lion_spared": True}], effects={"cha": 1, "int": 1}, weight=10, min_age=21)
    _res(add, 4124, "驯兽师的学徒找到你，问闸门怎么拆。你画了图，又把最关键的销子画成花。",
         flags_need=[{"arena_lion_trick": True}], effects={"int": 1, "wis": 1}, weight=10, min_age=20)
    _must(add, 4125, "仇家的名把你引到一条巷子。巷子比狮子窄，刀比狮子多。",
          [{"has_enemy_name": True}], d0(4127, 4129, 9141), min_age=21)
    _res(add, 4127, "你把刀撞开，把人撞到墙上。仇从力气里结束。",
         attrs=ge("str", 7), effects={"str": 1, "wis": 1}, flags_set={"has_enemy_name": None},
         wmod=[w_attr("str", 7, 3)], min_age=21)
    _res(add, 4129, "你没有拔剑。你从屋顶离开。刀砍在空处，像砍进你不要的那种荣耀。",
         attrs=ge("agi", 7), effects={"agi": 1, "wis": 1}, flags_set={"has_enemy_name": None},
         wmod=[w_attr("agi", 7, 3)], min_age=21)
    _res(add, 9141, "巷子没有出口。狮皮上的信比你先到。",
         attrs=lt_all(7, "str", "agi"), death=True, weight=10, min_age=21)
    _res(add, 4126, "你再去市郊。狮子不在了。草被压出一块形状，像一个坐过的人。",
         flags_need=[{"arena_lion_friend": True}], effects={"wis": 2}, weight=10, min_age=25)
    _res(add, 4128, "角斗场改建了神殿。沙还在缝里。有小孩问你狮子是不是真的。",
         flags_need=[{"gladiator_fame": True}], effects={"wis": 1, "cha": 1}, weight=10, min_age=24)


def _war(add, job_req) -> None:
    _fork(add, 4200, "边境的烽火连成一条线。征兵官把名册摊开，墨还没干。",
          17, 42, (4201, 4205, 4202, 4206, 4203, 4204), weight=9, group="war",
          extra={"ageModifiers": {"peak": 24, "decay": 0.95}})
    _res(add, 4201, "你应征。编号比名字先被记住。旗帜比家书近。",
         flags_need=job_req("fighter", "paladin", "ranger", "barbarian", "cleric") + [{"enlisted": True}],
         effects={"str": 1, "con": 1, "gold": 2}, flags_set={"at_war": True, "enlisted": True},
         wmod=[w_attr("str", 5, 2)], follow=[later(4210, 1), later(4220, 4)],
         weight=14, min_age=17, max_age=50)
    _res(add, 4205, "你不是军籍里的人，可你的胳膊被点中了。你走进了那条线。",
         attrs=ge("str", 8), effects={"str": 1, "con": 1}, flags_set={"at_war": True, "enlisted": True},
         wmod=[w_attr("str", 8, 3)], follow=[later(4210, 1), later(4220, 4)],
         weight=12, min_age=17, max_age=50)
    _res(add, 4202, "你被派去传令，而不是填壕。马比剑先认识你。",
         attrs=ge("int", 7), effects={"int": 1, "agi": 1}, flags_set={"at_war": True, "war_courier": True},
         wmod=[w_attr("int", 7, 3)], follow=[later(4215, 1), later(4221, 5)],
         min_age=17, max_age=50)
    _res(add, 4206, "你看懂了战场会怎么死。你选择跑信。有人说你怕，信却因此到达。",
         attrs=ge("wis", 8), effects={"wis": 1, "agi": 1}, flags_set={"at_war": True, "war_courier": True},
         wmod=[w_attr("wis", 8, 3)], follow=[later(4215, 1), later(4221, 5)],
         weight=12, min_age=17, max_age=50)
    _res(add, 4203, "你把金币推过去。有人替你去填名册。你改去运粮，粮比血贵。",
         attrs=ge("gold", 8), effects={"gold": -6, "int": 1, "wis": 1}, flags_set={"war_profiteer": True},
         wmod=[w_attr("gold", 8, 2, 0.2)], follow=[later(4224, 3), later(4225, 7)],
         weight=10, min_age=17, max_age=50)
    _res(add, 4204, "你没有应征。路变窄了。有人把你的名字从村口的光荣榜上划掉。",
         effects={"wis": 1, "cha": -1}, flags_set={"war_draft_dodger": True},
         follow=[later(4223, 6)], weight=5, min_age=17, max_age=50)
    _must(add, 4210, "夜袭开始。火把比军号更早到达你这一侧的壕。",
          [{"at_war": True}], d0(4211, 4212, 4213, 4214, 9142))
    _res(add, 4211, "你把攻上来的人连盾一起撞回去。这一夜你还活着，盾不是。",
         attrs=ge("str", 8), effects={"str": 1, "con": 1}, flags_set={"war_night_survived": True},
         wmod=[w_attr("str", 8, 3)], weight=14, min_age=18)
    _res(add, 4212, "你从死人堆里爬出侧面，割断了他们的火油袋。火改了方向。",
         attrs=ge("agi", 8), effects={"agi": 1, "wis": 1}, flags_set={"war_night_survived": True},
         wmod=[w_attr("agi", 8, 3)], weight=14, min_age=18)
    _res(add, 4213, "你让壕沟灌水。火把自己灭了。有人骂你毁了工事，活着的人不多嘴。",
         attrs=ge("int", 8), effects={"int": 1, "wis": 1}, flags_set={"war_night_survived": True},
         wmod=[w_attr("int", 8, 3)], min_age=18)
    _res(add, 4214, "你听出这是佯攻。真攻在东门。你把还能跑的人拽去东门。",
         attrs=ge("wis", 8), effects={"wis": 1, "cha": 1}, flags_set={"war_night_survived": True},
         wmod=[w_attr("wis", 8, 3)], min_age=18)
    _res(add, 9142, "火和铁同时到达。你没能把名字留给名册。",
         attrs=lt_all(8, "str", "agi", "int", "wis"), death=True, weight=11, min_age=18)
    _must(add, 4215, "你要在天亮前把信送到对岸。河水比印鉴冷。",
          [{"war_courier": True}], d0(4216, 4217, 4218, 9143))
    _res(add, 4216, "你把马催过断桥。桥在你身后说话，说的是坍塌。",
         attrs=ge("agi", 7), effects={"agi": 1, "con": 1}, flags_set={"war_letter_ok": True},
         wmod=[w_attr("agi", 7, 3)], weight=14, min_age=18)
    _res(add, 4217, "你改了路线，走没有画在图上的浅滩。信没有湿。",
         attrs=ge("wis", 7), effects={"wis": 1, "int": 1}, flags_set={"war_letter_ok": True},
         wmod=[w_attr("wis", 7, 3)], min_age=18)
    _res(add, 4218, "你被拦住。你把假信给他们，真信在靴底。他们不会看靴底。",
         attrs=ge("int", 7), effects={"int": 1, "cha": 1}, flags_set={"war_letter_ok": True},
         wmod=[w_attr("int", 7, 3)], min_age=18)
    _res(add, 9143, "信到了，你没有。对岸的人拆开蜡，蜡比你的血先干。",
         attrs=lt_all(7, "agi", "wis", "int"), death=True, weight=10, min_age=18)
    _res(add, 4220, "战争暂时停了。你把靴子倒出沙子和一颗不属于你的牙齿。",
         flags_need=[{"at_war": True}], effects={"con": 1, "wis": 1},
         flags_set={"at_war": None, "war_veteran": True}, follow=[later(4222, 4)],
         weight=10, min_age=20)
    _res(add, 4221, "多年后你才知道：你送出的那封信改了一寸边界。没人在地图上写你的名字。",
         flags_need=[{"war_letter_ok": True}, {"war_courier": True}], effects={"wis": 2, "int": 1},
         flags_set={"at_war": None, "war_veteran": True}, follow=[later(4222, 3)],
         weight=10, min_age=22)
    _res(add, 4222, "旧袍上的泥还在。有人叫你英雄，你叫他们把汤盛满。",
         flags_need=[{"war_veteran": True}, {"at_war": True}, {"war_courier": True}],
         effects={"wis": 1, "cha": 1}, weight=10, min_age=24)
    _res(add, 4223, "退役的人看着你完整的手。有人恨，有人羡慕。你请他们喝酒，酒不能解释。",
         flags_need=[{"war_draft_dodger": True}], effects={"wis": 1, "cha": -1}, weight=10, min_age=23)
    _must(add, 4224, "粮价因战争涨起来。你的仓库比良心满。有人在门上画了绞架，画得不像，恨意像。",
          [{"war_profiteer": True}], d0(4226, 4227), min_age=20, effects={"gold": 5, "cha": -1, "wis": 1})
    _res(add, 4226, "你把粮开仓。绞架的画被雨冲掉。有人仍不原谅你先赚钱。",
         attrs=ge("wis", 7), effects={"gold": -4, "cha": 2, "wis": 1},
         flags_set={"war_profiteer": None, "war_gave_grain": True},
         wmod=[w_attr("wis", 7, 2)], follow=[later(4228, 4)], weight=12, min_age=20)
    _res(add, 4227, "你把门加厚。钱还在。名字在巷子里走，不进门。",
         effects={"int": 1, "con": 1}, weight=8, min_age=20)
    _res(add, 4225, "战争结束。你的金币上有人的血味，洗不掉，只能花掉。",
         flags_need=[{"war_profiteer": True}],
         effects={"wis": 1, "gold": 1}, weight=10, min_age=24)
    _res(add, 4228, "战争结束。有人在名单上写你开仓，有人只写你先囤过。两行都是真的。",
         flags_need=[{"war_gave_grain": True}],
         effects={"wis": 1, "cha": 1, "gold": -1}, weight=10, min_age=24)


def _plot(add) -> None:
    add({
        "eventId": 4300,
        "desc": "你在澡堂听见三个人把国王的名字说得太轻。蒸汽把话蒸得像玩笑。",
        "minAge": 18, "maxAge": 55, "maxTriggers": 1, "baseWeight": 8,
        "cooldownGroups": ["court", "story_fork"], "cooldownMinInterval": 12,
        "flags": {"heard_plot": True},
        "followUp": d0(4301, 4302, 4303, 4304),
    })
    _res(add, 4301, "你听懂了暗号。不是情话，是日期、城门和一口井。",
         attrs=ge("int", 7), effects={"int": 1, "wis": 1}, flags_set={"knows_plot": True},
         wmod=[w_attr("int", 7, 3)], follow=[later(4310, 1)], weight=14, min_age=18, max_age=70)
    _res(add, 4302, "你听出谁在撒谎。是第三人。他的心跳比蒸汽响。",
         attrs=ge("wis", 7), effects={"wis": 2}, flags_set={"knows_plot": True},
         wmod=[w_attr("wis", 7, 3)], follow=[later(4310, 1)], min_age=18, max_age=70)
    _res(add, 4303, "你加入闲聊，套出第四个名字。他们把你当成自己人。酒是真的，刀也是。",
         attrs=ge("cha", 8), effects={"cha": 1, "int": 1},
         flags_set={"knows_plot": True, "plot_inside": True},
         wmod=[w_attr("cha", 8, 3)], follow=[later(4310, 1)], weight=12, min_age=18, max_age=70)
    _res(add, 4304, "你只当是酒话。蒸汽散了，名字也散了。你把背擦干。",
         effects={"con": 1}, follow=[later(4325, 3)], weight=6, min_age=18, max_age=70)
    _must(add, 4310, "你手里捏着三个名字。城卫的岗就在街角，灯火把你的影子拉得很长。",
          [{"knows_plot": True}], d0(4311, 4314, 4312, 4313), min_age=19)
    _res(add, 4311, "你报告了。有人记录，有人冷笑。文件比你先进入城堡。",
         attrs=ge("cha", 6), effects={"cha": 1, "wis": 1}, flags_set={"plot_reported": True},
         wmod=[w_attr("cha", 6, 2)], follow=[later(4320, 2)], min_age=19)
    _res(add, 4314, "你把日期、井和城门写成一封没有署名的信，塞进城卫的靴筒。",
         attrs=ge("int", 7), effects={"int": 1, "wis": 1}, flags_set={"plot_reported": True},
         wmod=[w_attr("int", 7, 3)], follow=[later(4320, 2)], weight=12, min_age=19)
    _res(add, 4312, "你把名字卖回给阴谋。双份危险，双份酒。他们敬你，像敬一柄迟早要转的刀。",
         flags_need=[{"plot_inside": True}], effects={"gold": 4, "cha": 1, "wis": 1},
         flags_set={"plot_double": True}, follow=[later(4322, 2)], weight=10, min_age=19)
    _res(add, 4313, "你把名字咽回去。咽下去的东西比酒沉。",
         effects={"wis": 1, "con": 1}, flags_set={"plot_silent": True},
         follow=[later(4321, 2)], weight=6, min_age=19)
    _res(add, 4320, "政变流产。有人在黎明被带走。你被请去喝酒，酒里没有毒。这一次。",
         flags_need=[{"plot_reported": True}], effects={"wis": 1, "cha": 1, "gold": 2},
         flags_set={"plot_foiled": True}, follow=[later(4330, 4)], weight=10, min_age=20)
    _must(add, 4321, "政变那天城门反锁。旗换了颜色。你在里面，像一封被误投的信。",
          [{"plot_silent": True, "knows_plot": True}], d0(4323, 4324, 4333, 9144), min_age=21)
    _res(add, 4323, "你从水道爬出城。新旗在头顶，旧水在腰间。你还是你。",
         attrs=ge("agi", 7), effects={"agi": 1, "con": 1, "wis": 1}, flags_set={"plot_exiled": True},
         wmod=[w_attr("agi", 7, 3)], min_age=21)
    _res(add, 4324, "你把话说圆。新主人需要一个知道旧秘密、却不像刺客的人。你留下。",
         attrs=ge("cha", 8), effects={"cha": 2, "int": 1}, flags_set={"plot_courtier": True},
         wmod=[w_attr("cha", 8, 3)], follow=[later(4332, 5)], weight=12, min_age=21)
    _res(add, 4333, "你用日期、井和城门换一夜活路。他们让你活，为了让你看见新旗怎么升起。",
         attrs=ge("int", 7), effects={"int": 1, "wis": 1, "cha": -1}, flags_set={"plot_exiled": True},
         wmod=[w_attr("int", 7, 3)], weight=12, min_age=21)
    _res(add, 9144, "他们需要一个名字来填黎明。你的名字够短。",
         attrs=lt_map(agi=7, cha=8, int=7), death=True, weight=11, min_age=21)
    _must(add, 4322, "双面刀终于要选边。两边的信同一天到达。",
          [{"plot_double": True}], d0(4328, 4329, 4334), min_age=21)
    _res(add, 4328, "你把两边的信都烧了，自己离开城。火比立场干净。",
         attrs=ge("wis", 8), effects={"wis": 2, "gold": -2},
         flags_set={"plot_exiled": True, "plot_double": None},
         wmod=[w_attr("wis", 8, 3)], weight=12, min_age=21)
    _res(add, 4329, "你把真信交给更可能赢的那边。赢的人记得你，输的人记得更清楚。",
         attrs=ge("int", 7), effects={"int": 1, "cha": 1, "gold": 3}, flags_set={"plot_courtier": True},
         wmod=[w_attr("int", 7, 3)], follow=[later(4332, 5)], weight=11, min_age=21)
    _res(add, 4334, "两边的信都没有回音。回音是刀。你在城外的沟里醒来，立场掉在门槛上。",
         attrs=lt_map(wis=8, int=7), effects={"con": -1, "cha": -2, "gold": -3},
         flags_set={"plot_exiled": True, "plot_double": None},
         weight=10, min_age=21)
    _must(add, 4325, "砖头砸进窗。你还当是醉汉。街上已经在换旗。",
          [{"heard_plot": True}], d0(4326, 4327), min_age=21, max_age=80, effects={"wis": 1, "con": -1})
    _res(add, 4326, "你带着能拿的东西从后门走。政变不认识你，石子却认识所有人的窗户。",
         attrs=ge("agi", 6), effects={"agi": 1, "wis": 1}, wmod=[w_attr("agi", 6, 2)], weight=12, min_age=21)
    _res(add, 4327, "你躲在地窖里把酒喝完。天亮时新税吏来数桶。你还在，桶不在。",
         effects={"con": 1, "gold": -2}, weight=9, min_age=21)
    _res(add, 4330, "新王——或者仍是旧王——给你一枚没有名字的戒指。戴上它，门卫少问一句。",
         flags_need=[{"plot_foiled": True}], effects={"cha": 1, "gold": 3, "wis": 1},
         flags_set={"royal_favor": True}, weight=10, min_age=24)
    _res(add, 4332, "宫廷要你作证一段你既在场、又不该在场的历史。你把动词说得很小心。",
         flags_need=[{"plot_courtier": True}], effects={"int": 1, "cha": 1, "wis": 1},
         weight=10, min_age=26)


def _black_well(add) -> None:
    _fork(add, 4400, "你接下探索黑井的契约。地图在第三页结束，血在第四页开始。",
          18, 45, (4401, 4402), group="dungeon")
    _res(add, 4401, "你点着火把走下去。井壁在出汗，像活的。",
         effects={"con": 1, "wis": 1}, flags_set={"dungeon_run": True},
         follow=[later(4410, 1)], weight=12, min_age=18, max_age=60)
    _res(add, 4402, "你把契约退回去。中介笑你，笑完把下一份更薄的地图卖给别人。",
         effects={"wis": 1, "gold": 1}, follow=[later(4440, 6)], weight=6, min_age=18, max_age=60)
    _must(add, 4410, "第二层。门上的谜语用死者的语法写成。门缝里有风，风里有牙。",
          [{"dungeon_run": True}], d0(4411, 4412, 4413, 9145), min_age=19)
    _res(add, 4411, "你把谜语读顺。门开了，像对一个懂礼貌的客人点头。",
         attrs=ge("int", 8), effects={"int": 1, "wis": 1}, wmod=[w_attr("int", 8, 3)],
         follow=[later(4420, 1)], weight=14, min_age=19)
    _res(add, 4412, "你把门砸开。谜语碎在地上，变成普通的石头。石头也会报复，只是慢。",
         attrs=ge("str", 8), effects={"str": 1, "con": -1}, wmod=[w_attr("str", 8, 3)],
         follow=[later(4420, 1)], weight=12, min_age=19)
    _res(add, 4413, "你从门轴的缝钻过去。谜语还在问，你已经在另一边。",
         attrs=ge("agi", 8), effects={"agi": 1, "int": 1}, wmod=[w_attr("agi", 8, 3)],
         follow=[later(4420, 1)], weight=12, min_age=19)
    _res(add, 9145, "门把你当成错误的答案。风停了。",
         attrs=lt_all(8, "int", "str", "agi"), death=True, weight=10, min_age=19)
    _must(add, 4420, "第三层。毒雾齐腰。火把变成一粒绿的星。",
          [{"dungeon_run": True}], d0(4421, 4422, 4423, 9146), min_age=20)
    _res(add, 4421, "你把毒雾走完。肺像进过铁屑，仍能数自己的步子。",
         attrs=ge("con", 8), effects={"con": 1, "wis": 1}, wmod=[w_attr("con", 8, 3)],
         follow=[later(4430, 1)], min_age=20)
    _res(add, 4422, "你找到一条没有雾的壁缝。壁缝像故意留给会看的人。",
         attrs=ge("wis", 8), effects={"wis": 1, "agi": 1}, wmod=[w_attr("wis", 8, 3)],
         follow=[later(4430, 1)], min_age=20)
    _res(add, 4423, "你用布和酒做了简陋的滤器。它很难看，有效。",
         attrs=ge("int", 7), effects={"int": 1, "con": 1}, wmod=[w_attr("int", 7, 3)],
         follow=[later(4430, 1)], weight=12, min_age=20)
    _res(add, 9146, "雾进到名字里。你倒在第三层，地图不会再多一页。",
         attrs=lt_all(8, "con", "wis", "int"), death=True, weight=10, min_age=20)
    _must(add, 4430, "底厅。有东西在睡觉，呼吸让灰尘起舞。钥匙在它枕头下。",
          [{"dungeon_run": True}], d0(4431, 4432, 4433, 4434, 9147), min_age=21)
    _res(add, 4431, "你从它的呼吸间隙摸走钥匙。它翻了个身，梦见别人。",
         attrs=ge("agi", 8), effects={"agi": 1, "gold": 6, "wis": 1},
         flags_set={"dungeon_cleared": True, "dungeon_run": None},
         wmod=[w_attr("agi", 8, 3)], follow=[later(4435, 8)], weight=14, min_age=21)
    _res(add, 4432, "你先下手。它没有完全醒来。底厅的灰尘变成你的旗帜。",
         attrs=ge("str", 8), effects={"str": 1, "con": 1, "gold": 5},
         flags_set={"dungeon_cleared": True, "dungeon_run": None},
         wmod=[w_attr("str", 8, 3)], follow=[later(4435, 8)], min_age=21)
    _res(add, 4433, "你对睡着的东西说话。它在梦里答应让路。钥匙自己跳进你手里。",
         attrs=ge("cha", 8), effects={"cha": 2, "wis": 1, "gold": 4},
         flags_set={"dungeon_cleared": True, "dungeon_run": None},
         wmod=[w_attr("cha", 8, 3)], follow=[later(4435, 8)], weight=12, min_age=21)
    _res(add, 4434, "你认出枕头是假的，钥匙在门后。你没有叫醒任何东西。",
         attrs=ge("int", 8), effects={"int": 1, "wis": 1, "gold": 5},
         flags_set={"dungeon_cleared": True, "dungeon_run": None},
         wmod=[w_attr("int", 8, 3)], follow=[later(4435, 8)], weight=12, min_age=21)
    _res(add, 9147, "它醒来。底厅需要一个新的枕头。",
         attrs=lt_all(8, "agi", "str", "cha", "int"), death=True, weight=10, min_age=21)
    _res(add, 4435, "黑井又开了。有人拿着你当年地图的抄本，问第四页怎么走。你说：别走。",
         flags_need=[{"dungeon_cleared": True}], effects={"wis": 2, "cha": 1}, weight=10, min_age=29)
    _res(add, 4440, "你在酒馆听见黑井的笑话。笑话里的人没有回来。中介还在卖地图。",
         effects={"wis": 1}, weight=10, min_age=24)


def _caravan(add) -> None:
    _fork(add, 4500, "商队雇你护卫。路线穿过据说已经没有盗匪的山谷。据说。",
          17, 50, (4501, 4502), group="money")
    _res(add, 4501, "你上了车辕。铃铛很响，像故意通知山谷。",
         effects={"gold": 2, "con": 1}, flags_set={"caravan_guard": True},
         follow=[later(4510, 1)], weight=12, min_age=17, max_age=60)
    _res(add, 4502, "你没有上。商队在晨雾里消失。铃铛声停得太整齐。",
         effects={"wis": 1}, follow=[later(4520, 2)], weight=6, min_age=17, max_age=60)
    _must(add, 4510, "山谷里的“已经没有盗匪”出现了。他们要货，也要你的名字。",
          [{"caravan_guard": True}], d0(4511, 4512, 4513, 4514, 9148), min_age=18)
    _res(add, 4511, "你把第一个冲上来的人连人带马撞开。商队从缺口跑。你最后走。",
         attrs=ge("str", 8), effects={"str": 1, "gold": 4, "cha": 1}, flags_set={"caravan_saved": True},
         wmod=[w_attr("str", 8, 3)], follow=[later(4515, 4)], min_age=18)
    _res(add, 4512, "你把商队带上没有路的坡。盗匪的马不会爬。货掉了两箱，人没掉。",
         attrs=ge("wis", 8), effects={"wis": 1, "agi": 1, "gold": 3}, flags_set={"caravan_saved": True},
         wmod=[w_attr("wis", 8, 3)], follow=[later(4515, 4)], min_age=18)
    _res(add, 4513, "你把他们的头目认成旧识——也许是假的。假的也够用。他们退了。",
         attrs=ge("cha", 8), effects={"cha": 2, "gold": 2},
         flags_set={"caravan_saved": True, "bandit_favor": True},
         wmod=[w_attr("cha", 8, 3)], follow=[later(4516, 5)], weight=12, min_age=18)
    _res(add, 4514, "你把货扔下山谷。人走了。雇主会骂，骂的人还活着。",
         effects={"wis": 1, "gold": -2, "cha": -1}, flags_set={"caravan_fled": True},
         follow=[later(4517, 3)], weight=9, min_age=18)
    _res(add, 9148, "山谷收回了铃铛。商队少了一名护卫，名单上的墨很淡。",
         attrs=lt_all(8, "str", "wis", "cha"), death=True, weight=8, min_age=18)
    _res(add, 4515, "商会把你写成“可雇”。印章比剑亮。你的价钱涨了，风险也是。",
         flags_need=[{"caravan_saved": True}], effects={"gold": 4, "cha": 1},
         flags_set={"guild_trusted": True}, weight=10, min_age=22)
    _res(add, 4516, "盗匪头目派人送酒。酒是真的，附言是：下次别认错人，认对了也行。",
         flags_need=[{"bandit_favor": True}], effects={"wis": 1, "gold": 2, "cha": 1}, weight=10, min_age=23)
    _res(add, 4517, "雇主在城里贴了你的画像，画得很丑。你还是付了两箱货的钱。",
         flags_need=[{"caravan_fled": True}], effects={"gold": -3, "wis": 1, "cha": -1}, weight=10, min_age=21)
    _res(add, 4520, "山谷里找到的车轮还在转，人已经不在。你默默把铃铛埋了。",
         effects={"wis": 1, "con": 1}, weight=10, min_age=19)


def _curse_ring(add) -> None:
    _fork(add, 4550, "你捡到一枚会发热的戒指。戴上的瞬间，远处有什么把头转了过来。",
          16, 50, (4551, 4552), weight=6, group="artifact")
    add({
        "eventId": 4551,
        "desc": "你还是戴了。戒指像一颗小的、属于别人的心脏。",
        "minAge": 16, "maxAge": 60, "naturalUnlock": False, "baseWeight": 11,
        "effects": {"int": 1, "cha": 1},
        "flags": {"cursed_ring": True},
        "flagsDelayed": [{"delay": 3, "flags": {"ring_hungry": True}}],
        "followUp": [later(4560, 3)],
    })
    _res(add, 4552, "你把戒指丢进河里。河面开了一朵没有香味的花，然后合上。",
         effects={"wis": 1}, follow=[later(4565, 7)], weight=8, min_age=16, max_age=60)
    _must(add, 4560, "戒指饿了。它在夜里敲你的骨头，要你给它一个名字，或者一笔血。",
          [{"cursed_ring": True}], d0(4561, 4562, 4563, 9149), min_age=19)
    _res(add, 4561, "你把一袋金币熔进火里喂它。戒指安静了，钱的气味却留下。",
         attrs=ge("gold", 6), effects={"gold": -6, "wis": 1, "int": 1},
         flags_set={"ring_hungry": None, "ring_fed": True},
         wmod=[w_attr("gold", 6, 2, 0.2)], follow=[later(4564, 6)], weight=12, min_age=19)
    _res(add, 4562, "你叫出它真正的名字。戒指结霜，像被认领的狗。",
         attrs=ge("int", 8), effects={"int": 2, "wis": 1},
         flags_set={"ring_hungry": None, "ring_named": True},
         wmod=[w_attr("int", 8, 3)], follow=[later(4566, 8)], min_age=19)
    _res(add, 4563, "你把它撬下来，连一层皮。血把饿喂饱了。你的手指少了一圈温度。",
         attrs=ge("wis", 7), effects={"wis": 1, "con": -1, "cha": 1},
         flags_set={"cursed_ring": None, "ring_hungry": None, "ring_scar": True},
         wmod=[w_attr("wis", 7, 2)], weight=10, min_age=19)
    _res(add, 9149, "戒指要的不是金子，是你。它得到了。",
         attrs=lt_all(8, "int", "wis"), death=True, weight=9, min_age=19)
    _res(add, 4564, "喂过的戒指开始替你开门。门后有时是路，有时是更饿的东西。",
         flags_need=[{"ring_fed": True}], effects={"int": 1, "wis": 1}, weight=10, min_age=25)
    _res(add, 4566, "有人循着真名来找戒指。你把名字写在纸上交给他们，戒指留在手上。",
         flags_need=[{"ring_named": True}], effects={"int": 1, "cha": 1, "gold": 3}, weight=10, min_age=27)
    _res(add, 4565, "七年后河水干了。河床上没有戒指，只有一圈锈，像一枚不肯离开的牙印。",
         effects={"wis": 1}, weight=10, min_age=23)


def _outlaw(add) -> None:
    _fork(add, 4600, "绞架下有人喊你的旧名——也许不是你的。绳子已经很紧。",
          17, 50, (4601, 4605, 4602), group="crime")
    _res(add, 4601, "你砍断绳子。那人落地，咳出一句：三年后还你。",
         attrs=ge("str", 7), effects={"str": 1, "cha": 1}, flags_set={"saved_outlaw": True},
         wmod=[w_attr("str", 7, 3)], follow=[later(4610, 3), later(4614, 9)], min_age=17)
    _res(add, 4605, "你用话把人群转开。绳子还在，人已经没了。你站在空绞架下像个傻子。",
         attrs=ge("cha", 8), effects={"cha": 2, "wis": 1}, flags_set={"saved_outlaw": True},
         wmod=[w_attr("cha", 8, 3)], follow=[later(4610, 3), later(4614, 9)], weight=12, min_age=17)
    _res(add, 4602, "你没有动手。绳子完成了工作。你在夜里把那句旧名嚼了很久。",
         effects={"wis": 1, "con": 1}, flags_set={"watched_hanging": True},
         follow=[later(4615, 5)], weight=6, min_age=17)
    _must(add, 4610, "那人成了帮主。请柬只有一行：来，或不来，都算还过。",
          [{"saved_outlaw": True}], d0(4611, 4612, 4613), min_age=20)
    _res(add, 4611, "你去了。酒是真的，人情也是。你多了一条能走的黑路。",
         attrs=ge("cha", 6), effects={"cha": 1, "gold": 3, "wis": 1},
         flags_set={"outlaw_ally": True}, wmod=[w_attr("cha", 6, 2)], min_age=20)
    _res(add, 4612, "你去了，只听不喝。他把一张旧通缉令烧掉，当礼物。",
         attrs=ge("wis", 7), effects={"wis": 1, "int": 1},
         flags_set={"outlaw_ally": True}, wmod=[w_attr("wis", 7, 2)], min_age=20)
    _res(add, 4613, "你没有去。人情挂在半空，像没砍完的绳子。",
         effects={"wis": 1}, weight=7, min_age=20)
    _res(add, 4614, "九年后，他的孩子来找你，说父亲的故事里你是一阵风。风不会留下地址。",
         flags_need=[{"saved_outlaw": True}], effects={"wis": 2, "cha": 1}, weight=10, min_age=26)
    _res(add, 4615, "有人按那天的绞架画了你。画得不像。你还是把画揭了。",
         flags_need=[{"watched_hanging": True}], effects={"wis": 1, "cha": -1}, weight=10, min_age=22)


def _treasure_map(add) -> None:
    _fork(add, 4650, "你得到半张藏宝图。缺口处有齿痕，像被谁咬走了另一半。",
          18, 45, (4651, 4652), weight=7, group="artifact")
    _res(add, 4651, "你把半张图缝进衬里。走路时纸轻轻响，像提醒你还欠世界一次贪婪。",
         effects={"int": 1}, flags_set={"has_map_half": True},
         follow=[later(4660, 2)], weight=12, min_age=18, max_age=60)
    _res(add, 4652, "你把半张图卖了。买主很急。你的口袋轻了，谣言重了。",
         effects={"gold": 3, "wis": 1}, follow=[later(4669, 4)], weight=7, min_age=18, max_age=60)
    _must(add, 4660, "另一半出现在仇敌——或者只是竞争者——手里。酒馆里两张纸隔桌对视。",
          [{"has_map_half": True}], d0(4661, 4662, 4663, 4670), min_age=20)
    _res(add, 4661, "你用钱把另一半买下来。地图合拢，像一对终于肯说话的唇。",
         attrs=ge("gold", 8), effects={"gold": -8, "int": 1}, flags_set={"has_map_full": True},
         wmod=[w_attr("gold", 8, 2, 0.2)], follow=[later(4664, 2)], weight=12, min_age=20)
    _res(add, 4662, "你把另一半偷走。合拢的声音很轻。对方的咒骂很响。",
         attrs=ge("agi", 8), effects={"agi": 1, "int": 1}, flags_set={"has_map_full": True},
         wmod=[w_attr("agi", 8, 3)], follow=[later(4664, 2)], min_age=20)
    _res(add, 4663, "你提议合伙。对方盯了你很久，点头。贪婪有时也讲信用。",
         attrs=ge("cha", 8), effects={"cha": 1, "wis": 1}, flags_set={"has_map_full": True, "map_partner": True},
         wmod=[w_attr("cha", 8, 3)], follow=[later(4664, 2)], weight=12, min_age=20)
    _res(add, 4670, "你既买不起，也偷不走，话也没说圆。对方把你的半张收进袖子。齿痕对齐的声音很轻。",
         attrs=lt_map(gold=8, agi=8, cha=8), effects={"cha": -1, "gold": -1, "wis": 1},
         flags_set={"has_map_half": None, "map_lost": True},
         follow=[later(4671, 5)], weight=11, min_age=20)
    _must(add, 4664, "标记指向一座没有门的山。风从没有的门里吹出来。",
          [{"has_map_full": True}], d0(4665, 4666, 4667, 9150), min_age=22)
    _res(add, 4665, "你把山壁读成句子。门是一句被写反的话。你把它读正。",
         attrs=ge("int", 8), effects={"int": 2, "gold": 8, "wis": 1},
         flags_set={"treasure_ok": True}, wmod=[w_attr("int", 8, 3)], follow=[later(4668, 6)], weight=14, min_age=22)
    _res(add, 4666, "你把山劈开一条缝。缝里是空的城，灯还亮着。",
         attrs=ge("str", 8), effects={"str": 1, "gold": 6, "con": 1},
         flags_set={"treasure_ok": True}, wmod=[w_attr("str", 8, 3)], follow=[later(4668, 6)], min_age=22)
    _res(add, 4667, "你对风说话。风让开。城里的灯为你亮了一盏。",
         attrs=ge("wis", 8), effects={"wis": 2, "gold": 5, "cha": 1},
         flags_set={"treasure_ok": True}, wmod=[w_attr("wis", 8, 3)], follow=[later(4668, 6)], min_age=22)
    _res(add, 9150, "山把你当成又一个句号。地图在黑暗里自己合拢。",
         attrs=lt_all(8, "int", "str", "wis"), death=True, weight=10, min_age=22)
    _res(add, 4668, "你把空城的事讲给别人听。没人信。你把金币花掉，让金币替你作证。",
         flags_need=[{"treasure_ok": True}],
         effects={"wis": 1, "cha": 1}, weight=10, min_age=28)
    _res(add, 4669, "买主的船沉了。有人说沉在图上缺口的位置。你没有出海去核对。",
         effects={"wis": 1}, weight=10, min_age=22)
    _res(add, 4671, "多年后你在别人的酒话里听见自己的半张图。它已经合上，不合在你手里。",
         flags_need=[{"map_lost": True}], effects={"wis": 1, "cha": -1}, weight=10, min_age=25)


def _hometown_siege(add) -> None:
    _fork(add, 4700, "信使说故乡被围。信纸上还有泥，像刚从城墙上刮下来。",
          20, 55, (4701, 4702, 4703), group="war")
    _res(add, 4701, "你连夜往回走。路比记忆短，恐惧比路长。",
         effects={"con": 1, "wis": 1}, flags_set={"home_siege": True},
         follow=[later(4710, 1)], weight=12, min_age=20, max_age=70)
    _res(add, 4702, "你把钱交给信使，让他雇兵。你自己不回去。钱比你跑得快，也比你更不像亲人。",
         attrs=ge("gold", 8), effects={"gold": -8, "wis": 1}, flags_set={"home_gold": True},
         wmod=[w_attr("gold", 8, 2, 0.2)], follow=[later(4720, 2)], weight=11, min_age=20, max_age=70)
    _res(add, 4703, "你没有回去。信被你叠进包里，像叠进一座暂时还存在的城。",
         effects={"wis": 1, "con": 1}, flags_set={"home_absent": True},
         follow=[later(4721, 3)], weight=6, min_age=20, max_age=70)
    _must(add, 4710, "故乡的城墙缺了一角。缺口里是人，也是火。",
          [{"home_siege": True}], d0(4711, 4712, 4713, 9151), min_age=21)
    _res(add, 4711, "你把缺口用车、门和自己的肩膀堵住。这一夜墙还在。",
         attrs=ge("str", 8), effects={"str": 1, "con": 1, "cha": 1},
         flags_set={"home_held": True}, wmod=[w_attr("str", 8, 3)], follow=[later(4714, 4)], weight=14, min_age=21)
    _res(add, 4712, "你带人从水道反冲。围城的人没有防备自己的屁股。",
         attrs=ge("int", 8), effects={"int": 1, "agi": 1, "wis": 1},
         flags_set={"home_held": True}, wmod=[w_attr("int", 8, 3)], follow=[later(4714, 4)], min_age=21)
    _res(add, 4713, "你把妇孺从缺口送走。城可以丢，名单不能丢。",
         attrs=ge("wis", 8), effects={"wis": 2, "cha": 1},
         flags_set={"home_evacuated": True}, wmod=[w_attr("wis", 8, 3)], follow=[later(4715, 4)], min_age=21)
    _res(add, 9151, "缺口吞人。故乡把你也算进砖里。",
         attrs=lt_all(8, "str", "int", "wis"), death=True, weight=11, min_age=21)
    _res(add, 4714, "围城退了。井水仍有烟味。有人把你的名字刻在补上的那块砖上，刻错了姓。",
         flags_need=[{"home_held": True}], effects={"cha": 1, "wis": 1, "con": 1}, weight=10, min_age=25)
    _res(add, 4715, "城丢了。你在外地的难民营看见邻居。他们问你墙后来怎样。你说：人先怎样。",
         flags_need=[{"home_evacuated": True}], effects={"wis": 2, "cha": 1}, weight=10, min_age=25)
    _res(add, 4720, "雇来的兵到了。城还在。账单也到了。有人说你买的是运气。",
         flags_need=[{"home_gold": True}], effects={"wis": 1, "cha": 1}, weight=10, min_age=22)
    _res(add, 4721, "难民里有故乡的口音。他们不认识你。你把仅剩的干粮分掉一半。",
         flags_need=[{"home_absent": True}], effects={"gold": -2, "wis": 1, "cha": 1}, weight=10, min_age=23)


def _cult(add, job_req) -> None:
    _fork(add, 4750, "龙影教的传单出现在井盖上：世界将在第三次月食结束。月食还有两次。",
          18, 50, (4751, 4752, 4753), group="weird")
    _res(add, 4751, "你混进去听。他们的歌很整齐，整齐得像已经排好谁先死。",
         attrs=ge("cha", 7), effects={"cha": 1, "int": 1}, flags_set={"cult_inside": True},
         wmod=[w_attr("cha", 7, 2)], follow=[later(4760, 2)], min_age=18, max_age=70)
    _res(add, 4752, "你把传单交给神殿。神父说这是第七次世界末日，仍把传单锁进柜子。",
         flags_need=job_req("cleric", "paladin") + [{"faith": True}],
         effects={"wis": 1, "cha": 1}, flags_set={"cult_reported": True},
         follow=[later(4764, 3)], weight=12, min_age=18, max_age=70)
    _res(add, 4753, "你把传单当引火纸。火很普通。你希望末日也普通。",
         effects={"wis": 1}, flags_set={"cult_ignored": True},
         follow=[later(4765, 6)], weight=6, min_age=18, max_age=70)
    _must(add, 4760, "第二次月食。教众要你献一件“活着的东西”。他们看着你的眼睛。",
          [{"cult_inside": True}], d0(4761, 4762, 4763, 9152), min_age=20)
    _res(add, 4761, "你献上一只自己养的鸡，并让他们把仪式做成晚饭。有人怒，有人饿。教裂了一道缝。",
         attrs=ge("int", 8), effects={"int": 1, "wis": 1, "cha": 1},
         flags_set={"cult_broken": True}, wmod=[w_attr("int", 8, 3)], follow=[later(4768, 6)], min_age=20)
    _res(add, 4762, "你当众把教主的预言读反。月食仍发生。预言不发生。人们开始散。",
         attrs=ge("wis", 8), effects={"wis": 2, "cha": 1},
         flags_set={"cult_broken": True}, wmod=[w_attr("wis", 8, 3)], follow=[later(4768, 6)], min_age=20)
    _res(add, 4763, "你把他们带去真的龙洞口。龙打了个哈欠。教众重新评估“龙影”。",
         attrs=ge("cha", 8), effects={"cha": 2, "wis": 1},
         flags_set={"cult_broken": True}, wmod=[w_attr("cha", 8, 3)], follow=[later(4768, 6)], weight=12, min_age=20)
    _res(add, 9152, "他们要的活物是你。月食很美。你没有机会评价。",
         attrs=lt_all(8, "int", "wis", "cha"), death=True, weight=10, min_age=20)
    _res(add, 4764, "神殿组织了一次扫荡。你当向导。柜子里的传单终于被烧掉。",
         flags_need=[{"cult_reported": True}], effects={"wis": 1, "str": 1, "cha": 1}, weight=10, min_age=21)
    _res(add, 4765, "第三次月食过去了。世界还在。井盖上换了新的传单，日期更远。",
         flags_need=[{"cult_ignored": True}], effects={"wis": 1, "int": 1}, weight=10, min_age=24)
    _res(add, 4768, "当年的教众在市集卖菜。有人仍用月食的名字给孩子起名。你买了一把葱。",
         flags_need=[{"cult_broken": True, "cult_inside": True}],
         effects={"wis": 1, "cha": 1}, weight=10, min_age=26)


def _echoes(add) -> None:
    add({
        "eventId": 4800,
        "desc": "有人按战时的番号叫你。你纠正了两次，第三次你应了。",
        "minAge": 25, "maxAge": 90, "baseWeight": 5,
        "requiredFlags": [{"war_veteran": True}],
        "effects": {"wis": 1, "cha": 1},
        "cooldownGroups": ["war_echo"], "cooldownMinInterval": 6,
    })
    add({
        "eventId": 4801,
        "desc": "门卫看见你的无名戒指，少问了一句，多敬了一寸。",
        "minAge": 24, "maxAge": 90, "baseWeight": 5,
        "requiredFlags": [{"royal_favor": True}],
        "effects": {"cha": 1, "gold": 1},
        "cooldownGroups": ["court"], "cooldownMinInterval": 7,
    })
    add({
        "eventId": 4802,
        "desc": "旅店把最好的床给你。老板说：狮口余生的人应当睡得着。",
        "minAge": 20, "maxAge": 85, "baseWeight": 5,
        "requiredFlags": [{"gladiator_fame": True}],
        "effects": {"con": 1, "cha": 1},
        "cooldownGroups": ["arena"], "cooldownMinInterval": 6,
    })
    add({
        "eventId": 4803,
        "desc": "商会的人只问你一句：还接山谷吗。你没有立刻回答。",
        "minAge": 22, "maxAge": 80, "baseWeight": 5,
        "requiredFlags": [{"guild_trusted": True}],
        "effects": {"gold": 2, "wis": 1},
        "cooldownGroups": ["money"], "cooldownMinInterval": 7,
    })
    add({
        "eventId": 4804,
        "desc": "黑井的抄本又出现在黑市。卖主看见你，把价格翻了三倍，又自己撕了。",
        "minAge": 30, "maxAge": 90, "baseWeight": 4,
        "requiredFlags": [{"dungeon_cleared": True}],
        "effects": {"wis": 1, "int": 1},
        "cooldownGroups": ["dungeon"], "cooldownMinInterval": 8,
    })
    add({
        "eventId": 4805,
        "desc": "你的手指在冷天先醒。那圈疤提醒你：有些东西摘下来比戴上贵。",
        "minAge": 22, "maxAge": 90, "baseWeight": 4,
        "requiredFlags": [{"ring_scar": True}],
        "effects": {"wis": 1, "con": 1},
        "cooldownGroups": ["artifact"], "cooldownMinInterval": 8,
    })
    add({
        "eventId": 4806,
        "desc": "夜路有人让行。黑话里夹着你的旧名。你没有接。",
        "minAge": 22, "maxAge": 85, "baseWeight": 4,
        "requiredFlags": [{"outlaw_ally": True}],
        "effects": {"wis": 1, "agi": 1},
        "cooldownGroups": ["crime"], "cooldownMinInterval": 7,
    })
    add({
        "eventId": 4807,
        "desc": "补墙的那块砖还在。错姓被草磨淡了。有孩子把你的故事讲成别人的。",
        "minAge": 28, "maxAge": 95, "baseWeight": 4,
        "requiredFlags": [{"home_held": True}],
        "effects": {"wis": 1, "cha": 1},
        "cooldownGroups": ["war_echo"], "cooldownMinInterval": 8,
    })
