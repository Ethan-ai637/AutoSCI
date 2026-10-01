# v1.7.2 conflict-disposition example

Synthetic full-manuscript release example showing `disclose_and_scope` with explicit conflict-side provenance.

- `C001` is a source-specific Results claim tied only to the canonical side.
- `C003` is the designated cross-side disclosure claim.
- `CF001.conflict_sides` binds canonical versus secondary source/evidence/value streams.
- `cross_side_claim_ids=["C003"]` permits C003 to mention both sides only because it is also the manuscript disclosure claim and visibly attributes both sources.

Expected: release PASS. Mutating C001 to link `E004`, or removing `canonical table`/`secondary export` attribution from C003, must fail release.
