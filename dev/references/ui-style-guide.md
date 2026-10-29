# UI Style Guide — TEMPLATE

> FILL IN with project facts verified against current source. Delete this
> notice when the template is filled. The rules below are the generic gate;
> the tables describe the project's actual tokens and primitives.

## Approved visual language

<!-- Describe the primary surface's approved style: typography scale, spacing system, color model, border-radius scale, shadow policy. This is what "preserving the approved style" means for this project. Do not redesign it unless the task explicitly requests a redesign. -->

## Theme tokens

| Token | Meaning | Notes |
| --- | --- | --- |
| <!-- e.g. --text-primary --> |  |  |

Rules:

- New colors always go through the token contract — never introduce a new semantic variable spelling alongside an existing one.
- Hardcoded literals are exceptions to be reviewed (see `niche_ui_style.md`), not patterns to copy.
- Non-theme fallbacks (e.g. `var(--x, #hex)` where `--x` is undefined) are bugs, not graceful degradation.

## Shared primitives

| Primitive | Location | Used by |
| --- | --- | --- |
| <!-- e.g. settings card / feedback / scroll --> |  |  |

Rules:

- Shared base styles live in one shared stylesheet; a subsystem only adds named modifiers, never a copy of the whole primitive.
- New shared base styles go into the shared file, not back into one consumer.
- Named classes over inline layout styles; data-driven inline styles (computed percentages) are acceptable.

## Style change gate

Before changing styles in any surface:

1. inspect the primary surface only to understand the approved visual language;
2. compare all surfaces that use the same primitive;
3. identify whether the rule belongs in the theme tokens, shared CSS, parent shell, or one component;
4. reuse semantic variables and established patterns;
5. make one narrow consistency pass and verify it structurally and, when possible, visually.

## Accessibility

<!-- Forced-colors / high-contrast handling, focus visibility, minimum interactive sizes — the project's accepted exceptions and their reasons. -->

## Visual verification

<!-- How appearance is verified: which windows/sizes/themes to inspect; any screenshot capture scripts and what they cover. Type/build checks do not prove appearance. -->
