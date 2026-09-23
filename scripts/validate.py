"""Validate stemmo-data. Run from the repository root: python scripts/validate.py

Checks every record against its JSON Schema, that it sits at the path its id
gives it, that it carries no comments, and that every id it points at exists.
CI runs exactly this; so can you, before pushing.
"""

import json
import pathlib
import re
import sys
import unicodedata

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors = []
invalid_ids = set()


def fail(where, message):
    errors.append(f"{where}: {message}")


class Loader(yaml.SafeLoader):
    """SafeLoader that reads dates as the strings they are written as, and only
    true/false as booleans. Plain SafeLoader turns the country code NO into False."""


Loader.yaml_implicit_resolvers = {
    first: [
        (tag, regexp)
        for tag, regexp in resolvers
        if tag not in ("tag:yaml.org,2002:timestamp", "tag:yaml.org,2002:bool")
    ]
    for first, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
Loader.add_implicit_resolver(
    "tag:yaml.org,2002:bool", re.compile(r"^(?:true|false)$"), list("tf")
)

# ISO 3166-1 alpha-2, officially assigned codes. A regex cannot tell GB from UK.
ISO_3166_1 = set("""
AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ
BL BM BN BO BQ BR BS BT BV BW BY BZ CA CC CD CF CG CH CI CK CL CM CN CO CR
CU CV CW CX CY CZ DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR
GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU
ID IE IL IM IN IO IQ IR IS IT JE JM JO JP KE KG KH KI KM KN KP KR KW KY KZ
LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK ML MM MN MO MP MQ
MR MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF
PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS RU RW SA SB SC SD SE SG SH SI
SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO TR
TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ZM ZW
""".split())

URL_SOURCE = re.compile(r"^https?://")
REGISTER_SOURCE = re.compile(r"^[A-Z]{2}/[A-Za-z][A-Za-z0-9_-]*: \S")
OWNERSHIP_FIELDS = ("parent", "ultimate_parent")


def rel(path):
    return path.relative_to(ROOT).as_posix()


def schema(name):
    document = json.loads((ROOT / "schema" / f"{name}.schema.json").read_text(encoding="utf-8"))
    return Draft202012Validator(document, format_checker=FormatChecker())


def comment_lines(text):
    """Line numbers carrying a # comment, full-line or trailing, outside quotes."""
    found = []
    for number, line in enumerate(text.splitlines(), 1):
        quote = None
        for index, char in enumerate(line):
            if quote:
                if char == quote:
                    quote = None
            elif char in "\"'":
                quote = char
            elif char == "#" and (index == 0 or line[index - 1] in " \t"):
                found.append(number)
                break
    return found


def load(path, validator):
    """Read one record file. Returns the mapping, or None if it cannot be used."""
    text = path.read_text(encoding="utf-8")
    for number in comment_lines(text):
        fail(f"{rel(path)}:{number}", "comments are not kept in records; "
             "put a fact that must survive in notes: (1-2 sentences)")
    try:
        document = yaml.load(text, Loader=Loader)
    except yaml.YAMLError as exc:
        fail(rel(path), f"not valid YAML: {exc}")
        return None
    if not isinstance(document, dict):
        fail(rel(path), "expected one record (a mapping), got a list or a scalar")
        return None
    ok = True
    for error in sorted(validator.iter_errors(document), key=lambda e: list(e.path)):
        location = "/".join(str(p) for p in error.path) or "(root)"
        fail(rel(path), f"{location}: {error.message}")
        ok = False
    if not ok:
        # Still counts as existing, so records pointing at it are not also reported.
        if isinstance(document.get("id"), str):
            invalid_ids.add(document["id"])
        return None
    return document


def check_path(path, expected):
    if rel(path) != expected:
        fail(rel(path), f"should be at {expected}")


def check_country(where, field, value):
    if isinstance(value, str) and value not in ISO_3166_1:
        fail(where, f"{field}: {value} is not an ISO 3166-1 alpha-2 country code")


def lei_checksum_ok(lei):
    """ISO 17442 / ISO 7064 Mod 97-10: letters map to 10..35, whole string mod 97 == 1."""
    return int("".join(str(int(c, 36)) for c in lei)) % 97 == 1


def fold(name):
    """The brand-name fold stemmo-pipeline matches on: case, accents, punctuation."""
    decomposed = unicodedata.normalize("NFKD", name)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", stripped.casefold()).strip()


def records(directory):
    base = ROOT / directory
    for path in sorted(base.rglob("*")):
        if path.is_file() and path.suffix in (".yaml", ".yml"):
            yield path
        elif path.is_file() and path.name != ".gitkeep":
            fail(rel(path), f"only .yaml records belong in {directory}/")


# ---- entities ---------------------------------------------------------------
entity_schema = schema("entity")
entities = {}
for path in records("entities"):
    document = load(path, entity_schema)
    if document is None:
        continue
    entity_id = document["id"]
    check_path(path, f"entities/{document['country']}/{entity_id}.yaml")
    check_country(rel(path), "country", document["country"])
    lei = document.get("lei")
    if lei and not lei_checksum_ok(lei):
        fail(rel(path), f"lei {lei}: fails the ISO 17442 check digits")
    for field in OWNERSHIP_FIELDS:
        if field in document and f"{field}_exception" in document:
            fail(rel(path), f"{field} and {field}_exception are mutually exclusive")
    has_url = any(URL_SOURCE.match(s) for s in document["sources"])
    has_register = any(REGISTER_SOURCE.match(s) for s in document["sources"])
    if has_register and not has_url and "registry_id" not in document:
        fail(rel(path), "sources cite a register with no URL, so registry_id is required")
    if entity_id in entities:
        fail(rel(path), f"duplicate entity id {entity_id}, already in {rel(entities[entity_id][0])}")
    else:
        entities[entity_id] = (path, document)

# ---- brands -----------------------------------------------------------------
brand_schema = schema("brand")
brands = {}
for path in records("brands"):
    document = load(path, brand_schema)
    if document is None:
        continue
    brand_id = document["id"]
    check_path(path, f"brands/{brand_id[2]}/{brand_id}.yaml")
    if brand_id in brands:
        fail(rel(path), f"duplicate brand id {brand_id}, already in {rel(brands[brand_id][0])}")
    else:
        brands[brand_id] = (path, document)

# ---- products ---------------------------------------------------------------
product_schema = schema("product")
products = {}
for path in records("products"):
    document = load(path, product_schema)
    if document is None:
        continue
    barcode = document["barcode"]
    check_path(path, f"products/{barcode[:3]}/{barcode}.yaml")
    if barcode in products:
        fail(rel(path), f"duplicate barcode {barcode}, already in {rel(products[barcode][0])}")
    else:
        products[barcode] = (path, document)

# ---- references -------------------------------------------------------------
for entity_id, (path, document) in entities.items():
    for field in OWNERSHIP_FIELDS:
        target = document.get(field)
        if target is None:
            continue
        if target == entity_id:
            fail(rel(path), f"{entity_id} is its own {field}")
        elif target not in entities and target not in invalid_ids:
            fail(rel(path), f"{field} {target} does not exist in entities/")

# Ownership must be a tree, across parent and ultimate_parent together.
state = dict.fromkeys(entities, "unvisited")


def walk(entity_id, trail):
    state[entity_id] = "open"
    document = entities[entity_id][1]
    for field in OWNERSHIP_FIELDS:
        target = document.get(field)
        if not isinstance(target, str) or target not in entities:
            continue
        if state[target] == "open":
            cycle = " -> ".join([*trail, entity_id, target])
            fail(rel(entities[entity_id][0]), f"ownership cycle via {field}: {cycle}")
        elif state[target] == "unvisited":
            walk(target, [*trail, entity_id])
    state[entity_id] = "closed"


for entity_id in entities:
    if state[entity_id] == "unvisited":
        walk(entity_id, [])

folded = {}
for brand_id, (path, document) in sorted(brands.items()):
    if document["brand_owner"] not in entities and document["brand_owner"] not in invalid_ids:
        fail(rel(path), f"brand_owner {document['brand_owner']} does not exist in entities/")
    for name in (document["name"], *document.get("aliases", ())):
        key = fold(name)
        if not key:
            fail(rel(path), f"name {name!r} has no letters or digits to match on")
        elif folded.setdefault(key, brand_id) != brand_id:
            fail(rel(path), f"name {name!r} matches brand {folded[key]} once case and accents are ignored")

for barcode, (path, document) in products.items():
    brand = document.get("brand")
    if brand and brand not in brands and brand not in invalid_ids:
        fail(rel(path), f"brand {brand} does not exist in brands/")
    seen = set()
    for record in document.get("markets", ()):
        market = record["market"]
        if market in seen:
            fail(rel(path), f"duplicate market {market}: one record per market")
        seen.add(market)
        check_country(rel(path), "market", market)
        check_country(rel(path), f"market {market}: made_in", record.get("made_in"))
        for field in ("operator", "placed_on_market_by"):
            target = record.get(field)
            if target and target not in entities and target not in invalid_ids:
                fail(rel(path), f"market {market}: {field} {target} does not exist in entities/")

counts = f"{len(entities)} entities, {len(brands)} brands, {len(products)} products"
if errors:
    print(f"Checked {counts}.\n\n{len(errors)} problem(s):\n")
    print("\n".join(f"  - {e}" for e in errors))
    sys.exit(1)
print(f"OK: {counts}.")
