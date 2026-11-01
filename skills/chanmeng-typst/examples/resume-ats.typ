// ATS-safe resume: one column, real headings, no images, delimited text.
// Rules and verification: references/ats-resume.md
// Compile: typst compile resume-ats.typ
// All details below are fictional sample data.

#set document(
  title: "Alex Rivera - Resume",
  author: "Alex Rivera",
  date: datetime(year: 2026, month: 1, day: 15),
)
#set page(paper: "a4", margin: 1.6cm, header: none, footer: none)
#set text(font: "Libertinus Serif", size: 10pt, fill: black, hyphenate: false)
#set par(leading: 0.68em, spacing: 0.9em)
#set list(marker: [-], spacing: 1.2em)
#set smartquote(enabled: false)

// Stops a line break at a hyphen, which extraction would turn into a lost hyphen.
#show regex("[\w.]+(-[\w.]+)+"): it => box(it)
#show link: underline

#show heading.where(level: 1): it => block(above: 18pt, below: 7pt, breakable: false, sticky: true, {
  set text(size: 10.5pt, weight: "bold")
  set block(above: 0pt, below: 3pt)
  it
  line(length: 100%, stroke: 0.5pt + black)
})

// One spacing scale: wrapped line < bullet < entry < section.
#let gap-entry = 14pt
#let gap-intra = 6pt

#let role(title: "", org: "", location: "", dates: "", bullets: ()) = block(
  above: 0pt,
  below: gap-entry,
  {
    block(above: 0pt, below: gap-intra, breakable: false, sticky: true)[
      #strong(title) \
      #org | #location | #dates
    ]
    for item in bullets { list.item(item) }
  },
)

#text(size: 16pt, weight: "bold")[Alex Rivera] \
Senior Software Engineer \
Wellington, New Zealand | +64 21 000 0000 | alex.rivera\@example.com | #link("https://github.com/example")[github.com/example]

= Summary

Full-stack engineer with eight years of experience building multi-tenant web platforms. Led a team of four and cut \~35% of page load time on a high-traffic product.

= Skills

*Languages:* TypeScript, Python, Go, SQL \
*Platforms:* AWS, Kubernetes, PostgreSQL, Redis \
*Practices:* CI/CD, observability, accessibility (WCAG 2.2), open-source maintenance

= Experience

#role(
  title: "Senior Software Engineer",
  org: "Example Systems",
  location: "Wellington",
  dates: "Mar 2022 - Present",
  bullets: (
    [Scope: led a team of four across the customer-facing web platform.],
    [Migrated a single-tenant service to a multi-tenant architecture serving 120 customers.],
    [Reduced median page load time by \~35% through server-side rendering and caching.],
  ),
)

#role(
  title: "Software Engineer",
  org: "Sample Labs",
  location: "Auckland",
  dates: "Jun 2018 - Feb 2022",
  bullets: (
    [Scope: one of six engineers on the billing product.],
    [Built a real-time reporting pipeline processing 2 million events a day.],
  ),
)

= Education

*BSc in Computer Science*, Example University | 2014 - 2017

= Certifications

AWS Certified Solutions Architect - Associate | 2023
