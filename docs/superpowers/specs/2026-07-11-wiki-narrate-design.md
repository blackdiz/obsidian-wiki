# wiki-narrate Design

## Purpose

Add a standalone `wiki-narrate` skill that turns the knowledge already compiled in an Obsidian vault into a readable Markdown narrative. It fills the output-layer gap between `wiki-query` (answers) and `wiki-synthesize` (creates knowledge pages), without adding facts that the vault does not support.

## Scope

The first release supports one input selector: a topic. It produces Markdown only and offers three canonical voices:

- `briefing` — a conclusion-first readout for fast orientation and decisions.
- `plain-language` — an accessible explanation with defined terms and short prose.
- `lecturer` — a progressive teaching readout from context through implications.

The skill presents its result in the conversation by default. It saves a derived Markdown view only when the user passes `--save`.

The first release does not support tag or page-list selection, HTML generation, slide generation, renderer handoffs, voice aliases, or writing new knowledge pages.

## Invocation

```text
/wiki-narrate <topic> [--voice briefing|plain-language|lecturer] [--save]
```

- The default voice is `briefing`.
- Voice values are canonical and case-sensitive. Unsupported values result in a short validation error listing the three supported values.
- `--save` writes the finished readout to `_readouts/<slug>.md`; without it, no readout file is created.

## Files and Integration Points

Create the following files:

```text
.skills/wiki-narrate/SKILL.md
.skills/wiki-narrate/references/voices.md
```

Update these existing documents:

- `AGENTS.md` — add `wiki-narrate` to the skill-routing table.
- `README.md` — add `wiki-narrate` to the skills table.

`wiki-narrate` remains independent from `wiki-query`. It repeats the relevant retrieval conventions instead of invoking another skill, preserving `wiki-query`'s read-only contract and making the new skill usable by agents that cannot chain skills.

## Retrieval and Narrative Flow

1. Resolve the vault configuration through the shared Config Resolution Protocol, including inline `@name` routing, and read the target vault's `AGENTS.md` when it exists.
2. Read `hot.md` and `index.md`; use titles, tags, summaries, and optional QMD results to identify topic candidates before opening page bodies.
3. Apply the existing visibility-filter rule when the request asks for public-only or user-facing output. Never read, cite, or expose filtered pages.
4. Read only the relevant sections of the strongest candidates, then read full pages only where needed to establish a claim or resolve a conflict.
5. Build a claim ledger before drafting. Each entry records the claim text, supporting vault page(s), and one of three statuses: supported fact, inferred connection, or ambiguous/conflicted.
6. Select the requested voice skeleton and draft from that ledger. The voice can alter order and prose, but cannot alter the ledger's factual boundary.
7. Audit the draft: every factual sentence needs an adjacent vault citation; inferred language needs `^[inferred]`; unresolved disagreement needs `^[ambiguous]`.
8. Return the readout. If `--save` is set, write the same Markdown to `_readouts/<slug>.md`, then update `log.md` and `hot.md`; otherwise append only the narration event to `log.md`.

## Output Format

All readouts contain:

1. A title naming the topic and selected voice.
2. Voice-specific sections from `references/voices.md`.
3. Adjacent citations using the configured `OBSIDIAN_LINK_FORMAT`.
4. A `## Coverage` footer listing cited pages, the count of inferred statements, and known evidence gaps.

The voice skeletons are:

| Voice | Sections |
| --- | --- |
| `briefing` | Executive Summary; Key Evidence; Implications; Open Questions |
| `plain-language` | What This Means; Key Ideas; How the Pieces Fit; What We Still Do Not Know |
| `lecturer` | Context; Core Concepts; How It Works; Implications and Limits; Recap |

When saved, a readout begins with frontmatter containing `title`, `topic`, `voice`, `sources`, `created`, and `updated`. `_readouts/` is an underscore-prefixed derived-view directory: saved files are not inserted into `index.md`, `.manifest.json`, or the knowledge graph.

## Citation and Safety Rules

- A factual claim must be followed by at least one citation to a vault page supporting it.
- A cross-page interpretation or connective claim must be marked `^[inferred]` and cite the source pages it connects.
- An unresolved source conflict must be marked `^[ambiguous]` and cite each conflicting page.
- The skill must not draw on web knowledge, model memory, or invented examples to fill evidence gaps.
- If evidence is insufficient, it must omit the claim and describe the gap in the coverage footer.
- Existing page lifecycle annotations and freshness information are preserved when relevant; the skill does not upgrade page trust on its own.

## Failure Handling

- No matching pages: explain that the vault lacks material for the topic; create no readout file even if `--save` was requested.
- Insufficient or contradictory evidence: produce only the supported portion, label ambiguity, and list gaps.
- Missing `_readouts/` directory: create it only for a successful `--save` output.
- QMD unavailable or unconfigured: fall back to the standard index and `rg` retrieval path.
- Write failure after successful drafting: return the readout in conversation, report that saving failed, and do not update `hot.md` as though the file was saved.

## Validation

The implementation must be checked with fixture vault content covering three cases:

1. A well-covered topic produces each of the three voices with the correct section structure and adjacent citations for all factual sentences.
2. Two source pages that disagree produce no unmarked resolution; the disagreement is labeled `^[ambiguous]`.
3. A missing topic reports the absence safely and does not create a `_readouts/` file.

Additionally, inspect the new `SKILL.md` for configuration compatibility, canonical voice validation, correct exclusion of `_readouts/` from the graph, and exact routing/table documentation changes.

## Non-Goals

- Rendering HTML, PDF, or slides.
- Calling third-party renderer skills.
- Creating or updating compiled knowledge pages.
- Adding tag, page-list, prior-query, or prior-research input modes.
- Supporting natural-language voice aliases.
