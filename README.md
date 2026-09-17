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

`entities/` and `brands/` hold one record per file. `products/` holds lists,
split across several files — see [How products/ is laid out](#how-products-is-laid-out).

### Entity

A real registered legal company.

| Field | Required | Notes |
|---|---|---|
| `id` | yes | slug, prefix `e_` |
| `name` | yes | the exact registered legal name |
| `country` | yes | ISO 3166-1 alpha-2, country of registration |
| `parent` | no | id of the entity that **directly** owns this one. Omit when unverified; `null` only when sourced — see below |
| `parent_exception` | no | set instead of `parent` when a source says the direct owner exists but is undisclosed |
| `ultimate_parent` | no | id of the entity at the **top** of the chain, same states as `parent` |
| `ultimate_parent_exception` | no | set instead of `ultimate_parent` when the top of the chain is undisclosed |
| `lei` | no | GLEIF Legal Entity Identifier, check digits validated |
| `registry_id` | no | national company register number |
| `sources` | yes | at least one URL or register citation — see below |
| `verified_on` | yes | ISO date |

**Ownership has four states, and `parent` is the direct owner only.**

| State | Written as | Meaning |
|---|---|---|
| Not established | field absent | nobody has looked, or looking found nothing |
| Named | entity id | a source names the owner |
| None | `null` | a source confirms there is no owner above |
| Withheld | `*_exception` | a source says the owner exists but is not disclosed |

`parent` is the entity that directly owns this one; `ultimate_parent` is the top
of the chain. They are independent — both may be present, either alone, or
neither — and putting an ultimate parent in `parent` is an overclaim, because it
asserts a direct holding no source established. The four states and the reason
the distinctions matter are in
[EDITORIAL-POLICY.md](EDITORIAL-POLICY.md).

### Brand

A marketing name printed on products. It is not a company.

| Field | Required | Notes |
|---|---|---|
| `id` | yes | slug, prefix `b_` |
| `name` | yes | |
| `aliases` | no | alternative spellings |
| `brand_owner` | yes | id of the entity owning the trademark |
| `sources` | yes | at least one URL or register citation — see below |
| `verified_on` | yes | ISO date |

### How sources are cited

A qualifying source on an entity or brand takes one of two forms:

| Form | Example |
|---|---|
| URL | `https://www.pfanner.com/de/impressum/` |
| Register citation | `BA/bizreg: MBS 1-5356`, `AT/Firmenbuch: FN 314034s` |

The second form exists because many national registers are search applications
that mint a session token per visit and publish no stable per-record link. Citing
such a register's search form produces a URL that passes validation and tells the
reader nothing — it is the same page for every company in the country. The
identifier is what makes the record checkable, so the identifier is what is
cited, and `registry_id` must carry it as a field rather than only inside a
source string. CI enforces that.

Transcribed label text is a valid supporting source and is never sufficient on
its own for an entity or brand record.

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
| `placed_on_market_by` | no | entity id of the importer, distributor, or own-brand retailer that places the product on this market |
| `sources` | yes | must cite a label photo or official statement |
| `verified_on` | yes | ISO date |

**`placed_on_market_by` is not `operator`.** `operator` is the company that ran
the plant; `placed_on_market_by` is the company that put the product in front of
consumers in that country — the importer, the distributor, or, for an own-brand
product, the retailer whose name is on the package. They are frequently different
companies, and on an imported product they are usually registered in different
countries.

This field earns its place because the information is nearly always printed.
Under BiH and EU food labelling rules, the business under whose name the food is
marketed — and, for imports, the importer — must be named on the package, so
almost every packaged product carries such a party. On an import it is very often
the *only* company named on the label at all: the foreign producer may appear as
a town and a country and nothing more, while the local importer is given in full,
with its address. Without this field that company has nowhere to go, and the one
piece of local corporate information the package actually supplies is thrown away.

It is market-variant, like `made_in` and `operator`, and for the same reason: the
same product is imported into different countries by different companies. It
belongs inside a `markets:` record and never at the top level of an entry.

## How products/ is laid out

Product records are split across several files, one per **three-digit prefix of
the barcode as written in the record**:

```
products/
├── README.md       what these records are, and the rules above in full
├── _example.yaml   the seeded template entry, example: true
├── 385.yaml
├── 387.yaml
├── 544.yaml
└── 900.yaml
```

`3856028503835` goes in `385.yaml`. The EAN-8 `54491472` goes in `544.yaml` on
the same rule — the first three digits, whatever the length of the barcode. A
file that does not exist yet is created, with the header comment the others
carry.

**The filename is a filing convention. It is not a country.** The first three
digits of a barcode record which GS1 member organisation issued the number. They
say nothing about where a product was made, who made it, or where the company is
registered, and [EDITORIAL-POLICY.md](EDITORIAL-POLICY.md) forbids drawing any
such conclusion from them. Origin is read from the `markets:` records, which cite
the label. It is never read off a filename.

That warning is repeated at the top of every one of these files, because a
directory listing that reads `385 387 544` looks like a country index — and
mistaking a prefix for a country is the exact error this dataset exists to
correct.

The split is there because it sorts the records and keeps two contributors
working on different products out of the same file. Nothing more rests on it:
the validator reads every `.yaml` file in the directory and concatenates the
lists, so downstream a barcode's file of origin is invisible, and the validator
deliberately does **not** check that a barcode matches the file it sits in.
Enforcing that would make the convention load-bearing.

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
> prefix below is invented, and none of it appears in any file in `products/`,
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
| Market-variant | made in, operating company, the company placing it on the market | depends on where the product was bought; requires a per-market record |

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
- checks that every id referenced actually exists — `parent`, `ultimate_parent`,
  `brand_owner`, `operator`, `placed_on_market_by`, `brand`;
- rejects an ownership field and its `_exception` set together, in either
  direction;
- verifies LEI check digits (ISO 17442 Mod 97-10);
- rejects duplicate ids, duplicate barcodes, duplicate market records, and
  ownership cycles across `parent` and `ultimate_parent` together — a barcode is
  unique across the whole of `products/`, and a duplicate spanning two files is
  reported with both filenames;
- requires `registry_id` on any entity whose only qualifying source is a register
  citation rather than a URL;
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
brands and barcodes in them are invented. In `products/` the example lives in its
own file, `_example.yaml`, outside the prefix filing convention.

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

## What the first four products cost

Recorded because it is the most useful thing learned so far, and because it bears
directly on what this dataset can currently claim to be.

Four real products produced eight entities and three brands. Every one of them is
sourced.

Ownership was attempted for three corporate groups. Four entities carry an LEI,
and each has two ownership fields — direct and ultimate — so there are eight
results to account for:

| Outcome | Count | Where |
|---|---|---|
| Edge established | 1 | `e_cchbc_bh` → `e_cchbc_ag`, ultimate parent, in force since 2017 |
| Sourced `null` | 2 | `e_cchbc_ag`, both fields, via `NON_CONSOLIDATING` |
| Exception | 5 | `e_cchbc_bh` direct and both of `e_pfanner`'s, all `NON_PUBLIC`; both of `e_tccc`'s, `NO_KNOWN_PERSON` |

One edge. One entity whose position at the top of its chain is sourced, on both
fields. Five fields where a source was found, read, and did not answer the
question.

### Identity and ownership come from different places

**National registers publish identity and mostly not ownership.** Four basic
bizreg extracts gave legal names, MBS, JIB, addresses and status, and carried no
ownership field at all. An Austrian imprint gave the Firmenbuch number, the court
and the VAT number, and named the company without naming its owners. An SEC
subsidiary exhibit listed what the filer owns as of 2008 and said nothing about
who owns the filer.

**GLEIF publishes ownership, but only for entities that have an LEI** — and most
of those did not answer. Five of the eight results were exceptions rather than
relationships.

An exception is not a failed lookup. `NON_PUBLIC` is a company stating that an
owner exists and is not published; `NO_KNOWN_PERSON` is a company reporting the
limit of its own knowledge. Both are facts worth recording, and neither is
surfaced by any competing product. But neither is an edge, and a graph cannot be
built from them.

Four of the seven curated entities carry an LEI. The other three have none, and
nothing else consulted for them carried ownership at all.

### One national register does publish ownership

The claim above — that national registers publish identity and mostly not
ownership — has an exception, found while recording a Croatian producer.

`sudreg.pravosudje.hr`, the Croatian business register, publishes an
`Osnivači/članovi društva` section naming the members of a company, each with an
identifier, and for corporate members their foreign registration number and the
register it belongs to. It also publishes capital history, merger history and
branch records. In the case that turned this up, that was enough to establish
that a company had changed both its seat and its name — a fact no single extract
stated, reconstructed from the identifier carried through the capital history.

This is the first register in this dataset that answers the ownership question at
all. Set against what the others do:

| Source | Answers ownership? |
|---|---|
| BA bizreg basic extract | no founder field at all |
| AT Impressum | names the company, not its owners |
| GLEIF | only for LEI holders, and about accounting consolidation rather than membership |
| HR sudreg | yes — members, with identifiers, from the same lookup as identity |

The consequence is about cost, and it is uneven. For a Croatian company an
ownership edge is cheap: it arrives from the same free lookup as the legal name,
with no LEI required and nothing to pay for. For a Bosnian company it remains
unavailable from the basic extract at any price this project has found. So the
cost of an ownership edge is jurisdiction-dependent, and a coverage estimate has
to be made per country. An aggregate figure over a mixed set of countries would
average together two situations that have nothing to do with each other.

**This is one register, and nothing more general follows from it.** It is not
evidence that EU registers publish ownership, or that any other register does.
Each one has to be checked on its own terms.

### The two chains do not terminate the same way

The bottling chain and the brand chain both run out of this dataset's four
products, and only one of them can be followed to its end.

| Chain | Ends at | How |
|---|---|---|
| Bottling | `e_cchbc_ag` | sourced `null` — `NON_CONSOLIDATING` on both fields |
| Brand | `e_tccc` | exception — `NO_KNOWN_PERSON` on both fields |

So this dataset can say where the Coca-Cola **bottling** chain ends, and cannot
say the same for the **brand**. The asymmetry is not about how hard anyone
looked: both records were checked against GLEIF on the same terms, minutes apart.
It is a difference in what the two companies reported about themselves. One made
a definite statement about its accounting structure; the other reported what it
knows.

### Ownership must be walked upward, not downward

GLEIF's `direct-children` endpoint is much thinner than the parent direction.
`Coca-Cola HBC AG` publishes exactly three direct children — one Serbian, one
Armenian, and a British Virgin Islands company — for a group that operates in far
more countries than that. The Bosnian entity that names it as its ultimate parent
**is not among them.**

The relationship is published from one end only. So ownership has to be resolved
per entity, upward from the company on the package, and there is no one-call
shortcut that enumerates a group and fills in its members.

### What this does not establish

Three groups is not a sample, and no coverage estimate should be drawn from it.
All three are beverage companies; one is listed and regulated, which is the most
favourable case for LEI coverage available. The open question is what fraction of
the entities this dataset actually cares about — retailers, contract dairies,
regional importers — have an LEI at all, and how many of those disclose. Neither
number is known.

## Open questions

Recorded here so they are not silently forgotten. None are decided.

- Do `markets` records need a `valid_from` date? Bottling arrangements change
  hands, and without one a record can go stale without any signal that it has.
- Should there be a lightweight way to mark a barcode as known to be
  multi-market, even before any individual market record exists? "Varies by
  market" and "nothing is recorded here yet" are currently indistinguishable
  downstream, though only the first is a fact about the product.
- Should the GS1 licensee of a barcode be recorded, and if so where? "Verified by
  GS1" publishes, free and authoritatively, the company that licensed a GTIN
  prefix, with its address and GLN. That company is none of the things this
  schema has a field for: it is not the brand owner, not the plant operator, and
  not the party placing the product on a market. For `5449000028921` it is a
  Belgian company, while the brand owner is American and the bottler for the BiH
  market is Bosnian — three different companies, only two of which can currently
  be written down. Recording it would also give an honest, sourced answer for
  barcodes that have no market record yet, which is the case the dataset is
  currently silent on.

  The two records added alongside that one are the argument against. For
  `9006900221690` the licensee is Hermann Pfanner Getränke GmbH — which is also
  the brand owner and also the producer, one company doing all three jobs. For
  `5449000028921` the licensee does none of them. So the licensee sometimes is
  the answer a consumer wants and sometimes is a company with no other role at
  all, and nothing in the GS1 record distinguishes the two cases. A field whose
  meaning changes depending on facts the field does not carry is close to the
  error this dataset exists to correct, and a `gtin_licensee` that consumers
  treated as "the company behind this product" would reproduce it.

  There is also a data-quality problem with the source itself. For
  `5449000028921` GS1 named the licensee `COCA-COLA SERVICES SA/NV` in a record
  it stated was last updated in March 2026. The Belgian Crossroads Bank for
  Enterprises has no active company of that name; the company at the address GS1
  gives (enterprise 0460.564.809, Chaussée de Mons 1424, Anderlecht) is
  `COCA-COLA EUROPACIFIC PARTNERS SERVICES`, a BV whose French name changed in
  August 2021. So either the GS1 record is stale on the licensee's own identity,
  or the two are different companies. Licensee data that disagrees with a
  national register about a company's name cannot be imported without a
  register lookup per record — at which point the register, not GS1, is the
  source, and the field has bought nothing.
- How should label-photo sources be stored? Hosting images has a cost;
  transcribed label text may be sufficient evidence and costs nothing.
- Should `name` be allowed to vary by market? It is market-invariant today, so a
  product sold under a different name in different countries has nowhere to
  record the second name. No field has been added for this.
- How should a company with **several members** be recorded? **This one is not
  hypothetical: it is live in the data, at
  [`entities/violeta-doo-hr.yaml`](entities/violeta-doo-hr.yaml).** The schema
  models ownership as `parent` and `ultimate_parent`: in each case a single
  entity. The Croatian register shows `VIOLETA d.o.o.` in Croatia with two
  members — one company (the Bosnian `e_violeta_ba`) and one natural person —
  and the extract examined carries no percentages.

  Neither `parent`, `ultimate_parent` nor their exceptions can express that.
  Writing a single entity into either field would assert sole or controlling
  ownership that the source does not establish, which is the overclaim the
  four-state model exists to prevent. Omitting the fields discards a real,
  sourced fact: that a named company holds part of this one.

  That record accordingly carries **no ownership field at all**, and states the
  membership in its comments instead. It is the first record in this dataset
  where the schema cannot carry a fact that a source does establish, and it is
  the record to revisit first if this question is ever decided.

  Any answer has to cope with all of: several members at once; members of mixed
  kinds, companies and individuals together; percentages that may or may not be
  published, so a share cannot be a required field; natural persons among the
  members, whom this dataset never names — see EDITORIAL-POLICY.md; and the
  existing `parent` semantics continuing to work unchanged for the ordinary
  single-owner case, which is most of them.

  GLEIF does not help here. It reports accounting consolidation, which is a
  different question from membership, and only for entities that have an LEI.

  No field has been added. The question is recorded, not decided.
