# Typst Pitfalls the Compiler Will Not Tell You About

A clean `typst compile` proves the source is valid, not that the document is right. Most entries here produced a PDF with no error at all and only showed up on a page render or a text extraction. Each was reproduced on Typst 0.15.1 with poppler 26.02, and the CJK entries were also checked on rendered pages.

Read this before tuning the layout of a dense document (CV, one-pager, report), and before any document that a machine will read.

## Contents

- [Spacing and layout](#spacing-and-layout)
- [Text that changes or disappears](#text-that-changes-or-disappears)
- [Images and icons](#images-and-icons)
- [CJK text](#cjk-text)
- [Fonts](#fonts)
- [Build and metadata](#build-and-metadata)
- [Fitting a page budget](#fitting-a-page-budget)

## Spacing and layout

### Block margins collapse to the larger one

The gap between blocks `A` and `B` is `max(A.below, B.above)`, not the sum. With `below: 10pt` and `above: 10pt` you get 10pt. If a gap seems to ignore your edit, the neighbour's margin is probably winning.

Let one side own the gap through a named value and set the other to `0pt`:

```typst
#let gap-entry = 12pt
#let entry(body) = block(above: 0pt, below: gap-entry, body)
```

### `v()` between two lines replaces the leading

`v()` splits the paragraph, so the gap becomes N rather than the leading plus N. A small value therefore moves the lines closer. A weak `v()` at the end of a block is discarded altogether. If a title looks glued to the line below it, or a spacing edit seems to do nothing, this is the likely cause.

Measured between two 9.5pt lines at `leading: 0.55em`:

| Between the lines | Gap |
|---|---|
| `linebreak()` alone | 5.2pt, the leading |
| `v(2pt, weak: true)` | 2pt |
| `v(8pt, weak: true)` | 8pt |
| `v(8pt, weak: true)` ending the first line's block | 0pt |

Give each line its own block, so the gap is exactly what you wrote:

```typst
#block(above: 0pt, below: 5pt)[*Job title*]
#block(above: 0pt)[Company | 2024 - Present]
```

### Use one spacing scale, and keep its steps distinct

Readers see structure through relative gaps. Each level should be clearly larger than the one below it: wrapped line, then bullet, then entry, then section. Define the whole ladder in one place and change the scale, not individual call sites, so the hierarchy survives edits.

### Keep list spacing well above the line leading

When the gap between bullets is close to the gap between wrapped lines, a list reads as one paragraph. As a rule of thumb, keep `list.spacing` at 1.7 times the leading or more, and lower both together when saving height:

```typst
#set par(leading: 0.65em)
#set list(spacing: 1.2em)   // about 1.8 times the leading
```

### Keep quotes, callouts and entry headers in one piece

A breakable block can strand its last line, such as a quote's attribution, alone on the next page. Use `breakable: false` so the whole block moves. Add `sticky: true` to a title block so it cannot sit at the foot of a page with its content overleaf:

```typst
#block(breakable: false, sticky: true)[*Job title* \ Company | 2024 - Present]
```

If the unbreakable block no longer fits, cut or move content instead of making it breakable.

### `align` in a grid aligns inside the cell

`grid(align: ...)` positions content within its cell. It does not move the column on the page, which is set by `columns:`. To put a left-aligned block on the right of a header, keep the column last and align only its contents:

```typst
#grid(
  columns: (auto, 1fr, auto),
  [Name], [], align(horizon + left)[Contact details],
)
```

## Text that changes or disappears

### A bare `~` is a non-breaking space

`~85%` renders as ` 85%`: the tilde is gone, with no warning. Write `\~85%` in markup. Code comments and strings are not affected.

### A bare `@` is a reference

`name@example.com` fails with ``error: label `<example.com>` does not exist in the document``. Write `name\@example.com` in markup, or put the address in a string.

### Line-end hyphens vanish on extraction

Typst may break a line at an explicit hyphen, and `pdftotext` then removes that hyphen when joining the lines, so `web-vitals` extracts as `webvitals`. `hyphenate: false` does not help, since it stops only automatic hyphenation. This silently breaks keyword search and resume screening.

Box every hyphenated compound so it cannot break:

```typst
#set text(hyphenate: false)
#show regex("[\w.]+(-[\w.]+)+"): it => box(it)
```

The trade-off is that a long compound moves to the next line whole, which can leave a short line in a narrow column. Also avoid a bare ` - ` as punctuation; use a colon, parentheses or an em dash.

### Space-separated items run together

Pills or tags laid out with gaps extract as one run of words (`Status line Plugins`), which makes item boundaries unrecoverable. Put a real delimiter in the text: commas between list items, ` | ` between contact fields.

### Columns can interleave

Plain `pdftotext` keeps grid cells in order, but layout-preserving extraction (`pdftotext -layout`) reads across columns and mixes them line by line. Some resume parsers behave the same way. If reading order matters to a machine, use one column.

## Images and icons

### SVG `currentColor` is not inherited

`image()` renders an SVG in isolation, so `stroke="currentColor"`, or a shape with no `fill`, comes out black whatever the surrounding `text(fill: ...)` says. Write the literal colour into the file:

```bash
sed 's/currentColor/#0B5FFF/g' icon.svg > icon-blue.svg
```

## CJK text

### Some Chinese fonts have no bold or italic

SimSun, SimHei and KaiTi ship one weight and no italic. With them, `*bold*`, `_emphasis_` and headings look exactly like body text, with no warning. Map those styles to fonts that have a visible difference:

```typst
#show strong: set text(font: ("Source Han Sans SC", "Noto Sans CJK SC", "PingFang SC", "Microsoft YaHei"))
#show emph: set text(font: ("Kaiti SC", "KaiTi"), style: "normal")
```

Check the result on a render. `pdffonts` should list more than one font when the document uses bold.

### A source line break adds a space

In Typst 0.15.1, a line break in the source between two Chinese or Japanese characters renders as a visible space, and that space is also in the extracted text. Keep each paragraph on one source line. A fix is on Typst's development branch but not yet released, so re-check this after upgrading.

### The first paragraph is not indented

`first-line-indent: 2em` skips the first paragraph after a heading, which suits Western typography. Chinese expects every paragraph to be indented:

```typst
#set par(first-line-indent: (amount: 2em, all: true))
```

### Numbering such as `一、` gets an extra space

`#set heading(numbering: "一、")` places a space after the number, which looks too wide next to the `、`. Draw the heading yourself to remove it:

```typst
#set heading(numbering: "一、")
#show heading: it => block(counter(heading).display(it.numbering) + it.body)
```

### Latin fonts can take Chinese punctuation

With a Latin font first in the chain, Chinese quotation marks come from that font and look narrow. Use `covers` so it only handles Latin text:

```typst
#set text(font: ((name: "Times New Roman", covers: "latin-in-cjk"), "SimSun"))
```

## Fonts

### Do not ignore `unknown font family`

This warning means Typst fell back to another font. The document still compiles, but metrics change, so line breaks and page count change too. Typst's bundled fonts are Libertinus Serif, New Computer Modern and DejaVu Sans Mono. `Linux Libertine` was renamed and no longer exists.

The exception is a fallback chain written to work across systems, where missing names are expected. Then confirm with `pdffonts` that the document used the fonts you meant.

For a variable font, use the family name without "Variable", "Var" or "VF". On Windows, `Segoe UI Variable` is an unknown family, while `Segoe UI` works.

For a document that must look the same everywhere, keep the fonts with the project and compile against them:

```bash
typst compile --font-path fonts doc.typ
typst fonts --font-path fonts
```

### Italics need an italic font file

If the family has no italic face, `style: "italic"` gives no warning and no true italic: a regular-only family rendered from its regular file. Check with `typst fonts --variants`, and avoid italics rather than ship a substitute in a formal document.

## Build and metadata

### A failed compile leaves the old PDF in place

`typst compile` exits non-zero and does not touch the existing output. A script that ignores the exit code, or a reader who just opens the file, sees the stale version with no sign of failure. Check the exit code, and fail any build script on it.

### `document(date:)` decides reproducibility

| Setting | Result |
|---|---|
| `date: auto` (default) | Current time, so the bytes change on every build |
| `date: none` | No `CreationDate` or `ModDate`, which legacy document parsers can reject |
| `date: datetime(year: 2026, month: 1, day: 2)` | Fixed dates and byte-identical rebuilds |

Pin the date when the PDF is committed or uploaded to a parser, and update it when the content changes. `--creation-timestamp` or `SOURCE_DATE_EPOCH` does the same from the command line.

### File paths must use forward slashes

Since 0.15, `image("images\photo.png")` is an error even on Windows. Use `/` in every Typst path.

## Fitting a page budget

Spacing changes accumulate: 2pt repeated across twenty entries adds a page without any warning. After every layout edit, confirm the page count, for example with `check-pdf.py --pages 2`.

When the document overflows:

1. Cut the lowest-value content first.
2. Then trim spacing nobody asked for, such as section padding and decorative rules.
3. Keep the spacing hierarchy and body size intact. Shrinking type or flattening gaps to fit produces a page that looks crowded and reads worse.
