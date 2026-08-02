from dataclasses import dataclass


RARITY_ORDER: tuple[str, ...] = (
    "F",
    "E",
    "D",
    "C",
    "B",
    "A",
    "S",
    "SS",
    "SR",
    "UR",
)

# Relative appearance weights used when generating each hourly shop.
# The steep falloff makes powerful cards genuinely difficult to find.
RARITY_APPEARANCE_WEIGHTS: dict[str, float] = {
    "F": 1000.0,
    "E": 500.0,
    "D": 250.0,
    "C": 120.0,
    "B": 60.0,
    "A": 25.0,
    "S": 8.0,
    "SS": 2.0,
    "SR": 0.5,
    "UR": 0.1,
}

RARITY_STOCK: dict[str, int] = {
    "F": 12,
    "E": 10,
    "D": 9,
    "C": 7,
    "B": 5,
    "A": 4,
    "S": 3,
    "SS": 2,
    "SR": 1,
    "UR": 1,
}


@dataclass(frozen=True)
class CardDefinition:
    card_id: str
    name: str
    set_name: str
    rarity: str
    price: int
    emoji: str
    description: str


@dataclass(frozen=True)
class CardGameplayDetails:
    abilities: tuple[str, ...]
    game_effect: str
    power_level: str


CARD_CATALOG: tuple[CardDefinition, ...] = (
    CardDefinition("ember-fox", "Ember Fox", "Wildfire", "F", 50, "🦊", "A quick little fox with a tail like a campfire."),
    CardDefinition("moon-moth", "Moon Moth", "Nightfall", "F", 75, "🦋", "Drawn to moonlight and quiet collector shelves."),
    CardDefinition("tide-rider", "Tide Rider", "Deep Blue", "E", 150, "🌊", "A wave-surfing hero from the edge of the map."),
    CardDefinition("iron-golem", "Iron Golem", "Foundry", "D", 300, "🗿", "Built for the arena and impossible to knock down."),
    CardDefinition("sky-whale", "Sky Whale", "Cloudbound", "C", 650, "🐋", "A gentle giant drifting above the weather."),
    CardDefinition("crystal-witch", "Crystal Witch", "Arcana", "C", 800, "🔮", "She keeps a spell for every kind of bad luck."),
    CardDefinition("neon-ninja", "Neon Ninja", "Afterdark", "B", 1400, "🥷", "Silent, speedy, and brighter than the city skyline."),
    CardDefinition("storm-dragon", "Storm Dragon", "Tempest", "A", 2800, "🐉", "A legendary storm given scales and wings."),
    CardDefinition("solar-knight", "Solar Knight", "Celestial", "S", 5500, "☀️", "The last guardian of a fading sun."),
    CardDefinition("void-oracle", "Void Oracle", "Beyond", "SS", 10000, "👁️", "A mysterious seer who has already seen this pull."),
    CardDefinition("aurora-spirit", "Aurora Spirit", "Celestial", "SR", 20000, "🌌", "A once-in-a-lifetime shimmer in card form."),
    CardDefinition("golden-comet", "Golden Comet", "Treasures", "UR", 50000, "☄️", "The rarest flash across the collector's sky."),
)


# Arabic combat-skill cards supplied for the expanded card collection. The
# first and second batches share "قبضة قوية" and "نفس طويل"; each is included
# once with the description from the larger batch.
ADDITIONAL_CARD_DATA: tuple[tuple[str, str, str, str, str], ...] = (
    # F
    ("quick-glance", "نظرة خاطفة", "F", "تزيد دقة الهجوم القادم", "👀"),
    ("beginner-luck", "حظ مبتدئ", "F", "ترفع فرصة الضربة القوية", "🍀"),
    ("light-fist", "قبضة خفيفة", "F", "زيادة بسيطة في الضرر", "👊"),
    ("focus", "تركيز", "F", "يرفع الدقة لمدة جولة", "🎯"),
    ("second-wind", "نفس طويل", "F", "استرجاع جزء من الطاقة", "🌬️"),
    # E
    ("swift-attack", "هجوم خاطف", "E", "تضرب قبل الخصم مرة واحدة", "🏹"),
    ("light-shield", "درع خفيف", "E", "يقلل ضرر هجمة واحدة", "🛡️"),
    ("energy-charge", "شحنة طاقة", "E", "تزيد الطاقة", "🔋"),
    ("quick-parry", "صد سريع", "E", "تصد ضربة عادية", "⚔️"),
    ("rush", "اندفاع", "E", "يزيد سرعة القتال", "🏃"),
    # D
    ("defense-break", "كسر الدفاع", "D", "يخفض دفاع الخصم", "🔨"),
    ("bleeding", "نزيف", "D", "يسبب ضرر مستمر", "🩸"),
    ("disable", "تعطيل", "D", "يمنع مهارة الخصم القادمة", "🚫"),
    ("regeneration", "تجديد", "D", "استرجاع صحة", "💚"),
    ("power-up", "زيادة قوة", "D", "رفع الهجوم مؤقتًا", "⬆️"),
    # C
    ("double-strike", "ضربة مزدوجة", "C", "تنفيذ هجومين", "✌️"),
    ("reflection", "انعكاس", "C", "يرجع جزء من الضرر", "🪞"),
    ("poison", "سم", "C", "ضرر مع الوقت", "☠️"),
    ("freeze", "تجميد", "C", "يبطئ الخصم", "❄️"),
    ("shock", "صدمة", "C", "تقليل طاقة الخصم", "⚡"),
    # B
    ("steel-shield", "درع فولاذي", "B", "تقليل الضرر بشكل كبير", "🔩"),
    ("absorption", "امتصاص", "B", "تحويل جزء من الضرر لصحة", "🌀"),
    ("full-protection", "حماية كاملة", "B", "إلغاء هجمة قوية", "🏰"),
    ("resistance", "مقاومة", "B", "تقليل تأثير المهارات", "🧱"),
    ("energy-barrier", "حاجز طاقة", "B", "منع ضرر معين", "🔰"),
    # A
    ("power-steal", "سرقة قوة", "A", "أخذ جزء من هجوم الخصم", "🖐️"),
    ("critical-strike", "ضربة حرجة", "A", "ضرر مضاعف", "💥"),
    ("penetration", "اختراق", "A", "تجاهل الدفاع", "🗡️"),
    ("execution", "إعدام", "A", "ضرر قوي ضد الخصم الضعيف", "⚰️"),
    ("domination", "سيطرة", "A", "منع استخدام بطاقة", "⛓️"),
    # S
    ("earthquake", "زلزال", "S", "ضرر قوي جدًا", "🌋"),
    ("storm", "عاصفة", "S", "عدة ضربات متتالية", "🌪️"),
    ("battle-turn", "قلب المعركة", "S", "يعكس حالة القتال", "🔄"),
    ("rage", "غضب", "S", "مضاعفة الهجوم", "😡"),
    ("energy-lock", "قفل الطاقة", "S", "منع مهارات الخصم", "🔒"),
    # SS
    ("island-judgment", "حكم الجزيرة", "SS", "تغيير قانون القتال", "⚖️"),
    ("arena-king", "ملك الساحة", "SS", "رفع جميع الإحصائيات", "👑"),
    ("round-end", "نهاية الجولة", "SS", "إنهاء الجولة بتأثير خاص", "🏁"),
    ("total-control", "سيطرة كاملة", "SS", "التحكم بالمعركة مؤقتًا", "🎮"),
    ("boss-power", "قوة الزعيم", "SS", "تمنح وضع قوة خارق", "💠"),
    # SR
    ("sr-execution", "الإعدام", "SR", "ضربة حاسمة", "🩸"),
    ("power-erasure", "محو القوة", "SR", "إلغاء قدرات الخصم", "🧿"),
    ("king-fall", "سقوط الملك", "SR", "خفض كل الإحصائيات", "🏳️"),
    ("soul-break", "كسر الروح", "SR", "منع الخصم من القتال", "💔"),
    ("final-judgment", "الحكم الأخير", "SR", "تأثير نادر جدًا", "🔱"),
    # UR
    ("rule-breaker", "كسر القواعد", "UR", "استخدام أي تأثير", "🌀"),
    ("immortality", "الخلود", "UR", "منع الموت مرة واحدة", "♾️"),
    ("time-rewind", "إعادة الزمن", "UR", "إرجاع حالة القتال", "⏳"),
    ("legendary-power", "قوة الأسطورة", "UR", "رفع كل الإحصائيات", "✨"),
    ("island-master", "سيد الجزيرة", "UR", "أقوى بطاقة في اللعبة", "🏝️"),
)

_RARITY_BASE_PRICES: dict[str, int] = {
    "F": 50,
    "E": 150,
    "D": 300,
    "C": 650,
    "B": 1400,
    "A": 2800,
    "S": 5500,
    "SS": 10000,
    "SR": 20000,
    "UR": 50000,
}


def _build_additional_cards() -> tuple[CardDefinition, ...]:
    rarity_counts: dict[str, int] = {}
    cards: list[CardDefinition] = []
    for card_id, name, rarity, description, emoji in ADDITIONAL_CARD_DATA:
        index = rarity_counts.get(rarity, 0)
        rarity_counts[rarity] = index + 1
        base_price = _RARITY_BASE_PRICES[rarity]
        price_step = max(1, base_price // 10)
        cards.append(
            CardDefinition(
                card_id,
                name,
                "مهارات المعركة",
                rarity,
                base_price + index * price_step,
                emoji,
                description,
            )
        )
    return tuple(cards)


ADDITIONAL_CARDS: tuple[CardDefinition, ...] = _build_additional_cards()
CARD_CATALOG = CARD_CATALOG + ADDITIONAL_CARDS


CARD_GAMEPLAY_DETAILS: dict[str, CardGameplayDetails] = {
    "ember-fox": CardGameplayDetails(
        ("تزيد سرعة الهجوم قليلًا.", "تمنح فرصة صغيرة لتفادي الضربة.", "تساعد على تنفيذ الحركة الأولى في المعركة."),
        "مناسبة للضربات السريعة وبدء القتال.",
        "منخفضة",
    ),
    "moon-moth": CardGameplayDetails(
        ("تستعيد قدرًا بسيطًا من الطاقة.", "تزيد فعالية المهارات الليلية.", "تمنح حماية خفيفة من تأثيرات الإبطاء."),
        "تدعم البقاء وتساعد على استخدام المهارات بوتيرة أسرع.",
        "منخفضة",
    ),
    "tide-rider": CardGameplayDetails(
        ("تزيد الحركة أثناء المعارك المائية.", "تمنح درعًا صغيرًا بعد صد الهجوم.", "تحسن فرصة المناورة حول الخصم."),
        "تجعل الحركة أكثر مرونة وتمنح حماية مؤقتة.",
        "متوسطة منخفضة",
    ),
    "iron-golem": CardGameplayDetails(
        ("تزيد قوة الدفاع.", "تقلل الضرر القادم.", "تمنح ثباتًا أمام الضربات الثقيلة."),
        "بطاقة دفاعية ممتازة لحماية الفريق.",
        "متوسطة",
    ),
    "sky-whale": CardGameplayDetails(
        ("تزيد نقاط الحياة القصوى.", "تمنح درعًا عند بداية المعركة.", "تقلل أثر الضربات بعيدة المدى."),
        "تدعم الفريق وتجعله أكثر قدرة على تحمل الضرر.",
        "متوسطة",
    ),
    "crystal-witch": CardGameplayDetails(
        ("تزيد قوة المهارات السحرية.", "تمنح فرصة لإعادة استخدام مهارة.", "تضعف مقاومة الخصم للسحر."),
        "تضاعف قيمة الهجمات السحرية وتمنح فائدة إضافية للمهارات.",
        "متوسطة مرتفعة",
    ),
    "neon-ninja": CardGameplayDetails(
        ("تزيد سرعة الهجوم بوضوح.", "تمنح ضربة إضافية أحيانًا.", "ترفع فرصة الضربة الحرجة."),
        "مناسبة للهجمات المتتابعة والقضاء السريع على الخصوم.",
        "مرتفعة",
    ),
    "storm-dragon": CardGameplayDetails(
        ("تزيد قوة الهجوم بنسبة 25٪.", "تمنح صاعقة إضافية عند استخدام الهجوم.", "لها تأثير خاص يضعف دفاع الخصم أثناء المعارك."),
        "تمنح أفضلية هجومية كبيرة وتسبب ضررًا إضافيًا من العاصفة.",
        "مرتفعة جدًا",
    ),
    "solar-knight": CardGameplayDetails(
        ("تزيد الهجوم والدفاع بنسبة 30٪.", "تمنح درعًا شمسيًا عند انخفاض الصحة.", "تزيل تأثيرًا سلبيًا واحدًا عند تفعيلها."),
        "بطاقة متوازنة قوية للهجوم والدفاع في المعارك الصعبة.",
        "نخبوية",
    ),
    "void-oracle": CardGameplayDetails(
        ("تزيد قوة جميع المهارات بنسبة 40٪.", "تمنح فرصة لتوقع هجوم الخصم.", "تضعف أقوى تأثير إيجابي لدى الخصم."),
        "تغيّر مجرى المعركة عبر تعزيز المهارات وتعطيل الخصم.",
        "أسطورية",
    ),
    "aurora-spirit": CardGameplayDetails(
        ("تزيد الهجوم والدفاع بنسبة 50٪.", "تستعيد جزءًا من الصحة والطاقة.", "تمنح حماية من أول ضربة قاضية."),
        "تمنح أفضلية شاملة وقد تنقذ الفريق من الهزيمة.",
        "فوق أسطورية",
    ),
    "golden-comet": CardGameplayDetails(
        ("تزيد كل الإحصاءات بنسبة 75٪.", "تطلق ضربة نيزكية نادرة تسبب ضررًا هائلًا.", "تمنح تأثيرًا خاصًا يتجاوز دفاع الخصم."),
        "أقوى تأثير هجومي شامل في نظام اللعبة.",
        "أقصى قوة",
    ),
}

_RARITY_POWER_LEVELS: dict[str, str] = {
    "F": "منخفضة",
    "E": "منخفضة",
    "D": "متوسطة منخفضة",
    "C": "متوسطة",
    "B": "متوسطة مرتفعة",
    "A": "مرتفعة",
    "S": "مرتفعة جدًا",
    "SS": "نخبوية",
    "SR": "أسطورية",
    "UR": "أقصى قوة",
}

CARD_GAMEPLAY_DETAILS.update(
    {
        card_id: CardGameplayDetails(
            (description,),
            description,
            _RARITY_POWER_LEVELS[rarity],
        )
        for card_id, _, rarity, description, _ in ADDITIONAL_CARD_DATA
    }
)

ARABIC_CARD_TRANSLATIONS: dict[str, tuple[str, str, str, str]] = {
    "ember-fox": ("ثعلب الجمر", "البرية المشتعلة", "F", "ثعلب سريع بذيل يتوهج كالنار."),
    "moon-moth": ("عثة القمر", "سقوط الليل", "F", "تنجذب إلى ضوء القمر ورفوف الجامعين الهادئة."),
    "tide-rider": ("راكب المد", "الأزرق العميق", "E", "بطل يركب الأمواج من أطراف الخريطة."),
    "iron-golem": ("العملاق الحديدي", "المسبك", "D", "صُنع للحلبة ومن الصعب إسقاطه."),
    "sky-whale": ("حوت السماء", "ما وراء السحاب", "C", "عملاق لطيف يسبح فوق الطقس."),
    "crystal-witch": ("ساحرة الكريستال", "الأسرار", "C", "تحتفظ بتعويذة لكل نوع من الحظ السيئ."),
    "neon-ninja": ("نينجا النيون", "ما بعد الظلام", "B", "صامت وسريع وأكثر سطوعًا من أضواء المدينة."),
    "storm-dragon": ("تنين العاصفة", "العاصفة", "A", "عاصفة أسطورية اكتسبت حراشف وأجنحة."),
    "solar-knight": ("فارس الشمس", "السماوية", "S", "الحارس الأخير لشمس آخذة في الأفول."),
    "void-oracle": ("عرّاف الفراغ", "ما وراء الوجود", "SS", "عرّاف غامض رأى هذه السحبة من قبل."),
    "aurora-spirit": ("روح الشفق", "السماوية", "SR", "بريق لا يتكرر إلا مرة واحدة في العمر."),
    "golden-comet": ("المذنب الذهبي", "الكنوز", "UR", "أندر ومضة تعبر سماء الجامعين."),
}

ARABIC_CARD_TRANSLATIONS.update(
    {
        card_id: (name, "مهارات المعركة", rarity, description)
        for card_id, name, rarity, description, _ in ADDITIONAL_CARD_DATA
    }
)


def card_by_id(card_id: str) -> CardDefinition | None:
    return next((card for card in CARD_CATALOG if card.card_id == card_id), None)


def localized_card_fields(card_id: str) -> tuple[str, str, str, str]:
    """Return Arabic card fields without changing stored card rows."""
    translation = ARABIC_CARD_TRANSLATIONS.get(card_id)
    if translation:
        return translation
    card = card_by_id(card_id)
    if card:
        return card.name, card.set_name, card.rarity, card.description
    return card_id, "", "", ""


def rarity_appearance_weight(rarity: str) -> float:
    return RARITY_APPEARANCE_WEIGHTS.get(rarity, 0.0)


def rarity_appearance_percentage(rarity: str) -> float:
    """Approximate per-card chance for the first weighted shop draw."""
    total_weight = sum(
        rarity_appearance_weight(card.rarity) for card in CARD_CATALOG
    )
    card_weight = rarity_appearance_weight(rarity)
    return (card_weight / total_weight) * 100 if total_weight else 0.0


def gameplay_details(card_id: str) -> CardGameplayDetails:
    return CARD_GAMEPLAY_DETAILS.get(
        card_id,
        CardGameplayDetails(
            ("تمنح فائدة إضافية أثناء استخدامها.",),
            "تضيف تأثيرًا مساعدًا داخل المعركة.",
            "غير محددة",
        ),
    )


def stock_for_rarity(rarity: str) -> int:
    return RARITY_STOCK.get(rarity, 1)
