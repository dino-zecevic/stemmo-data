# stemmo-data

Hand-curated data linking the brand on a product to the registered company that
owns it, and that company to the companies that own it. Every record has a source
anyone can check and the date someone last checked it.

Product databases record brands as free text. Company registers know companies
but not brands. This dataset is the link between the two, built one brand at a
time.

## Layout

```
entities/<country>/<id>.yaml        a registered company      entities/BA/e_violeta_ba.yaml
brands/<first letter>/<id>.yaml     a brand name              brands/v/b_violeta.yaml
products/<first 3 digits>/<barcode>.yaml   a product          products/387/3873508991982.yaml
schema/                             JSON Schema for each record type
scripts/validate.py                 the checks CI runs
docs/                               field reference and open questions
```

One record per file, and the filename is the record's id, so you can find any
record from an id or barcode without searching. The validator checks that each
file is where its id says it should be.

The first three digits of a barcode say which GS1 office issued it. They are only
used to split the folder, and say nothing about where the product was made.

## What a record looks like

```yaml
id: b_violeta
name: Violeta

brand_owner: e_violeta_ba

sources:
  - 'BA/IIP-BIH: trade mark 1619857, combined mark VIOLETA, classes 03/05/16/21/35, ...'

notes: Separate trademark from b_teta_violeta (1619857 vs 1619510); do not merge.

verified_on: 2026-09-17
```

Records have no comments. If a fact has to stay with the record so nobody makes a
wrong edit later, it goes in `notes`, in one or two sentences. How you researched
it goes in the pull request description.

Every field is described in [docs/fields.md](docs/fields.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). If you don't use Git, open an issue. The
templates ask for the same information.

The rules for what gets accepted are in [EDITORIAL-POLICY.md](EDITORIAL-POLICY.md).
In short: everything has a checkable source, unknown stays unknown, and only
corporate structure is recorded, never opinions about companies.

## Validation

```bash
pip install -r scripts/requirements.txt
python scripts/validate.py
```

CI runs the same script on every pull request. It checks each record against its
schema, that it sits at the right path and has no comments, that every
referenced id exists, that ownership has no cycles, LEI check digits, country
codes, and that no two brands match the same name.

`main` is protected: every change goes through a pull request and the check must
pass. One maintainer makes final decisions.

## Used by

[stemmo-pipeline](https://github.com/dino-zecevic/stemmo-pipeline) builds the
files the Stemmo app reads from this data. The dataset stands on its own and is
useful without the app.

## Licence

[ODbL-1.0](LICENSE). Use it for anything, including commercially. Credit the
source, and if you publish a database derived from this one, publish it under
ODbL too. An app that only queries the data can stay closed-source.

The dataset was first published as CC0 and relicensed to ODbL before it had any
outside contributors.
