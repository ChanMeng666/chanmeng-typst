# chanmeng-typst

An agent skill that turns document requests into verified PDFs through the Typst CLI. It ships as a Claude Code plugin and marketplace from this one repo. The default branch is `master`.

## Current state

- **Release:** v0.6.0, released 2026-11-01. `CHANGELOG.md` has the history.
- **Tested on:** Typst 0.15.1, the latest official release when this was written. CI pins that version in `.github/workflows/validate.yml`.
- **Not tested:** the unreleased Typst `main` branch. Only its commit list was read.

## Layout

```
.claude-plugin/          plugin.json (holds the version), marketplace.json
.github/scripts/         compile-templates.py
.github/workflows/       validate.yml, the only CI workflow
skills/chanmeng-typst/
  SKILL.md               workflow, decision tree, gotchas, recovery
  references/            loaded on demand; typst-pitfalls.md lists silent bugs
  scripts/               verify-typst.sh, check-pdf.py
  examples/              compiled by CI
  evals/                 4 test cases in the `claude plugin eval` layout
```

## Checks

Run these before opening a PR. CI runs the same checks on Linux with Typst built from source.

```bash
python .github/scripts/compile-templates.py
typst compile --pdf-standard ua-1 skills/chanmeng-typst/examples/resume-ats.typ out.pdf
python skills/chanmeng-typst/scripts/check-pdf.py out.pdf \
  --source skills/chanmeng-typst/examples/resume-ats.typ --ats --pages 1
```

`compile-templates.py` compiles all 9 templates in `references/typst-templates.md`. Compiling cleanly proves little here, because the bugs this skill targets produce no error. To check a layout or CJK claim, render the PDF and look at it, or read `pdffonts` and `pdftotext`.

## Rules

- Test every claim about Typst behaviour on a real compile, and say which version you tested.
- Add new silent bugs to `references/typst-pitfalls.md`. Add a `check-pdf.py` check only when the bug can be detected without false alarms.
- Change a template and its example together. Both `cjk-document` copies must stay in step.
- Keep personal data out of this repo. Examples use invented people, such as Alex Rivera.
- Do not recommend an unmaintained package. Check its version on Typst Universe before naming it.

## Release

1. Branch from `master` and bump the version in `.claude-plugin/plugin.json`.
2. Add a dated section to `CHANGELOG.md`. Update the README if features changed.
3. Open a PR, wait for CI, then squash-merge.
4. Tag `vX.Y.Z` on `master` and create the GitHub release from that changelog section.
5. Install it fresh. A separate config directory leaves the real one untouched:

   ```bash
   CLAUDE_CONFIG_DIR=/some/empty/dir claude plugin marketplace add ChanMeng666/chanmeng-typst
   CLAUDE_CONFIG_DIR=/some/empty/dir claude plugin install chanmeng-typst@chanmeng-typst
   ```

6. Confirm `claude plugin list` shows the new version, then compile an example from the installed copy.

Docs-only changes do not need a version bump.

## Upgrading Typst

1. Upgrade locally. On Windows: `winget upgrade Typst.Typst`.
2. Read the full release notes, not only the highlights.
3. Set `TYPST_VERSION` in `validate.yml`, which also rolls the CI cache.
4. Compile every Typst block in `SKILL.md` and `references/`, plus every example, and look for deprecation warnings.
5. Compare `typst <command> --help` against `references/typst-cli-reference.md`.
6. Compare package versions in the skill against Typst Universe.

## Known limits

- **Line breaks between Chinese characters:** on 0.15.1 they add a visible space. A fix titled "Discard newline spaces adjacent to Chinese/Japanese text" is on Typst `main` but unreleased. When a release includes it, retest, then update `typst-pitfalls.md` and the `check-pdf.py` warning.
- **`check-pdf.py` bold warning:** it infers bold from font names and source patterns, so it is a warning, not a failure.

## Evals

Each case has a prompt and graders. To compare versions, run the same prompt on the new skill and on a snapshot of the old one, then render the outputs.

| Comparison | Result |
|---|---|
| Earlier iteration, new skill against old | 17/17 and 16/17 |
| v0.6.0 against v0.5.1, Chinese report only | 6/6 and 6/6, one run each |

The Chinese report tie is not a score gain. The old skill reached 6/6 only because the model overrode its wrong guidance and used a font that happened to be installed. The new skill reached it by following its own guidance with a portable font chain.
