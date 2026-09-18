# -*- coding: utf-8 -*-
"""Rewrite gated event text so players can feel the check without numbers."""
from __future__ import annotations

JOB = {
    "fighter": "战士",
    "paladin": "圣武士",
    "cleric": "牧师",
    "wizard": "法师",
    "rogue": "盗贼",
    "ranger": "游侠",
    "barbarian": "野蛮人",
    "bard": "吟游诗人",
    "sorcerer": "术士",
    "druid": "德鲁伊",
    "monk": "武僧",
    "warlock": "魔契师",
}

ORIGIN = {
    "priest": "牧师家庭",
    "soldier": "军人家庭",
    "mage": "法师家庭",
    "merchant": "商人家庭",
    "farmer": "农人家庭",
    "artisan": "工匠家庭",
    "street": "街头",
    "noble": "贵族",
    "tribe": "氏族部落",
    "temple_order": "骑士团",
}

RACE = {
    "human": "人类",
    "elf": "精灵",
    "dwarf": "矮人",
    "halfling": "半身人",
    "gnome": "侏儒",
    "half_orc": "半兽人",
    "half_elf": "半精灵",
    "dragonborn": "龙裔",
    "tiefling": "提夫林",
}

ITEM = {
    "has_sword": "长剑",
    "has_masterwork": "那柄好剑",
    "has_pet": "兽伴",
    "has_mount": "坐骑",
    "has_house": "能锁门的小屋",
    "item_silver_blade": "银刃短剑",
    "item_oak_bow": "橡木弓",
    "item_twin_axe": "双头斧",
    "item_rapier": "刺剑",
    "item_iron_spear": "铁矛",
    "item_scale_mail": "鳞甲",
    "item_shadow_cloak": "影斗篷",
    "item_lucky_ring": "幸运戒指",
    "item_iron_boots": "铁靴",
    "item_deer_gloves": "鹿皮手套",
    "item_thief_tools": "开锁工具",
    "item_alembic": "蒸馏瓶",
    "item_miner_lamp": "矿灯",
    "item_star_astrolabe": "星盘",
    "item_craft_hammer": "工匠锤",
    "item_heal_potion": "治疗药水",
    "item_invis_phial": "隐身药",
    "item_antitoxin": "解毒剂",
    "item_rage_phial": "怒气药",
    "item_sleep_dust": "睡粉",
    "item_talking_skull": "会说话的头骨",
    "item_path_compass": "寻路罗盘",
    "item_fold_boat": "折叠船",
    "item_endless_sack": "无底袋",
    "item_memory_crystal": "记忆晶石",
    "item_pardon": "赦书",
    "item_noble_letter": "贵族荐信",
    "item_fake_papers": "假文书",
    "item_map_scrap": "残图",
    "item_pact_copy": "契约抄本",
    "item_holy_water": "圣水",
    "item_druid_seed": "林地的种子",
    "item_dragon_scale": "龙鳞",
    "item_fey_bell": "妖精铃",
    "item_dead_coin": "死人钱",
    "item_coin_mold": "铸币模",
    "item_run_purse": "跑路钱袋",
    "item_tax_stamp": "税印",
    "item_pearl_ear": "珍珠耳坠",
    "item_ivory_chess": "象牙棋",
    "item_phoenix_feather": "凤凰羽",
    "item_basilisk_eye": "石化蜥眼",
    "item_hive_jar": "蜂罐",
    "item_owl_whistle": "枭哨",
    "item_wolf_tooth": "狼牙",
    "item_thirst_dagger": "渴血匕首",
    "item_whisper_mask": "耳语面具",
    "item_black_candle": "黑烛",
    "item_upside_glass": "颠倒镜",
    "item_nameless_ash": "无名骨灰",
}

SKILL = {
    "skill_shield_bash": "盾击",
    "skill_double_cut": "连斩",
    "skill_throwing": "投掷",
    "skill_trip": "绊摔",
    "skill_sunder": "破甲",
    "skill_magic_missile": "魔法飞弹",
    "skill_mage_armor": "法师护甲",
    "skill_detect_illusion": "识破幻术",
    "skill_grease": "油腻术",
    "skill_flash": "闪光",
    "skill_heal": "治疗术",
    "skill_turn_undead": "驱散亡灵",
    "skill_bless": "祝福",
    "skill_holy_light": "圣光",
    "skill_calm": "安定心神",
    "skill_beast_speech": "兽语",
    "skill_entangle": "纠缠",
    "skill_water_walk": "水上行走",
    "skill_bird_message": "鸟传信",
    "skill_barkskin": "树肤",
    "skill_silent_step": "无声步",
    "skill_lockpick": "开锁",
    "skill_disguise": "易容",
    "skill_shadow_hide": "匿影",
    "skill_poisoner": "用毒",
    "skill_war_song": "战歌",
    "skill_lullaby": "催眠曲",
    "skill_satire": "讽刺",
    "skill_memory_ballad": "记忆谣",
    "skill_countercharm": "反魅惑",
    "skill_iron_bone": "铁骨",
    "skill_hold_breath": "闭气",
    "skill_bell_body": "金钟罩",
    "skill_light_step": "轻身",
    "skill_cold_resist": "耐寒",
    "skill_lip_read": "读唇",
    "skill_detect_lie": "识谎",
    "skill_steady": "心如止水",
    "skill_dream_recall": "梦忆",
    "skill_mind_ward": "护心",
    "skill_enchant_weapon": "附魔武器",
    "skill_alchemy": "炼金",
    "skill_temper": "淬火",
    "skill_survey": "勘测",
    "skill_cook_magic": "魔法烹调",
    "skill_blood_rite": "血仪",
    "skill_dead_whisper": "亡语",
    "skill_raise_pact": "唤契",
    "skill_fate_thread": "命运线",
    "skill_feign_death": "假死",
}

BOOL_YES = {
    "faith": "因为你心里有神",
    "lucky": "运气站在你这边",
    "keen_senses": "因为你耳目比常人尖",
    "long_lived": "因为你的岁月还长",
    "stout": "因为你天生禁得起折腾",
    "stone_blood": "因为你的血像石头一样沉",
    "small_stature": "因为你身形小，空隙对你是路",
    "tinkerer": "因为你手能让死物重新讲理",
    "savage": "因为你身上那股让人先退一步的气",
    "two_worlds": "因为你两边的话都能接上",
    "dragon_breath": "因为你气息里还留着热",
    "infernal": "因为凡火不太敢咬你",
    "stigma": "因为别人先看见你的角，再看见你",
    "versatile": "因为你什么都肯学一点",
    "liturgy": "因为祷词在你嘴里有形状",
    "drill": "因为口令长在你骨头里",
    "arcane_tutelage": "因为符文对你不是外国话",
    "ledger": "因为账本对你像家谱",
    "soil_sense": "因为地会跟你说话",
    "craft_eye": "因为裂和钉你一眼能分清",
    "streetwise": "因为巷子的规矩你比卫兵熟",
    "heraldry": "因为袖扣和纹章对你不是装饰",
    "ancestral_fire": "因为风和火是你的亲戚",
    "oath_child": "因为誓言比玩具先到你手里",
    "choir_voice": "因为你起个头，别人就肯跟着",
    "watch_habit": "因为你值夜时比钟准",
    "cantrip_spark": "因为你指尖比火折子快",
    "credit_name": "因为你的名字能当几天押金",
    "weather_eye": "因为天色你比公鸡先看见",
    "maker_mark": "因为钉子上的手你认得",
    "rooftop_path": "因为瓦对你比石板熟",
    "court_manners": "因为头衔和叉子你都怕用错，所以更小心",
    "wild_track": "因为雨洗过的脚印你还读得动",
    "squire_token": "因为骑士团的规矩还在你膝盖上",
    "in_guild": "因为公会还认你的名",
    "guild_settled": "因为你已经不是见习栏里的人",
    "enlisted": "因为你身上还有编号",
    "knows_old_tongue": "因为古碑上的字你读得顺",
    "has_child": "因为家里有人等你回来",
    "has_apprentice": "因为有人还管你叫老师",
    "married": "因为你已经把戒指戴上了",
    "in_school": "因为你还在名册上",
}

BOOL_NO = {
    "faith": "你并不把神明放在嘴边",
    "lucky": "运气这回没站在你这边",
    "keen_senses": "你的耳朵并不比别人尖",
    "long_lived": "你的岁月并没有余量可挥霍",
    "stout": "你禁不起这样的折腾",
    "stone_blood": "粉尘对你并不手软",
    "small_stature": "你的身形挡不住迎面来的东西",
    "tinkerer": "死物不肯听你的话",
    "savage": "你吓不住人，也由不得人怕你",
    "two_worlds": "两边的桌子都不完全是你的",
    "dragon_breath": "你的气息里没有能点亮夜路的热",
    "infernal": "凡火并不认得你",
    "stigma": "神殿没有多看你一眼，也没有少看你一眼",
    "versatile": "你顶不上那个空出来的行当",
    "liturgy": "祷词在你嘴里只是声音",
    "drill": "口令对你只是喊声",
    "arcane_tutelage": "符文对你仍是外国话",
    "ledger": "账本对你只是纸",
    "soil_sense": "地不跟你说话",
    "craft_eye": "裂和钉在你眼里都是一样的铁",
    "streetwise": "巷子的规矩你并不比卫兵熟",
    "heraldry": "袖扣对你只是扣子",
    "ancestral_fire": "风和火并不把你当亲戚",
    "oath_child": "誓言对你还太重",
    "choir_voice": "你起不了那个头",
    "watch_habit": "值夜的钟点你并不比别人准",
    "cantrip_spark": "你的指尖点不亮蜡烛",
    "credit_name": "你的名字当不了押金",
    "weather_eye": "天色并不先告诉你",
    "maker_mark": "钉子上的手你认不得",
    "rooftop_path": "瓦对你仍是屋顶",
    "court_manners": "头衔和叉子你都可能用错",
    "wild_track": "雨洗过的脚印你读不动",
    "squire_token": "骑士团的规矩不在你膝盖上",
    "has_sword": "没有趁手的武器",
    "has_masterwork": "你手里没有那柄靠得住的剑",
    "has_pet": "身边没有兽替你先醒",
    "has_mount": "你没有马可以催",
    "has_house": "你没有一扇能锁上的门",
    "in_guild": "公会并不认你的名",
    "knows_old_tongue": "碑上的字对你只是花纹",
    "in_school": "你不在名册上",
}

STATUS_FLAGS = {
    "sick", "wounded", "poisoned", "plague", "failing_heart", "cursed_moon",
    "cursed_ring", "ring_hungry", "engaged", "dating", "married", "has_child",
}
ATTR_OK_MARK = ("轻松", "聪明的你", "很快就", "身法轻巧", "一眼就", "身子骨硬朗", "能说会道", "钱袋够", "掏得出钱", "一身力气")
ATTR_FAIL_MARK = ("用尽力气", "绞尽脑汁", "手脚不听", "察觉得太晚", "撑不住", "话说得再漂亮", "钱不够", "钱袋空")


def apply_gate_voice(events: list[dict]) -> None:
    for ev in events:
        if ev.get("type") in {"fallback"}:
            continue
        eid = int(ev.get("eventId") or 0)
        if 1001 <= eid <= 1230:
            continue
        flags = ev.get("requiredFlags") or []
        attrs = ev.get("requiredAttrs") or {}
        if not flags and not attrs:
            continue
        desc = ev.get("desc") or ""
        if not desc:
            continue
        ev["desc"] = _voice(desc, flags if isinstance(flags, list) else [], attrs if isinstance(attrs, dict) else {})


def _voice(desc: str, groups: list, attrs: dict) -> str:
    desc = _voice_attr(desc, attrs)
    clause = _flag_clause(desc, groups)
    if not clause:
        return desc
    if desc.startswith(clause) or desc.startswith(clause + "，") or desc.startswith(clause + "。"):
        return desc
    return f"{clause}，{desc}"


def _attr_spec(spec):
    if isinstance(spec, dict) and "operator" in spec:
        return str(spec.get("operator") or "=="), spec.get("value")
    return ">=", spec


def _voice_attr(desc: str, attrs: dict) -> str:
    if not attrs:
        return desc
    fails = []
    oks = []
    for key, spec in attrs.items():
        op, val = _attr_spec(spec)
        if op in ("<", "<="):
            fails.append(key)
        elif op in (">", ">="):
            oks.append(key)
    if fails:
        if any(m in desc for m in ATTR_FAIL_MARK):
            return desc
        return _attr_fail(desc, fails[0])
    if oks:
        if any(m in desc for m in ATTR_OK_MARK):
            return desc
        primary = oks[0]
        for prefer in ("str", "agi", "int", "wis", "con", "cha", "gold"):
            if prefer in oks:
                primary = prefer
                break
        _op, val = _attr_spec(attrs[primary])
        return _attr_ok(desc, primary, val)
    return desc


def _rest(desc: str) -> str:
    if desc.startswith("你"):
        return desc[1:]
    return desc


def _attr_ok(desc: str, attr: str, value=None) -> str:
    rest = _rest(desc)
    if attr == "str":
        if rest.startswith("徒手"):
            return "你凭着一身力气，" + rest
        if rest.startswith(("把", "用", "举起", "掰", "挪", "扛", "推", "拉开", "握住")):
            return "你轻松" + rest
        return "你凭着力气，轻松就" + rest
    if attr == "agi":
        return "身法轻巧的你，" + rest
    if attr == "int":
        return "聪明的你很快就" + rest
    if attr == "wis":
        return "心细的你，" + rest
    if attr == "con":
        return "身子骨硬朗的你，" + rest
    if attr == "cha":
        return "能说会道的你，" + rest
    if attr == "gold":
        try:
            n = int(value or 0)
        except (TypeError, ValueError):
            n = 8
        if n <= 2:
            return "你还掏得出一笔小钱，" + desc
        return "钱袋够用，" + desc
    return desc


def _attr_fail(desc: str, attr: str) -> str:
    rest = _rest(desc)
    if attr == "str":
        return "你用尽力气，却还是" + rest
    if attr == "agi":
        return "你手脚不听使唤，" + desc
    if attr == "int":
        return "你绞尽脑汁，却还是" + rest
    if attr == "wis":
        return "你察觉得太晚，" + desc
    if attr == "con":
        return "你的身子骨撑不住，" + desc
    if attr == "cha":
        return "你把话说得再漂亮也没用，" + desc
    if attr == "gold":
        return "钱不够，" + desc
    return desc


def _flag_clause(desc: str, groups: list) -> str:
    parsed = []
    for g in groups:
        if isinstance(g, dict) and g:
            parsed.append(g)
    if not parsed:
        return ""
    if len(parsed) == 1:
        parts = _and_parts(desc, parsed[0])
        return "，".join(parts) if parts else ""
    return _or_cover(desc, parsed)


def _mentioned(desc: str, *needles: str) -> bool:
    return any(n and n in desc for n in needles)


def _and_parts(desc: str, group: dict) -> list[str]:
    parts = []
    job = group.get("job")
    origin = group.get("origin")
    race = group.get("race")
    identity_in_text = False
    if job is False:
        parts.append("因为你不是干那一行的人")
    elif isinstance(job, str):
        name = JOB.get(job, "")
        if name and not _mentioned(desc, name, "这门行当", "这一行"):
            if job == "paladin" and any(w in desc for w in ("不能", "不许", "拒绝", "没能")):
                parts.append("因为你是圣武士，誓言不允许你随便来")
            else:
                parts.append(f"因为你是{name}")
        else:
            identity_in_text = True
    if origin is False:
        parts.append("因为你不是那种出身")
    elif isinstance(origin, str):
        clause = _origin_yes(origin)
        name = ORIGIN.get(origin, "")
        if clause and not _mentioned(desc, "出身", name, "贵族", "街头", "骑士团"):
            if origin == "noble" and any(w in desc for w in ("不能", "不许", "拒绝", "没能", "荣誉")):
                parts.append("因为你是个贵族，荣誉不允许你乱来")
            else:
                parts.append(clause)
        else:
            identity_in_text = True
    if race is False:
        parts.append("因为你并没有那种血统")
    elif isinstance(race, str):
        name = RACE.get(race, "")
        if name and not _mentioned(desc, name, "血脉", "血统", "你是一个"):
            parts.append(f"因为你是{name}")
        else:
            identity_in_text = True
    if identity_in_text:
        return parts
    for key, val in group.items():
        if key in {"job", "origin", "race"} or key in STATUS_FLAGS:
            continue
        part = _kv_part(desc, key, val)
        if part:
            parts.append(part)
    return parts


def _origin_yes(origin: str) -> str:
    if origin == "noble":
        return "因为你是个贵族"
    if origin == "street":
        return "因为你是在街头长大的"
    if origin == "temple_order":
        return "因为你是在骑士团院长大的"
    if origin == "tribe":
        return "因为你出身氏族"
    name = ORIGIN.get(origin)
    if not name:
        return ""
    return f"因为你出身{name}"


def _job_cover(jobs: set[str]) -> str:
    if len(jobs) == 1:
        name = JOB.get(next(iter(jobs)), "")
        return f"因为你是{name}" if name else "凭你这门行当"
    if jobs <= {"paladin", "cleric"}:
        return "因为你侍奉神明"
    if jobs <= {"wizard", "sorcerer", "warlock"}:
        return "因为你会法术"
    if jobs <= {"fighter", "paladin", "barbarian"}:
        return "因为你是习武之人"
    if jobs <= {"rogue", "bard", "monk"}:
        return "因为你擅长手法和走位"
    if jobs <= {"druid", "ranger"}:
        return "因为你跟荒野打过交道"
    if jobs <= {"fighter", "paladin", "ranger", "rogue", "barbarian", "monk"}:
        return "因为你是能动手的人"
    if jobs <= {"wizard", "sorcerer", "warlock", "bard", "cleric", "druid"}:
        return "因为你会弄超凡的手段"
    names = [JOB[j] for j in jobs if j in JOB]
    if len(names) == 1:
        return f"因为你是{names[0]}"
    return "凭你这门行当"


def _or_cover(desc: str, groups: list[dict]) -> str:
    if any(g.get("faith") is True for g in groups) and "心里有神" not in desc and "侍奉神明" not in desc:
        jobs = {g["job"] for g in groups if isinstance(g.get("job"), str)}
        if not jobs or jobs <= {"cleric", "paladin"}:
            return "因为你心里有神"
    if all(list(g.keys()) == ["job"] for g in groups):
        jobs = {g["job"] for g in groups if isinstance(g.get("job"), str)}
        names = [JOB[j] for j in jobs if j in JOB]
        if _mentioned(desc, *names):
            return ""
        return _job_cover(jobs)
    if all(list(g.keys()) == ["origin"] for g in groups):
        origins = {g["origin"] for g in groups if isinstance(g.get("origin"), str)}
        names = [ORIGIN[o] for o in origins if o in ORIGIN]
        if _mentioned(desc, "出身", *names):
            return ""
        if origins == {"street", "merchant"}:
            return "因为你在市井里混过"
        if len(origins) == 1:
            return _origin_yes(next(iter(origins)))
        return "因为你的出身在这件事上用得上"
    if all(list(g.keys()) == ["race"] for g in groups):
        races = {g["race"] for g in groups if isinstance(g.get("race"), str)}
        names = [RACE[r] for r in races if r in RACE]
        if _mentioned(desc, "你是一个", "血脉", "血统", *names):
            return ""
        if races <= {"elf", "half_elf"}:
            return "因为你身上有精灵的血"
        if len(races) == 1:
            return f"因为你是{RACE[next(iter(races))]}"
        return "因为你的血统在这件事上用得上"
    jobs = {g["job"] for g in groups if isinstance(g.get("job"), str)}
    origins = {g["origin"] for g in groups if isinstance(g.get("origin"), str)}
    races = {g["race"] for g in groups if isinstance(g.get("race"), str)}
    if jobs and all("job" in g for g in groups):
        names = [JOB[j] for j in jobs if j in JOB]
        if not _mentioned(desc, *names, "行当"):
            return _job_cover(jobs)
    if jobs or origins or races:
        return "凭你眼下这身来历"
    return ""


def _kv_part(desc: str, key: str, val) -> str:
    if key in STATUS_FLAGS:
        return ""
    if key in ITEM:
        name = ITEM[key]
        if val is False:
            if _mentioned(desc, "没有趁手", "没有那柄", "手里没有", name):
                return ""
            if key in {"has_sword", "has_masterwork"}:
                return "没有趁手的武器"
            return f"你手里没有{name}"
        if _mentioned(desc, name, "抽出", "磨亮", "剑", "弓", "斧", "矛", "刃"):
            return ""
        if key in {"has_sword", "has_masterwork", "item_silver_blade", "item_rapier", "item_twin_axe", "item_iron_spear", "item_thirst_dagger"}:
            return f"因为你手握{name}"
        if key == "has_pet":
            return "因为有兽伴在你身边"
        if key == "has_mount":
            return "因为你还有坐骑可催"
        if key == "has_house":
            return "因为你有一扇能锁上的门"
        return f"因为你带着{name}"
    if key in SKILL:
        name = SKILL[key]
        if val is False:
            return f"你还不会{name}" if not _mentioned(desc, name) else ""
        if _mentioned(desc, name):
            return ""
        return f"因为你会{name}"
    if val is False:
        text = BOOL_NO.get(key, "")
        if text and (text in desc or desc.startswith(text[:6]) or desc.startswith("你不会")):
            return ""
        if text:
            return text
        if key.startswith("item_"):
            return "你手里没有那件该用的东西"
        if key.startswith("skill_"):
            return "你还不会那门本事"
        return ""
    if val is True:
        text = BOOL_YES.get(key, "")
        if text and not _mentioned(desc, text[2:6] if len(text) > 6 else text):
            return text
        return ""
    return ""
