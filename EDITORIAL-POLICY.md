# Editorial policy

This is the rule set the maintainer applies when accepting or rejecting a change.
It is written down so that a rejection is never a surprise, and never a matter of
opinion.

## Every claim needs a source anyone can check

An ownership claim is only worth as much as the source behind it. Every record in
this dataset carries at least one source a stranger can go and check for
themselves, and a `verified_on` date saying when a human last did exactly that.

A claim without a date cannot be re-checked later, and being re-checkable is the
entire point of this dataset.

### Acceptable sources

- National company registers.
- GLEIF records.
- Annual reports.
- Official company websites.
- Official acquisition press releases.

### How a source is cited

A qualifying source takes one of two forms.

**A URL**, where the source has one that leads to the record itself.

**A structured register citation**, `<ISO country>/<register>: <identifier>` — for
example `BA/bizreg: MBS 1-5356` or `AT/Firmenbuch: FN 314034s`. Many national
registers are search applications that mint a session token per visit and publish
no stable per-record link. Citing such a register's search form is a URL that
satisfies a pattern and tells the reader nothing: it is the same page for every
company in the country. What makes the record checkable is the identifier, so the
identifier is what gets cited, and it must also appear in `registry_id` so that
nothing rests on a human reading the source string.

Neither form is the stronger one. A register citation with an identifier is
better evidence than a link to a page that happens to resolve.

### Identity and ownership come from different sources

These are two different claims and the best source for each is a different one.

**A national register is the authority on identity.** It is the body that issues
the legal name, and the name it prints is the name. Most registers publish little
or no ownership.

**GLEIF is the better source for ownership.** It publishes parent relationships
no national register does, and it publishes them in a form that says explicitly
when an owner exists but is undisclosed. It is the only source in use here that
answers the ownership question at all.

**GLEIF is the weaker source for identity.** It normalises legal names — often to
upper case, sometimes dropping the diacritics or the capitalisation the register
uses — and its own metadata frequently admits the name was not fully checked: a
`corroborationLevel` below `FULLY_CORROBORATED`, or a `conformityFlag` of
`NON_CONFORMING`.

So where a register and GLEIF disagree about a legal name, **the register wins**.
Cite GLEIF for the ownership claim and the register for the name, in the same
record.

The case that established this: GLEIF returned `COCA-COLA HBC B-H D.O.O.
SARAJEVO` while bizreg prints `Coca-Cola HBC B-H d.o.o. Sarajevo`. Same company,
same registry number 65-01-0806-09, and GLEIF's own record for it is
`PARTIALLY_CORROBORATED` and `NON_CONFORMING`. The register's form is kept.

This is not a reason to distrust GLEIF's ownership data. A registration agent may
verify a parent relationship thoroughly and still transcribe a name in upper
case. Take each source for the thing it is authoritative about.

### Not acceptable

- News articles alone.
- Wikipedia alone.
- Other apps.
- Common knowledge.

A news article may well be how you found out, and saying so alongside a register
entry is useful. It is not, by itself, enough.

### A comment is a claim

A claim stated in a file's comments is held to the same standard as a claim in a
field. If a comment describes what a source says, that source is cited on the
record. Reviewers read comments as fact, and an uncited comment is
indistinguishable from a checked one.

**Unsourced submissions are rejected regardless of whether they look correct.**
This is not scepticism about your particular claim. A dataset where some records
can be checked and others cannot is a dataset where none of them can be trusted.

### A GLEIF negative is cited by recording the query

Most companies in this dataset have no LEI. "This company has no LEI" is a claim
like any other and has to be reproducible, but an empty search returns no record
and therefore no URL — there is nothing to link to. So the negative is cited by
recording the search that produced it: the exact search term, the country filter,
and the date it was run, written into the record's comment.

That is **not** a `sources` entry. A query is not a document, and `sources` is for
documents. It is a maintainer note, and its whole job is to let the next person
re-run the same search rather than guess at what was asked. "GLEIF has nothing"
is not reproducible; `search "Sarajevski Kiseljak", country filter BA, 2026-09-16
-> no records` is.

**Where the name allows it, a negative rests on at least two queries:** the full
legal name, and a shorter distinctive fragment of it. A single narrow query
returning nothing may only mean the name is spelled differently in GLEIF, which
is common — GLEIF normalises case and diacritics and does not always carry the
register's form of a name. Two queries that both come back empty rule out a good
deal more than one. Where the broad query returns something that is *not* this
company, say so and say why it was rejected: a near-miss left unrecorded is a
near-miss the next person has to investigate again.

No schema field records any of this. It is a rule about comments.

## Unknown is recorded as unknown

If a fact is not known, the field is left out. It is never filled with a guess, a
likely answer, or a default.

### Ownership has four states, not two

Ownership is recorded in two independent fields — `parent`, the entity that
directly owns this one, and `ultimate_parent`, the top of the chain — and each of
them can be in any of four states.

| State | Written as | Meaning |
|---|---|---|
| Not established | field absent, no exception | nobody has looked, or looking found nothing |
| Named | field set to an entity id | a source names the owner |
| None | field set to `null` | a source confirms there is no owner above |
| Withheld | `*_exception` set | a source says the owner exists but is not disclosed |

The distinctions are the entire value of the fields, and three of them are easy
to collapse by accident.

**Absent is not null.** `null` is a positive claim and needs a source like any
other. It is not the cautious way to say "no parent found" — that is an absent
field. Recording an unverified entity as `null` is the same class of error as
guessing a parent, and harder to spot: anything walking a chain upwards treats
`null` as the end and stops, so the guess is never revisited. A record whose
parent is missing announces that work remains. One filled with `null` looks
finished.

**Absent is not withheld.** "We have not looked" and "we looked, the owner
exists, and it is deliberately undisclosed" are different facts, and the second
is worth publishing in its own right. A company whose immediate owner is not
disclosed is telling you something about itself, and no consumer-facing product
currently tells anyone that. Use an exception only where a source states it.

**Direct is not ultimate.** Writing an ultimate parent into `parent` asserts a
direct holding that the source did not establish, and it is not allowed. The two
fields are independent: both may be present, either may appear alone, and both
may be absent. This is not a hypothetical tidiness rule — real ownership data
routinely publishes one and withholds the other.

### Which reporting-exception reasons justify null

Where ownership comes from GLEIF, the reporting-exception reasons do not all mean
the same thing, and copying them mechanically into `*_exception` — or into
`null` — gets it wrong in both directions. Two of them are statements about
ownership. The rest are statements about disclosure or knowledge.

| Reason | Record as | Because |
|---|---|---|
| `NON_CONSOLIDATING` | `null` | a definite statement about accounting structure: nothing consolidates this entity, so it sits at the top of its chain |
| `NATURAL_PERSONS` | `null` | a definite statement that the owners are individuals, so the corporate chain ends at this company |
| everything else, including `NON_PUBLIC` and `NO_KNOWN_PERSON` | `*_exception` | the source is not asserting that there is no owner |

`NO_KNOWN_PERSON` is the one worth stating explicitly, because it reads at a
glance as if it meant "nobody owns this". It does not. It reports the limit of
the entity's own knowledge rather than a fact about its ownership — closer to "we
do not know" than to "there is nobody". Recording it as `null` would convert an
absence of knowledge into a positive claim, which is the precise error the
absent-versus-null rule exists to prevent.

The practical consequence, in the data: The Coca-Cola Company is almost certainly
the top of its chain, and this dataset does not say so. Its GLEIF record reports
`NO_KNOWN_PERSON` for both parents, which is a statement about what the company
knows rather than about what is true, so the record carries an exception and not
a `null`. Closing it properly needs the cover page of a current Form 10-K, which
names the registrant and would establish that it is nobody's subsidiary.

That is the rule working, not the rule being awkward. A dataset that guessed here
— on the one company where the guess is easy and would almost certainly be right
— would be a dataset that guesses everywhere the answer looks obvious.

Note finally what GLEIF's relationships are: accounting-consolidation
relationships. "Top of the chain" means "not consolidated into anyone else's
accounts", which is a precise claim and a narrower one than "owned by nobody in
any sense". A `null` sourced from `NON_CONSOLIDATING` carries that sense and no
more, and records should say so.

### A commercial relationship is not ownership

Companies appear together on a package for many reasons, and only one of them is
ownership. A contract manufacturer making a product for a retailer, a bottler
working under licence, an importer distributing a foreign producer's goods — all
three put two company names on one label, and none of them is evidence that
either company owns the other. Quite the opposite: the label names two companies
precisely because they are two companies.

`parent` records ownership and nothing else. A manufacturing, bottling, licensing
or distribution relationship is recorded, where the schema has a field for it, as
`operator` or `placed_on_market_by` — and otherwise not at all.

**Nothing is ever guessed from a barcode prefix.** A barcode prefix records only
which GS1 member organisation issued the number. It is not evidence of where a
product was made, where the company is based, or who made it, and it is never
used as such.

## Manufacturing claims are market-specific

One barcode can have many manufacturing origins. The same number appears on
bottles filled in different countries by different companies. Barcode to
manufacturing country is not a function — the information is genuinely not in the
barcode.

The company that places a product on a market is market-specific for the same
reason: the same product is imported into different countries by different
importers, and sold under a shop's own name in one country and the producer's in
the next. `placed_on_market_by` is therefore recorded per market, like `made_in`
and `operator`, and never at the top level.

Therefore:

- A `made_in`, `operator` or `placed_on_market_by` claim must cite a label photo
  or an official company statement.
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

### Natural persons are never recorded

This dataset records corporate structure. It never records natural persons.

Where an ownership chain reaches individuals, **that fact is recorded** — the
chain ends here, and what is above is people rather than companies. That is the
answer to the question this dataset exists to answer, and it is worth publishing.
What is not recorded, in any form, is **who they are**: no name, no identifier, no
address, no date of birth, no shareholding, for any individual. Not in a field,
not in a comment, not in a commit message, not in the README.

GLEIF's `NATURAL_PERSONS` reporting exception says exactly this: a company
reporting that its owners are individuals, without naming them. A record whose
chain ends in private hands is written the same way.

**Live in the data:** [`entities/bingo-doo-tuzla.yaml`](entities/bingo-doo-tuzla.yaml)
is the first record here whose chain reaches individuals. Note how it is written.
Both ownership fields are `null` — a sourced claim that the corporate chain ends
— and **not** a `*_exception`, because `NATURAL_PERSONS` is a statement about
ownership rather than about disclosure; see "Which reporting-exception reasons
justify null" above. The fact that the chain ends in private hands is recorded.
Nothing whatever about the individuals is.

The rule is written once, in advance, rather than decided case by case, because
the situation is not rare. Registers that publish ownership publish people: a
single Croatian extract consulted for this dataset supplied five named
individuals with identifiers and home addresses, as members, board members and
prokuristi. Every Croatian lookup will supply the same. A rule applied per record
under time pressure is a rule that eventually gets applied wrongly, once, in
public.

The reason is short. Information being public in a court register and information
being republished in a bulk dataset that a consumer app queries are different
things, and the second carries obligations the first does not. A register
discloses to someone who looks up one company for a reason; a dataset hands the
same data to everyone at once, indexed and joinable. Recording that a chain ends
in private ownership answers the question. Naming the owners adds nothing to the
answer and changes what this dataset is.

**Consequence for the several-members case.** A company with one corporate member
and one individual member is recorded as part-owned by the company — see the open
question in the README about how several members are represented at all — with
the remainder ending in private ownership and no individual named. The corporate
edge is a fact and is kept. The individual is not a gap in the record; not naming
them is the record.

## Licence: ODbL, and so is anything made from it

This dataset is licensed under [ODbL-1.0](LICENSE). Anyone may use it, for
anything, including commercially, on these terms: credit the source, and if they
publish a database derived from it, publish that derived database under ODbL
too. An application that queries the data is not itself a derived database, so a
closed application is permitted; a closed derived database is not.

Anything generated from this data is ODbL because **this dataset** is ODbL. The
licence is not derived from the licence of any source a pipeline reads, and no
argument about what some source permits changes the terms on the output. That
holds whether or not another source is ever added, since a share-alike source
would impose the same terms anyway.

A contribution accepted into this repository is published under that licence.
The dataset was CC0 when first published and was relicensed before it had any
outside contributors; the README records the change and why.

## Rejection is not a judgement about truth

A rejected submission is not a claim that you are wrong. It usually means the
record could not be checked in the form it arrived in. Sourced resubmissions are
welcome, and there is no penalty for having had one turned down.

## Decisions

One maintainer makes final decisions.
