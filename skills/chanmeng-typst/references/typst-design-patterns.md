# Typst Design Patterns

Reusable patterns for document design in Typst — from basic setup to advanced layouts.

---

## Basic Document Setup

The canonical preamble pattern — put `set` rules at the top, then write content:

```typst
#set page(paper: "a4", margin: 2.5cm)
#set text(font: "Libertinus Serif", size: 11pt)
#set heading(numbering: "1.1")
#set par(justify: true, leading: 0.8em)

= Introduction
Content here...
```

---

## CJK Document Setup

Set the text language and a font fallback chain for Chinese, Japanese or Korean. Omitting `lang` or a CJK-capable font causes missing glyphs (tofu □).

```typst
#let cjk-serif = ("Source Han Serif SC", "Noto Serif CJK SC", "Songti SC", "SimSun")
#let cjk-sans = ("Source Han Sans SC", "Noto Sans CJK SC", "PingFang SC", "Microsoft YaHei")
#let cjk-kai = ("Kaiti SC", "KaiTi")

#set text(lang: "zh", region: "cn", font: cjk-serif)
#set par(first-line-indent: (amount: 2em, all: true))
#show strong: set text(font: cjk-sans)
#show emph: set text(font: cjk-kai, style: "normal")
#show heading: set text(font: cjk-sans, weight: "bold")
```

To give Latin text its own font, put it first with `covers`. Without `covers`, the Latin font also takes Chinese quotation marks and sets them narrow:

```typst
#set text(font: ((name: "Times New Roman", covers: "latin-in-cjk"), "SimSun"))
```

For Japanese or Korean, change `lang` and use families such as `Noto Serif CJK JP`, `Yu Mincho`, `Noto Serif CJK KR` or `Malgun Gothic`. `references/typst-pitfalls.md` § CJK text explains these choices.

---

## Math Equations

```typst
$ integral_0^infinity e^(-x^2) dif x = sqrt(pi) / 2 $
```

---

## Including External Data

```typst
#let data = json("data.json")
#let records = csv("data.csv")
#let config = yaml("config.yaml")
```

---

## Using Packages

```typst
#import "@preview/cetz:0.5.3": canvas, draw
#import "@preview/showybox:2.0.4": showybox
```

First compile with a new `@preview` package requires internet access. Use the native `table` for row spans, column spans and header rows instead of the older `tablex` package.

---

## Theme System (Cascading Defaults)

Use a dictionary-based theme with a fallback helper for customizable templates:

```typst
#let default-theme = (
  margin: 26pt,
  font: "Libre Baskerville",
  font-size: 8pt,
  font-secondary: "Roboto",
  font-tertiary: "Montserrat",
  text-color: rgb("#3f454d"),
)

#let my-template(theme: (), body) = {
  let th(key) = if key in theme { theme.at(key) } else { default-theme.at(key) }
  set text(font: th("font"), size: th("font-size"), fill: th("text-color"))
  body
}
```

---

## Scope-Based Show Rules

Nest `show` rules inside blocks to apply styling only within a specific scope:

```typst
{
  show heading: set text(size: 26pt, weight: "regular")
  show heading: set block(above: 3pt, below: 0pt)
  heading(level: 1, last-name)
}
// The show rules above do NOT affect content outside this block
```

---

## Visual Hierarchy Through Text Color

Use `text.fill.lighten()` inside `context` blocks for secondary/tertiary text:

```typst
context {
  set text(weight: "light", fill: text.fill.lighten(30%))
  timeframe   // renders lighter than surrounding text
}
```

---

## Multi-Column Layout with Grid

Use fractional units for responsive sidebar + main layouts:

```typst
#grid(
  columns: (3fr, 26pt, 6fr),  // aside, gutter, main
  aside-content,
  [],  // empty gutter
  main-content,
)
```

---

## Circular Profile Pictures

```typst
{
  set block(radius: 100%, clip: true, above: 1fr, below: 1fr)
  set align(center)
  set image(width: 55%)
  image("photo.jpg")
}
```

---

## Modular Component Functions

Build reusable entry components for structured documents (resumes, reports):

```typst
#let work-entry(timeframe: "", title: "", organization: "", location: "", body) = {
  stack(dir: ltr, spacing: 1fr,
    context { set text(weight: "light", fill: text.fill.lighten(30%)); timeframe },
    context { set text(weight: "light", fill: text.fill.lighten(30%)); location },
  )
  { set text(weight: "bold"); upper(title) } + " – " + organization
  line(stroke: 0.1pt, length: 100%)
  body
}
```

---

## Long-Lived Document Projects

A CV, report or brand template that will be edited for months should not be one file. Separate what changes for different reasons:

```text
cv/
├── main.typ          # Page setup; includes the sections in order
├── tokens.typ        # Colours, fonts, sizes, and the one spacing scale
├── components.typ    # Reusable blocks such as entry() and section()
├── sections/         # Content only, with no layout decisions
├── data/             # Facts as YAML or JSON, when several outputs share them
├── fonts/            # Licensed fonts kept with the project
└── build.sh          # Compiles, then runs the checks
```

Compile from the project root:

```bash
typst compile --root . --font-path fonts main.typ build/cv.pdf
```

- **Name every value.** Components use `gap-entry` and `accent`, never literal `12pt` or a hex code, so a design change is a one-line edit.
- **Paths starting with `/` resolve from `--root`.** Files outside the root are rejected, so shared assets belong inside it.
- **Variants import, they do not copy.** A second layout should reuse `tokens.typ` and the same data. A copied block of facts drifts from the original without any error.
- **Trace figures to a source.** For reports and CVs, load facts from the data files or keep a note of where each number came from.
- **Make the build fail loudly.** Stop on a non-zero `typst compile` exit, then run `scripts/check-pdf.py`. See `references/typst-pitfalls.md` § Build and metadata.

---

## Accessible PDFs

Typst tags PDFs by default, but the tags are only as good as the source. These habits follow the official accessibility guide:

- Use real headings, lists and `table.header` instead of styled text, and never skip a heading level.
- Set `title` in `#set document(...)` and `lang` in `#set text(...)`.
- Give every meaningful image `alt`, and every equation an `alt` through `math.equation`.
- Keep text contrast high, especially light grey captions.

To enforce the checks the compiler can make, target PDF/UA-1. It stops on problems such as a missing title or missing alt text. Compatible standards can be combined:

```bash
typst compile --pdf-standard ua-1 report.typ
typst compile --pdf-standard a-2a,ua-1 report.typ
```

---

## Several Outputs from One Project (Experimental)

Bundle export writes several files from one source, which suits a designed CV and an ATS CV that share the same data. It needs a feature flag and may change between releases.

```typst
#document("cv-designed.pdf", title: [CV])[= Designed version]
#document("cv-ats.pdf", title: [CV])[= ATS version]
```

```bash
typst compile --features bundle --format bundle main.typ out/
```

---

## Custom Fonts with `--font-path`

When using non-system fonts, bundle them and compile with:

```bash
typst compile --font-path ./fonts document.typ
```

Use `typst fonts --font-path ./fonts` to verify fonts are discovered.

---

## Conditional Rendering (PDF vs HTML)

`target()` needs `context`. Use it to produce format-specific output:

```typst
#let note(body) = context {
  if target() == "html" {
    // HTML: semantic element
    html.elem("div", attrs: (class: "note"), body)
  } else {
    // PDF: styled block
    block(fill: luma(240), inset: 10pt, radius: 4pt)[*Note:* #body]
  }
}
```

---

## Responsive Layout with `layout()`

Adapt content based on available width:

```typst
#let responsive-columns(body) = layout(size => {
  if size.width > 400pt {
    columns(2, gutter: 12pt, body)
  } else {
    body
  }
})
```

---

## Common Compiler Error Patterns

| Error message pattern | Cause | Fix |
|---|---|---|
| `unknown variable: foo` | Misspelled function or missing import | Check spelling; add `#import` |
| `expected X, found Y` | Type mismatch (e.g., string vs content) | Wrap in `[]` for content or use `str()` for string |
| `can only be used when context is known` | Using counter/state outside `context` | Wrap in `context { ... }` |
| `unexpected end of block comment` | Unclosed `/*` | Close with `*/` |
| `cannot mutate a captured variable` | Modifying outer variable in closure | Use `state()` instead |
| `duplicate key` | Repeated dictionary key | Remove duplicate or rename |
| `file not found` | Wrong path or missing file | Use forward slashes, check relative path from project root |
| `unknown font family` | Font not available on system | Run `typst fonts` to list available; use `--font-path` |

---

## Advanced Counter Patterns

Auto-numbering custom elements (theorems, definitions, etc.):

```typst
#let theorem-counter = counter("theorem")
#let theorem(body) = {
  theorem-counter.step()
  block(fill: luma(240), inset: 10pt, width: 100%, radius: 4pt)[
    *Theorem #context theorem-counter.display().* #body
  ]
}

#theorem[Every even integer greater than 2 is the sum of two primes.]
#theorem[There are infinitely many prime numbers.]
```

---

## Tiling (Repeating Pattern Fills)

```typst
#let dots = tiling(size: (10pt, 10pt))[
  #place(center + horizon, circle(radius: 1.5pt, fill: gray))
]
#rect(width: 100pt, height: 50pt, fill: dots)
```

---

## PDF Output Capabilities

Typst's PDF backend (powered by `pdf-writer`) supports:

- **PDF standards**: PDF 1.4–2.0, PDF/A-1b through PDF/A-4e, PDF/UA-1
- **Tagged PDF**: Accessible documents with structure tags (enabled by default)
- **Color spaces**: RGB, CMYK, grayscale, ICC profiles, Lab color, spot colors
- **Fonts**: Full Unicode/CJK support via composite fonts (Type0 + CID)
- **Advanced graphics**: Transparency, blending modes, soft masks, gradients
- **Interactive elements**: Clickable links, annotations
- **Reproducible builds**: Pin `document(date: ...)`, or set `SOURCE_DATE_EPOCH`, for byte-identical output
