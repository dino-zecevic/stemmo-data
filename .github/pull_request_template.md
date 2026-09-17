<!--
One product per pull request, including any entity or brand it needs that does
not exist yet. Several products from one producer may share a pull request where
the entity and brand work is shared. A correction is its own pull request. Never
mix a data addition with a schema or editorial-policy change.

The full rule is in CONTRIBUTING.md, under "What goes in one pull request".

Fill in what applies and delete the rest, including these comments. A heading
with nothing under it is fine if that work genuinely was not needed — an empty
GLEIF section is not, because an empty search result is itself a claim.
-->

## What this adds

<!-- Product names and barcodes, and the entities and brands they needed. -->

## Company register

<!--
Which register, and the identifier it gave you — not "I looked it up".
  BA/bizreg: MBS 1-5356
  HR/sudreg: MBS 081180379, OIB 02233362849
  AT/Firmenbuch: FN 314034s
Note where the register's legal name differs from the name printed on the pack.
-->

## Trademark register

<!--
Which register, and the mark number.
  BA/IIP-BIH: trade mark 1417973, word mark BINGO, classes 29/30/35/39
Say so if the mark is figurative rather than a word mark, or if its registration
has expired. Both weaken the citation; both are fine to record.
-->

## GLEIF queries

<!--
Every query you ran, INCLUDING the ones that returned nothing. An empty result
is the claim "this company has no LEI", and it is reproducible only with the
search term, the country filter and the date written down. Two queries where the
name allows it — the full legal name and a shorter distinctive fragment.

  search "Sarajevski Kiseljak", country filter BA, 2026-09-16 -> no records
  search "Sarajevski",          country filter BA, 2026-09-16 -> no records

State any near-miss and why you rejected it, rather than leaving it out.
See EDITORIAL-POLICY.md, "A GLEIF negative is cited by recording the query".
-->

## Ownership

<!--
For each entity: what you established, and from which source. If a parent or
ultimate parent is absent, say whether you looked. If it is null or an
exception, name the source that says so.
-->

## What you could not establish

<!-- Anything you looked for and did not find. This is useful, not a failure. -->
