# Public Sources and Rationale

This skill combines established scientific-presentation practices with stronger
constraints designed for automated slide generation.

Useful public references include:

- OpenAI Academy — Skills
  https://openai.com/academy/skills/
  Rationale: reusable skills can combine a focused SKILL.md with references,
  templates, examples, and final checks.

- OpenAI/JetBrains Slides Skill mirror
  https://github.com/JetBrains/skills/blob/main/slides/SKILL.md
  Rationale: build from editable source, render, and validate the rendered deck.

- MIT EECS Communication Lab — Slide Presentation
  https://mitcommlab.mit.edu/eecs/commkit/slideshow/
  Rationale: adapt figures for presentation, guide audience attention, and use
  message-oriented visual communication.

- MIT EECS Communication Lab — Figure Design
  https://mitcommlab.mit.edu/eecs/commkit/figure-design/
  Rationale: visual form should follow the scientific question; presentation
  figures often need redesign relative to publication figures.

- MIT AeroAstro Communication Lab — Slide Design
  https://mitcommlab.mit.edu/aeroastro/commkit/slide-design/
  Rationale: figures copied directly from papers may be too dense for oral use.

The V3-specific hard gates—diagram edge specs, arrow-direction verification,
source-visual preflight, and page-furniture contamination checks—are introduced
to catch recurring failure modes of automated PPT generation. They are
engineering safeguards rather than claims that every scientist follows one
single slide style.
