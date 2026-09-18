# Contributing

This repository holds data, not code. A contribution is a YAML file you add or a
few lines you change. If you have used Git before but never worked on this repo,
this page is everything you need.

Read [EDITORIAL-POLICY.md](EDITORIAL-POLICY.md) first. It is short, and it is the
reason most rejected pull requests get rejected.

---

## The first rule: everything is sourced

Every record carries sources someone else can go and check, and a `verified_on`
date saying when a human last checked them. A record that looks right but cannot
be checked is not accepted.

A source is written in one of two forms:

| Form | Example | Use it when |
|---|---|---|
| URL | `https://www.pfanner.com/de/impressum/` | the source has a link to the record itself |
| Register citation | `BA/bizreg: MBS 1-5356` | the register publishes no stable per-record link |

The second form is explained under [Citing a register with no stable
URL](#citing-a-register-with-no-stable-url) below. Transcribed label text is a
valid extra source everywhere, and is never enough on its own for an entity or
brand record.

---

## The second rule: know which facts depend on the market

This is the one contributors get wrong most often, so it comes before anything
else on this page.

Some facts about a product are the same wherever in the world you pick it up.
Others change depending on which country you bought it in. The two kinds are
stored in different places, and they must never be mixed.

| Class | Fields | Where it is stored |
|---|---|---|
| **Market-invariant** | `brand`, `brand_owner`, `parent`, `ultimate_parent` | `brands/`, `entities/`, and the top level of a product override |
| **Market-variant** | `made_in`, `operator`, `placed_on_market_by` | **only** inside a `markets:` record, next to the market it applies to |

**Market-invariant** means: the trademark is owned by the same company whoever
buys the product and wherever they buy it, and that company is owned by the same
parent. `brand_owner` and `parent` are facts about companies, not about
packages. They go in `brands/` and `entities/` and are true everywhere.

**Market-variant** means: the plant that filled the bottle, the country it
stands in, and the company that brought the product into the country depend on
where the product was sold. `made_in`, `operator` and `placed_on_market_by` are
facts about one production run reaching one market — and the very same barcode
can be filled by a different company in the country next door, and imported by a
different company again.

So:

- **`made_in`, `operator` and `placed_on_market_by` must never be recorded
  without a market.** Not at the top level of an override, not in an entity
  file, not anywhere else. A manufacturing or import claim with no market
  attached is not a weaker claim; it is a claim about nothing, because it does
  not say what it is about. The schemas reject it, and so does review.
- **`brand_owner` and `parent` must never be given a market.** There is no field
  for one. If you believe the trademark owner genuinely differs by territory,
  that is two brands or two entities, not one with a caveat.

If you only know what a product is and not where it was made, record the brand
and stop. Downstream consumers say "varies by market — check the label" when no
market record matches, which is a true answer. A guessed country is not.

---

## Getting set up

```bash
git clone https://github.com/<your-username>/stemmo-data.git
cd stemmo-data
git checkout -b add-lumio-brand
```

There is nothing to install and nothing to build. You edit YAML files with a text
editor.

To run the same checks CI runs, before you push:

```bash
pip install "jsonschema[format]" pyyaml
# then paste the validator from .github/workflows/validate.yml, or just push and
# let CI tell you.
```

Most contributors skip this and let CI do it. That is fine — CI comments on the
pull request within a minute or two, and its error messages name the file and the
field.

---

## How the data is arranged

```
entities/   one file per legal company    id starts with e_
brands/     one file per brand name       id starts with b_
products/   product records               keyed by barcode AND market
```

`entities/` and `brands/` are one record per file. `products/` is lists, split
across files by barcode prefix — see [Which file your entry goes in](#which-file-your-entry-goes-in).

An **entity** is a real registered company, the kind that appears in a national
company register.

A **brand** is a name printed on a package. A brand is not a company. It is owned
by an entity.

Most contributions are one new brand file, or one new entity file plus one brand
file.

> The companies in the worked examples below are invented, so that nobody pastes
> an unchecked registry number into the dataset by copying this page. The shape
> and the order of the steps are real.

---

## Worked example 1: adding a brand whose owner is already here

Say the dataset already has `entities/example-holding-ltd.yaml`, with the id
`e_example_holding_ltd`. You have found that the same company owns a second brand,
Lumio, and Lumio is not in `brands/` yet.

**Step 1 — check the owner is really there.**

```bash
grep -rl "e_example_holding_ltd" entities/
# entities/example-holding-ltd.yaml
```

It is. So no new entity file is needed. This is the easy case.

**Step 2 — find your sources before you write anything.**

You need something showing that Example Holding Ltd owns the Lumio trademark. A
trademark register entry, or the brands page of the company's own website. Not a
news article, not Wikipedia, not another app. Keep the URLs.

**Step 3 — create `brands/lumio.yaml`.**

File names are the brand name, lowercased, with hyphens for spaces.

```yaml
id: b_lumio
name: Lumio
aliases:
  - Lumio Original
  - LUMIO
brand_owner: e_example_holding_ltd
sources:
  - https://example.com/trademarks/lumio
  - https://example.com/about/our-brands
verified_on: 2026-09-14
```

`aliases` is optional, but worth filling in. It is what lets the brand be matched
against product databases that spell it differently, in a different language, or
in a different script.

**Sub-brands do not get their own file.** A range sold under a parent brand — a
"value" line, a "premium" line, a flavour family — does not change who owns the
trademark, and ownership is what `brands/` records. Put the range in the product
name in `products/` instead. One brand file per brand owner's mark, not per
marketing line.

`verified_on` is today's date — the day you actually opened those two URLs.

**Step 4 — commit and open a pull request.**

```bash
git add brands/lumio.yaml
git commit -m "Add brand Lumio (owner: Example Holding Ltd)"
git push -u origin add-lumio-brand
```

Then open the pull request on GitHub. In the description, say where you checked.
CI validates the file against `schema/brand.schema.json` and confirms that
`e_example_holding_ltd` exists. A typo in the owner id fails the build with a
message naming the missing id.

---

## Worked example 2: adding a brand whose owner is not here yet

Now say you want to add the brand Brightwater, and its owner — Brightwater
Drinks Ltd — is not in `entities/` at all. Brightwater Drinks is itself a
subsidiary: it is owned by Example Holding Ltd, which already has a file.

You need two files, and the entity has to come first, because the brand points at
it.

**Step 1 — find the company in a register.**

Look the company up in the national company register of the country it is
registered in. You want the exact legal name as the register prints it, including
the legal form — `Ltd`, `plc`, `GmbH`, `S.A.`, `Pty Ltd`. Not the trading name,
not the name on the shopfront. It is normal for this to differ from the name on
the package; when it does, say so in a one-line comment on the record.

### Citing a register with no stable URL

Many national registers are search applications that mint a session token per
visit, so the URL you are looking at when you find a company is not a URL anyone
else can open. The BiH business register at `bizreg.pravosudje.ba` works this
way, and so do a good number of others.

Do not cite the register's search form. It satisfies the schema and tells the
reader nothing, because it is the same page for every company in the country.
Cite the identifier instead:

```yaml
registry_id: "1-5356"             # MBS
sources:
  - "BA/bizreg: MBS 1-5356"
  - "label text: Na tržište BiH stavlja: Bingo doo Tuzla, ul. Bosanska poljana bb"
```

The form is `<ISO country>/<register>: <identifier>`. When a record's only
qualifying source is a register citation, `registry_id` must be filled in too —
CI fails the build otherwise, because the identifier is the only thing making the
record checkable and it should not depend on someone parsing a source string.

Where a register does publish a real per-record URL, use it. Austria's imprint
requirement, for instance, means an Austrian company's own website carries its
Firmenbuch number on a stable page, which is why
`entities/hermann-pfanner-getraenke-gmbh.yaml` cites a URL and the BiH records
do not.

If the company has a GLEIF LEI, take that too. It is optional but it makes the
record much easier for anyone else to re-check.

**Step 2 — work out the parent, and source it separately.**

The parent link is a separate claim and needs its own source. An annual report
listing subsidiaries, an ownership section of a register entry, a GLEIF record,
or the press release announcing the acquisition. "It is obviously the same group"
is not a source.

Most national registers will not help you here. In practice they publish identity
— name, number, address, status — and not ownership. If the company has an LEI,
`https://api.gleif.org/api/v1/lei-records/<LEI>` is currently the most productive
source in use in this repository, needs no API key, and publishes stable
per-record URLs you can cite directly.

**There are two ownership fields, and they are not interchangeable.**

| Field | Means |
|---|---|
| `parent` | the entity that **directly** owns this one |
| `ultimate_parent` | the entity at the **top** of the chain |

They are independent. Both may be present, either may appear alone, and both may
be absent — GLEIF will quite often give you the ultimate parent while the direct
parent is withheld. Putting an ultimate parent in `parent` is an overclaim and
review rejects it: it asserts a direct holding your source did not establish.

**Each field has four possible states.**

| You write | It means |
|---|---|
| nothing | ownership has not been established |
| `parent: e_something` | a source names the direct owner |
| `parent: null` | a source confirms there is no owner above |
| `parent_exception: NON_PUBLIC` | a source says an owner exists but is undisclosed |

A field and its exception are mutually exclusive, and CI enforces that.

`null` is not the cautious option — it is a positive, sourced claim, and anything
walking the chain upwards stops there. If you looked and found nothing, leave the
field out. If you cannot source the parent, leave it out: a correct entity with
no parent is useful, while an entity with a guessed parent is worse than nothing
because it looks finished.

**Read GLEIF's exception reasons before copying them.** `NON_PUBLIC` means a
parent exists and is not disclosed, which is the exception state. But
`NON_CONSOLIDATING` means the entity is not consolidated into anybody's accounts,
which is a sourced claim of *no* parent and is written as `null`. Same field,
same API, opposite meanings. Record which one you saw in a comment on the file.

**Step 3 — create `entities/brightwater-drinks-ltd.yaml`.**

```yaml
id: e_brightwater_drinks
name: Brightwater Drinks Ltd
country: GB
parent: e_example_holding_ltd        # the direct owner
ultimate_parent: e_example_holding_ltd   # here they happen to be the same entity
lei: EXAMPLE00000000LEI88
registry_id: "00000001"
sources:
  - https://example.com/register/company/00000001
  - https://example.com/investors/annual-report-2025.pdf
verified_on: 2026-09-15
```

`country` is where the company is **registered**, which is not always where it
operates and is rarely where its products are made.

**Step 4 — create `brands/brightwater.yaml`.**

```yaml
id: b_brightwater
name: Brightwater
aliases:
  - Brightwater Original
brand_owner: e_brightwater_drinks
sources:
  - https://example.com/brands/brightwater
verified_on: 2026-09-15
```

**Step 5 — commit both together.**

```bash
git add entities/brightwater-drinks-ltd.yaml brands/brightwater.yaml
git commit -m "Add Brightwater Drinks Ltd and brand Brightwater"
git push -u origin add-brightwater
```

Both files must be in the same pull request. A brand pointing at an entity that
does not exist yet fails CI, so splitting them across two pull requests just
breaks the first one.

---

## Adding a product override

**Your entry is the only record of that product there is.** No public product
database feeds this dataset, so there is nothing upstream for your entry to
correct and nothing upstream to fall back on — see [No public product database
supplies any of this](README.md#no-public-product-database-supplies-any-of-this).
A barcode is either recorded here or it is not recorded anywhere. ("Override" is
a historical name; nothing is being overridden.)

What follows from that is one thing you have to supply. **`name` is optional in
the schema but required in practice**, because without it nothing downstream has
anything to display — the product would exist as a barcode with no name
attached. A short, factual name as printed on the package:

```yaml
- barcode: "9990007654324"
  name: Brightwater Still Water 750 ml
  brand: b_brightwater
```

Keep it under 200 characters, which the schema enforces. Do not put marketing
copy, flavour text or a market in it.

### Which file your entry goes in

`products/` is split into several files. Take the **first three digits of the
barcode, as you have written it**, and that is the filename:

```
products/
├── README.md       what these records are, and the rules, in full
├── _example.yaml   the template entry — copy from here, never add to it
├── 385.yaml
├── 387.yaml
├── 544.yaml
└── 900.yaml
```

So `3856028503835` goes in `385.yaml`, and the EAN-8 `54491472` goes in
`544.yaml` — the first three digits, whatever the length of the barcode. No
padding, no reasoning about what the digits mean. Just the first three, as
written.

**If that file does not exist yet, create it.** Start it with the same header
comment every other prefix file carries — copy it verbatim from any of them:

```bash
# say your barcode is 4001234567890, and products/400.yaml does not exist
sed -n '/^# THE FILENAME IS A FILING CONVENTION/,/^# See products\/README.md/p' \
    products/385.yaml > products/400.yaml
# then add a blank line and your entry underneath
```

Then add your entry after a blank line. Nothing else is needed: CI reads every
`.yaml` file in the directory, so a new file is picked up with no change to the
workflow and no list to register it in.

**The filename is a filing convention and nothing else. It is not a country.**
The first three digits of a barcode record which GS1 member organisation issued
the number. They say nothing about where the product was made, who made it, or
where the company is registered, and [EDITORIAL-POLICY.md](EDITORIAL-POLICY.md)
forbids drawing any conclusion from them. Never pick a file because the product
is Bosnian, or Croatian, or Austrian — pick it from the digits, and record origin
in the `markets:` record where it belongs.

The convention exists to sort the records and to keep two contributors working on
different products out of the same file. That is the whole of it. CI does not
check that a barcode matches the file it sits in, and will not be made to: a
misfiled entry is untidy, not wrong, and enforcing the convention would make it
load-bearing. What CI does enforce is that a barcode appears **once** across the
whole directory — a duplicate spanning two files fails the build with both
filenames named.

### Which facts go where

Read this part carefully, because it is the part people get wrong.

**One barcode can have many manufacturing origins.** The digits identify the
product a registrant sells, not the plant that filled it. A drink sold under one
brand is routinely bottled by different licensee companies in different
countries, all of them using the same barcode. You cannot get from the barcode to
the country of manufacture, because that information is not in the barcode. The
README works through an invented example of this in full.

This is the second rule above, in its concrete form:

| Class | Fields | Where it goes |
|---|---|---|
| Market-invariant | `name`, `brand` (and through it, brand owner and ultimate parent) | top level of the entry |
| Market-variant | `made_in`, `operator`, `placed_on_market_by` | inside a `markets:` record |

Never put `made_in`, `operator` or `placed_on_market_by` at the top level, and
never record any of them without a market. The schema will not let you do the
first; review will catch the second.

```yaml
- barcode: "9990007654324"
  name: Brightwater Still Water 750 ml
  brand: b_brightwater
  markets:
    - market: GB
      made_in: GB
      operator: e_brightwater_drinks
      sources: ["label text: Bottled by Brightwater Drinks Ltd, Unit 2"]
      verified_on: 2026-09-15
```

`market` is where you **bought** it. `made_in` is where the **label** says it was
made. They are frequently different, and when they are, that is exactly the fact
worth recording.

### Who put it on the market

`placed_on_market_by` records the company that places the product on that
market — the importer, the distributor, or, where a shop sells a product under
its own name, the retailer. It is optional, it lives inside the `markets:`
record, and it is **not** the same field as `operator`:

| Field | The company that… |
|---|---|
| `operator` | ran the plant and made the product |
| `placed_on_market_by` | brought it to consumers in this country |

Read the label for both, and expect them to be different companies. Under BiH and
EU food labelling rules the business under whose name the food is marketed must
be named on the package, and an imported product must additionally name its
importer — so almost every packaged product you pick up carries such a party, and
it is worth recording.

On imports it is often the only company named on the label at all. The producer
may appear as no more than a town and a country, while the local importer is
given in full with its address:

```yaml
- market: BA
  made_in: AT                       # what the label says
  operator: e_pfanner               # the Austrian producer
  placed_on_market_by: e_dzajic     # the BiH importer named on the back
  sources:
    - "label text: Mjesto porijekla: Austrija"
    - "label text: Uvoznik i distributer za BiH: Džajić-Commerce d.o.o., A.G. Matoša 22, 88320 Ljubuški, BiH"
  verified_on: 2026-09-15
```

For a shop's own-brand product the two fields point in the other direction: the
retailer on the front of the pack is `placed_on_market_by`, and the contract
manufacturer named in the small print is the `operator`.

**If the label names no separate party, leave the field out.** Do not fill it
with the manufacturer because it is the only company printed. "Who made it" and
"who put it on the market" are different questions, and a package that answers
only the first should be recorded as answering only the first.

If the barcode is already listed, add a record to its existing `markets:` list
rather than adding a second entry with the same barcode. CI rejects duplicate
barcodes across the whole of `products/`, not just within one file, so check the
directory rather than the one file you are working in:

```bash
grep -n '3856028503835' products/*.yaml
# products/385.yaml:16:- barcode: "3856028503835"
```

### Sources for a manufacturing claim

A `made_in` or `operator` claim must cite a label photo or an official company
statement. In practice, transcribed label text is what you will use:

```yaml
sources: ["label text: Bottled under licence by Brightwater Drinks Ltd, Unit 2"]
```

Type it out exactly as printed, in its original language, rather than translating
or summarising it. It is the whole of the evidence, and a translation cannot be
re-checked against the package.

---

## What goes in one pull request

**One product per pull request, with everything it needs.** If a product needs an
entity or a brand that does not exist yet, those records go in the same pull
request. The three records are useless apart: CI cannot validate a brand whose
owner entity is missing, and a reviewer checking your sourcing needs the whole
chain — product, brand, entity, and the parent above it — in one view. Splitting
them across pull requests produces a red build on the first and an unreviewable
diff on the second.

**Several products from one producer may share a pull request**, where the entity
and brand work is shared between them. Forty products from one retailer is one
pull request, not forty: they resolve to the same entity, cite the same register
extract, and are reviewed once. The test is whether the sourcing is shared, not
how many barcodes there are.

**A correction to an existing record is its own pull request**, and may be a
single line. Fixing a misspelled legal name or a stale `verified_on` does not
need to wait for anything else, and it is reviewed on its own terms.

**Never mix a product addition with a schema or editorial-policy change.** Adding
a field to `schema/`, changing the validator, or changing a rule in
[EDITORIAL-POLICY.md](EDITORIAL-POLICY.md) is a separate pull request making its
own argument. A schema change buried in a data submission gets waved through with
the data; a data submission attached to a schema change gets held up by an
argument it has nothing to do with. Land the rule first, then the records that
use it.

### What the description has to say

The description is the review checklist as much as it is a description. State
what you checked and where, so the reviewer re-checks your sources rather than
guessing at them:

- **The company register** — which register, and the identifier it gave you.
  `BA/bizreg: MBS 1-5356`, `HR/sudreg: MBS 081180379`, `AT/Firmenbuch: FN
  314034s`. The identifier, not "I looked it up".
- **The trademark register** — which register, and the mark number. Say if the
  mark is figurative rather than a word mark, and say if its registration has
  expired. Both weaken the citation and both are fine to record; hiding them is
  not.
- **Every GLEIF query you ran, including the ones that returned nothing.** An
  empty result is a claim — "this company has no LEI" — and it is reproducible
  only if the search term, the country filter and the date are written down. See
  [A GLEIF negative is cited by recording the
  query](EDITORIAL-POLICY.md#a-gleif-negative-is-cited-by-recording-the-query);
  the rule asks for two queries where the name allows it, and for near-misses to
  be stated and rejected explicitly rather than left out.
- **What you could not establish.** A parent you looked for and did not find is
  worth a line. It tells the reviewer the field is absent because the answer is
  not available, not because nobody looked.

`.github/pull_request_template.md` prompts for all of this when you open the pull
request. It is the same list.

---

## What gets rejected

- Anything without a source, however obviously correct.
- A source that is only a news article, only Wikipedia, or another app.
- A `made_in` or `operator` claim with no market attached.
- Anything inferred from a barcode prefix.
- Stances, conduct, positions, boycott information. This dataset records
  corporate structure only, and pull requests adding such content are closed.
- A pull request mixing a data addition with a schema or editorial-policy
  change. Not rejected on the merits — split into two and both get reviewed.

Rejection is not a judgement about whether you are right. Sourced resubmissions
are welcome.

---

## Licence

This dataset is **[ODbL-1.0](LICENSE)**, and so is anything generated from it.
By opening a pull request, or an issue containing data, you agree that your
contribution is published under that licence.

For anyone using the data: use it for anything, including commercially; credit
the source; and if you publish a database derived from it, publish that database
under ODbL too. Using the data inside a closed application is permitted —
share-alike applies to a derived database, not to an application that queries
one. The README says this in full under [Licence](README.md#licence).

---

## Not sure, or do not want to use Git?

Open an issue instead. There are two templates — "Incorrect data" and "Missing
product" — and they ask for the same things a pull request would.
