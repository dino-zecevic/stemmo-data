# Contributing

A contribution is usually one product, plus the brand and company it needs if
they aren't here yet. Read [EDITORIAL-POLICY.md](EDITORIAL-POLICY.md) first; it
is the list of reasons a pull request gets turned down.

Don't use Git? Open an issue with the **Missing product** or **Incorrect data**
template instead.

## Setup

```bash
git clone https://github.com/<you>/stemmo-data.git
cd stemmo-data
git checkout -b add-<something>
pip install -r scripts/requirements.txt   # optional: CI runs the same check
```

## Adding a product

Say you are holding a bottle with barcode `3873508991982`.

1. **Check it isn't here already:** `ls products/387/3873508991982.yaml`. If it
   is, add a `markets` record for your country to that file.
2. **Find the brand** in `brands/`. If it's missing, add it (below).
3. **Find the companies on the label** in `entities/`: the manufacturer and, if
   the label names one, the importer or retailer. Add any that are missing
   (below).
4. **Create `products/387/3873508991982.yaml`**, starting from
   `products/999/9990007654324.yaml`:

```yaml
barcode: "3873508991982"
name: Bingo domaće mlijeko 2,0% m.m. 1L
brand: b_bingo

markets:
  - market: BA
    made_in: BA
    operator: e_mi99
    placed_on_market_by: e_bingo
    sources:
      - 'label text: Za Bingo, d.o.o. Tuzla proizvodi: Mliječna industrija 99 d.o.o., ...'
      - 'label text: Zemlja porijekla: Bosna i Hercegovina'
    verified_on: 2026-09-15
```

`market` is where you bought it. `made_in` is what the label says. Type the label
text exactly as printed, in its own language.

## Adding a brand

Create `brands/<first letter>/b_<slug>.yaml`, for example `brands/j/b_jana.yaml`.
The best source is a trademark register entry: [TMview](https://www.tmdn.org/tmview/)
or [WIPO](https://branddb.wipo.int/) cited by mark number. The owner's own
website is acceptable but weaker.

## Adding a company

Create `entities/<country>/e_<slug>.yaml`, for example
`entities/HR/e_jamnica_plus.yaml`.

1. **Name and number from the national register.** Use the exact legal name the
   register prints. It often differs from the name on the pack.
2. **LEI and ownership from GLEIF**, if the company has an LEI. `stemmo-tools
   gleif search` and `gleif resolve` do the lookups and draft the record.
3. **Leave ownership out unless a source states it.** `null` means a source
   confirms there is no owner, not "I found nothing". See
   [docs/fields.md](docs/fields.md#ownership-four-states-per-field).

Which registers answer what, as far as this project has found:

| Register | Gives you |
|---|---|
| BA bizreg | legal name, MBS, address. No owners, and no stable link, so cite `BA/bizreg: MBS ...` |
| HR sudreg | legal name, MBS, OIB, and members, with a stable link per company |
| RS APR | legal name, matični broj. No stable link |
| AT Firmenbuch | via the company's Impressum page |
| GLEIF | ownership, but only for companies with an LEI |

## Records have no comments

Write the facts in fields. If something must stay with the record to stop a wrong
edit later, put it in `notes` in one or two sentences. CI rejects `#` comments.

## The pull request

- One product per pull request, together with any brand or company it needs.
  Several products that share the same companies can go together.
- A correction is its own pull request.
- Schema or policy changes are separate from data.

The description is where your research goes. The template asks for the register
identifiers, trademark numbers, **every GLEIF search you ran, including the ones
that found nothing** (search term, country filter, date), and anything you
couldn't establish.

## What gets rejected

- Anything without a checkable source, however obviously right.
- A news article, Wikipedia or another app as the only source.
- `made_in` or `operator` without a market, or guessed from a barcode prefix.
- Opinions, conduct, boycott information. Only corporate structure is recorded.
- Names or details of private individuals.

A rejection means the record couldn't be checked as submitted, not that you were
wrong. Resubmissions are welcome.
