# Editorial policy

The rules the maintainer applies when accepting or rejecting a change.

## Every claim needs a source anyone can check

Each record has at least one source a stranger can check, and a `verified_on`
date for when someone last did. Unsourced submissions are rejected however
correct they look: if some records can't be checked, none of them can be trusted.

**Acceptable:** national company registers, GLEIF, trademark registers, annual
reports, official company websites, official acquisition press releases, and, for
market records, the product label.

**Not acceptable on their own:** news articles, Wikipedia, other apps, common
knowledge.

How to cite a source is in [docs/fields.md](docs/fields.md#sources).

### Take each source for what it is good at

A national register is the authority on a company's **identity**: its legal name
and number. GLEIF is usually the only source for **ownership**, but it normalises
names, often to upper case. When a register and GLEIF disagree about a name, the
register wins.

### Research goes in the pull request, not the record

Search queries, dead ends and reasoning belong in the pull request description,
where the review happens. That includes GLEIF searches that returned nothing:
give the search term, country filter and date, and try both the full legal name
and a shorter distinctive part of it. A record keeps only the facts, plus a short
`notes` line where one is needed to stop a wrong edit. A note is a claim like any
other and needs a source on the record.

## Unknown is recorded as unknown

If a fact isn't known, leave the field out. Never fill it with a guess or a
likely answer.

### Ownership has four states, not two

`parent` (the direct owner) and `ultimate_parent` (the top of the chain) can each
be: left out (not established), an entity id (named by a source), `null` (a
source confirms there is no owner), or an `_exception` (a source says the owner
exists but is withheld). The table is in [docs/fields.md](docs/fields.md#ownership-four-states-per-field).

- **Left out is not `null`.** `null` is a claim and needs a source. Anything
  walking up the chain stops at `null`, so a wrong `null` never gets revisited.
- **Left out is not withheld.** "Nobody looked" and "the owner exists and is
  undisclosed" are different facts. Use an exception only when a source says so.
- **Direct is not ultimate.** Putting the top of the chain in `parent` claims a
  direct holding no source established.

GLEIF's reporting-exception reasons map like this:

| GLEIF reason | Record as |
|---|---|
| `NON_CONSOLIDATING` | `null`: nothing consolidates this company |
| `NATURAL_PERSONS` | `null`: the owners are individuals, so the corporate chain ends |
| anything else, including `NON_PUBLIC` and `NO_KNOWN_PERSON` | `*_exception` |

`NO_KNOWN_PERSON` reads like "nobody owns this" but means the company doesn't
know. So The Coca-Cola Company, almost certainly the top of its chain, carries an
exception until a source such as a 10-K says otherwise.

### A commercial relationship is not ownership

A contract manufacturer, a licensed bottler and an importer all put a second
company name on a label, and none of that is ownership. Those companies go in
`operator` or `placed_on_market_by`, never in `parent`.

## Manufacturing claims are market-specific

The same barcode can be made by different companies in different countries and
imported by different companies again. So `made_in`, `operator` and
`placed_on_market_by`:

- must cite the label or an official company statement;
- must name the market (the country it was bought in);
- are never inferred from a barcode prefix, which only says which GS1 office
  issued the number.

Where no market record exists, apps say "varies by market, check the label".

## Scope: corporate structure only

Who owns what, and where those companies are registered. No stances, conduct,
positions or boycott information. Ownership can be checked against a register,
and opinions can't.

### Natural persons are never recorded

When a chain reaches individuals, that fact is recorded (the chain ends there,
usually as `null` from `NATURAL_PERSONS`). Who they are is never recorded: no
name, identifier, address or shareholding, in any field, note, commit or pull
request. A register shows one company to someone who looks it up; a bulk dataset
hands the same details to everyone at once.

## Licence

Contributions are published under [ODbL-1.0](LICENSE), and so is anything
generated from this dataset.

## Decisions

One maintainer makes final decisions. A rejection means the record couldn't be
checked as submitted, and sourced resubmissions are welcome.

## Changes

- **2026-09-23:** Records no longer carry comments. Research, including GLEIF
  searches that found nothing, now goes in the pull request description instead
  of a comment on the record. Facts that must stay with a record go in the new
  `notes` field. The rules themselves are unchanged.
