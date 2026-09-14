# Editorial policy

This is the rule set the maintainer applies when accepting or rejecting a change.
It is written down so that a rejection is never a surprise, and never a matter of
opinion.

## Every claim needs a source anyone can check

An ownership claim is only worth as much as the source behind it. Every record in
this dataset carries at least one source that a stranger can open and read for
themselves, and a `verified_on` date saying when a human last did exactly that.

A claim without a date cannot be re-checked later, and being re-checkable is the
entire point of this dataset.

### Acceptable sources

- National company registers.
- GLEIF records.
- Annual reports.
- Official company websites.
- Official acquisition press releases.

### Not acceptable

- News articles alone.
- Wikipedia alone.
- Other apps.
- Common knowledge.

A news article may well be how you found out, and saying so alongside a register
entry is useful. It is not, by itself, enough.

**Unsourced submissions are rejected regardless of whether they look correct.**
This is not scepticism about your particular claim. A dataset where some records
can be checked and others cannot is a dataset where none of them can be trusted.

## Unknown is recorded as unknown

If a fact is not known, the field is left out. It is never filled with a guess, a
likely answer, or a default.

**Nothing is ever guessed from a barcode prefix.** A barcode prefix records only
which GS1 member organisation issued the number. It is not evidence of where a
product was made, where the company is based, or who made it, and it is never
used as such.

## Manufacturing claims are market-specific

One barcode can have many manufacturing origins. The same number appears on
bottles filled in different countries by different companies. Barcode to
manufacturing country is not a function — the information is genuinely not in the
barcode.

Therefore:

- A `made_in` or `operator` claim must cite a label photo or an official company
  statement.
- It must name the market it applies to — the country the product was bought in.
- It is never inferred from a barcode prefix.
- It is never recorded without a market.

Where no market record exists, consumers of this data say "varies by market —
check the label". That is a true answer, and a better one than a flag.

## Scope: corporate structure only

This dataset records who owns what, and where those companies are registered.

It records no stances, no conduct, no positions, and no boycott information.
There are no fields for such content, and none will be added. Pull requests
adding it are closed.

The reason is narrow and practical: ownership is a matter of public record and
can be checked against a register. Conduct is a matter of judgement and cannot.
Mixing the two would make the checkable part unverifiable too.

## Rejection is not a judgement about truth

A rejected submission is not a claim that you are wrong. It usually means the
record could not be checked in the form it arrived in. Sourced resubmissions are
welcome, and there is no penalty for having had one turned down.

## Decisions

One maintainer makes final decisions.
