# Niche UI Style Review Queue — TEMPLATE

> This file records local, low-frequency UI styles and omissions that have not
> reached consensus. It is not a project-wide spec and not a copy template.
> Start it the first time a local exception is found; until then this file can
> hold just the rules below.

## Usage rules

- New work must not reuse a pattern just because this file recorded it.
- Only content confirmed by human review to be generalizable migrates to `ui-style-guide.md`.
- Fix one small verifiable style issue at a time; avoid opportunistic refactoring of the primary surface.
- Item statuses: `待审` (pending review), `接受为局部例外` (accepted local exception), `计划统一` (planned unification), `已处理` (resolved).
- Update items with evidence from current source and actual rendering — never substitute a TODO checkbox for the check.

## Current items

| Status | Scope | Current evidence | Review question |
| ------ | ----- | ---------------- | --------------- |
| 待审 |  |  |  |

## Temporarily accepted but non-generalizable local patterns

Patterns that may have good reasons; do not classify as defects before review. Examples of the kind of entry that belongs here:

- fixed high-contrast/system colors inside forced-colors or contrast media queries;
- black translucent overlays to keep controls visible over arbitrary media;
- fixed semantic syntax colors for code readability;
- geometric values (`50%`, `999px`) for knobs, pills, and full-screen masks;
- inline styles that display actual user-selected data (swatches) or data-driven values.

## Review procedure

1. Pick one table item at a time; compare in default dark, light, and custom themes (screenshots or a real run).
2. Decide whether it belongs to general UI, surface-specific UI, media/content rendering, or an accessibility exception.
3. If generalizable: define the semantics and all consumers first, then update `ui-style-guide.md`.
4. If a local exception: record the reason and boundary in the table.
5. If planned for unification: split into an independent minimal commit with static checks and visual verification.
6. Set status to `已处理` with new source symbols or test/screenshot evidence; never just "looks unified now".

## New item template

```markdown
| 待审 | <page/component> | <direct source or runtime evidence> | <the question a human must decide> |
```

Do not write temporary design ideas, one-off task notes, or unverified guesses into this file.
