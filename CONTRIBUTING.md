# Contributing

This repository holds data, not code. A contribution is a YAML file you add or a
few lines you change. If you have used Git before but never worked on this repo,
this page is everything you need.

Read [EDITORIAL-POLICY.md](EDITORIAL-POLICY.md) first. It is short, and it is the
reason most rejected pull requests get rejected.

---

## The first rule: everything is sourced

Every record carries sources that someone else can open, and a `verified_on` date
saying when a human last checked them. A record that looks right but cannot be
checked is not accepted.

---

## The second rule: know which facts depend on the market

This is the one contributors get wrong most often, so it comes before anything
else on this page.

Some facts about a product are the same wherever in the world you pick it up.
Others change depending on which country you bought it in. The two kinds are
stored in different places, and they must never be mixed.

| Class | Fields | Where it is stored |
|---|---|---|
| **Market-invariant** | `brand`, `brand_owner`, `parent` (and so the ultimate parent) | `brands/`, `entities/`, and the top level of a product override |
| **Market-variant** | `made_in`, `operator` | **only** inside a `markets:` record, next to the market it applies to |

**Market-invariant** means: the trademark is owned by the same company whoever
buys the product and wherever they buy it, and that company is owned by the same
parent. `brand_owner` and `parent` are facts about companies, not about
packages. They go in `brands/` and `entities/` and are true everywhere.

**Market-variant** means: the plant that filled the bottle, and the country it
stands in, depend on where the product was sold. `made_in` and `operator` are
facts about one production run reaching one market — and the very same barcode
can be filled by a different company in the country next door.

So:

- **`made_in` and `operator` must never be recorded without a market.** Not at
  the top level of an override, not in an entity file, not anywhere else. A
  manufacturing claim with no market attached is not a weaker claim; it is a
  claim about nothing, because it does not say what it is about. The schemas
  reject it, and so does review.
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
products/   barcode-level corrections     keyed by barcode AND market
```

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
not the name on the shopfront.

If the company has a GLEIF LEI, take that too. It is optional but it makes the
record much easier for anyone else to re-check.

**Step 2 — work out the parent, and source it separately.**

The parent link is a separate claim and needs its own source. An annual report
listing subsidiaries, an ownership section of a register entry, or the press
release announcing the acquisition. "It is obviously the same group" is not a
source.

If you cannot source the parent, leave it out. A correct entity with no parent is
useful. An entity with a guessed parent is worse than nothing, because it looks
finished.

**Step 3 — create `entities/brightwater-drinks-ltd.yaml`.**

```yaml
id: e_brightwater_drinks
name: Brightwater Drinks Ltd
country: GB
parent: e_example_holding_ltd
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

An entry in `products/` does one of two jobs, and which one it is changes what
you must supply.

**Correcting a product that already exists.** A public product database carries
the barcode, but the brand is wrong, unmatched, or attributed to the wrong
company. You supply the corrected fields. The product's name already exists
upstream, so `name` is optional here — leave it out unless the upstream name is
itself wrong.

**Supplying a product that exists nowhere else.** The barcode is in no public
product database. Your entry is not a correction of anything; it is the only
record of that product there is. **`name` is optional in the schema but required
in practice here**, because without it nothing downstream has anything to
display — the product would exist as a barcode with no name attached. A short,
factual name as printed on the package:

```yaml
- barcode: "9990007654324"
  name: Brightwater Still Water 750 ml
  brand: b_brightwater
```

Keep it under 200 characters, which the schema enforces. Do not put marketing
copy, flavour text or a market in it.

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
| Market-variant | `made_in`, `operator` | inside a `markets:` record |

Never put `made_in` or `operator` at the top level, and never record either of
them without a market. The schema will not let you do the first; review will
catch the second.

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

If the barcode is already listed, add a record to its existing `markets:` list
rather than adding a second entry with the same barcode. CI rejects duplicate
barcodes.

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

## What gets rejected

- Anything without a source, however obviously correct.
- A source that is only a news article, only Wikipedia, or another app.
- A `made_in` or `operator` claim with no market attached.
- Anything inferred from a barcode prefix.
- Stances, conduct, positions, boycott information. This dataset records
  corporate structure only, and pull requests adding such content are closed.

Rejection is not a judgement about whether you are right. Sourced resubmissions
are welcome.

---

## Not sure, or do not want to use Git?

Open an issue instead. There are two templates — "Incorrect data" and "Missing
product" — and they ask for the same things a pull request would.
