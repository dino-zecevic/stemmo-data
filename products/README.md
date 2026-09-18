# products/

Product-level records, keyed by barcode.

## What these files are for

One job: **being the ONLY record of a product.**

No public product database feeds this dataset — see [No public product database
supplies any of this](../README.md#no-public-product-database-supplies-any-of-this).
So an entry here has nothing upstream to correct and nothing upstream to fall
back on. A barcode is either recorded in this directory or it is not recorded
anywhere.

That is why `name` matters. Nothing downstream has a name to display unless
these files supply one. The schema marks `name` optional and it stays optional,
in case a product source is ever added — but an entry without a name has
nothing for a consumer to display, so in practice every entry carries one.

## Which file an entry goes in

One file per three-digit prefix of the barcode **as written in the record**:

```
products/
├── _example.yaml   the seeded template entry, example: true
├── 385.yaml
├── 387.yaml
├── 544.yaml
└── 900.yaml
```

`3856028503835` goes in `385.yaml`. The EAN-8 `54491472` goes in `544.yaml` on
the same rule — the first three digits, whatever the length of the barcode. If
the file does not exist yet, create it and give it the header comment every other
prefix file carries.

### The filename is a filing convention. It is not a country.

The first three digits of a barcode record **which GS1 member organisation issued
the number**. They say nothing about where a product was made, who made it, or
where the company is registered, and [EDITORIAL-POLICY.md](../EDITORIAL-POLICY.md)
forbids drawing any such conclusion from them.

This has to be said out loud because a directory listing that reads `385 387 544`
looks like a country index, and mistaking a prefix for a country is precisely the
error this dataset exists to correct. Origin lives in the `markets:` records,
sourced from the label. It is never read off the filename.

The convention exists for two dull reasons: it sorts the records, and it keeps
two contributors working on different products out of the same file. Nothing
more. The validator deliberately does **not** check that a barcode matches the
file it sits in — enforcing it would make the convention load-bearing, and it is
not.

## Why entries are keyed by market

A barcode identifies who registered the number, not who made the product. Barcode
to manufacturing country is not a function: one number, many correct answers, and
nothing in the number to tell them apart. The [README](../README.md) works
through an illustration of this in full, under "Why product overrides are keyed
by market". That illustration is not a record and is in none of these files.

So facts split in two:

| Class | Fields | Where it lives |
|---|---|---|
| Market-invariant | name, brand, brand owner, ultimate parent | the top level of an entry — the same everywhere |
| Market-variant | made in, operating company, who placed it on the market | ONLY inside a `markets:` record, next to the market it applies to |

Never write `made_in`, `operator` or `placed_on_market_by` at the top level. If
you only know that a product exists and not where it was made, write the name and
brand and stop. Consumers of this data show "varies by market — check the label"
when no market record matches, which is a true answer. A guessed flag is not.

## Validation

CI reads **every** `.yaml` file in this directory and concatenates the lists, so
the split across files is invisible downstream. A barcode may appear only once in
the whole directory; a duplicate across two files fails the build with both
filenames named. Add a `markets:` record to the existing entry instead.
