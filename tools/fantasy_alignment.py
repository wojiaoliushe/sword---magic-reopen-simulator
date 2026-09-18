# -*- coding: utf-8 -*-
"""Stamp lawful/chaotic and good/evil on fantasy events, rewrite deeds, add beats."""
from __future__ import annotations

from collections import defaultdict

CODES = ("lg", "ng", "cg", "ln", "cn", "le", "ne", "ce")
DELTA = {
    "lg": (1, 1),
    "ng": (0, 1),
    "cg": (-1, 1),
    "ln": (1, 0),
    "cn": (-1, 0),
    "le": (1, -1),
    "ne": (0, -1),
    "ce": (-1, -1),
}
SKIP_TYPES = {"death", "forced", "fallback"}
SKIP_ID_MAX = 1199
NO_REWRITE_PREFIX = ("ach_", "heritage", "flag_", "talent")
SKIP_VICTIM = {"sickness", "heart", "drown", "fall", "frailty", "wound", "poison", "plague"}

JOB_CODE = {
    "paladin": "lg",
    "cleric": "lg",
    "monk": "ln",
    "fighter": "ln",
    "wizard": "ln",
    "rogue": "cn",
    "ranger": "ng",
    "barbarian": "cn",
    "bard": "cg",
    "sorcerer": "cn",
    "druid": "ng",
    "warlock": "ne",
}
ORIGIN_CODE = {
    "priest": "lg",
    "temple_order": "lg",
    "soldier": "ln",
    "noble": "ln",
    "farmer": "ng",
    "artisan": "ln",
    "merchant": "ln",
    "mage": "cn",
    "street": "cn",
    "tribe": "cg",
}
GROUP_CODE = {
    "church": "lg",
    "fey": "cg",
    "weird": "cn",
    "tavern": "cn",
    "arena": "cn",
    "curse": "ne",
    "undead": "ne",
    "origin_noble": "ln",
    "origin_priest": "lg",
    "origin_soldier": "ln",
    "origin_street": "cn",
    "origin_temple_order": "lg",
    "origin_farmer": "ng",
    "origin_tribe": "cg",
    "job_paladin": "lg",
    "job_cleric": "lg",
    "job_monk": "ln",
    "job_fighter": "ln",
    "job_wizard": "ln",
    "job_rogue": "cn",
    "job_ranger": "ng",
    "job_barbarian": "cn",
    "job_bard": "cg",
    "job_sorcerer": "cn",
    "job_druid": "ng",
    "job_warlock": "ne",
}

GOOD_KW = (
    "帮", "救", "施舍", "放过", "分给", "照顾", "保护", "怜悯", "归还", "原谅",
    "护送", "让给", "收养", "弱者", "治好", "修好", "分享", "捐", "守夜替", "给孩子",
)
EVIL_KW = (
    "灭口", "勒索", "背叛", "出卖", "折磨", "敲诈", "诬", "奴隶", "下毒", "抢来",
    "见死不救", "活祭", "卖人", "栽赃", "拆人", "落井下石",
)
LAW_KW = (
    "法庭", "按律", "告示", "巡夜", "税册", "合同", "誓约", "军纪", "里正", "登记",
    "授勋", "律法", "值班",
)
CHAOS_KW = (
    "黑市", "抗命", "撕掉告示", "撬开", "即兴", "醉后", "不打招呼", "砸开", "逃役",
    "随手改", "违令",
)

LINES = {
    "lg": [
        "你把捡到的钱袋交给巡夜人，还按村约登了记",
        "你护送税车走完山路，车上少的那枚铜是你垫上的",
        "你在法庭上为不识字的农人原样复述他听见的话",
        "你把逃兵送回营地，拦住了准备抽鞭的士官",
        "你守完别人的夜班，把更鼓按时敲响",
        "你修了桥板，还把工钱收据钉在桥头",
        "你把迷途的孩子送到里正处，不收谢礼",
        "你按骑士誓词把剑横在弱者身前，没有多问出身",
        "你把拾荒者领去施粥处，自己排在队尾",
        "你当众归还错发的赏金，账本上多了一条红字",
        "你替受伤的卫兵站岗到换班铃响",
        "你把偷麦的孩子交给家长，求里正改罚为补种",
        "你在瘟疫封路上给隔离的人送水，水桶放在线外",
        "你拒绝私刑，坚持把人送到有证人的地方",
        "你把战利品按军令登记，自己那份写在最后",
        "你为无人认领的死者立了名牌，字迹端正",
        "你把神殿多收的香火钱退回，祭司脸红了一瞬",
        "你护送寡妇去领抚恤，中途没有让她请客",
        "你把找到的誓约残页交还骑士团，不抄走一句",
        "你在雨里把倒塌的路标扶正，方向仍指着村子",
    ],
    "ng": [
        "你把热汤从窗口递出去，不问对方叫什么",
        "你给发烧的陌生人留下药，人走了碗还在",
        "你把斗篷让给淋雨的人，自己挨到旅店",
        "你夜里给流浪狗留了门缝和一块饼",
        "你把最后的干粮掰成两半，一半递给更瘦的那人",
        "你替不会写信的人写下：我还活着",
        "你把走散的羊抱回圈里，牧人睡眼还没睁开",
        "你给井台打了干净的水，先让排队的老人喝",
        "你把伤口包扎好，收了铜又悄悄放回他口袋",
        "你在火场里先抱出孩子，袍子烧了一角",
        "你把能睡的铺让给产妇，自己靠墙坐到天亮",
        "你把多出来的薪柴堆到邻居门口，没有留名",
        "你顺着哭声找到井边的人，把他拉上来",
        "你把旧毯子拆了给两个孩子各改一件",
        "你在路上把刺从马蹄里挑出，马主还在骂天",
        "你把讨饭的人领到灶边，先盛汤再问从哪来",
        "你替战死的人把信送到他母亲手里，没有添字",
        "你把能吃的部分分给病号，自己啃硬皮",
        "你在雪地里把自己的手套塞进陌生人袖管",
        "你看见有人要冻僵，就把火塘让出半边",
    ],
    "cg": [
        "你撬开领主粮仓，麦子连夜进了灾民的口袋",
        "你把不公的告示撕下来，自己用炭写了新的",
        "你放走不该关的囚，锁还挂在空荡的门上",
        "你把税吏的秤砣换成公平的，没有请示任何人",
        "你趁夜把示众的木枷锯开，人已经跑了",
        "你把贵族猎场的篱笆拆出缺口，好让村子的羊进去吃草",
        "你当众把鞭子夺下来折断，围观的人来不及鼓掌",
        "你把奴隶颈环的钥匙丢进河里，请他们自己决定往哪走",
        "你假传撤退令，让不该送死的新兵活着回来",
        "你把禁书抄了三页塞给识字的孩子，封面仍锁着",
        "你把城门门闩从里面打开，难民比卫兵先到",
        "你把审判席的假发摘下来当火种，烤熟了分给冻着的人",
        "你把高利贷的账本浇了酒，字迹开花，债消失了一半",
        "你把绞索改成秋千，广场上的孩子先笑出声",
        "你把巡逻队灌醉，把他们要抓的人送出城",
        "你把神像抬到雨里，让它对着灾民的脸好好看看",
        "你把领主的猎鹰放生，鹰比主人先懂自由",
        "你把军棍插进粪车，队伍只好改道，村子免了一场征发",
        "你把盖章的驱逐令叠成船，放进水沟漂走",
        "你把牢饭加了肉，狱卒来问时你说是猫偷的",
    ],
    "ln": [
        "你把合同读完最后一行才签字，不多也不少",
        "你值班到铃响才离开，钥匙交给下一班的手",
        "你把该交的税一文不少放进箱子，箱子响了一下",
        "你按操典把武器擦到能照见自己，然后收好",
        "你把借条抄成两份，各执一张，日期写清",
        "你在队列里不插队，前面的人慢，你也慢",
        "你把遗失物清点后公示三天，第四天才允许认领",
        "你拒绝提前开城门，即便里面有你认识的人",
        "你把军令复述一遍，确认无误才出发",
        "你把账对到分文不差，多出来的铜单独搁着",
        "你按神殿时刻敲钟，雨大也没有提前",
        "你把誓言写在纸上再烧掉，灰进了鞋里当记性",
        "你把换班的口令说对，才让人通过栅栏",
        "你把该敬礼的时候敬礼，该沉默的时候把嘴闭上",
        "你把地图按北向上折好，交给下一个人",
        "你把请假条按规定格式写完，没有加私人理由",
        "你把赌债按字据还清，牌桌从此对你无趣",
        "你把尸体按风俗朝向安放，不问他活着时站哪边",
        "你把通行证看了两遍，印章模糊就要求重开",
        "你把训练按时开始按时结束，中途没有加私刑",
    ],
    "cn": [
        "你把骰子换成自己的，点数听话了许多",
        "你不打招呼离开佣兵团，背包里多了一块别人的饼",
        "你即兴改路，地图在口袋里没有打开",
        "你把酒钱记在别人名下，自己先走",
        "你把帽徽摘了塞进靴筒，今晚不想被认出来",
        "你把计划撕成条，条随风，人随条",
        "你在仪式中途打了个呵欠，然后从侧门溜走",
        "你把路牌转了九十度，看后来的人怎么骂",
        "你把合同折成飞机扔出窗，签字的事明天再说",
        "你把值班换成去河边看鱼，鱼比口令有趣",
        "你把队伍的行军歌唱成酒馆调，队长的脸皱了",
        "你把别人的马解开缰绳，马自己决定回不回家",
        "你把禁区的绳子当跳绳，跳完再系上，结不一样了",
        "你把今晚的宿营地点改成屋顶，星星比规章亮",
        "你把命令听成了建议，建议被你放进阴沟",
        "你把钱袋口朝下抖了抖，铜币的去向你也不清楚",
        "你把身份换成旅人，旅人没有昨天",
        "你把箭靶搬到树上，谁也没规定靶必须在地上",
        "你把集会的椅子抽走一把，看谁先坐空",
        "你把晨号吹晚了半拍，世界没有因此停止",
    ],
    "le": [
        "你按律没收寡妇逾期未税的田，手续齐全",
        "你用合法的附加税把村子抽干，账本干净得像刀",
        "你当众执行残酷但写在条款里的杖刑",
        "你把逃税的人的名字钉上告示栏，字比人高",
        "你以军纪为名克扣口粮，克扣条上有三枚印章",
        "你把异端按条文送进石室，祈祷被规定为非法",
        "你让债契延期，利息按复利写进边注",
        "你把战俘编成劳役名册，工钱是不被处死",
        "你在法庭上用引用压死求情，引用比泪水硬",
        "你把夜禁提前一个时辰，违者罚款充实金库",
        "你把孤儿送进矿里，文件上写着安置与教育",
        "你把告密奖赏写成制度，邻居开始互相量脚步",
        "你把赦免权卖给付得起的人，贫穷成为罪证",
        "你把火葬改成示众，为了让条文被看见",
        "你把征兵名额精确到户，病弱也有编号",
        "你把神殿座位按捐款排列，跪垫分出贵贱",
        "你把俘虏的武器登记入库，人登记进坟",
        "你把请愿书以格式错误退回，退回即结案",
        "你把连坐写进村约，一人跑，十人修路",
        "你把绞刑改在集市日，好让秩序被记住",
    ],
    "ne": [
        "你把假药卖给赶路的人，瓶上画着很像的叶子",
        "你在战场上翻死者口袋，金币比名字先被记住",
        "你把秘密卖给出价更高的那一边，两边都叫你朋友",
        "你把井水掺进酒里再高价卖，醉得慢，付钱快",
        "你把别人的功劳写进自己的报告，墨不撒谎，人撒谎",
        "你把迷药放进晚宴的盐，醒来时你已经走远",
        "你把人质的信改了两个字，战争因此多停一周，赏金多一袋",
        "你把护身符做成空壳，壳里是砂，砂比神便宜",
        "你把伤兵的药留下自己用，他的呻吟成为背景",
        "你把地图卖给土匪，又卖给卫队，两条路都堵",
        "你把小孩领去“学手艺”，手艺是望风",
        "你把诅咒写在仇人喝过的杯底，杯洗不掉",
        "你把火灾现场的首饰装进口袋，救人的事让给别人",
        "你把盟约的副本藏起一页，缺的那页最贵",
        "你把瘟疫消息晚送两天，好让存货先出手",
        "你把朋友的把柄抄了三份，一份自用两份待价",
        "你把祭品换成朽肉，神如果在意，会来找你",
        "你把临终嘱托听完，遗产指向你事先准备的名字",
        "你把灯油掺水卖给守夜人，夜因此更黑，你更安全",
        "你把求救当成行情，行情好时你才出现",
    ],
    "ce": [
        "你把井里扔进死猫，看谁先喝出味道",
        "你无故砍伤拦路问询的人，血比理由先到",
        "你放火烧空仓，只为看火比月亮高",
        "你把孩子的名字教给魔鬼，换一句听不清的笑",
        "你在桥上抽掉一块板，听下面的水与人同时响",
        "你把神殿的灯油浇到坐垫上，祈祷变成烟",
        "你把醉汉推进河，河接受了一切",
        "你把锁着的马厩打开，再在门口设绊索，看谁先摔",
        "你把瘟疫衣裳挂上集市衣架，价格写着便宜",
        "你把求饶的舌头割下一截，话因此变短",
        "你把村口的井绳割断，渴比法律快",
        "你把婚礼的酒换成溶剂，誓词还没说完杯子先化",
        "你把哨兵的喉咙当成练习，刀法需要活的靶",
        "你把神像的眼睛挖出来当骰子，点数跟谁急",
        "你把产妇的门从外面闩上，听里面自己结束",
        "你把毒药抹在门环上，拜访成为遗产",
        "你把俘虏放进兽笼，自己在外面下注",
        "你把粮种倒进粪坑，明年的饥饿从今天开始",
        "你把求救的火堆浇灭，黑暗里你最清楚路",
        "你把名字刺进仇人的皮肤，字比刀浅，恨比刀深",
    ],
}

FLAVOR = {
    "generic": ["。天还没亮透。", "。有人看见，没有出声。", "。风把这件事吹薄了一点。", "。你没有回头。"],
    "town": ["。街上的泥把脚印留住。", "。摊贩把秤拨回原处。", "。城门的影子刚好移开。"],
    "church": ["。香灰落在袖口。", "。钟声晚半拍。", "。圣像的眼睛仍旧朝前。"],
    "court": ["。书记官的羽毛笔停了一下。", "。旁听席有人把帽子拿下来。"],
    "crime": ["。巷口的狗没有叫。", "。月光只照到刀背。"],
    "social": ["。酒杯碰了一下又分开。", "。有人把这话当成笑话。"],
    "family": ["。灶里的火塌了一截。", "。门口的鞋还是湿的。"],
    "war": ["。旗在烟里辨认自己。", "。号角把句子切断。"],
    "sea": ["。甲板还在咸。", "。浪把这件事拍扁。"],
    "dungeon": ["。火把爆了一颗火花。", "。石头出汗。"],
    "childhood": ["。大人以为你在玩。", "。你的鞋带仍开着。"],
    "job_paladin": ["。誓词在齿间发苦。", "。剑鞘轻敲了一下靴。"],
    "job_rogue": ["。锁孔还温着。", "。口袋比刚才重。"],
    "job_cleric": ["。祷文少了半句。", "。圣水干在手腕上。"],
    "job_bard": ["。弦还在抖。", "。掌声来得不是时候。"],
    "money": ["。铜币的声音比话真。", "。账本合上一角。"],
}

NEW_EVENTS = {
    "lg": [
        (8, 70, "你把逃出的奴隶按律登记为自由民，并护送他们走过税卡。"),
        (12, 60, "你拒绝私了命案，坚持验伤、证人、记录三样齐。"),
        (16, 55, "你把拾到的军饷交还军团，自己的肚子叫了一夜。"),
        (20, 65, "你在封城日给隔离线外送粮，粮袋放在规定的白线外。"),
        (18, 50, "你把错判的人从示众架上解下，补了一份公开的更正。"),
        (14, 70, "你替阵亡骑士把誓词念完，然后把剑按礼仪入鞘。"),
        (10, 40, "你把迷路的朝圣者带到驿站，路费按官价，不收向导钱。"),
        (22, 60, "你把贪墨的账摊在长桌上，请所有人一起算。"),
        (16, 48, "你把即将被充公的农具赎回，收据贴在村庙门口。"),
        (24, 70, "你守着粮仓的钥匙过夜，老鼠来了你也没先盛一碗。"),
    ],
    "ng": [
        (6, 70, "你把身上最后一块干饼掰给更饿的人，自己喝了井水。"),
        (12, 55, "你通宵照看发烧的陌生人，天亮他叫得出你的名字。"),
        (16, 60, "你把能卖的披风换成药，药进了别人的碗。"),
        (8, 40, "你把走丢的孩子背回集市，孩子的糖还含在嘴里。"),
        (20, 65, "你跳进结冰的河把人捞上来，岸上的人开始生火。"),
        (18, 50, "你把床让给产妇，自己坐在门槛上听第一声哭。"),
        (14, 70, "你把旧伤药分给一串伤兵，瓶子见底时你笑了一下。"),
        (10, 45, "你为无人收殓的旅人挖坑，墓碑只写：路过。"),
        (22, 60, "你把讨债的人拦在门外，先让屋里的病人喝完汤。"),
        (16, 55, "你把能避雨的屋檐让给三个人，自己淋着。"),
    ],
    "cg": [
        (14, 55, "你把领主的猎场栅栏锯开，羊比猎人先到青草那里。"),
        (16, 50, "你当众撕掉不准施粥的告示，粥仍在冒热气。"),
        (18, 60, "你把地牢钥匙扔进井里，囚徒比守卫先学会游泳。"),
        (12, 45, "你把税簿最后一页烧掉，穷户的名字变成烟。"),
        (20, 55, "你把绞架改成晾衣架，衣服在风里像旗帜。"),
        (10, 40, "你把城门从里面顶开，灾民的脚步比军令响。"),
        (22, 58, "你把贵族的酒窖打开，酒流向灾年。"),
        (16, 48, "你把奴隶契约当众浸进墨缸，字认不出自己。"),
        (14, 52, "你把禁书拆成纸鸢，孩子比审查官飞得高。"),
        (19, 60, "你把不公平的秤砣换成石头，市场第一次安静。"),
    ],
    "ln": [
        (12, 70, "你把换班口令对了三遍，才把钥匙交出去。"),
        (16, 55, "你拒绝为熟人提前盖章，印章在盒子里睡觉。"),
        (18, 60, "你把军械按编号归位，缺的那一件写进报告。"),
        (10, 50, "你把路税点清，多出的一枚单独存放待查。"),
        (20, 65, "你按时刻表开闸放水，下游的田按时湿。"),
        (14, 45, "你把遗嘱按格式誊抄，一个亲属的名字都没改。"),
        (22, 58, "你在队列里纠正自己的步距，没有纠正别人。"),
        (8, 40, "你把借书按期归还，书页比你的手干净。"),
        (16, 70, "你把夜禁的铃准时敲响，包括你自己在门外。"),
        (24, 60, "你把审讯记录逐字读给被告听，他点头后你才签字。"),
    ],
    "cn": [
        (12, 55, "你把行军路线画成圈，队伍在同一棵树下遇见自己。"),
        (16, 50, "你把骰盅扣在军令上，点数代替长官。"),
        (18, 60, "你把马鞍换到别的马上，两匹马都表示理解。"),
        (10, 45, "你把今晚的岗哨改成看月亮，月亮比偷袭准时。"),
        (20, 55, "你把身份牌扔进河里，河水给你新的姓。"),
        (14, 48, "你把帐篷钉在规定范围外三步，三步刚好能看见河。"),
        (8, 40, "你把课程改成爬树，老师的点名簿落在地上。"),
        (22, 58, "你把酒窖的锁换成自己的，钥匙的去向成为传说。"),
        (16, 52, "你把集会改到屋顶，议题随风减少。"),
        (19, 60, "你把箭袋背反，抽出箭时先抽出一根羽毛。"),
    ],
    "le": [
        (16, 60, "你把欠税名单当众宣读，读完才允许他们回家。"),
        (18, 55, "你按条文把逃亡农奴的家人编入劳役。"),
        (20, 65, "你把示众改到集市高峰，好让罚则被记住。"),
        (14, 50, "你把赦免写成价目表，贫穷的人先被处决。"),
        (22, 58, "你用连坐修完了桥，桥很结实，村很空。"),
        (12, 45, "你把异端的书按目录焚毁，目录本身留下。"),
        (16, 70, "你把口粮克扣写成节约条例，条例比粥厚。"),
        (24, 60, "你把夜禁提前，违禁罚款充实金库，金库有三把锁。"),
        (18, 52, "你把战俘编号后送去采石，编号比名字耐用。"),
        (20, 48, "你在法庭用脚注压垮求情，脚注比哭声长。"),
        (15, 56, "你把乞讨写成违法，罚款刚好够修你的围墙。"),
        (19, 62, "你把忏悔室的内容归档进黑名单，赦免另行计价。"),
        (13, 46, "你把病假一律记为逃役，病死的人仍欠训练。"),
        (21, 58, "你把遗产税提前到人还没咽气，公证人站在床边。"),
        (17, 51, "你把连环保守写进村约，告密有赏，沉默有罪。"),
        (23, 64, "你把神判改成你提前写好的签，签上只有罪。"),
        (11, 43, "你把儿童编进劳役名册，名册的字比手大。"),
        (16, 49, "你把死刑改在晨祷之后，好让秩序沾一点香火。"),
        (20, 55, "你把减刑条例写得很细，细到只有识得起律师的人能读完。"),
    ],
    "ne": [
        (14, 55, "你把过期的药换了标签，病人的感谢来得很快。"),
        (16, 50, "你把两边的军情都卖了，战争因此更公平地糟糕。"),
        (18, 60, "你在废墟里专捡首饰，呼救当作风声。"),
        (12, 45, "你把朋友的把柄抄成三份，一份今晚就用。"),
        (20, 58, "你把瘟疫消息压到存货出清，出清后你才善良。"),
        (10, 40, "你把小孩领去望风，工钱是一块糖和一句闭嘴。"),
        (22, 55, "你把盟约藏起关键页，缺页的价格最高。"),
        (16, 52, "你把伤员的水留下自己喝，他的眼睛还睁着。"),
        (18, 48, "你把诅咒写进情书，情书比刀近。"),
        (19, 60, "你把求救当成拍卖，价高者得你的出现。"),
        (15, 58, "你把解毒剂换成清水，病人的感谢写进你的账。"),
        (21, 62, "你把友军的撤退路线卖给对面，自己先走另一条。"),
        (13, 47, "你把募捐箱的底板做成活动的，善款有两条路。"),
        (17, 53, "你把遗言听成对自己有利的版本，证人只有你。"),
        (23, 61, "你把瘟疫死者的衣物洗了再卖，洗不掉的你不管。"),
        (11, 44, "你把别人的情书拿去要挟，墨比刀便宜。"),
        (19, 57, "你把守夜人灌醉，仓库的门认识你的钥匙。"),
        (14, 49, "你把祭坛后面的暗格掏空，神如果计较会降账。"),
        (20, 54, "你把伤员名单少抄两个，口粮刚好够你多吃。"),
    ],
    "ce": [
        (14, 50, "你把井绳割断，看谁先用衣服去吊桶。"),
        (16, 55, "你把火把扔进谷仓，只为验证干草的脾气。"),
        (12, 45, "你把问路的人推下坡，坡比答案短。"),
        (18, 60, "你把毒药抹在门环上，拜访成为遗产分配。"),
        (20, 52, "你把神殿坐垫浇上油，祈祷的膝盖先着火。"),
        (10, 40, "你把孩子的名字教给不该听见的东西。"),
        (22, 58, "你把粮种倒进河，明年从今天开始饿。"),
        (16, 48, "你把哨兵的喉咙当练习，刀需要温的靶。"),
        (19, 55, "你把俘虏放进兽笼下注，牙齿比骰子响。"),
        (8, 35, "你把死鼠塞进饼炉，饼仍出炉，集市仍排队。"),
        (13, 46, "你把梯子从井口抽走，井底的人还在喊你的名字。"),
        (17, 54, "你把新娘的头纱点火，喜宴改成烟。"),
        (21, 59, "你把俘虏的眼睛蒙上再松开绳，看他们自己找崖。"),
        (15, 50, "你把村里的井盖打开不盖，夜路自己会找到它。"),
        (19, 56, "你把牧师的酒换成溶剂，祝福先烧喉咙。"),
        (23, 63, "你把求饶写成乐谱，音符是叫喊。"),
        (12, 44, "你把门从外面钉死，火从里面开始。"),
        (18, 52, "你把粮袋划开，麦子进河，人进冬天。"),
        (10, 41, "你把路标指向沼泽，自己走干路。"),
    ],
}


def _groups(ev: dict) -> list[str]:
    out = []
    seen = set()
    raw = list(ev.get("cooldownGroups") or [])
    if ev.get("group"):
        raw.append(str(ev["group"]))
    for item in raw:
        name = str(item)
        if name and name not in seen:
            seen.add(name)
            out.append(name)
    return out


def _jobs(ev: dict) -> list[str]:
    out = []
    flags = ev.get("flags") if isinstance(ev.get("flags"), dict) else {}
    if flags.get("job"):
        out.append(str(flags["job"]))
    for group in ev.get("requiredFlags") or []:
        if isinstance(group, dict) and group.get("job"):
            out.append(str(group["job"]))
    return out


def _origins(ev: dict) -> list[str]:
    out = []
    flags = ev.get("flags") if isinstance(ev.get("flags"), dict) else {}
    if flags.get("origin"):
        out.append(str(flags["origin"]))
    for group in ev.get("requiredFlags") or []:
        if isinstance(group, dict) and group.get("origin"):
            out.append(str(group["origin"]))
    return out


def _count_hits(text: str, words: tuple[str, ...]) -> int:
    return sum(1 for w in words if w in text)


def _kw_code(desc: str) -> str | None:
    g = _count_hits(desc, GOOD_KW)
    e = _count_hits(desc, EVIL_KW)
    l = _count_hits(desc, LAW_KW)
    c = _count_hits(desc, CHAOS_KW)
    moral = 1 if g > e else -1 if e > g else 0
    order = 1 if l > c else -1 if c > l else 0
    if moral == 0 and order == 0:
        return None
    for code, delta in DELTA.items():
        if delta == (order, moral):
            return code
    return None


def _group_code(ev: dict) -> str | None:
    eid = int(ev.get("eventId") or 0)
    for job in _jobs(ev):
        if job in JOB_CODE:
            return JOB_CODE[job]
    for origin in _origins(ev):
        if origin in ORIGIN_CODE:
            return ORIGIN_CODE[origin]
    groups = _groups(ev)
    for g in groups:
        if g in GROUP_CODE:
            return GROUP_CODE[g]
        if g.startswith("job_") and g[4:] in JOB_CODE:
            return JOB_CODE[g[4:]]
        if g.startswith("origin_") and g[7:] in ORIGIN_CODE:
            return ORIGIN_CODE[g[7:]]
    if "court" in groups:
        return ("lg", "ln", "le")[eid % 3]
    if "war" in groups:
        return ("lg", "ln", "le", "ce")[eid % 4]
    if "bounty" in groups:
        return ("lg", "le", "ne", "ce")[eid % 4]
    if "crime" in groups:
        return ("le", "ne", "ce")[eid % 3]
    if "money" in groups:
        return ("ln", "ne", "cn")[eid % 3]
    if "social" in groups:
        return ("ng", "cg", "cn", "ne")[eid % 4]
    if "family" in groups or "pet" in groups:
        return ("ng", "ln", None)[eid % 3]
    return None


def _in_pool(ev: dict) -> bool:
    if ev.get("type", "normal") != "normal":
        return False
    if ev.get("naturalUnlock") is False:
        return False
    if ev.get("requiredFlags") or ev.get("requiredAttrs"):
        return False
    if _is_child(ev):
        return False
    groups = set(_groups(ev))
    if "childhood" in groups or "teen" in groups:
        return False
    return True


def _skip_event(ev: dict) -> bool:
    if ev.get("type", "normal") in SKIP_TYPES:
        return True
    eid = int(ev.get("eventId") or 0)
    if eid <= SKIP_ID_MAX:
        return True
    groups = set(_groups(ev))
    if groups & SKIP_VICTIM:
        return True
    if _is_child(ev) or "childhood" in groups or "teen" in groups:
        return True
    return False


_REWRITTEN: set[int] = set()
_LINE_I: dict[str, int] = defaultdict(int)


BAD_FLAG_KEYS = {
    "sick", "plague", "wounded", "wound", "faith", "patron_god", "god_hated",
    "dating", "engaged", "married", "has_apprentice",
}


def _has_bad_flags(ev: dict) -> bool:
    for item in ev.get("requiredFlags") or []:
        if isinstance(item, dict) and any(key in item for key in BAD_FLAG_KEYS):
            return True
    return False


def _keep_original_text(ev: dict) -> bool:
    desc = str(ev.get("desc") or "")
    if desc.startswith("你出身") or desc.startswith("你是一个") or desc.startswith("因为"):
        return True
    if "你成为了" in desc:
        return True
    return False


def _is_child(ev: dict) -> bool:
    try:
        return int(ev.get("maxAge") or 120) <= 16
    except (TypeError, ValueError):
        return False


def _can_rewrite(ev: dict) -> bool:
    eid = int(ev.get("eventId") or 0)
    if 1610 <= eid <= 1621:
        return False
    if 1200 <= eid <= 1360:
        return False
    if _keep_original_text(ev):
        return False
    if _is_child(ev):
        return False
    if _jobs(ev) or _origins(ev):
        return False
    groups = _groups(ev)
    if "childhood" in groups or "teen" in groups:
        return False
    if "class" in groups or ev.get("group") == "class":
        return False
    for g in groups:
        for prefix in NO_REWRITE_PREFIX:
            if g.startswith(prefix):
                return False
        if g.startswith("job_") or g.startswith("origin_") or g.startswith("item_") or g.startswith("skill_"):
            return False
    return True


def _code_to_delta(code: str, strong: bool = False) -> tuple[int, int]:
    order, moral = DELTA[code]
    if strong:
        order = 2 if order > 0 else -2 if order < 0 else 0
        moral = 2 if moral > 0 else -2 if moral < 0 else 0
    return order, moral


def _compose(eid: int, code: str, groups: list[str], child: bool) -> str:
    lines = LINES[code]
    idx = _LINE_I[code]
    _LINE_I[code] = idx + 1
    head = lines[idx % len(lines)]
    if child:
        flavs = FLAVOR["childhood"]
    elif groups and groups[0] in FLAVOR:
        flavs = FLAVOR[groups[0]]
    else:
        flavs = FLAVOR["generic"]
    tail = flavs[(idx + eid) % len(flavs)]
    return head + tail


def _stamp(ev: dict, code: str, rewrite: bool, strong: bool = False) -> None:
    if _is_child(ev) and code in {"le", "ne", "ce"}:
        code = {"le": "ln", "ne": "cn", "ce": "cn"}[code]
    order, moral = _code_to_delta(code, strong)
    fx = ev.get("effects")
    if not isinstance(fx, dict):
        fx = {}
        ev["effects"] = fx
    if order:
        fx["order"] = order
    else:
        fx.pop("order", None)
    if moral:
        fx["moral"] = moral
    else:
        fx.pop("moral", None)
    if rewrite and _can_rewrite(ev):
        ev["desc"] = _compose(int(ev["eventId"]), code, _groups(ev), _is_child(ev))
        _REWRITTEN.add(int(ev["eventId"]))


def _pool_weight(ev: dict) -> int:
    try:
        w = int(ev.get("baseWeight") if ev.get("baseWeight") is not None else 10)
    except (TypeError, ValueError):
        w = 10
    return max(0, w)


def _fx_code(ev: dict) -> str | None:
    fx = ev.get("effects") or {}
    o = int(fx.get("order") or 0)
    m = int(fx.get("moral") or 0)
    o = 1 if o > 0 else -1 if o < 0 else 0
    m = 1 if m > 0 else -1 if m < 0 else 0
    if o == 0 and m == 0:
        return None
    for code, delta in DELTA.items():
        if delta == (o, m):
            return code
    return None


def _abs_sums(rows: list[dict]) -> tuple[int, int, int, int]:
    op = on_ = mp = mn = 0
    for ev in rows:
        if not _in_pool(ev):
            continue
        fx = ev.get("effects") or {}
        w = _pool_weight(ev)
        o = int(fx.get("order") or 0)
        m = int(fx.get("moral") or 0)
        if o > 0:
            op += w * o
        elif o < 0:
            on_ += w * (-o)
        if m > 0:
            mp += w * m
        elif m < 0:
            mn += w * (-m)
    return op, on_, mp, mn


FLIP_MORAL_DOWN = {"ng": "ne", "lg": "le", "cg": "ce"}
FLIP_MORAL_UP = {"ne": "ng", "le": "lg", "ce": "cg"}
FLIP_ORDER_DOWN = {"ln": "cn", "lg": "ng", "le": "ce"}
FLIP_ORDER_UP = {"cn": "ln", "ng": "lg", "ce": "le", "cg": "lg"}


def _code_pool(events: list[dict]) -> dict[str, int]:
    out = {k: 0 for k in CODES}
    for ev in events:
        if not _in_pool(ev):
            continue
        code = _fx_code(ev)
        if code:
            out[code] += _pool_weight(ev)
    return out


def _pick_rewrite(events: list[dict], mapping: dict[str, str]) -> dict | None:
    for ev in events:
        if not _in_pool(ev) or not _can_rewrite(ev):
            continue
        if int(ev["eventId"]) not in _REWRITTEN:
            continue
        code = _fx_code(ev)
        if code in mapping:
            return ev
    return None


def _spread_axis_safe(events: list[dict]) -> bool:
    op, on_, mp, mn = _abs_sums(events)
    weights = _code_pool(events)
    cur = abs(op - on_) + abs(mp - mn)
    for keys in (["le", "ne", "ce"], ["lg", "ng", "cg"], ["ln", "cn"]):
        vals = [weights[k] for k in keys]
        hi, lo = max(vals), min(vals)
        if hi <= int(lo * 1.32) + 80:
            continue
        src = keys[vals.index(hi)]
        best = None
        best_score = None
        for dst in keys:
            if dst == src:
                continue
            so, sm = DELTA[src]
            do, dm = DELTA[dst]
            w = 8
            nop = op + w * (max(do, 0) - max(so, 0))
            non = on_ + w * (max(-do, 0) - max(-so, 0))
            nmp = mp + w * (max(dm, 0) - max(sm, 0))
            nmn = mn + w * (max(-dm, 0) - max(-sm, 0))
            axis = abs(nop - non) + abs(nmp - nmn)
            if axis > cur + 12:
                continue
            score = axis + weights[dst]
            if best_score is None or score < best_score:
                best_score = score
                best = dst
        if not best:
            continue
        ev = _pick_rewrite(events, {src: best})
        if ev:
            _stamp(ev, best, rewrite=True)
            return True
    return False


def _rebalance(events: list[dict]) -> None:
    for _ in range(500):
        op, on_, mp, mn = _abs_sums(events)
        ev = None
        mapping = None
        if mp > int(mn * 1.08) + 30:
            mapping = FLIP_MORAL_DOWN
            ev = _pick_rewrite(events, mapping)
        if ev is None and mn > int(mp * 1.08) + 30:
            mapping = FLIP_MORAL_UP
            ev = _pick_rewrite(events, mapping)
        if ev is None and op > int(on_ * 1.08) + 30:
            mapping = FLIP_ORDER_DOWN
            ev = _pick_rewrite(events, mapping)
        if ev is None and on_ > int(op * 1.08) + 30:
            mapping = FLIP_ORDER_UP
            ev = _pick_rewrite(events, mapping)
        if ev is not None and mapping is not None:
            _stamp(ev, mapping[_fx_code(ev)], rewrite=True)
            continue
        if _spread_axis_safe(events):
            continue
        break


def _choose_code(events: list[dict], used: dict[str, int], weight: int) -> str:
    op, on_, mp, mn = _abs_sums(events)
    w = max(1, weight)
    best = "ln"
    best_score = None
    for code in CODES:
        o, m = DELTA[code]
        nop = op + w * max(o, 0)
        non = on_ + w * max(-o, 0)
        nmp = mp + w * max(m, 0)
        nmn = mn + w * max(-m, 0)
        axis = abs(nop - non) + abs(nmp - nmn)
        score = (axis, used[code])
        if best_score is None or score < best_score:
            best_score = score
            best = code
    return best


def _is_aligned(ev: dict) -> bool:
    fx = ev.get("effects") or {}
    return bool(int(fx.get("order") or 0) or int(fx.get("moral") or 0))


def apply_alignment(events: list[dict], add) -> None:
    _REWRITTEN.clear()
    _LINE_I.clear()
    fill_candidates: list[dict] = []
    for ev in events:
        if _skip_event(ev):
            continue
        kw = _kw_code(str(ev.get("desc") or ""))
        grp = _group_code(ev)
        code = kw or grp
        if code:
            strong = kw is not None and (
                _count_hits(str(ev.get("desc") or ""), EVIL_KW) >= 2
                or _count_hits(str(ev.get("desc") or ""), GOOD_KW) >= 2
            )
            _stamp(ev, code, rewrite=kw is None, strong=strong)
        elif _in_pool(ev):
            fill_candidates.append(ev)

    fill_candidates.sort(key=lambda e: int(e["eventId"]))
    used = defaultdict(int)
    for ev in fill_candidates:
        best = _choose_code(events, used, _pool_weight(ev))
        _stamp(ev, best, rewrite=_can_rewrite(ev), strong=False)
        used[best] += 1

    cover_used = defaultdict(int)
    rot = 0
    leftovers = [
        ev for ev in events
        if ev.get("type", "normal") == "normal"
        and not _skip_event(ev)
        and not _is_aligned(ev)
        and _can_rewrite(ev)
        and not _has_bad_flags(ev)
    ]
    leftovers.sort(key=lambda e: int(e["eventId"]))
    for ev in leftovers:
        if _in_pool(ev):
            best = _choose_code(events, used, _pool_weight(ev))
            _stamp(ev, best, rewrite=True, strong=False)
            used[best] += 1
        else:
            best = CODES[rot % len(CODES)]
            rot += 1
            _stamp(ev, best, rewrite=True, strong=False)
            cover_used[best] += 1

    _rebalance(events)
    existing = {int(ev["eventId"]) for ev in events}
    next_id = 9400
    added = 0
    for code in CODES:
        o, m = DELTA[code]
        rows = list(NEW_EVENTS[code])
        take = min(10, len(rows))
        for min_age, max_age, desc in rows[:take]:
            while next_id in existing:
                next_id += 1
            if next_id > 9699:
                break
            fx = {}
            if o:
                fx["order"] = o
            if m:
                fx["moral"] = m
            add({
                "eventId": next_id,
                "desc": desc,
                "minAge": min_age,
                "maxAge": max_age,
                "effects": fx,
                "cooldownGroups": [f"align_{code}"],
                "cooldownMinInterval": 5,
                "baseWeight": 8,
            })
            existing.add(next_id)
            next_id += 1
            added += 1

    _rebalance(events)

    n_align = sum(
        1 for ev in events
        if int((ev.get("effects") or {}).get("order") or 0)
        or int((ev.get("effects") or {}).get("moral") or 0)
    )
    op, on_, mp, mn = _abs_sums(events)
    pool = _code_pool(events)
    codes = " ".join(f"{k}={pool[k]}" for k in CODES)
    print(
        f"alignment stamped {n_align}/{len(events)} "
        f"({100 * n_align / max(1, len(events)):.0f}%) "
        f"pool序乱 +{op}/-{on_} 善恶 +{mp}/-{mn} added={added} [{codes}]"
    )


if __name__ == "__main__":
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    path = root / "data" / "fantasy" / "events.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    events = data["events"]
    ids = {int(ev["eventId"]) for ev in events}

    def add(event: dict) -> None:
        eid = int(event["eventId"])
        if eid in ids:
            return
        ids.add(eid)
        events.append(event)

    apply_alignment(events, add)
    path.write_text(json.dumps({"events": events}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(events)} events to {path}")
