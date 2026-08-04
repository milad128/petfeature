"""
roadmap_data.py — Hardcoded PM Learning Roadmap constants.

Everything in this file is authored once and changes only via a code deploy.
DB-backed content (resource links, homework text) lives in RoadmapResource.

Milad: fill every string marked  # TODO  before launch.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ── Level definitions ──────────────────────────────────────────────────────

@dataclass
class Level:
    slug: str           # URL segment: 'hiring' | 'apm' | 'pm' | ...
    num: str            # "مسیر ۰"  "سطح ۱"  ...
    fa: str             # Farsi display name
    en: str             # English name (LTR)
    spec: str           # One-sentence description (Farsi)
    thesis: str         # Thesis sentence (Farsi) — empty for L0
    required: str       # Persian numeral string
    reading: str        # e.g. "~۳۵ ساعت"
    sprint: str         # e.g. "۱۸ هفته"
    tenure: str         # e.g. "۳ تا ۶ ماه"
    sprint_weeks: int   # numeric for bar calculations
    tenure_months: int  # numeric for bar calculation (0 = open/campaign)
    is_track: bool = False   # True for L0 (campaign, not a seniority level)
    flag: str = ""           # special banner text (e.g. "کمپین است، نه سطح")
    matrix_label: str = ""   # short column header in depth matrix (e.g. "APM")


LEVELS: list[Level] = [
    Level(
        slug="hiring",
        num="مسیر ۰",
        fa="مسیر استخدام",
        en="Getting Hired — not a seniority level",
        spec="تصمیم می‌گیرید که مدیریت محصول شغل درستی است یا نه، رزومه و نمونه‌کاری می‌سازید که به زبان محصول خوانده شود، سه فرمت مصاحبه را تمرین می‌کنید. رزومه درست می‌کنید و اپلای می‌کنید.",
        thesis="",
        required="۹",
        reading="~۱۸٫۵ ساعت",
        sprint="۱۲ هفته (~۳ ماه)",
        tenure="۳ تا ۶ ماه",
        sprint_weeks=12,
        tenure_months=0,
        is_track=True,
        flag="کمپین است، نه سطح — روزی که امضا کنید تمام می‌شود",
    ),
    Level(
        slug="apm",
        num="سطح ۱",
        fa="مبتدی (APM)",
        en="Associate PM",
        spec="مبانی را یاد می‌گیرد، زیر نظر دیگران در اجرا سهم دارد و مهارت‌های پایه‌ی تحلیلی، فنی و ارتباطی را می‌سازد.",
        thesis="TODO: APM thesis sentence",  # TODO
        required="۱۵",
        reading="~۵۳ ساعت",
        sprint="۳۱ هفته (~۷ ماه)",
        tenure="۱۲ تا ۲۴ ماه",
        sprint_weeks=31,
        tenure_months=18,
        matrix_label="APM",
    ),
    Level(
        slug="pm",
        num="سطح ۲",
        fa="مدیر محصول",
        en="Product Manager",
        spec="مستقل مالک یک محصول یا قابلیت است، مسئله‌ی مشتری را کشف می‌کند و نتیجه‌ی تجاری قابل اندازه‌گیری تحویل می‌دهد.",
        thesis="",
        required="۱۸",
        reading="~۸۱ ساعت",
        sprint="۵۸ هفته (~۱۳٫۵ ماه)",
        tenure="۲۴ تا ۳۶ ماه",
        sprint_weeks=58,
        tenure_months=30,
        matrix_label="PM",
    ),
    Level(
        slug="senior-pm",
        num="سطح ۳",
        fa="مدیر محصول ارشد",
        en="Senior PM",
        spec="مسائل مبهم را حل می‌کند، ابتکارهای استراتژیک را رهبری می‌کند و بر جهت چند تیم اثر می‌گذارد.",
        thesis="",
        required="۱۶",
        reading="~۸۶ ساعت",
        sprint="۵۴ هفته (~۱۲٫۵ ماه)",
        tenure="۲۴ تا ۳۶ ماه",
        sprint_weeks=54,
        tenure_months=30,
        matrix_label="Sr PM",
    ),
    Level(
        slug="lead",
        num="سطح ۴",
        fa="لید محصول",
        en="Product Lead",
        spec="گروه کوچکی از PMها را رهبری می‌کند و پل میان تعالی فردی و رهبری آدم‌هاست. کم‌ترین منبع، بیشترین شکست.",
        thesis="",
        required="۸",
        reading="~۴۹ ساعت",
        sprint="۱۹ هفته (~۴٫۵ ماه)",
        tenure="۱۲ تا ۲۴ ماه",
        sprint_weeks=19,
        tenure_months=18,
        flag="سبک‌ترین مطالعه، سخت‌ترین عبور",
        matrix_label="Lead",
    ),
    Level(
        slug="director",
        num="سطح ۵",
        fa="دایرکتور محصول",
        en="Director of Product",
        spec="تیم می‌سازد و رهبری می‌کند، استراتژی و فرایند عملیاتی تعریف می‌کند و سرمایه‌گذاری را با اهداف کسب‌وکار هم‌راستا می‌کند.",
        thesis="",
        required="۱۵",
        reading="~۸۳ ساعت",
        sprint="۵۲ هفته (~۱۲ ماه)",
        tenure="۳۶ تا ۶۰ ماه",
        sprint_weeks=52,
        tenure_months=48,
        matrix_label="Director",
    ),
    Level(
        slug="cpo",
        num="سطح ۶",
        fa="CPO",
        en="Chief Product Officer",
        spec="مالک چشم‌انداز و سبد محصول شرکت است، استراتژی بلندمدت را شکل می‌دهد و رهبری اجرایی را حول فرصت‌های بازار هم‌راستا می‌کند.",
        thesis="",
        required="۱۱",
        reading="~۶۵ ساعت",
        sprint="۴۴ هفته (~۱۰ ماه)",
        tenure="باز",
        sprint_weeks=44,
        tenure_months=0,
        matrix_label="CPO",
    ),
]

LEVEL_BY_SLUG: dict[str, Level] = {lv.slug: lv for lv in LEVELS}

# Levels with full public pages in v16
FULL_PAGE_SLUGS: set[str] = set()
# Levels that show stub in v16
STUB_SLUGS = {"apm", "pm", "senior-pm", "lead", "director", "cpo"}


# ── Competency definitions ──────────────────────────────────────────────────

@dataclass
class Competency:
    slug: str
    fa: str               # Farsi display name
    domain: str           # domain group (Farsi)
    is_habit: bool = False  # True = عادتی, False = دانشی


COMPETENCIES: list[Competency] = [
    # پیشه‌ی محصول
    Competency("product-discovery",    "کشف محصول",               "پیشه‌ی محصول",      is_habit=False),
    Competency("delivery-execution",   "تحویل و اجرا",             "پیشه‌ی محصول",      is_habit=False),
    Competency("prioritization",       "اولویت‌بندی و موازنه",     "پیشه‌ی محصول",      is_habit=False),
    Competency("experimentation",      "آزمایش و اعتبارسنجی",      "پیشه‌ی محصول",      is_habit=False),
    # تحلیل و کسب‌وکار
    Competency("technical-literacy",   "سواد فنی",                 "تحلیل و کسب‌وکار",  is_habit=False),
    Competency("data-metrics",         "داده، متریک و هدف‌گذاری",  "تحلیل و کسب‌وکار",  is_habit=False),
    Competency("business-acumen",      "درک کسب‌وکار و تجاری",     "تحلیل و کسب‌وکار",  is_habit=False),
    # استراتژی
    Competency("product-vision",       "چشم‌انداز محصول",          "استراتژی",           is_habit=False),
    Competency("product-strategy",     "استراتژی محصول",           "استراتژی",           is_habit=False),
    Competency("market-competitive",   "بازار و رقبا",              "استراتژی",           is_habit=True),
    # رهبری و نفوذ
    Competency("communication",        "ارتباط و نوشتن",           "رهبری و نفوذ",       is_habit=True),
    Competency("stakeholder-influence","نفوذ بر ذی‌نفعان و مدیران","رهبری و نفوذ",       is_habit=True),
    Competency("people-leadership",    "رهبری افراد",              "رهبری و نفوذ",       is_habit=True),
    Competency("coaching-talent",      "کوچینگ، استخدام و استعداد","رهبری و نفوذ",       is_habit=True),
    Competency("org-design",           "طراحی سازمان و فرهنگ",     "رهبری و نفوذ",       is_habit=True),
]

COMPETENCY_BY_SLUG: dict[str, Competency] = {c.slug: c for c in COMPETENCIES}


# ── Depth matrix: competency_slug → [L1, L2, L3, L4, L5, L6] ──────────────
# 0 = not required ("—"), 1–5 = depth level

DEPTH_MATRIX: dict[str, list[int]] = {
    "product-discovery":     [3, 4, 4, 4, 5, 5],
    "delivery-execution":    [3, 4, 4, 3, 2, 2],
    "prioritization":        [2, 4, 4, 4, 5, 5],
    "experimentation":       [1, 3, 4, 4, 4, 4],
    "technical-literacy":    [3, 3, 3, 3, 3, 3],
    "data-metrics":          [1, 4, 4, 4, 5, 5],
    "business-acumen":       [1, 2, 3, 3, 4, 5],
    "product-vision":        [1, 2, 4, 4, 4, 5],
    "product-strategy":      [1, 3, 4, 4, 5, 5],
    "market-competitive":    [1, 3, 4, 3, 4, 5],
    "communication":         [3, 3, 4, 4, 4, 5],
    "stakeholder-influence": [2, 3, 4, 4, 4, 5],
    "people-leadership":     [0, 0, 1, 3, 4, 5],
    "coaching-talent":       [0, 1, 3, 4, 5, 5],
    "org-design":            [0, 0, 1, 2, 4, 5],
}

# Depth label lookup
DEPTH_LABELS: dict[int, str] = {
    0: "—",
    1: "آگاه",
    2: "راهنمایی‌شده",
    3: "مستقل",
    4: "رهبری می‌کند",
    5: "تعریف می‌کند",
}


# ── Per-level competency detail (sprint, maturation, reading, category) ─────

@dataclass
class CompetencyLevelData:
    category: str        # 'entry' | 'core' | 'supporting' | 'bridge' | 'passive'
    sprint_weeks: int
    maturation_months: int
    reading_hours: float
    # 'passive' subtypes
    passive_how: str = ""   # how it's acquired at this level (hardcoded text)


# APM (level_slug='apm') competency data
APM_COMPETENCY_DATA: dict[str, CompetencyLevelData] = {
    "delivery-execution":    CompetencyLevelData("core",       8,  6,  12.0),
    "product-discovery":     CompetencyLevelData("core",       8,  6,  12.0),
    "communication":         CompetencyLevelData("core",       6,  4,   8.0),
    "technical-literacy":    CompetencyLevelData("core",       5,  4,   8.0),
    "stakeholder-influence": CompetencyLevelData("supporting", 2,  6,   5.0),
    "prioritization":        CompetencyLevelData("supporting", 2,  4,   5.0),
    "data-metrics":          CompetencyLevelData("passive",    0,  0,   0.0,
                              passive_how="رایگان به دست می‌آید — در دل کار با داده‌ها"),
    "business-acumen":       CompetencyLevelData("passive",    0,  0,   0.0,
                              passive_how="رایگان به دست می‌آید — با مشاهده‌ی جلسات"),
    "experimentation":       CompetencyLevelData("passive",    0,  0,   0.0,
                              passive_how="رایگان به دست می‌آید — با نگاه کردن به آزمایش‌های تیم"),
    "product-strategy":      CompetencyLevelData("passive",    0,  0,   0.0,
                              passive_how="رایگان به دست می‌آید — با خواندن استراتژی شرکت"),
    "product-vision":        CompetencyLevelData("passive",    0,  0,   0.0,
                              passive_how="رایگان به دست می‌آید — با گوش دادن به رهبری"),
    "market-competitive":    CompetencyLevelData("passive",    0,  0,   0.0,
                              passive_how="رایگان به دست می‌آید — با زندگی در محصول"),
    # people-leadership, coaching-talent, org-design → not applicable at L1
}


# ── L0 — Phase definitions ──────────────────────────────────────────────────

@dataclass
class L0Phase:
    slug: str
    n: str        # Persian numeral "۱"
    fa: str       # "آماده‌سازی"
    en: str       # "Preparation"
    sprint: str   # "هفته‌های ۱ تا ۶"
    start_week: int
    end_week: int
    open_ended: bool = False
    note: str = ""


L0_PHASES: list[L0Phase] = [
    L0Phase(
        slug="preparation",
        n="۱",
        fa="آماده‌سازی",
        en="Preparation",
        sprint="۳ هفته",
        start_week=1,
        end_week=3,
        note="",
    ),
    L0Phase(
        slug="practice",
        n="۲",
        fa="مصاحبه",
        en="Practice",
        sprint="۹ هفته",
        start_week=4,
        end_week=12,
        note="بعد از آماده شدن رزومه، باید برای مصاحبه واقعی آماده شوید. برای این کار باید ابتدا بدانید با چه سوالاتی ممکن است روبرو شوید، بهترین روش پاسخ دادن به آن سوال‌ها را یاد بگیرید و در آخر برای پاسخ دادن به آن‌ها تمرین کنید.",
    ),
]


# ── L0 — Area definitions ───────────────────────────────────────────────────

@dataclass
class L0Area:
    slug: str
    n: str           # Persian numeral
    name: str        # full Farsi area name
    short: str       # short name used in the visual map
    phase_slug: str
    sprint_weeks: int
    reading: str     # total reading time string, e.g. "۳٫۵ ساعت"
    maturation: str  # e.g. "۳ ماه تمرین مداوم"
    is_habit: bool
    body: str
    homework: str
    persian_market_note: str = ""


L0_AREAS: list[L0Area] = [
    L0Area(
        slug="role-clarity",
        n="۱",
        name="آشنایی با نقش — واقعاً همین شغل را می‌خواهید؟",
        short="آشنایی با نقش",
        phase_slug="preparation",
        sprint_weeks=1,
        reading="۳٫۵ ساعت",
        maturation="—",
        is_habit=False,
        body=(
            "بیشتر کسانی که وارد مدیریت محصول می‌شوند، واقعاً نمی‌دانند که کار یک مدیر محصول چیست "
            "و چه مسئولیت‌هایی بر عهده دارد. یک هفته وقت بگذارید و مطمئن شوید کارِ روزمره‌ی واقعی "
            "یک مدیر محصول را می‌خواهید — که بیشترش نوشتن است، جلسه، و «نه» گفتن. نه مدیریت کردن!"
        ),
        homework=(
            "با یک مدیر محصول شاغل ۳۰ دقیقه مصاحبه کنید: هفته‌ی معمولی‌اش، سخت‌ترین بخش کارش، "
            "و چیزی که کاش زودتر می‌دانست. یک صفحه خلاصه بنویسید، بعد صادقانه و کتبی جواب بدهید "
            "که آن هفته برایتان جذاب است یا نه."
        ),
    ),
    L0Area(
        slug="resume",
        n="۲",
        name="رزومه و روایت شغلی",
        short="رزومه و روایت شغلی",
        phase_slug="preparation",
        sprint_weeks=2,
        reading="۵ ساعت",
        maturation="—",
        is_habit=False,
        body=(
            "اولین بخش و مهمترین بخش فاز یک نوشتن رزومه‌ای است که بتواند به تنهایی تمام تجربه و مهارت "
            "شما را در بین سطرهای نوشته‌ها به خواننده منتقل کنید. این بخش را جدی بگیرید و برای آن وقت و انرژی بگذارید."
        ),
        homework=(
            "با توجه به آموزش‌ها، یکی از قالب‌های ارائه‌شده را انتخاب کنید و رزومه‌ی خود را آماده کنید."
        ),
    ),
    L0Area(
        slug="interview-pm",
        n="۳",
        name="مصاحبه‌ی عمومی مدیریت محصول",
        short="مصاحبه عمومی",
        phase_slug="practice",
        sprint_weeks=4,
        reading="۵ ساعت",
        maturation="۳ ماه تمرین مداوم",
        is_habit=True,
        body=(
            "معمولاً اولین مصاحبه مدیریت محصول، مصاحبه عمومی است که بیشتر در مورد خود شما و تجربه‌های "
            "گذشته شما است. بهتر است با فرمت آن آشنا شوید و چند نمونه مصاحبه ببینید."
        ),
        homework=(
            "دو هفته، هر روز یک سؤال طراحی محصول را بلند و ضبط‌شده جواب بدهید، هر بار بیست دقیقه. "
            "سه تا را دوباره تماشا کنید. دنبال یک چیز باشید: آیا قبل از شروع حل‌کردن، ساختارتان را اعلام کردید؟"
        ),
    ),
    L0Area(
        slug="interview-analytics",
        n="۴",
        name="مصاحبه‌ی حل مسئله‌ی مدیریت محصول",
        short="مصاحبه حل مسئله",
        phase_slug="practice",
        sprint_weeks=3,
        reading="۳ ساعت",
        maturation="۳ ماه تمرین مداوم",
        is_habit=True,
        body=(
            "اندازه‌گیری بازار، تعریف متریک، و «این عدد ۲۰٪ افت کرده، چرا؟» مصاحبه‌گر روشِ قابل مشاهده "
            "می‌خواهد، نه عددِ درست."
        ),
        homework=(
            "ده سؤال تخمین بردارید و هر کدام را زیر شش دقیقه جواب بدهید، با نوشتن فرض‌ها پیش از هر محاسبه‌ای. "
            "بعد برگردید و ببینید کدام فرض، اگر غلط بود، بیشترین تغییر را در جوابتان می‌داد — همان یکی است "
            "که در مصاحبه‌ی واقعی باید بلند بگویید."
        ),
    ),
    L0Area(
        slug="interview-behavior",
        n="۵",
        name="مصاحبه طراحی محصول",
        short="مصاحبه طراحی محصول",
        phase_slug="practice",
        sprint_weeks=2,
        reading="۲ ساعت",
        maturation="۲ ماه تمرین مداوم",
        is_habit=True,
        body=(
            "مصاحبه طراحی محصول تقریباً سخت‌ترین بخش مصاحبه تخصصی است که بیشتر برای مهارت طراحی "
            "محصول از صفر است. این مهارت برای لیدها و بالاتر بسیار مهم و حیاتی است."
        ),
        homework=(
            "هشت داستان STAR بنویسید: یک تعارض، یک شکست، یک متقاعدکردن، یک تصمیم داده‌محور، "
            "یک لحظه‌ی رهبری بدون اختیار، یک چیز عرضه‌شده، یک چیز متوقف‌شده، و یک بار که اشتباه می‌کردید. "
            "هر کدام زیر نود ثانیه‌ی گفتاری. زمان بگیرید."
        ),
    ),
]

L0_AREA_BY_SLUG: dict[str, L0Area] = {a.slug: a for a in L0_AREAS}
L0_PHASE_BY_SLUG: dict[str, L0Phase] = {p.slug: p for p in L0_PHASES}


# ── APM (L1) section texts ──────────────────────────────────────────────────
# Milad: author all these in Persian before launch.
# Keys match section IDs; values are displayed verbatim in templates.

APM_TEXTS: dict[str, str] = {
    "entry_note": "TODO: APM entry section intro note",          # TODO
    "entry_callout": "TODO: APM entry callout text (مسیر ۰ reference)",  # TODO
    "entry_quote": "TODO: APM entry quote",                      # TODO
    "entry_homework": "TODO: APM entry homework text",           # TODO
    "core_note": "TODO: APM core section intro note",            # TODO
    "supporting_note": "TODO: APM supporting section intro note",  # TODO
    "passive_note": "TODO: APM passive section intro note",      # TODO
    "sequence_note": "TODO: APM sequence section intro paragraph",  # TODO
    "bridge_note": "TODO: APM bridge section intro note",        # TODO
    "tenure_bar_note": "۱۲ تا ۲۴ ماه تصدی — ۷ ماه اسپرینت",
    "tenure_bar_body": "TODO: APM tenure bar explanation",       # TODO
    "asks_note": "TODO: APM competency table intro",             # TODO
}

# Per-core-competency richtext (shown expanded in the core <details> card)
APM_CORE_RATIONALE: dict[str, dict[str, str]] = {
    "delivery-execution": {
        "rationale": "TODO: why delivery-execution is core for APM",    # TODO
        "quote": "TODO: quote for delivery-execution",                  # TODO
        "practice": "TODO: practice exercise for delivery-execution",   # TODO
    },
    "product-discovery": {
        "rationale": "TODO: why product-discovery is core for APM",     # TODO
        "quote": "TODO: quote for product-discovery",                   # TODO
        "practice": "TODO: practice exercise for product-discovery",    # TODO
    },
    "communication": {
        "rationale": "TODO: why communication is core for APM",         # TODO
        "quote": "TODO: quote for communication",                       # TODO
        "practice": "TODO: practice exercise for communication",        # TODO
    },
    "technical-literacy": {
        "rationale": "TODO: why technical-literacy is core for APM",    # TODO
        "quote": "TODO: quote for technical-literacy",                  # TODO
        "practice": "TODO: practice exercise for technical-literacy",   # TODO
    },
}

# Per-supporting-competency (shown in supporting section cards)
APM_SUPPORTING_DETAIL: dict[str, dict[str, str]] = {
    "stakeholder-influence": {
        "owner_note": "TODO: who owns stakeholder-influence at APM level",   # TODO
    },
    "prioritization": {
        "owner_note": "TODO: who owns prioritization at APM level",          # TODO
    },
}

# APM bridge checklist items (hardcoded, never in DB)
APM_BRIDGE_CHECKLIST: list[str] = [
    "TODO: bridge checklist item 1",  # TODO
    "TODO: bridge checklist item 2",  # TODO
    "TODO: bridge checklist item 3",  # TODO
    "TODO: bridge checklist item 4",  # TODO
    "TODO: bridge checklist item 5",  # TODO
]

# L0 immigration interview videos (placeholder — fill titles/URLs when ready)
L0_IMMIGRATION_VIDEOS: list[dict[str, str]] = [
    {
        "title": "عنوان ویدیوی اول",
        "where": "گفت‌وگو با یک مدیر محصول مهاجرت‌کرده",
        "url": "#",
    },
    {
        "title": "عنوان ویدیوی دوم",
        "where": "گفت‌وگو با یک مدیر محصول مهاجرت‌کرده",
        "url": "#",
    },
    {
        "title": "عنوان ویدیوی سوم",
        "where": "گفت‌وگو با یک مدیر محصول مهاجرت‌کرده",
        "url": "#",
    },
]

# L0 audience cards
L0_AUDIENCE: list[dict[str, str]] = [
    {
        "title": "تغییر مسیر شغلی",
        "body": (
            "از مهندسی، طراحی، مارکتینگ، پشتیبانی یا مشاوره به محصول می‌آیید. "
            "کل مسیر برای شماست، از فاز یک."
        ),
        "tag": "همه‌ی پنج حوزه",
    },
    {
        "title": "دانش‌آموخته‌ی تازه",
        "body": (
            "دنبال نقش APM یا کارشناس محصول هستید. سابقه‌ی کاری کمی دارید، "
            "پس روایت رزومه و عملکردتان در مصاحبه بیشترین چیزی است که ارزیابی می‌شود."
        ),
        "tag": "هر دو فاز، بدون رد کردن",
    },
    {
        "title": "PM شاغل، شرکت جدید",
        "body": (
            "همین حالا مدیر محصولید و جابه‌جا می‌شوید. "
            "فاز یک را رد کنید و فاز دو را به‌عنوان یادآوری بگیرید."
        ),
        "tag": "فاز ۱ را رد کنید",
    },
]


# ── Four categories ─────────────────────────────────────────────────────────

FOUR_CATEGORIES: list[dict[str, str]] = [
    {
        "n": "۱",
        "fa": "ورود",
        "desc": "برای گرفتن این عنوان به چه چیزی نیاز دارم؟ فقط خواندن کافی است.",
        "when": "پیش از عنوان",
    },
    {
        "n": "۲",
        "fa": "هسته",
        "desc": "روزانه شخصاً پاسخ‌گوی چه چیزی هستم؟ مواردی که شما شخصاً مسئول شکست و موفقیت آن خواهید بود.",
        "when": "ماه ۱ تا ۶",
    },
    {
        "n": "۳",
        "fa": "حمایتی",
        "desc": "در چه چیزی سهم دارم اما مالکش نیستم؟ مواردی که فرد دیگری مسئول آن است ولی به مهارت شما در آن نیاز دارد.",
        "when": "ماه ۶ تا ۱۸",
    },
    {
        "n": "۴",
        "fa": "پل",
        "desc": "برای درخواستِ ارتقا به چه چیزی نیاز دارم؟ پیش‌نمایشی کم‌ریسک از سطح بعد.",
        "when": "۶ ماه آخر",
    },
]

# ── Depth scale legend ──────────────────────────────────────────────────────

DEPTH_SCALE: list[dict[str, str]] = [
    {"n": "۱", "fa": "آگاه",            "desc": "واژگان را می‌داند، تولید نمی‌کند"},
    {"n": "۲", "fa": "راهنمایی‌شده",   "desc": "با پشتیبانی یا الگو انجام می‌دهد"},
    {"n": "۳", "fa": "مستقل",           "desc": "در دامنه‌ی خودش، خوب و بدون کمک"},
    {"n": "۴", "fa": "رهبری می‌کند",   "desc": "رویکرد را برای دیگران تعیین می‌کند"},
    {"n": "۵", "fa": "تعریف می‌کند",   "desc": "روش کل سازمان را می‌سازد"},
    {"n": "—", "fa": "لازم نیست",       "desc": "در این سطح اصلاً بخشی از شغل نیست"},
]

# ── Resource type choices (for admin form) ──────────────────────────────────

RESOURCE_TYPES: list[tuple[str, str]] = [
    ("book",          "کتاب"),
    ("article",       "مقاله"),
    ("video",         "ویدیو"),
    ("podcast",       "پادکست"),
    ("practice-tool", "ابزار تمرین"),
    ("course",        "دوره"),
    ("tool",          "ابزار"),
    ("guide",         "راهنما"),
]

# ── Category choices (for admin form) ───────────────────────────────────────

CATEGORY_CHOICES: list[tuple[str, str]] = [
    ("entry",      "ورود"),
    ("core",       "هسته"),
    ("supporting", "حمایتی"),
    ("bridge",     "پل"),
]

# Competency slugs available per level (for admin form dynamic filtering)
LEVEL_COMPETENCY_SLUGS: dict[str, list[str]] = {
    "apm": [
        "delivery-execution",
        "product-discovery",
        "communication",
        "technical-literacy",
        "stakeholder-influence",
        "prioritization",
        "data-metrics",
        "business-acumen",
        "experimentation",
        "product-strategy",
        "product-vision",
        "market-competitive",
    ],
    "pm": [c.slug for c in COMPETENCIES],
    "senior-pm": [c.slug for c in COMPETENCIES],
    "lead": [c.slug for c in COMPETENCIES],
    "director": [c.slug for c in COMPETENCIES],
    "cpo": [c.slug for c in COMPETENCIES],
}

# Area slugs for L0 (admin form) — derived from L0_AREAS
L0_AREA_SLUGS: list[tuple[str, str]] = [
    (a.slug, a.name) for a in L0_AREAS
]

# ── L0 levels list (for the closing "pick your level" grid) ─────────────────
L0_LEVELS_GRID: list[dict[str, str]] = [
    {"num": "سطح ۱", "fa": "مبتدی (APM)",          "slug": "apm"},
    {"num": "سطح ۲", "fa": "مدیر محصول",            "slug": "pm"},
    {"num": "سطح ۳", "fa": "مدیر محصول ارشد",       "slug": "senior-pm"},
    {"num": "سطح ۴", "fa": "لید محصول",              "slug": "lead"},
    {"num": "سطح ۵", "fa": "دایرکتور محصول",         "slug": "director"},
    {"num": "سطح ۶", "fa": "CPO",                    "slug": "cpo"},
]
