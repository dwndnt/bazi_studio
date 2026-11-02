
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from html import escape
from typing import Any
import math

import streamlit as st

try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderServiceError, GeocoderTimedOut
    GEOPY_AVAILABLE = True
except ImportError:
    Nominatim = None
    GEOPY_AVAILABLE = False

    class GeocoderServiceError(Exception):
        pass

    class GeocoderTimedOut(Exception):
        pass

try:
    from bazi_engine import build_chart
    BAZI_ENGINE_AVAILABLE = True
    BAZI_ENGINE_ERROR = None
except Exception as exc:
    build_chart = None
    BAZI_ENGINE_AVAILABLE = False
    BAZI_ENGINE_ERROR = exc


# ============================================================
# KONFIGURASI APLIKASI
# ============================================================

PAGE_CHART = "Chart BaZi"
PAGE_COMPATIBILITY = "Uji Kecocokan Pasangan"
PAGE_ABOUT = "Tentang"

PROFILE_A_NAME = "Profil Anda"
PROFILE_B_NAME = "Profil Pasangan"

APP_NAME = "BAZI STUDIO"
APP_OWNER = "Dewan Dinata"
APP_VERSION = "1.4.3"

DEFAULT_LOCATION = {
    "name": "Medan, Sumatera Utara, Indonesia",
    "latitude": 3.5952,
    "longitude": 98.6722,
}

LOCATION_ALIASES = {
    "medan": "Medan, Sumatera Utara, Indonesia",
    "medan kota": "Medan, Sumatera Utara, Indonesia",
    "kota medan": "Medan, Sumatera Utara, Indonesia",
    "medan city": "Medan, Sumatera Utara, Indonesia",
    "medan area": "Medan Area, Medan, Sumatera Utara, Indonesia",
    "kota medan, indonesia": "Medan, Sumatera Utara, Indonesia",
    "medan, indonesia": "Medan, Sumatera Utara, Indonesia",
}

st.set_page_config(
    page_title=APP_NAME,
    page_icon="☯️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bazi-bg: #0b1220;
    --bazi-panel: #131e30;
    --bazi-border: rgba(148,163,184,.20);
    --bazi-text: #e8eef8;
    --bazi-muted: #9aabc2;
    --bazi-gold: #d9b56d;
}

html, body, [class*="css"] {
    font-family: Inter, sans-serif;
}

.stApp {
    background: radial-gradient(ellipse at 10% 0%, #172943 0%, transparent 45%),
                linear-gradient(145deg,#0b1220 0%,#101a2b 60%,#0b1220 100%);
    color: var(--bazi-text);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#101a2b,#0b1220);
    border-right: 1px solid var(--bazi-border);
}

.bazi-hero {
    padding: 28px 30px;
    border: 1px solid var(--bazi-border);
    border-radius: 22px;
    background: linear-gradient(120deg,#192b43,#111c2e 70%);
    margin-bottom: 24px;
    box-shadow: 0 12px 36px rgba(0,0,0,.20);
}

.bazi-eyebrow {
    color: var(--bazi-gold);
    text-transform: uppercase;
    letter-spacing: 3px;
    font-size: 11px;
    font-weight: 700;
}

.bazi-title {
    color: #f4f7fb;
    font-size: clamp(28px,4vw,42px);
    font-weight: 800;
    letter-spacing: -1px;
    margin: 8px 0;
}

.bazi-subtitle {
    color:#b5c4d8;
    font-size:14px;
    line-height:1.7;
    max-width:760px;
}

.bazi-owner {
    color:var(--bazi-gold);
    font-size:12px;
    margin-top:16px;
}

.bazi-pillar {
    border:1px solid var(--bazi-border);
    border-radius:16px;
    padding:18px 10px;
    text-align:center;
    background:linear-gradient(180deg,#19283d,#111b2b);
    min-height:190px;
}

.bazi-pillar-label {
    color:#aebdd0;
    font-size:12px;
    letter-spacing:1px;
    margin-bottom:12px;
}

.bazi-pillar-stem {
    color:#f2d59b;
    font-size:35px;
    font-weight:800;
    line-height:1.3;
}

.bazi-pillar-branch {
    color:#f0f4fa;
    font-size:35px;
    font-weight:800;
    line-height:1.3;
}

.bazi-pillar-meta {
    color:#aebdd0;
    font-size:12px;
    margin-top:8px;
}

.bazi-section {
    font-size:19px;
    font-weight:700;
    color:#f0f4fa;
    margin:18px 0 12px;
}

.bazi-element-panel {
    border:1px solid var(--bazi-border);
    border-radius:20px;
    padding:22px;
    background:linear-gradient(145deg,#17263b,#101a2a);
    height:100%;
}

.bazi-element-heading {
    color:#f0f4fa;
    font-size:17px;
    font-weight:750;
    margin-bottom:5px;
}

.bazi-element-subheading {
    color:#9aabc2;
    font-size:12px;
    line-height:1.6;
    margin-bottom:18px;
}

.bazi-donut-area {
    display:flex;
    justify-content:center;
    align-items:center;
    padding:8px 0 20px;
}

.bazi-donut {
    width:220px;
    height:220px;
    max-width:100%;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    position:relative;
    box-shadow:0 12px 32px rgba(0,0,0,.20);
}

.bazi-donut-center {
    width:142px;
    height:142px;
    border-radius:50%;
    background:#111c2d;
    border:1px solid rgba(255,255,255,.08);
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;
    text-align:center;
}

.bazi-donut-total {
    color:#f4d69b;
    font-size:35px;
    line-height:1.2;
    font-weight:800;
}

.bazi-donut-label {
    color:#9aabc2;
    font-size:11px;
    margin-top:5px;
    letter-spacing:.7px;
    text-transform:uppercase;
}

.bazi-element-legend {
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:10px;
    margin-top:4px;
}

.bazi-element-item {
    display:flex;
    align-items:center;
    gap:9px;
    padding:11px;
    border-radius:11px;
    background:rgba(255,255,255,.035);
    border:1px solid rgba(148,163,184,.10);
    min-width:0;
}

.bazi-element-dot {
    width:10px;
    height:10px;
    border-radius:50%;
    flex-shrink:0;
}

.bazi-element-name {
    color:#dce6f4;
    font-size:12px;
    font-weight:600;
}

.bazi-element-value {
    color:#9aabc2;
    font-size:11px;
    margin-top:3px;
}

.bazi-footer {
    text-align:center;
    border-top:1px solid var(--bazi-border);
    padding:20px 0 8px;
    margin-top:40px;
    color:#91a2b9;
    font-size:12px;
}

.bazi-footer strong {
    color:var(--bazi-gold);
}

div[data-testid="stMetric"] {
    background:rgba(25,40,61,.72);
    border:1px solid var(--bazi-border);
    padding:16px;
    border-radius:14px;
}

div[data-testid="stMetricLabel"] {
    color:#aebdd0;
}

div[data-testid="stMetricValue"] {
    color:#f2d59b;
}

.stButton > button {
    border-radius:10px;
    font-weight:650;
    min-height:42px;
    transition:all .2s ease;
}

.stButton > button:hover {
    border-color:var(--bazi-gold);
    transform:translateY(-1px);
}

div[data-testid="stDataFrame"] {
    border:1px solid var(--bazi-border);
    border-radius:12px;
    overflow:hidden;
}

@media(max-width:700px) {
    .bazi-hero {
        padding:22px 18px;
    }

    .bazi-donut {
        width:190px;
        height:190px;
    }

    .bazi-donut-center {
        width:124px;
        height:124px;
    }

    .bazi-element-panel {
        padding:16px;
    }

    .bazi-element-legend {
        grid-template-columns:1fr;
    }
}
</style>
""")


# ============================================================
# KAMUS BAZI
# ============================================================

STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

BRANCHES = [
    "子", "丑", "寅", "卯", "辰", "巳",
    "午", "未", "申", "酉", "戌", "亥"
]

STEM_INFO = {
    "甲": ("Kayu", "Yang"),
    "乙": ("Kayu", "Yin"),
    "丙": ("Api", "Yang"),
    "丁": ("Api", "Yin"),
    "戊": ("Tanah", "Yang"),
    "己": ("Tanah", "Yin"),
    "庚": ("Logam", "Yang"),
    "辛": ("Logam", "Yin"),
    "壬": ("Air", "Yang"),
    "癸": ("Air", "Yin"),
}

BRANCH_INFO = {
    "子": ("Tikus", "Air"),
    "丑": ("Kerbau", "Tanah"),
    "寅": ("Macan", "Kayu"),
    "卯": ("Kelinci", "Kayu"),
    "辰": ("Naga", "Tanah"),
    "巳": ("Ular", "Api"),
    "午": ("Kuda", "Api"),
    "未": ("Kambing", "Tanah"),
    "申": ("Monyet", "Logam"),
    "酉": ("Ayam", "Logam"),
    "戌": ("Anjing", "Tanah"),
    "亥": ("Babi", "Air"),
}

HIDDEN_STEMS = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "戊", "庚"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"],
}

ELEMENTS = ["Kayu", "Api", "Tanah", "Logam", "Air"]

ELEMENT_COLORS = {
    "Kayu": "#48c78e",
    "Api": "#ff6b6b",
    "Tanah": "#e7b85c",
    "Logam": "#c1c9d8",
    "Air": "#58a6ff",
}

GENERATES = {
    "Kayu": "Api",
    "Api": "Tanah",
    "Tanah": "Logam",
    "Logam": "Air",
    "Air": "Kayu",
}

CONTROLS = {
    "Kayu": "Tanah",
    "Tanah": "Air",
    "Air": "Api",
    "Api": "Logam",
    "Logam": "Kayu",
}

BRANCH_ORDER = {x: i for i, x in enumerate(BRANCHES)}
STEM_ORDER = {x: i for i, x in enumerate(STEMS)}

PILLAR_LABELS = {
    "year": "Tahun",
    "year_pillar": "Tahun",
    "年柱": "Tahun",
    "tahun": "Tahun",
    "month": "Bulan",
    "month_pillar": "Bulan",
    "月柱": "Bulan",
    "bulan": "Bulan",
    "day": "Hari",
    "day_pillar": "Hari",
    "日柱": "Hari",
    "hari": "Hari",
    "hour": "Jam",
    "hour_pillar": "Jam",
    "时柱": "Jam",
    "時柱": "Jam",
    "jam": "Jam",
}

STEM_KEYS = {
    "stem", "heavenly_stem", "heavenlystem", "gan", "天干", "batang",
    "stem_char", "stem_symbol", "tiangan", "tian_gan",
}

BRANCH_KEYS = {
    "branch", "earthly_branch", "earthlybranch", "zhi", "地支", "cabang",
    "branch_char", "branch_symbol", "dizhi", "di_zhi",
}

PILLAR_KEYS = {
    "pillar", "pillars", "four_pillars", "bazi", "八字",
    "四柱", "chart", "natal_chart", "natal"
}


# ============================================================
# NORMALISASI SCHEMA ENGINE
# ============================================================

def object_to_dict(value: Any) -> dict:
    if isinstance(value, dict):
        return value

    if hasattr(value, "__dict__"):
        try:
            return vars(value)
        except Exception:
            return {}

    return {}


def normalize_symbol(
    value: Any,
    valid_symbols: list[str]
) -> str | None:

    if value is None:
        return None

    if isinstance(value, (list, tuple)):
        for item in value:
            found = normalize_symbol(item, valid_symbols)

            if found:
                return found

        return None

    if isinstance(value, dict) or hasattr(value, "__dict__"):
        data = object_to_dict(value)

        preferred = (
            "symbol", "char", "character", "chinese", "value", "name",
            "stem", "branch", "gan", "zhi", "天干", "地支", "code",
        )

        for key in preferred:
            if key in data:
                found = normalize_symbol(
                    data[key],
                    valid_symbols
                )

                if found:
                    return found

        return None

    text = str(value).strip()

    return next(
        (symbol for symbol in valid_symbols if symbol in text),
        None
    )


def _key_norm(key: Any) -> str:
    return (
        str(key)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


def _find_key(mapping: dict, aliases: set[str]) -> Any:
    for key, value in mapping.items():
        if _key_norm(key) in aliases:
            return value

    return None


def _label_from_key(key: Any) -> str | None:
    return PILLAR_LABELS.get(_key_norm(key))


def _direct_pillar_candidates(chart: Any) -> list[tuple[str, Any]]:
    data = object_to_dict(chart)
    candidates: list[tuple[str, Any]] = []

    for key, value in data.items():
        label = _label_from_key(key)

        if label and value is not None:
            candidates.append((label, value))

    for container_key, container_value in data.items():

        if _key_norm(container_key) in PILLAR_KEYS:
            nested = object_to_dict(container_value)

            for key, value in nested.items():
                label = _label_from_key(key)

                if label and value is not None:
                    candidates.append((label, value))

    result = []
    seen = set()

    for label, value in candidates:
        if label not in seen:
            result.append((label, value))
            seen.add(label)

    return result


def extract_pillars(chart: Any) -> list[dict]:
    """Extract four pillars from the actual bazi_engine schema."""

    data = object_to_dict(chart)
    pillars_data = object_to_dict(data.get("pillars", {}))

    mapping = {
        "year": "Tahun",
        "month": "Bulan",
        "day": "Hari",
        "hour": "Jam",
    }

    result = []

    for key, label in mapping.items():

        pillar = object_to_dict(
            pillars_data.get(key, {})
        )

        stem_data = object_to_dict(
            pillar.get("stem", {})
        )

        branch_data = object_to_dict(
            pillar.get("branch", {})
        )

        stem_raw = (
            stem_data.get("han")
            or stem_data.get("symbol")
            or stem_data.get("pinyin")
        )

        branch_raw = (
            branch_data.get("han")
            or branch_data.get("symbol")
            or branch_data.get("pinyin")
        )

        stem = normalize_symbol(stem_raw, STEMS)
        branch = normalize_symbol(branch_raw, BRANCHES)

        if not stem or not branch:
            continue

        result.append({
            "Pilar": label,
            "stem": stem,
            "branch": branch,
            "raw": pillar,
        })

    return result


# ============================================================
# LIMA ELEMEN DAN TEN GODS
# ============================================================

def stem_element(stem: str | None) -> str | None:
    return STEM_INFO.get(stem, (None, None))[0]


def stem_polarity(stem: str | None) -> str | None:
    return STEM_INFO.get(stem, (None, None))[1]


def branch_animal(branch: str | None) -> str:
    return BRANCH_INFO.get(
        branch,
        ("Tidak diketahui", "")
    )[0]


def ten_god(
    day_stem: str | None,
    other_stem: str | None
) -> str:

    if day_stem not in STEM_INFO or other_stem not in STEM_INFO:
        return "—"

    dm_element, dm_polarity = STEM_INFO[day_stem]
    other_element, other_polarity = STEM_INFO[other_stem]

    same = dm_polarity == other_polarity

    if dm_element == other_element:
        return (
            "比肩 (Friend)"
            if same
            else "劫财 (Rob Wealth)"
        )

    if GENERATES[other_element] == dm_element:
        return (
            "偏印 (Indirect Resource)"
            if same
            else "正印 (Direct Resource)"
        )

    if GENERATES[dm_element] == other_element:
        return (
            "食神 (Eating God)"
            if same
            else "伤官 (Hurting Officer)"
        )

    if CONTROLS[dm_element] == other_element:
        return (
            "偏财 (Indirect Wealth)"
            if same
            else "正财 (Direct Wealth)"
        )

    if CONTROLS[other_element] == dm_element:
        return (
            "七杀 (Seven Killings)"
            if same
            else "正官 (Direct Officer)"
        )

    return "—"


class ElementEngine:

    def analyze(self, chart: Any) -> dict:

        pillars = extract_pillars(chart)

        day_stem = next(
            (
                p["stem"]
                for p in pillars
                if p["Pilar"] == "Hari"
            ),
            None
        )

        counts = {
            element: 0.0
            for element in ELEMENTS
        }

        details = []

        for pillar in pillars:

            stem = pillar.get("stem")
            branch = pillar.get("branch")

            stem_el = stem_element(stem)

            if stem_el:
                counts[stem_el] += 1.0

            hidden = HIDDEN_STEMS.get(branch, [])

            for hidden_stem in hidden:
                element = stem_element(hidden_stem)

                if element:
                    counts[element] += 0.5

            details.append({
                "Pilar": pillar["Pilar"],
                "Batang Langit": stem or "Tidak dikenali",
                "Elemen batang": stem_el or "—",
                "Cabang Bumi": branch or "Tidak dikenali",
                "Shio": branch_animal(branch) if branch else "—",
                "Hidden Stems": "、".join(hidden) if hidden else "—",
                "Ten Gods batang": (
                    ten_god(day_stem, stem)
                    if day_stem and stem
                    else "—"
                ),
            })

        return {
            "details": details,
            "counts": counts,
            "day_stem": day_stem,
            "pillars": pillars,
        }


# ============================================================
# WAKTU KELAHIRAN
# ============================================================

def equation_of_time_minutes(day_of_year: int) -> float:

    gamma = (
        2.0
        * math.pi
        / 365.0
        * (day_of_year - 1)
    )

    return 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2 * gamma)
        - 0.040849 * math.sin(2 * gamma)
    )


def localize_birth(
    birth_date: date,
    birth_time: time,
    utc_offset_hours: float,
    longitude: float,
    apply_solar_correction: bool = True,
    apply_equation_of_time: bool = True,
) -> tuple[datetime, dict]:

    civil_dt = datetime.combine(
        birth_date,
        birth_time
    )

    correction = 0.0
    meridian = 15.0 * utc_offset_hours

    if apply_solar_correction:
        correction += 4.0 * (
            longitude - meridian
        )

    if apply_equation_of_time:
        correction += equation_of_time_minutes(
            civil_dt.timetuple().tm_yday
        )

    adjusted_dt = civil_dt + timedelta(
        minutes=correction
    )

    return adjusted_dt, {
        "civil_datetime": civil_dt,
        "adjusted_datetime": adjusted_dt,
        "utc_offset_hours": utc_offset_hours,
        "longitude": longitude,
        "standard_meridian": meridian,
        "correction_minutes": correction,
        "solar_correction_enabled": apply_solar_correction,
        "equation_of_time_enabled": apply_equation_of_time,
    }


def safe_chart(
    local_dt: datetime,
    offset_hours: float,
    gender: str,
    luck_count: int = 8,
    annual_count: int = 10,
) -> Any:

    if not BAZI_ENGINE_AVAILABLE:
        raise RuntimeError(
            "bazi_engine tidak tersedia."
        )

    return build_chart(
        local_dt,
        offset_hours=offset_hours,
        gender=gender,
        luck_count=luck_count,
        annual_count=annual_count,
    )


# ============================================================
# GEOCODING
# ============================================================

def normalize_location_query(query: str) -> str:

    cleaned = " ".join(
        query.strip().split()
    )

    if not cleaned:
        return ""

    alias = LOCATION_ALIASES.get(
        cleaned.casefold()
    )

    if alias:
        return alias

    if "," not in cleaned:
        cleaned = f"{cleaned}, Indonesia"

    return cleaned


@st.cache_data(ttl=3600, show_spinner=False)
def geocode_location(query: str) -> dict | None:
    """Cache hasil koordinat sukses saja; kegagalan tidak di-cache."""

    if not GEOPY_AVAILABLE or not query.strip():
        return None

    try:

        geolocator = Nominatim(
            user_agent=f"bazi-studio/{APP_VERSION}"
        )

        result = geolocator.geocode(
            query,
            exactly_one=True,
            addressdetails=True,
            timeout=10,
            country_codes="id",
        )

        if result is None:
            return None

        return {
            "name": result.address,
            "latitude": float(result.latitude),
            "longitude": float(result.longitude),
        }

    except (GeocoderTimedOut, GeocoderServiceError):
        return None

    except Exception:
        return None


# ============================================================
# RELASI CABANG DAN KOMPATIBILITAS HEURISTIK
# ============================================================

SIX_CLASHES = {
    frozenset(("子", "午")),
    frozenset(("丑", "未")),
    frozenset(("寅", "申")),
    frozenset(("卯", "酉")),
    frozenset(("辰", "戌")),
    frozenset(("巳", "亥")),
}

SIX_COMBINATIONS = {
    frozenset(("子", "丑")),
    frozenset(("寅", "亥")),
    frozenset(("卯", "戌")),
    frozenset(("辰", "酉")),
    frozenset(("巳", "申")),
    frozenset(("午", "未")),
}

THREE_HARMONIES = [
    ({"申", "子", "辰"}, "Air"),
    ({"亥", "卯", "未"}, "Kayu"),
    ({"寅", "午", "戌"}, "Api"),
    ({"巳", "酉", "丑"}, "Logam"),
]


def branch_relationships(pillars: list[dict]) -> list[str]:

    branches = [
        (p["Pilar"], p.get("branch"))
        for p in pillars
        if p.get("branch") in BRANCHES
    ]

    notes = []

    for i in range(len(branches)):

        for j in range(i + 1, len(branches)):

            la, a = branches[i]
            lb, b = branches[j]

            pair = frozenset((a, b))

            if a == b:
                notes.append(
                    f"{la}–{lb}: cabang berulang ({a})"
                )

            if pair in SIX_CLASHES:
                notes.append(
                    f"{la}–{lb}: clash / benturan ({a}–{b})"
                )

            if pair in SIX_COMBINATIONS:
                notes.append(
                    f"{la}–{lb}: kombinasi enam ({a}–{b})"
                )

    branch_set = {
        b for _, b in branches
    }

    for trio, element in THREE_HARMONIES:

        if trio.issubset(branch_set):

            ordered = "".join(
                sorted(trio, key=BRANCH_ORDER.get)
            )

            notes.append(
                f"Tiga Harmoni lengkap: {ordered} → {element}"
            )

    return notes or [
        "Tidak ada relasi utama yang terdeteksi dari aturan sederhana ini."
    ]


def compatibility_report(
    chart_a: Any,
    chart_b: Any
) -> dict:

    analysis_a = ElementEngine().analyze(chart_a)
    analysis_b = ElementEngine().analyze(chart_b)

    pillars_a = analysis_a["pillars"]
    pillars_b = analysis_b["pillars"]

    branches_a = {
        p["branch"]
        for p in pillars_a
        if p.get("branch") in BRANCHES
    }

    branches_b = {
        p["branch"]
        for p in pillars_b
        if p.get("branch") in BRANCHES
    }

    stems_a = {
        p["stem"]
        for p in pillars_a
        if p.get("stem") in STEMS
    }

    stems_b = {
        p["stem"]
        for p in pillars_b
        if p.get("stem") in STEMS
    }

    shared_branches = branches_a & branches_b
    shared_stems = stems_a & stems_b

    clashes = []
    combinations = []

    for a in branches_a:

        for b in branches_b:

            pair = frozenset((a, b))

            if pair in SIX_CLASHES:
                clashes.append(f"{a}–{b}")

            if pair in SIX_COMBINATIONS:
                combinations.append(f"{a}–{b}")

    score = 50 + min(
        15,
        5 * len(shared_branches)
    )

    score += min(
        10,
        3 * len(set(combinations))
    )

    score -= min(
        15,
        4 * len(set(clashes))
    )

    score += min(
        5,
        2 * len(shared_stems)
    )

    score = max(
        0,
        min(100, score)
    )

    return {
        "score": score,
        "shared_branches": sorted(
            shared_branches,
            key=BRANCH_ORDER.get
        ),
        "shared_stems": sorted(
            shared_stems,
            key=STEM_ORDER.get
        ),
        "clashes": sorted(set(clashes)),
        "combinations": sorted(set(combinations)),
        "elements_a": analysis_a["counts"],
        "elements_b": analysis_b["counts"],
    }


# ============================================================
# KOMPONEN TAMPILAN
# ============================================================

def display_pillar_table(analysis: dict) -> None:

    if not analysis["details"]:

        st.warning(
            "Detail pilar belum tersedia. Silakan periksa kembali "
            "data kelahiran dan hasil perhitungan."
        )

        return

    st.dataframe(
        analysis["details"],
        use_container_width=True,
        hide_index=True,
    )


def render_pillar_cards(pillars: list[dict]) -> None:

    order = [
        "Tahun",
        "Bulan",
        "Hari",
        "Jam",
    ]

    by_label = {
        p["Pilar"]: p
        for p in pillars
    }

    columns = st.columns(4)

    for column, label in zip(columns, order):

        pillar = by_label.get(label)

        with column:

            if pillar is None:

                st.html(f"""
                <div class="bazi-pillar">
                    <div class="bazi-pillar-label">{escape(label.upper())}</div>
                    <div class="bazi-pillar-meta">Belum tersedia</div>
                </div>
                """)

                continue

            stem = pillar.get("stem", "—")
            branch = pillar.get("branch", "—")

            stem_meta = STEM_INFO.get(
                stem,
                ("—", "—")
            )

            branch_meta = BRANCH_INFO.get(
                branch,
                ("—", "—")
            )

            hidden = "、".join(
                HIDDEN_STEMS.get(branch, [])
            ) or "—"

            st.html(f"""
            <div class="bazi-pillar">
                <div class="bazi-pillar-label">{escape(label.upper())}</div>
                <div class="bazi-pillar-stem">{escape(str(stem))}</div>
                <div class="bazi-pillar-meta">
                    {escape(stem_meta[0])} · {escape(stem_meta[1])}
                </div>
                <div class="bazi-pillar-branch">{escape(str(branch))}</div>
                <div class="bazi-pillar-meta">
                    {escape(branch_meta[0])} · {escape(branch_meta[1])}
                </div>
                <div class="bazi-pillar-meta">
                    Hidden Stems: {escape(hidden)}
                </div>
            </div>
            """)


def render_element_distribution(
    counts: dict,
    title: str = "Distribusi Lima Elemen",
) -> None:

    total = sum(
        max(
            0.0,
            float(counts.get(e, 0.0) or 0.0)
        )
        for e in ELEMENTS
    )

    safe_title = escape(str(title))

    if total <= 0:

        st.html(f"""
        <div class="bazi-element-panel">
            <div class="bazi-element-heading">{safe_title}</div>
            <div class="bazi-element-subheading">
                Belum ada data elemen yang dapat divisualisasikan.
            </div>
        </div>
        """)

        return

    start = 0.0
    segments = []
    legend_items = []

    for element in ELEMENTS:

        value = max(
            0.0,
            float(counts.get(element, 0.0) or 0.0)
        )

        percentage = value / total * 100.0
        end = start + percentage
        color = ELEMENT_COLORS[element]

        segments.append(
            f"{color} {start:.2f}% {end:.2f}%"
        )

        legend_items.append(f"""
        <div class="bazi-element-item">
            <span class="bazi-element-dot"
                  style="background-color:{color};"></span>
            <div>
                <div class="bazi-element-name">{element}</div>
                <div class="bazi-element-value">
                    {value:.1f} poin · {percentage:.1f}%
                </div>
            </div>
        </div>
        """)

        start = end

    gradient = ", ".join(segments)
    legend = "\n".join(legend_items)

    st.html(f"""
    <div class="bazi-element-panel">
        <div class="bazi-element-heading">{safe_title}</div>
        <div class="bazi-element-subheading">
            Proporsi skor indikator setiap elemen dalam chart.
        </div>
        <div class="bazi-donut-area">
            <div class="bazi-donut"
                 style="background:conic-gradient({gradient});">
                <div class="bazi-donut-center">
                    <div class="bazi-donut-total">{total:.1f}</div>
                    <div class="bazi-donut-label">Total poin</div>
                </div>
            </div>
        </div>
        <div class="bazi-element-legend">{legend}</div>
    </div>
    """)

    st.caption(
        "Pembobotan indikator: 1 poin untuk setiap batang langit dan "
        "0,5 poin untuk setiap hidden stem. Persentase dinormalisasi "
        "terhadap total poin; ini bukan probabilitas maupun ukuran baku "
        "kekuatan Day Master."
    )


def render_chart_result(
    chart: Any,
    title: str
) -> None:

    st.subheader(title)

    analysis = ElementEngine().analyze(chart)
    pillars = analysis["pillars"]

    if len(pillars) < 4:

        st.warning(
            f"Hanya {len(pillars)} dari 4 pilar yang berhasil dikenali. "
            "Aplikasi tidak akan menebak posisi pilar yang tidak memiliki label."
        )

    st.html(
        '<div class="bazi-section">Empat Pilar Kelahiran</div>'
    )

    render_pillar_cards(pillars)

    with st.expander("Tabel detail pilar"):
        display_pillar_table(analysis)

    day_stem = analysis["day_stem"]

    if day_stem:

        element, polarity = STEM_INFO[day_stem]

        c1, c2, c3 = st.columns(3)

        c1.metric("Day Master", day_stem)
        c2.metric("Elemen Day Master", element)
        c3.metric("Polaritas", polarity)

    else:

        st.warning(
            "Day Master belum berhasil dikenali karena pilar Hari belum tersedia."
        )

    col1, col2 = st.columns(
        [1.1, 0.9],
        gap="large"
    )

    with col1:
        render_element_distribution(
            analysis["counts"]
        )

    with col2:

        st.markdown("#### Relasi antarcabang")

        for note in branch_relationships(pillars):
            st.write(f"• {note}")


# ============================================================
# NAVIGASI
# ============================================================

def set_active_page(page_name: str) -> None:
    """Mengubah halaman aktif sebelum Streamlit menjalankan ulang aplikasi."""

    st.session_state["active_page"] = page_name


# ============================================================
# APLIKASI UTAMA
# ============================================================

def main() -> None:

    st.session_state.setdefault(
        "birth_location",
        DEFAULT_LOCATION.copy()
    )

    st.session_state.setdefault(
        "location_b",
        DEFAULT_LOCATION.copy()
    )

    st.session_state.setdefault(
        "chart_a",
        None
    )

    st.session_state.setdefault(
        "chart_a_meta",
        None
    )

    st.session_state.setdefault(
        "chart_a_label",
        PROFILE_A_NAME
    )

    st.session_state.setdefault(
        "location_query",
        "Medan"
    )

    st.session_state.setdefault(
        "b_location_query",
        "Medan"
    )

    # Menjaga halaman aktif dan hasil analisis selama session.
    st.session_state.setdefault(
        "active_page",
        PAGE_CHART
    )

    st.session_state.setdefault(
        "compatibility_chart_b",
        None
    )

    st.session_state.setdefault(
        "compatibility_report",
        None
    )

    st.session_state.setdefault(
        "compatibility_meta_b",
        None
    )

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    st.html(f"""
    <div class="bazi-hero">
        <div class="bazi-eyebrow">
            Traditional Chinese Metaphysics
        </div>

        <div class="bazi-title">
            ☯ {escape(APP_NAME)}
        </div>

        <div class="bazi-subtitle">
            Personal BaZi chart analysis, Five Elements, Ten Gods,
            Hidden Stems, Da Yun, dan branch relationships.
        </div>

        <div class="bazi-owner">
            Created and developed by
            <strong>{escape(APP_OWNER)}</strong>
            &nbsp;·&nbsp; Version {APP_VERSION}
        </div>
    </div>
    """)

    if not BAZI_ENGINE_AVAILABLE:
        st.error("Fitur perhitungan BaZi sedang tidak tersedia.")
        st.info(
            "Silakan hubungi pengelola aplikasi apabila masalah ini terus terjadi."
        )
        st.stop()

    # ========================================================
    # SIDEBAR: PROFIL ANDA
    # ========================================================

    with st.sidebar:

        st.markdown("## ☯ BaZi Studio")
        st.caption(f"Created by {APP_OWNER}")
        st.divider()

        st.header("Data Kelahiran Anda")

        person_label = st.text_input(
            "Nama Anda",
            value=PROFILE_A_NAME,
            placeholder="Masukkan nama Anda",
        )

        birth_date = st.date_input(
            "Tanggal lahir",
            value=date(2000, 12, 19),
            min_value=date(1900, 1, 1),
            max_value=date.today(),
        )

        birth_time = st.time_input(
            "Jam lahir",
            value=time(22, 23),
        )

        gender_label = st.selectbox(
            "Jenis kelamin untuk Da Yun",
            [
                "Laki-laki",
                "Perempuan",
                "Tidak ditentukan",
            ],
            index=0,
        )

        gender_map = {
            "Laki-laki": "male",
            "Perempuan": "female",
            "Tidak ditentukan": "unknown",
        }

        utc_offset_a = st.number_input(
            "UTC offset zona waktu",
            min_value=-12.0,
            max_value=14.0,
            value=7.0,
            step=0.5,
            key="utc_offset_a",
            help="WIB = UTC+7, WITA = UTC+8, WIT = UTC+9.",
        )

        st.markdown("### 📍 Lokasi kelahiran")

        location_query = st.text_input(
            "Kota atau area",
            key="location_query",
            placeholder="Contoh: Medan Area, Medan atau Jakarta",
        )

        if not GEOPY_AVAILABLE:

            st.warning(
                "Pencarian lokasi memerlukan geopy. "
                "Instal dengan: python -m pip install geopy"
            )

        if st.button(
            "🔎 Cari lokasi",
            key="search_birth_location",
            use_container_width=True,
            disabled=not GEOPY_AVAILABLE,
        ):

            normalized = normalize_location_query(
                location_query
            )

            if not normalized:

                st.warning(
                    "Masukkan nama lokasi terlebih dahulu."
                )

            else:

                with st.spinner(
                    "Mencari koordinat lokasi..."
                ):

                    found = geocode_location(
                        normalized
                    )

                if found:

                    st.session_state["birth_location"] = found
                    st.success(
                        "Lokasi berhasil ditemukan."
                    )

                else:

                    st.warning(
                        "Lokasi tidak ditemukan atau layanan geocoding tidak tersedia."
                    )

        selected_location = st.session_state["birth_location"]

        latitude_a = float(
            selected_location["latitude"]
        )

        longitude_a = float(
            selected_location["longitude"]
        )

        st.caption(
            selected_location["name"]
        )

        loc1, loc2 = st.columns(2)

        loc1.metric(
            "Lintang",
            f"{latitude_a:.5f}°"
        )

        loc2.metric(
            "Bujur",
            f"{longitude_a:.5f}°"
        )

        st.caption(
            "Geocoding: OpenStreetMap / Nominatim"
        )

        solar_correction = st.checkbox(
            "Koreksi Bujur Lokasi",
            value=True,
            help=(
                "Menyesuaikan jam lokal berdasarkan selisih "
                "bujur dengan meridian zona waktu."
            ),
        )

        eot_correction = st.checkbox(
            "Koreksi Waktu Lokal",
            value=True,
            help=(
                "Menambahkan estimasi persamaan waktu "
                "berdasarkan hari dalam tahun."
            ),
        )

        st.divider()

        luck_options = {
            "4 Siklus": 4,
            "6 Siklus": 6,
            "8 Siklus (Rekomendasi)": 8,
            "10 Siklus": 10,
            "12 Siklus": 12,
        }

        annual_options = {
            "5 Tahun": 5,
            "10 Tahun (Rekomendasi)": 10,
            "15 Tahun": 15,
            "20 Tahun": 20,
            "30 Tahun": 30,
        }

        luck_selection = st.selectbox(
            "Jumlah Siklus Da Yun",
            options=list(luck_options.keys()),
            index=2,
            help="Pilih jumlah siklus keberuntungan Da Yun yang ingin ditampilkan.",
        )

        annual_selection = st.selectbox(
            "Cakupan Analisis Tahunan",
            options=list(annual_options.keys()),
            index=1,
            help="Pilih rentang tahun yang ingin dianalisis.",
        )

        luck_count = luck_options[luck_selection]
        annual_count = annual_options[annual_selection]
        calculate = st.button(
                "Hitung BaZi",
                type="primary",
                use_container_width=True,
            )

    # ========================================================
    # INFORMASI METODE WAKTU
    # ========================================================

    with st.expander(
        "Metode penentuan waktu kelahiran"
    ):

        st.write(
            "**Waktu lokal** adalah tanggal dan jam resmi "
            "yang dimasukkan untuk lokasi kelahiran."
        )

        st.write(
            "**Perkiraan waktu matahari** menyesuaikan jam lokal "
            "menggunakan koreksi bujur dan, jika diaktifkan, "
            "persamaan waktu."
        )

        st.write(
            "Koreksi bujur menggunakan 4 menit untuk setiap "
            "derajat selisih bujur dari meridian zona waktu."
        )

        st.caption(
            "Perhatikan kemungkinan penerapan koreksi waktu yang sama lebih dari "
            "satu kali. Koreksi ganda dapat memengaruhi hasil perhitungan empat pilar."
        )

    # ========================================================
    # HITUNG CHART PROFIL ANDA
    # ========================================================

    if calculate:

        adjusted_dt, meta = localize_birth(
            birth_date,
            birth_time,
            utc_offset_a,
            longitude_a,
            solar_correction,
            eot_correction,
        )

        try:

            chart = safe_chart(
                adjusted_dt,
                utc_offset_a,
                gender_map[gender_label],
                luck_count,
                annual_count,
            )

            st.session_state["chart_a"] = chart
            st.session_state["chart_a_meta"] = meta

            st.session_state["chart_a_label"] = (
                person_label.strip()
                or PROFILE_A_NAME
            )

            # Hasil analisis pasangan sebelumnya tidak lagi valid
            # setelah Profil Anda dihitung ulang.
            st.session_state["compatibility_chart_b"] = None
            st.session_state["compatibility_report"] = None
            st.session_state["compatibility_meta_b"] = None

            st.session_state["active_page"] = PAGE_CHART

            st.success(
                "Perhitungan BaZi berhasil diselesaikan."
            )

        except Exception:

            st.error(
                "Perhitungan chart gagal. Periksa kembali data kelahiran "
                "dan konfigurasi engine."
            )

    # ========================================================
    # NAVIGASI UTAMA
    # ========================================================

    active_page = st.radio(
        "Navigasi BaZi Studio",
        [
            PAGE_CHART,
            PAGE_COMPATIBILITY,
            PAGE_ABOUT,
        ],
        key="active_page",
        horizontal=True,
        label_visibility="collapsed",
    )

    # ========================================================
    # HALAMAN CHART BAZI
    # ========================================================

    if active_page == PAGE_CHART:

        if st.session_state["chart_a"] is None:

            st.info(
                "Masukkan data kelahiran di sidebar, "
                "lalu tekan **Hitung BaZi**."
            )

        else:

            meta = (
                st.session_state["chart_a_meta"]
                or {}
            )

            st.caption(
                f'{st.session_state["chart_a_label"]} · '
                f'Waktu lokal: {meta.get("civil_datetime", "—")} · '
                f'Perkiraan waktu matahari: {meta.get("adjusted_datetime", "—")} · '
                f'Koreksi: {meta.get("correction_minutes", 0):+.2f} menit'
            )

            render_chart_result(
                st.session_state["chart_a"],
                st.session_state["chart_a_label"],
            )

    # ========================================================
    # HALAMAN UJI KECOCOKAN PASANGAN
    # ========================================================

    elif active_page == PAGE_COMPATIBILITY:

        st.subheader(
            "Uji Kecocokan Pasangan"
        )

        st.write(
            "Bandingkan batang dan cabang yang sama, kombinasi enam, "
            "serta clash antara dua chart BaZi. Skor yang dihasilkan "
            "merupakan heuristik aplikasi, bukan ukuran ilmiah "
            "kecocokan hubungan."
        )

        if st.session_state["chart_a"] is None:

            st.warning(
                "Hitung chart Profil Anda terlebih dahulu "
                "dari halaman Chart BaZi."
            )

        # ----------------------------------------------------
        # LOKASI PROFIL PASANGAN
        # ----------------------------------------------------

        st.markdown(
            "#### Lokasi Profil Pasangan"
        )

        st.text_input(
            "Kota atau area",
            key="b_location_query",
            placeholder="Contoh: Jakarta atau Medan",
        )

        if st.button(
            "🔎 Cari lokasi pasangan",
            key="search_location_b",
            disabled=not GEOPY_AVAILABLE,
        ):

            query_b = normalize_location_query(
                st.session_state.get(
                    "b_location_query",
                    "Medan"
                )
            )

            if query_b:

                with st.spinner(
                    "Mencari lokasi pasangan..."
                ):

                    result_b = geocode_location(
                        query_b
                    )

                if result_b:

                    st.session_state["location_b"] = result_b

                    st.success(
                        "Lokasi pasangan berhasil ditemukan."
                    )

                else:

                    st.warning(
                        "Lokasi pasangan tidak ditemukan. "
                        "Periksa nama kota dan provinsinya."
                    )

        selected_b = st.session_state["location_b"]

        b_longitude = float(
            selected_b["longitude"]
        )

        st.caption(
            f'Lokasi aktif: {selected_b["name"]}'
        )

        st.caption(
            f'Lintang: {selected_b["latitude"]:.5f}° · '
            f'Bujur: {b_longitude:.5f}°'
        )

        # ----------------------------------------------------
        # FORM INPUT PROFIL PASANGAN
        # ----------------------------------------------------

        with st.form("compatibility_form"):

            c1, c2 = st.columns(2)

            with c1:

                b_date = st.date_input(
                    "Tanggal lahir pasangan",
                    value=date(2001, 6, 15),
                    min_value=date(1900, 1, 1),
                    max_value=date.today(),
                    key="b_date",
                )

                b_time = st.time_input(
                    "Jam lahir pasangan",
                    value=time(12, 0),
                    key="b_time",
                )

                b_gender_label = st.selectbox(
                    "Jenis kelamin untuk Da Yun",
                    [
                        "Laki-laki",
                        "Perempuan",
                        "Tidak ditentukan",
                    ],
                    index=1,
                    key="b_gender",
                )

            with c2:

                b_offset = st.number_input(
                    "UTC offset zona waktu",
                    min_value=-12.0,
                    max_value=14.0,
                    value=7.0,
                    step=0.5,
                    key="b_offset",
                )

                b_solar = st.checkbox(
                    "Koreksi Bujur Lokasi",
                    value=True,
                    key="b_solar",
                )

                b_eot = st.checkbox(
                    "Koreksi Waktu Lokal",
                    value=True,
                    key="b_eot",
                )

            submitted = st.form_submit_button(
                "Analisis Kecocokan",
                type="primary",
                use_container_width=True,
                on_click=set_active_page,
                args=(PAGE_COMPATIBILITY,),
            )

        # ----------------------------------------------------
        # PROSES PERHITUNGAN PROFIL PASANGAN
        # ----------------------------------------------------

        if submitted:

            if st.session_state["chart_a"] is None:

                st.warning(
                    "Hitung chart Profil Anda terlebih dahulu "
                    "dari halaman Chart BaZi."
                )

            else:

                b_adjusted, b_meta = localize_birth(
                    b_date,
                    b_time,
                    b_offset,
                    b_longitude,
                    b_solar,
                    b_eot,
                )

                try:

                    chart_b = safe_chart(
                        b_adjusted,
                        b_offset,
                        gender_map[b_gender_label],
                        luck_count,
                        annual_count,
                    )

                    report = compatibility_report(
                        st.session_state["chart_a"],
                        chart_b,
                    )

                    # Simpan hasil agar tetap tersedia setelah rerun.
                    st.session_state["compatibility_chart_b"] = chart_b
                    st.session_state["compatibility_report"] = report
                    st.session_state["compatibility_meta_b"] = b_meta

                    st.success(
                        "Analisis kecocokan berhasil diselesaikan."
                    )

                except Exception:

                    st.error(
                        "Perhitungan kecocokan gagal. "
                        "Periksa kembali data Profil Anda dan Profil Pasangan."
                    )

        # ----------------------------------------------------
        # TAMPILKAN HASIL ANALISIS
        # ----------------------------------------------------

        report = st.session_state.get(
            "compatibility_report"
        )

        chart_b = st.session_state.get(
            "compatibility_chart_b"
        )

        b_meta = (
            st.session_state.get(
                "compatibility_meta_b"
            )
            or {}
        )

        if report is not None and chart_b is not None:

            st.divider()

            st.markdown(
                "### Hasil Analisis Pasangan"
            )

            st.metric(
                "Skor heuristik",
                f'{report["score"]}/100',
            )

            st.caption(
                "Skor ini berasal dari aturan berbobot dalam kode, "
                "bukan persentase keberhasilan hubungan."
            )

            cc1, cc2 = st.columns(2)

            with cc1:

                st.write(
                    "Cabang yang sama:",
                    "、".join(
                        report["shared_branches"]
                    ) or "Tidak ada",
                )

                st.write(
                    "Batang yang sama:",
                    "、".join(
                        report["shared_stems"]
                    ) or "Tidak ada",
                )

            with cc2:

                st.write(
                    "Kombinasi enam:",
                    "、".join(
                        report["combinations"]
                    ) or "Tidak ada",
                )

                st.write(
                    "Clash:",
                    "、".join(
                        report["clashes"]
                    ) or "Tidak ada",
                )

            if b_meta:

                st.caption(
                    f'Profil Pasangan — waktu lokal: '
                    f'{b_meta.get("civil_datetime", "—")}; '
                    f'perkiraan waktu matahari: '
                    f'{b_meta.get("adjusted_datetime", "—")}; '
                    f'koreksi: '
                    f'{b_meta.get("correction_minutes", 0):+.2f} menit.'
                )

            chart_col1, chart_col2 = st.columns(
                2,
                gap="large"
            )

            with chart_col1:

                render_element_distribution(
                    report["elements_a"],
                    "Distribusi Lima Elemen — Profil Anda",
                )

            with chart_col2:

                render_element_distribution(
                    report["elements_b"],
                    "Distribusi Lima Elemen — Profil Pasangan",
                )

            with st.expander(
                "Detail Chart Profil Pasangan"
            ):

                render_chart_result(
                    chart_b,
                    PROFILE_B_NAME,
                )

        else:

            st.info(
                "Masukkan data kelahiran Profil Pasangan, lalu tekan "
                "**Analisis Kecocokan** untuk melihat hasil perbandingan."
            )

    # ========================================================
    # HALAMAN TENTANG
    # ========================================================

    elif active_page == PAGE_ABOUT:

        st.subheader(
            "Tentang BaZi Studio"
        )

        st.markdown("""
BaZi Studio adalah aplikasi untuk menyusun dan mengeksplorasi chart BaZi berdasarkan
tanggal, jam, dan lokasi kelahiran. Aplikasi menggabungkan perhitungan BaZi,
analisis elemen, visualisasi, dan aturan perbandingan.

**Penting:** BaZi merupakan sistem metafisika tradisional, bukan metode prediksi ilmiah
yang tervalidasi. Rumus di bawah menjelaskan implementasi program ini, bukan seluruh
teori BaZi.
""")

        st.divider()

        st.markdown(
            "### Metode waktu"
        )

        st.latex(
            r"\lambda_{\mathrm{standar}}=15^\circ \times UTC\ offset"
        )

        st.latex(
            r"C_{\mathrm{bujur}}=4(\lambda-\lambda_{\mathrm{standar}})\ \mathrm{menit}"
        )

        st.markdown(
            "Program dapat menambahkan estimasi persamaan waktu "
            "(Equation of Time). Waktu hasil koreksi diteruskan ke "
            "`bazi_engine.build_chart`. "
        )

        st.divider()

        st.markdown(
            "### Pembobotan lima elemen"
        )

        st.latex(
            r"W(e)=N_{\mathrm{batang}}(e)+0.5N_{\mathrm{hidden}}(e)"
        )

        st.latex(
            r"p(e)=\frac{W(e)}{\sum_e W(e)}\times100\%"
        )

        st.markdown(
            "Bobot 1 dan 0,5 adalah heuristik aplikasi, bukan bobot "
            "standar universal atau ukuran lengkap kekuatan Day Master."
        )

        st.divider()

        st.markdown(
            "### Skor kecocokan pasangan"
        )

        st.markdown(
            "Skor dimulai dari 50, kemudian disesuaikan berdasarkan "
            "cabang dan batang yang sama, kombinasi enam, serta clash. "
            "Implementasi memakai himpunan simbol unik sehingga frekuensi "
            "posisi yang berulang tidak dihitung secara terpisah. "
            "Skor bukan probabilitas atau ukuran tervalidasi."
        )

        st.divider()

        st.markdown(
            "### Informasi aplikasi"
        )

        st.markdown(f"""
- **Nama:** {APP_NAME}
- **Versi:** {APP_VERSION}
- **Pembuat:** {APP_OWNER}
""")

    # ========================================================
    # FOOTER
    # ========================================================

    st.html(f"""
    <div class="bazi-footer">
        {escape(APP_NAME)} · v{APP_VERSION}<br>
        Created and developed by
        <strong>{escape(APP_OWNER)}</strong><br>
        For educational and traditional-metaphysics exploration only.
    </div>
    """)


if __name__ == "__main__":
    main()
