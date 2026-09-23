# Open questions

Undecided. Listed so they aren't forgotten.

- **Several members.** How should a company owned by more than one member be
  recorded? `e_violeta_hr` has two members and no published shares, so no parent
  is set. Any answer has to handle mixed company and individual members, missing
  percentages, and never naming individuals.
- **Dating market records.** Should `markets` records get a `valid_from` date?
  Bottling arrangements change, and a record can go stale without any sign.
- **Known multi-market.** Should a barcode be markable as multi-market before any
  market record exists? Today, downstream, "varies by market" looks the same as
  "nothing recorded yet".
- **GS1 licensee.** Should the company that licensed a barcode prefix be
  recorded? Sometimes it is the brand owner and producer (Pfanner), sometimes a
  company with no other role (a Belgian Coca-Cola services company). GS1 data has
  also disagreed with national registers about company names.
- **Label photos.** Should label photos be stored? Hosting has a cost, and
  transcribed label text may be enough.
- **Names by market.** Should `name` be allowed to vary by market, for products
  sold under different names in different countries?
- **Why a chain ends.** A sourced `null` can come from `NON_CONSOLIDATING`
  (`e_cchbc_ag`: nothing consolidates it) or `NATURAL_PERSONS` (`e_bingo`: the
  owners are individuals), and both are written as a bare `null`. Should a field
  record the reason, as `parent_exception` does for withheld owners? It would need
  values that also work for a `null` sourced from a national register.
