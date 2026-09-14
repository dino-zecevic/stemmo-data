# stemmo-data

Hand-curated data linking consumer product brands to the legal entities that own
them, and those entities to each other.

This repository contains data only. No code, no build scripts. The one executable
thing here is the CI workflow that validates the data.

## What this is for

Two kinds of public database already exist and do not talk to each other.

Product databases — Open Food Facts and others — know that a barcode is a bottle
of a particular drink, made by a brand with a particular name. They record the
brand as free text.

Company registers — national registers, GLEIF — know that a company exists, where
it is registered, what its legal name is, and sometimes who owns it. They record
companies, and know nothing about brands.

The link between the two is missing. A brand name on a package is not a company
name, is not unique, changes between languages and markets, and is spelled
inconsistently in every product database that records it. Getting from "the word
printed on this bottle" to "the registered company that owns that trademark" is
the gap, and it is a gap that has to be crossed by hand, one brand at a time,
with a source for each crossing.

That is what this repository is: that mapping, curated by hand, with sources.

## Structure

```
entities/     one file per legal company        ids prefixed e_
brands/       one file per brand name           ids prefixed b_
products/     barcode-level corrections         keyed by barcode and market
schema/       JSON Schema for each of the three
```

### Entity

A real registered legal company.

| Field | Required | Notes |
|---|---|---|
| `id` | yes | slug, prefix `e_` |
| `name` | yes | the exact registered legal name |
| `country` | yes | ISO 3166-1 alpha-2, country of registration |
| `parent` | no | id of the entity that owns this one, or null |
| `lei` | no | GLEIF Legal Entity Identifier |
| `registry_id` | no | national company register number |
| `sources` | yes | at least one URL |
| `verified_on` | yes | ISO date |

### Brand

A marketing name printed on products. It is not a company.

| Field | Required | Notes |
|---|---|---|
| `id` | yes | slug, prefix `b_` |
| `name` | yes | |
| `aliases` | no | alternative spellings |
| `brand_owner` | yes | id of the entity owning the trademark |
| `sources` | yes | at least one URL |
| `verified_on` | yes | ISO date |

### Product override

Corrects or supplies product-level facts, and is keyed by barcode **and market**.

| Field | Required | Notes |
|---|---|---|
| `barcode` | yes | EAN/UPC as a string |
| `name` | no | product name, max 200 characters — market-invariant. Optional when correcting a product a public database already carries; needed when this override is the only record of the product |
| `brand` | no | brand id — market-invariant |
| `markets` | no | list of per-market records |

Each entry in `markets`:

| Field | Required | Notes |
|---|---|---|
| `market` | yes | ISO 3166-1 alpha-2 — where the product is sold |
| `made_in` | no | ISO 3166-1 alpha-2 |
| `operator` | no | entity id of the company running the plant |
| `sources` | yes | must cite a label photo or official statement |
| `verified_on` | yes | ISO date |

## What an override is for

An entry in `products/` does one of two distinct jobs, and it is worth being
clear about which, because they have different requirements.

**1. Correcting a record that already exists.** A public product database
carries the barcode, but its brand is wrong, spelled in a way nothing matches,
or attributed to the wrong company. The override supplies the corrected fields.
The product's name already exists upstream, so `name` can be left out.

**2. Supplying a record that exists nowhere else.** The barcode is in no public
product database at all — a regional line, a shop's own label, a product that
simply never got entered. Here the override is not a correction of anything. It
is the only record of that product in existence, and if it does not carry a
`name`, there is nothing for anything downstream to display. In this case `name`
is required in practice, even though the schema marks it optional.

Downstream builds take **the union** of public product data and the barcodes
recorded only here: every barcode the public data covers, plus every barcode
that appears solely in this directory. An override-only entry is therefore not a
second-class record. For the products in case 2, it is the record.

## Why product overrides are keyed by market

One barcode can have many manufacturing origins. This is the single design
constraint that shapes the products/ directory, so it is worth setting out in
full.

### A worked example

> **This is an illustration, not a record.** Every company, brand, barcode and
> prefix below is invented, and none of it appears in `products/overrides.yaml`,
> because nothing is written into this dataset until someone has checked it
> against a source and dated it. It is here to explain the shape of the problem,
> not to be relied on or copied in.

Fizzco Ltd is a fictional drinks company. It sells a sparkling drink under the
invented brand Fizzwell, and the can carries the barcode `9990001234560`.

Fizzco registered with a GS1 member organisation and was allocated the fictional
prefix `999`. That allocation is what the leading digits of the barcode record:
**which GS1 office issued the number, and to which registrant.** That is the
whole of what a prefix encodes.

It does not encode where the can was filled.

Fizzwell is not bottled by Fizzco. Like most drinks brands, it is bottled under
licence by separate companies holding territorial agreements:

| Bought in | Filled by | Filled in |
|---|---|---|
| New Zealand | Harbourline Bottling Ltd | New Zealand |
| Ireland | Greenfield Drinks Ltd | Ireland |

Both cans carry `9990001234560`. The digits identify the product Fizzco sells,
not the plant that filled it, and the two plants belong to two unrelated
companies in two countries.

So:

- **Barcode to brand owner is a function.** `9990001234560` is a Fizzwell
  product, owned by Fizzco, wherever you find it. That fact is stable, and it is
  derivable from the barcode alone.
- **Barcode to manufacturing country is not a function.** One input, two correct
  answers here and potentially a dozen in reality, with nothing in the number to
  tell them apart. The information is genuinely not there.

An app that reads the prefix and displays a flag has not computed anything. It
has guessed — and in one of those two countries it has guessed wrong, on a shelf
where the correct answer is printed on the back of the can.

### What follows from that

Facts fall into two classes:

| Class | Facts | Behaviour |
|---|---|---|
| Market-invariant | name, brand owner, ultimate parent | the same everywhere; derivable from the barcode; reliable |
| Market-variant | made in, operating company | depends on where the product was bought; requires a per-market record |

Market-variant facts are therefore stored only inside a `markets:` record, next
to the market they were observed in, and are never recorded without one. The
structure, using the illustration above, would be:

```yaml
# illustration — invented, and not a record in this dataset
- barcode: "9990001234560"
  name: Fizzwell Sparkling 330 ml     # market-invariant
  brand: b_fizzwell                   # market-invariant: true wherever it is bought
  markets:
    - market: NZ                      # where it was bought
      made_in: NZ                     # what the label says
      operator: e_harbourline_bottling # who filled it, for this market
      sources: ["label text: Bottled by Harbourline Bottling Ltd"]
      verified_on: 2026-09-15

    - market: IE                      # the same barcode, a different country
      made_in: IE
      operator: e_greenfield_drinks   # a different company entirely
      sources: ["label text: Bottled by Greenfield Drinks Ltd"]
      verified_on: 2026-09-15
    # The second record does not overwrite the first. Both are true, each of
    # its own market, and neither could be derived from the barcode.
```

Note what has to be present before such a record can exist: a market, and a
source that is a label photo or an official company statement. Each market record
is one observation, dated, of one package bought in one country.

### How consumers are expected to present it

The device country is a hint for selecting a market, not an answer in itself. The
result must be labelled honestly — "In New Zealand, this is bottled by…" — never
a bare "Made in NZ", which asserts something the data does not say.

Where no market record matches, the correct output is "varies by market — check
the label". That is a true statement, and a more useful one than a flag that
might be wrong.

**A barcode prefix records only which GS1 office issued the number.** It is not
evidence of where a product was made, and is never used as such here — not in the
data, and not by anything reading it.

## Editorial rules

Every claim carries a source anyone can independently check, and a date on which
a human last checked it. Unsourced submissions are rejected regardless of whether
they look correct. Unknown is recorded as unknown, never guessed.

This dataset records corporate structure only: who owns what, registered where.
It records no stances, no conduct, no positions and no boycott information.

The full rules are in [EDITORIAL-POLICY.md](EDITORIAL-POLICY.md).

## Validation

`.github/workflows/validate.yml` runs on every pull request. It:

- validates every YAML file against its JSON Schema;
- checks that every id referenced actually exists — `parent`, `brand_owner`,
  `operator`, `brand`;
- rejects duplicate ids, duplicate barcodes, duplicate market records and
  ownership cycles;
- checks country codes against the ISO 3166-1 alpha-2 list.

A broken reference fails the build.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md), which walks through adding a brand whose
owner is already present, and adding one where a new entity is needed too. If you
would rather not use Git, the two issue templates ask for the same information.

### Branch protection

`main` is protected:

- pull requests are required;
- direct pushes to `main` are not permitted, including by the maintainer;
- the `validate` check must pass before a pull request can be merged.

One maintainer makes final decisions.

## Example files

Each directory is seeded with exactly one example, marked `example: true` and
carrying a header comment saying so. They exist as templates. The companies,
brands and barcodes in them are invented.

## Licence

**The curated data in this repository is CC0. Files generated downstream by
combining it with Open Food Facts are ODbL, because ODbL is share-alike.**

The curated data in this repository is released under
[CC0 1.0 Universal](LICENSE) — public domain dedication. Anyone may use it for
anything, including in a closed commercial product, with no attribution required.

Files generated **downstream** by combining this data with
[Open Food Facts](https://world.openfoodfacts.org/) are a different matter. Open
Food Facts is licensed under the
[ODbL](https://opendatacommons.org/licenses/odbl/), which is share-alike, so a
derived database that mixes the two is ODbL and must be distributed as such.
CC0 here does not and cannot relax that.

In short: this repository is CC0. Generated shard files that include Open Food
Facts data are ODbL.

[LICENSE](LICENSE) is the full, unmodified CC0 1.0 Universal legal code as
published by Creative Commons.

## Consumers

A mobile app consumes this data. The dataset is maintained to stand on its own,
and is useful without it.

## Open questions

Recorded here so they are not silently forgotten. None are decided.

- Do `markets` records need a `valid_from` date? Bottling arrangements change
  hands, and without one a record can go stale without any signal that it has.
- Should there be a lightweight way to mark a barcode as known to be
  multi-market, even before any individual market record exists? "Varies by
  market" and "nothing is recorded here yet" are currently indistinguishable
  downstream, though only the first is a fact about the product.
- How should label-photo sources be stored? Hosting images has a cost;
  transcribed label text may be sufficient evidence and costs nothing.
- Should `name` be allowed to vary by market? It is market-invariant today, so a
  product sold under a different name in different countries has nowhere to
  record the second name. No field has been added for this.
