# Fields

The schemas in [`../schema/`](../schema) are the authority. This page explains
what the fields mean.

## Entity: `entities/<country>/<id>.yaml`

A registered legal company.

| Field | Required | |
|---|---|---|
| `id` | yes | `e_` + a slug. Also the filename. |
| `name` | yes | The exact legal name as the national register prints it. |
| `former_names` | no | Earlier legal names, as a register records them. |
| `country` | yes | ISO 3166-1 alpha-2 country of registration. Also the folder. |
| `lei` | no | GLEIF Legal Entity Identifier. |
| `registry_id` | no | National register number, quoted. Required when the only qualifying source is a register citation. |
| `parent` | no | The entity that **directly** owns this one. |
| `parent_exception` | no | Instead of `parent`, when a source says the owner exists but is not disclosed. |
| `ultimate_parent` | no | The entity at the **top** of the chain. |
| `ultimate_parent_exception` | no | Instead of `ultimate_parent`, when it is undisclosed. |
| `sources` | yes | See [Sources](#sources). |
| `notes` | no | See [Notes](#notes). |
| `verified_on` | yes | Date someone last checked the sources. |

### Ownership: four states per field

| State | Written as | Meaning |
|---|---|---|
| Not established | field left out | nobody has looked, or looking found nothing |
| Named | `parent: e_something` | a source names the owner |
| None | `parent: null` | a source confirms there is no owner above |
| Withheld | `parent_exception: NON_PUBLIC` | a source says the owner exists but is not disclosed |

`parent` and `ultimate_parent` are independent. Either can be set without the
other. Don't put an ultimate parent in `parent`. The policy behind this is in
[EDITORIAL-POLICY.md](../EDITORIAL-POLICY.md#ownership-has-four-states-not-two).

## Brand: `brands/<first letter>/<id>.yaml`

A name printed on products. A brand belongs to an entity; it is not one.

| Field | Required | |
|---|---|---|
| `id` | yes | `b_` + a slug. Also the filename; the folder is the first letter after `b_`. |
| `name` | yes | As normally written. |
| `aliases` | no | Other spellings seen in use. |
| `brand_owner` | yes | The entity that owns the trademark. |
| `sources` | yes | A trademark register entry is best. |
| `notes` | no | |
| `verified_on` | yes | |

Ranges and flavours (Coca-Cola Cherry, Violeta PREMIUM) go in the product name,
not in a brand of their own.

## Product: `products/<first 3 digits>/<barcode>.yaml`

This dataset is the only record of the products in it: nothing upstream supplies
them.

| Field | Required | |
|---|---|---|
| `barcode` | yes | As printed, quoted, leading zeros kept. Also the filename. |
| `name` | in practice | As printed, with size. Nothing else records it. |
| `brand` | no | The brand on the package. |
| `notes` | no | |
| `markets` | no | One record per country the product was bought in. |

Each `markets` record:

| Field | Required | |
|---|---|---|
| `market` | yes | Country where the product was **bought**. |
| `made_in` | one of these two | Country of manufacture, as the **label** states it. |
| `operator` | one of these two | The company that made it for this market. |
| `placed_on_market_by` | no | The importer, distributor or own-brand retailer the label names. Not the manufacturer. |
| `sources` | yes | Label text, transcribed as printed: `"label text: ..."`. |
| `verified_on` | yes | |

The same barcode can be made by different companies in different countries, so
`made_in`, `operator` and `placed_on_market_by` exist only inside a market
record. If the label names nobody separate from the manufacturer, leave
`placed_on_market_by` out.

## Sources

An entity or brand needs at least one source in one of these forms:

| Form | Example |
|---|---|
| URL to the record itself | `https://api.gleif.org/api/v1/lei-records/549300K4P51ZN6YBMH96` |
| Register citation | `BA/bizreg: MBS 1-5356` — `<country>/<register>: <identifier>` |

Use the citation form for registers without a stable link per company, such as
BiH bizreg or Serbian APR. Don't link to a register's search page. Label text is
a good extra source, but never enough on its own for an entity or brand.

## Notes

Optional, at most 300 characters. Write one only when, without it, the next
editor would probably make a wrong change the validator can't catch. For example:

```yaml
notes: "Do not attach LEI 74780000F06H8UWC7I70: it belongs to JAMNICA d.d. (MBS 080001412), a different, retired company."
```

State the fact. The research story belongs in the pull request.

## Example records

`entities/GB/e_example_holding_ltd.yaml`, `brands/e/b_example_brand.yaml` and
`products/999/9990007654324.yaml` are invented templates marked `example: true`.
Copy one to start a new record.
