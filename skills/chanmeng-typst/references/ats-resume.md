# ATS-Safe Resumes

An applicant tracking system (ATS) extracts text from a resume before a person sees it, so layout that looks fine can still lose a job title, date or keyword. Use this reference when the resume will be uploaded to a job portal, or when the user asks for an "ATS-friendly" or "machine-readable" resume.

A designed resume with columns, icons and colour suits a personal site or a direct email to a person. When both are useful, keep two files from the same facts, because a single file cannot serve both readers well. `references/typst-templates.md` § 4b is the designed version; `examples/resume-ats.typ` is the machine-readable starting point.

## Rules

Each rule exists because of how extractors behave, so keep them even where the result looks plain.

**Structure**

- Use one column, with no grids, tables or `columns()`. Layout-aware parsers read across columns and mix them. Put dates on the organisation line behind a `|`, not right-aligned in a grid.
- Use native `= HEADING` so the PDF contains real heading structure.
- Use section names a parser recognises, such as Summary, Skills, Experience, Projects, Education and Certifications. A creative heading can be absorbed into the section before it.
- Do not use page headers or footers. Some parsers discard text near the page edge or splice it into the body. For the same reason, keep margins at 1.5cm or more.

**Content**

- Do not use images, icons or text boxes. Bold and full-width hairlines under headings are enough decoration.
- Use black body text at 10pt, because small text degrades parsers that fall back to OCR.
- Avoid italics unless the font has a real italic face.
- Delimit everything with real characters: commas between skills, ` | ` between contact fields.
- Make links show their target, using the bare URL or a real name. "Portfolio" or "here" tells a text extractor nothing.
- Prefer plain ASCII where meaning allows: `-` for bullets and date ranges, and straight quotes with `smartquote(enabled: false)`. Keep accented characters in names.
- Write dates in one format throughout, such as `Mar 2025 - Feb 2026`.

**Integrity**

- Do not add hidden text, white text or a `/Keywords` list. Screeners can read these, and they look like keyword stuffing.
- Use only facts the user supplied. Rewording and reordering are fine, but do not invent metrics, titles or dates to fill space. Ask, or leave a visible placeholder.
- If a role's scope is unclear from its title, say so in plain terms. Readers calibrate a title from its scope.

**File**

- Pin `date: datetime(...)` in `#set document(...)`. A PDF with no dates can trip legacy parsers.
- Set `title` and `author`.
- Keep tagged PDF on, which is the default. Do not pass `--no-pdf-tags`.

## Skeleton

Start from `examples/resume-ats.typ`. These lines do most of the work:

```typst
#set document(
  title: "Your Name - Resume",
  author: "Your Name",
  date: datetime(year: 2026, month: 1, day: 15),
)
#set page(paper: "a4", margin: 1.6cm, header: none, footer: none)
#set text(font: "Libertinus Serif", size: 10pt, fill: black, hyphenate: false)
#set par(leading: 0.68em, spacing: 0.9em)
#set list(marker: [-], spacing: 1.2em)
#set smartquote(enabled: false)

// Stops a line break at a hyphen, which extraction would turn into a lost hyphen.
#show regex("[\w.]+(-[\w.]+)+"): it => box(it)

#show heading.where(level: 1): it => block(above: 18pt, below: 7pt, breakable: false, sticky: true, {
  set text(size: 10.5pt, weight: "bold")
  set block(above: 0pt, below: 3pt)
  it
  line(length: 100%, stroke: 0.5pt + black)
})
```

## Verify

Run the bundled checker on the output:

```bash
python scripts/check-pdf.py resume.pdf --source resume.typ --ats --pages 2 \
  --require "Your Name" "you@example.com" "Senior Engineer"
```

`--require` takes the facts that must survive extraction: name, email, phone, each employer and each job title. With `--ats`, the script fails on images, grids, a `/Keywords` entry, missing dates or untagged output. Then read `pdftotext -layout resume.pdf -` as a parser would, and render the pages to PNG to check the hairlines and spacing.

## Limits of PDF checks

Passing these checks makes parsing likely, not certain. A portal can refuse a PDF that passes all of them. Tell the user to:

- Keep a `.docx` fallback for portals that reject the PDF. Use a font recipients already have, such as Arial, real heading styles and real numbered bullets.
- Keep a plain `.txt` copy for "paste your resume" fields.
- Attach the file to a real application form and confirm that name, email and experience auto-fill before relying on it.

Regenerate these fallbacks from one source so the text cannot drift between formats.
