# Dynamic writing-profile release fixture

Synthetic v2.0 fixture showing the runtime interface:

`writing_context -> writing_sources -> writing_profile -> manuscript_contract -> manuscript`.

`ExampleConf` is intentionally fictional. The fixture tests provenance and contract enforcement without depending on the web.

The fixture also declares `article_type=conference_paper` and `track=main`, so release QA verifies applicability across venue, year, article type, track, and submission stage rather than only venue name.
