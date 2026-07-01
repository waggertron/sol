#!/usr/bin/env python3
"""Import open OCEAN assessment keys from downloaded official HTML pages.

This is a local acquisition helper. It expects source HTML files to already
exist in a download directory and writes normalized JSON assessment files under
`assessments/ocean/`.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

try:
    from bs4 import BeautifulSoup
except ImportError as exc:  # pragma: no cover - import-time operator guidance
    raise SystemExit(
        "This import helper requires beautifulsoup4 for old IPIP HTML parsing."
    ) from exc


IPIP_RESPONSE_SCALE = {
    "type": "likert_1_5_accuracy",
    "values": [
        {"value": 1, "label": "Very Inaccurate"},
        {"value": 2, "label": "Moderately Inaccurate"},
        {"value": 3, "label": "Neither Inaccurate nor Accurate"},
        {"value": 4, "label": "Moderately Accurate"},
        {"value": 5, "label": "Very Accurate"},
    ],
}

IPIP_LICENSE = {
    "status": "public_domain",
    "evidence": (
        "The official IPIP site states that its items and scales are in the "
        "public domain and can be copied, edited, translated, or used for any "
        "purpose without permission or a fee."
    ),
    "source_url": "https://ipip.ori.org/",
}

TIPI_LICENSE = {
    "status": "permissive_use",
    "evidence": (
        "The official TIPI page states that anyone can use it for any purpose "
        "without asking permission."
    ),
    "source_url": (
        "https://gosling.psy.utexas.edu/scales-weve-developed/"
        "ten-item-personality-measure-tipi/"
    ),
}

DOMAIN_ALIASES = {
    "openness": "openness",
    "openness to experience": "openness",
    "intellect": "openness",
    "intellect or imagination": "openness",
    "openness/intellect": "openness",
    "conscientiousness": "conscientiousness",
    "extraversion": "extraversion",
    "surgency or extraversion": "extraversion",
    "agreeableness": "agreeableness",
    "neuroticism": "neuroticism",
    "negative emotionality": "neuroticism",
    "emotional stability": "emotional_stability",
    "honesty-humility": "honesty_humility",
    "honesty humility": "honesty_humility",
}

NEO_PREFIX_DOMAINS = {
    "N": "neuroticism",
    "E": "extraversion",
    "O": "openness",
    "A": "agreeableness",
    "C": "conscientiousness",
}

BFAS_DOMAINS = {
    "volatility": "neuroticism",
    "withdrawal": "neuroticism",
    "compassion": "agreeableness",
    "politeness": "agreeableness",
    "industriousness": "conscientiousness",
    "orderliness": "conscientiousness",
    "enthusiasm": "extraversion",
    "assertiveness": "extraversion",
    "intellect": "openness",
    "openness": "openness",
}

TOPIC_REVIEW_KEYWORDS = {
    "politics": ["vote", "political", "conservative", "liberal", "tax"],
    "children": ["children"],
    "religion": ["religion", "religious", "god"],
    "substance_or_impulse": ["drink", "drugs", "binges", "overindulge"],
    "self_evaluation": ["dislike myself", "low opinion of myself"],
}


@dataclass(frozen=True)
class ImportSource:
    id: str
    name: str
    file_name: str
    url: str
    parser: str
    construct_system: str
    family: str = "OCEAN"
    notes: tuple[str, ...] = ()


SOURCES = [
    ImportSource(
        id="ipip_big_five_factor_markers",
        name="IPIP Goldberg Big-Five Factor Markers",
        file_name="newBigFive5broadKey.htm",
        url="https://ipip.ori.org/newBigFive5broadKey.htm",
        parser="rows",
        construct_system="Big Five factor markers",
    ),
    ImportSource(
        id="mini_ipip",
        name="Mini-IPIP Big Five Factors",
        file_name="MiniIPIPKey.htm",
        url="https://ipip.ori.org/MiniIPIPKey.htm",
        parser="rows",
        construct_system="Big Five factor markers short form",
    ),
    ImportSource(
        id="mini_ipip6",
        name="Mini-IPIP6 Big Six Factors",
        file_name="MiniIPIP6Key.htm",
        url="https://ipip.ori.org/MiniIPIP6Key.htm",
        parser="rows",
        construct_system="Big Six / HEXACO-adjacent short form",
        family="OCEAN_adjacent",
        notes=("Includes Honesty-Humility in addition to the five broad factors.",),
    ),
    ImportSource(
        id="ipip_big_five_aspects",
        name="IPIP Big Five Aspects Scales",
        file_name="BFASKeys.htm",
        url="https://ipip.ori.org/BFASKeys.htm",
        parser="bfas_blocks",
        construct_system="Big Five aspects",
    ),
    ImportSource(
        id="ipip_ab5c_45_facets",
        name="IPIP AB5C 45 Facets",
        file_name="newAB5CKey.htm",
        url="https://ipip.ori.org/newAB5CKey.htm",
        parser="rows",
        construct_system="Abridged Big Five Circumplex facets",
    ),
    ImportSource(
        id="ipip_neo_domains_goldberg_1999",
        name="IPIP NEO-PI-R Domain Representation",
        file_name="newNEODomainsKey.htm",
        url="https://ipip.ori.org/newNEODomainsKey.htm",
        parser="rows",
        construct_system="NEO-PI-R domain representation",
    ),
    ImportSource(
        id="ipip_neo_facets_goldberg_1999",
        name="IPIP NEO-PI-R Facet Representation",
        file_name="newNEOFacetsKey.htm",
        url="https://ipip.ori.org/newNEOFacetsKey.htm",
        parser="rows",
        construct_system="NEO-PI-R facet representation",
    ),
    ImportSource(
        id="ipip_neo_120_johnson_2014",
        name="IPIP-NEO-120 Johnson 2014",
        file_name="30FacetNEO-PI-RItems.htm",
        url="https://ipip.ori.org/30FacetNEO-PI-RItems.htm",
        parser="rows",
        construct_system="IPIP-NEO-120 facet representation",
    ),
    ImportSource(
        id="ipip_neo_120_maples_2014",
        name="IPIP-NEO-120 Maples et al. 2014",
        file_name="30FacetNEO-PI-RItems_Maples_etal.htm",
        url="https://ipip.ori.org/30FacetNEO-PI-RItems_Maples_etal.htm",
        parser="rows",
        construct_system="IPIP-NEO-120 facet representation",
    ),
    ImportSource(
        id="ipip_neo_60_maples_keller_2019",
        name="IPIP-NEO-60 Maples-Keller et al. 2019",
        file_name="IPIP-NEO-60ScoringKeys.htm",
        url="https://ipip.ori.org/IPIP-NEO-60ScoringKeys.htm",
        parser="neo60",
        construct_system="IPIP-NEO-60 domain representation",
    ),
]


def clean_text(value: str) -> str:
    value = value.replace("\xa0", " ")
    value = value.replace("\u2013", "-")
    value = value.replace("\u2014", "-")
    value = value.replace("\u201c", '"').replace("\u201d", '"')
    value = value.replace("\u2019", "'").replace("\u2018", "'")
    return " ".join(value.split()).strip()


def slugify(value: str) -> str:
    value = clean_text(value).lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "scale"


def decode_html(path: Path) -> str:
    data = path.read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("windows-1252", errors="replace")


def soup_for(path: Path) -> BeautifulSoup:
    return BeautifulSoup(decode_html(path), "html.parser")


def direct_cells(row: Any) -> list[str]:
    return [
        clean_text(cell.get_text(" ", strip=True))
        for cell in row.find_all(["td", "th"], recursive=False)
    ]


def parse_alpha(text: str) -> float | None:
    match = re.search(r"Alpha\s*=\s*\.?(\d+)", text, flags=re.I)
    if match:
        return float(f"0.{match.group(1)}")
    match = re.search(r"correlation\s*=\s*\.?(\d+)", text, flags=re.I)
    if match:
        return float(f"0.{match.group(1)}")
    match = re.search(r"\(\s*\.?(\d{2})\s*\)", text)
    if match:
        return float(f"0.{match.group(1)}")
    return None


def detect_domain(label: str, code: str | None = None) -> str | None:
    if code:
        prefix = code[:1].upper()
        if prefix in NEO_PREFIX_DOMAINS:
            return NEO_PREFIX_DOMAINS[prefix]
    lower = clean_text(label).lower()
    for alias, domain in DOMAIN_ALIASES.items():
        if alias in lower:
            return domain
    if lower in BFAS_DOMAINS:
        return BFAS_DOMAINS[lower]
    return None


def construct_from_header(text: str) -> dict[str, Any] | None:
    text = clean_text(text)
    if not text:
        return None

    prefix = re.split(r"\s+[+-]\s*keyed|\s+\d+-item scale", text, maxsplit=1)[0]
    prefix = clean_text(prefix)

    if len(prefix) > 140:
        return None
    if prefix.lower().startswith(("the items", "return ", "combined ")):
        return None

    ab5c = re.match(
        r"(?P<code>[IVX]+[+-]/[IVX]+[+-]\s+vs\s+[IVX]+[+-]/[IVX]+[+-])"
        r"\s+\((?:Alpha\s*=\s*)?(?P<alpha>\.?\d+)\)\s+(?P<label>.+)$",
        prefix,
        flags=re.I,
    )
    if ab5c:
        label = clean_text(ab5c.group("label")).title()
        return {
            "code": clean_text(ab5c.group("code")),
            "label": label,
            "alpha": parse_alpha(ab5c.group("alpha")),
            "domain": detect_domain(ab5c.group("code")),
            "start_scale": True,
        }

    neo = re.match(
        r"(?P<code>[NEOAC]\d)\s*:\s*(?P<label>[A-Za-z][A-Za-z /'-]+)"
        r"(?:\s*\(?\s*Alpha\s*=\s*\.?\d+\s*\)?)?",
        prefix,
        flags=re.I,
    )
    if neo and "scale" not in prefix.lower():
        code = neo.group("code").upper()
        label = clean_text(neo.group("label")).title()
        alpha = parse_alpha(prefix)
        return {
            "code": code,
            "label": label,
            "alpha": alpha,
            "domain": detect_domain(label, code),
            "start_scale": alpha is not None,
        }

    factor = re.match(r"Factor\s+[IVX]+\s*\((?P<label>[^)]+)\)", prefix, flags=re.I)
    if factor:
        label = clean_text(factor.group("label")).title()
        return {
            "code": None,
            "label": label,
            "alpha": None,
            "domain": detect_domain(label),
            "start_scale": False,
        }

    factor_inline_alpha = re.match(
        r"Factor\s+[IVX]+\s+(?P<label>.+?)\s*\(Alpha\s*=\s*\.?\d+\)",
        prefix,
        flags=re.I,
    )
    if factor_inline_alpha:
        label = clean_text(factor_inline_alpha.group("label")).title()
        return {
            "code": None,
            "label": label,
            "alpha": parse_alpha(prefix),
            "domain": detect_domain(label),
            "start_scale": True,
        }

    factor_inline_retest = re.match(
        r"Factor\s+[IVX]+\s+(?P<label>.+?)\s*"
        r"\(One-year test-retest correlation\s*=\s*\.?\d+\)",
        prefix,
        flags=re.I,
    )
    if factor_inline_retest:
        label = clean_text(factor_inline_retest.group("label")).title()
        return {
            "code": None,
            "label": label,
            "alpha": None,
            "test_retest_correlation": parse_alpha(prefix),
            "domain": detect_domain(label),
            "start_scale": True,
        }

    broad = prefix.title()
    broad_normalized = broad.lower()
    if broad_normalized in DOMAIN_ALIASES or any(
        broad_normalized == key for key in BFAS_DOMAINS
    ):
        return {
            "code": None,
            "label": broad,
            "alpha": parse_alpha(prefix),
            "domain": detect_domain(broad),
            "start_scale": parse_alpha(prefix) is not None,
        }

    if re.match(r"^[A-Z][A-Z /-]+(?:\s*\(Alpha\s*=\s*\.?\d+\))?$", prefix):
        label = re.sub(r"\s*\(Alpha.*?\)\s*", "", prefix).title()
        return {
            "code": None,
            "label": label,
            "alpha": parse_alpha(prefix),
            "domain": detect_domain(label),
            "start_scale": parse_alpha(prefix) is not None,
        }

    return None


def scale_header(text: str) -> dict[str, Any] | None:
    text = clean_text(text)
    if text.lower().startswith("combined "):
        return None
    match = re.search(r"(?P<count>\d+)-item scale\s*\(Alpha\s*=\s*\.?(?P<alpha>\d+)\)", text, flags=re.I)
    if not match:
        return None
    return {
        "item_count_declared": int(match.group("count")),
        "alpha": float(f"0.{match.group('alpha')}"),
        "label": f"{match.group('count')}-item scale",
    }


def keyed_value(text: str) -> str | None:
    text = clean_text(text).lower()
    if not text:
        return None
    if text.startswith("+") and "keyed" in text:
        return "positive"
    if text.startswith("-") and "keyed" in text:
        return "negative"
    return None


def review_flags(text: str) -> list[str]:
    lower = text.lower()
    flags = []
    for flag, keywords in TOPIC_REVIEW_KEYWORDS.items():
        if any(keyword in lower for keyword in keywords):
            flags.append(flag)
    return flags


def normalize_item_text(text: str) -> str:
    text = clean_text(text)
    text = re.sub(r"\s+[a-z]\s*$", "", text)
    return text


def start_scale(
    scales: list[dict[str, Any]],
    instrument_id: str,
    label: str,
    domain: str | None,
    construct_code: str | None,
    alpha: float | None,
    declared_count: int | None = None,
    source_construct: str | None = None,
    test_retest_correlation: float | None = None,
) -> dict[str, Any]:
    scale_id_base = slugify("_".join(filter(None, [domain, construct_code, label])))
    scale_id = f"{instrument_id}:{scale_id_base}"
    duplicate_count = sum(1 for scale in scales if scale["id"].startswith(scale_id))
    if duplicate_count:
        scale_id = f"{scale_id}_{duplicate_count + 1}"

    scale = {
        "id": scale_id,
        "label": label,
        "domain": domain,
        "construct_code": construct_code,
        "source_construct": source_construct or label,
        "reliability_alpha": alpha,
        "test_retest_correlation": test_retest_correlation,
        "declared_item_count": declared_count,
        "items": [],
    }
    scales.append(scale)
    return scale


def append_item(
    scale: dict[str, Any],
    instrument_id: str,
    text: str,
    keyed: str,
    facet: str | None = None,
) -> None:
    text = normalize_item_text(text)
    if not text:
        return
    if scale.get("declared_item_count") and len(scale["items"]) >= scale["declared_item_count"]:
        return
    if text.lower().startswith(
        (
            "return ",
            "click ",
            "alphas based",
            "note.",
            "a this item",
            "b this item",
            "c this item",
            "d this item",
            "john, ",
        )
    ):
        return
    if text in {item["text"] for item in scale["items"]}:
        return
    item_index = len(scale["items"]) + 1
    item = {
        "id": (
            f"{instrument_id}:{slugify(scale['id'].split(':', 1)[-1])}:"
            f"item:{item_index:03d}"
        ),
        "text": text,
        "keyed": keyed,
        "source_order": item_index,
    }
    if facet:
        item["facet_source"] = facet
    flags = review_flags(text)
    if flags:
        item["review_flags"] = flags
    scale["items"].append(item)


def parse_rows(source: ImportSource, html_path: Path) -> list[dict[str, Any]]:
    soup = soup_for(html_path)
    scales: list[dict[str, Any]] = []
    current_construct: dict[str, Any] | None = None
    current_scale: dict[str, Any] | None = None
    current_key: str | None = None

    for row in soup.find_all("tr"):
        cells = direct_cells(row)
        if not cells:
            continue
        row_text = clean_text(row.get_text(" ", strip=True))

        construct = construct_from_header(row_text)
        if construct:
            current_construct = construct
            current_key = None
            if construct.get("start_scale"):
                current_scale = start_scale(
                    scales,
                    source.id,
                    construct["label"],
                    construct.get("domain"),
                    construct.get("code"),
                    construct.get("alpha"),
                    test_retest_correlation=construct.get("test_retest_correlation"),
                    source_construct=construct["label"],
                )
            continue

        header = scale_header(row_text)
        if header and current_construct:
            label = f"{current_construct['label']} {header['label']}"
            current_scale = start_scale(
                scales,
                source.id,
                label,
                current_construct.get("domain"),
                current_construct.get("code"),
                header.get("alpha"),
                header.get("item_count_declared"),
                source_construct=current_construct["label"],
            )
            current_key = None
            continue

        key = keyed_value(cells[0])
        if key:
            current_key = key
            item_text = cells[1] if len(cells) > 1 else ""
        elif current_key and len(cells) > 1 and not cells[0]:
            item_text = cells[1]
        else:
            item_text = ""

        if current_scale and current_key and item_text:
            append_item(current_scale, source.id, item_text, current_key)

    return [scale for scale in scales if scale["items"]]


def block_texts(soup: BeautifulSoup) -> list[str]:
    blocks = []
    for tag in soup.find_all(["h1", "h2", "h3", "p", "td", "th", "li"]):
        text = clean_text(tag.get_text(" ", strip=True))
        if text and (not blocks or blocks[-1] != text):
            blocks.append(text)
    return blocks


def parse_bfas_blocks(source: ImportSource, html_path: Path) -> list[dict[str, Any]]:
    soup = soup_for(html_path)
    scales: list[dict[str, Any]] = []
    current_construct: dict[str, Any] | None = None
    current_scale: dict[str, Any] | None = None
    current_key: str | None = None

    for text in block_texts(soup):
        lower = text.lower()
        if lower.startswith(("the items", "combined ", "this item", "return ")):
            continue

        if lower in BFAS_DOMAINS:
            current_construct = {
                "label": clean_text(text).title(),
                "domain": BFAS_DOMAINS[lower],
                "code": None,
            }
            current_scale = None
            current_key = None
            continue

        header = scale_header(text)
        if header and current_construct:
            current_scale = start_scale(
                scales,
                source.id,
                f"{current_construct['label']} {header['label']}",
                current_construct.get("domain"),
                current_construct.get("code"),
                header.get("alpha"),
                header.get("item_count_declared"),
                source_construct=current_construct["label"],
            )
            current_key = None
            continue

        key = keyed_value(text)
        if key:
            current_key = key
            continue

        if current_scale and current_key:
            append_item(current_scale, source.id, text, current_key)

    return [scale for scale in scales if scale["items"]]


def parse_neo60(source: ImportSource, html_path: Path) -> list[dict[str, Any]]:
    soup = soup_for(html_path)
    scales: list[dict[str, Any]] = []
    current_scale: dict[str, Any] | None = None
    current_key: str | None = None
    current_facet: str | None = None

    for row in soup.find_all("tr"):
        cells = direct_cells(row)
        if not cells:
            continue
        text = clean_text(cells[0])
        construct = construct_from_header(text)

        if construct and construct.get("domain") and construct.get("alpha"):
            current_scale = start_scale(
                scales,
                source.id,
                construct["label"],
                construct.get("domain"),
                construct.get("code"),
                construct.get("alpha"),
                declared_count=12,
                source_construct=construct["label"],
            )
            current_key = None
            current_facet = None
            continue

        facet = re.match(r"([NEOAC]\d)\s*:\s*(.+)", text, flags=re.I)
        if facet and len(cells) == 1:
            current_facet = f"{facet.group(1).upper()}: {clean_text(facet.group(2)).title()}"
            current_key = None
            continue

        key = keyed_value(cells[0])
        if key:
            current_key = key
            item_text = cells[1] if len(cells) > 1 else ""
        elif current_key and len(cells) > 1 and not cells[0]:
            item_text = cells[1]
        else:
            item_text = ""

        if current_scale and current_key and item_text:
            append_item(current_scale, source.id, item_text, current_key, current_facet)

    return [scale for scale in scales if scale["items"]]


def build_instrument(source: ImportSource, html_path: Path) -> dict[str, Any]:
    if source.parser == "rows":
        scales = parse_rows(source, html_path)
    elif source.parser == "bfas_blocks":
        scales = parse_bfas_blocks(source, html_path)
    elif source.parser == "neo60":
        scales = parse_neo60(source, html_path)
    else:
        raise ValueError(f"Unknown parser {source.parser}")

    return {
        "schema_version": 1,
        "id": source.id,
        "name": source.name,
        "family": source.family,
        "construct_system": source.construct_system,
        "source": {
            "publisher": "International Personality Item Pool",
            "url": source.url,
            "retrieved_date": date.today().isoformat(),
        },
        "license": IPIP_LICENSE,
        "response_scale": IPIP_RESPONSE_SCALE,
        "scoring": {
            "method": "sum_keyed_items",
            "positive_keyed": "1=Very Inaccurate through 5=Very Accurate",
            "negative_keyed": "reverse score 1-5 responses before summing",
            "score_interpretation": "Higher scores indicate greater endorsement of the named construct.",
        },
        "notes": list(source.notes),
        "scales": scales,
    }


def build_tipi() -> dict[str, Any]:
    items = [
        ("Extraverted, enthusiastic.", "extraversion", "positive"),
        ("Critical, quarrelsome.", "agreeableness", "negative"),
        ("Dependable, self-disciplined.", "conscientiousness", "positive"),
        ("Anxious, easily upset.", "emotional_stability", "negative"),
        ("Open to new experiences, complex.", "openness", "positive"),
        ("Reserved, quiet.", "extraversion", "negative"),
        ("Sympathetic, warm.", "agreeableness", "positive"),
        ("Disorganized, careless.", "conscientiousness", "negative"),
        ("Calm, emotionally stable.", "emotional_stability", "positive"),
        ("Conventional, uncreative.", "openness", "negative"),
    ]
    item_objects = [
        {
            "id": f"tipi:item:{index:03d}",
            "text": text,
            "domain": domain,
            "keyed": keyed,
            "source_order": index,
        }
        for index, (text, domain, keyed) in enumerate(items, start=1)
    ]
    scale_pairs = {
        "extraversion": [1, 6],
        "agreeableness": [2, 7],
        "conscientiousness": [3, 8],
        "emotional_stability": [4, 9],
        "openness": [5, 10],
    }
    return {
        "schema_version": 1,
        "id": "tipi",
        "name": "Ten Item Personality Inventory",
        "family": "OCEAN",
        "construct_system": "Big Five very brief measure",
        "source": {
            "publisher": "Gosling Lab, University of Texas at Austin",
            "url": (
                "https://gosling.psy.utexas.edu/scales-weve-developed/"
                "ten-item-personality-measure-tipi/ten-item-personality-inventory-tipi/"
            ),
            "retrieved_date": date.today().isoformat(),
        },
        "license": TIPI_LICENSE,
        "response_scale": {
            "type": "likert_1_7_agreement",
            "values": [
                {"value": 1, "label": "Disagree strongly"},
                {"value": 2, "label": "Disagree moderately"},
                {"value": 3, "label": "Disagree a little"},
                {"value": 4, "label": "Neither agree nor disagree"},
                {"value": 5, "label": "Agree a little"},
                {"value": 6, "label": "Agree moderately"},
                {"value": 7, "label": "Agree strongly"},
            ],
        },
        "scoring": {
            "method": "average_two_items_per_domain",
            "reverse_scored_items": [2, 4, 6, 8, 10],
            "score_interpretation": "Average the domain item and reverse-scored paired item.",
        },
        "items": item_objects,
        "scales": [
            {
                "id": f"tipi:{domain}",
                "label": domain.replace("_", " ").title(),
                "domain": domain,
                "item_refs": [f"tipi:item:{item:03d}" for item in refs],
            }
            for domain, refs in scale_pairs.items()
        ],
        "notes": [
            "Very brief measure; use only when short administration length is more important than precision.",
            "The official TIPI page cautions that brief measures have diminished psychometric properties.",
        ],
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_manifest(out_dir: Path, instruments: list[dict[str, Any]]) -> None:
    manifest = {
        "schema_version": 1,
        "updated": date.today().isoformat(),
        "description": "Manifest of acquired OCEAN and OCEAN-adjacent assessment instruments stored in this repo.",
        "policy": {
            "full_item_text_allowed_only_when_permissive": True,
            "protected_or_uncertain_instruments": "metadata_only_or_reference_only",
        },
        "instrument_count": len(instruments),
        "scale_count": sum(len(instrument.get("scales", [])) for instrument in instruments),
        "item_count": sum(
            sum(len(scale.get("items", [])) for scale in instrument.get("scales", []))
            + len(instrument.get("items", []))
            for instrument in instruments
        ),
        "instruments": [
            {
                "id": instrument["id"],
                "name": instrument["name"],
                "family": instrument["family"],
                "construct_system": instrument["construct_system"],
                "path": f"instruments/{instrument['id']}.json",
                "scale_count": len(instrument.get("scales", [])),
                "item_count": sum(
                    len(scale.get("items", [])) for scale in instrument.get("scales", [])
                )
                + len(instrument.get("items", [])),
                "license_status": instrument["license"]["status"],
                "source_url": instrument["source"]["url"],
            }
            for instrument in instruments
        ],
    }
    write_json(out_dir / "manifest.json", manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", required=True, type=Path)
    parser.add_argument("--out-dir", default=Path("assessments/ocean"), type=Path)
    args = parser.parse_args()

    instruments: list[dict[str, Any]] = []
    for source in SOURCES:
        html_path = args.source_dir / source.file_name
        if not html_path.exists():
            raise SystemExit(f"Missing source file: {html_path}")
        instrument = build_instrument(source, html_path)
        write_json(args.out_dir / "instruments" / f"{source.id}.json", instrument)
        instruments.append(instrument)

    tipi = build_tipi()
    write_json(args.out_dir / "instruments" / "tipi.json", tipi)
    instruments.append(tipi)
    write_manifest(args.out_dir, instruments)

    print(
        f"Imported {len(instruments)} instruments, "
        f"{sum(len(i.get('scales', [])) for i in instruments)} scales"
    )


if __name__ == "__main__":
    main()
