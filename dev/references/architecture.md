# Architecture — TEMPLATE

> FILL IN with project facts verified against current source. Delete this
> notice when the template is filled. Record responsibilities, source symbols,
> and invariants — not fragile counts. Split into separate references when a
> section outgrows this file (e.g. `search.md`, `sync.md`).

## Layers

```text
<!-- FILL IN: the project's actual layering, e.g.
UI components → state stores → service/API wrappers → backend commands
→ services → storage/external systems -->
```

## Frontend / client layer

| Module | Responsibility | Key symbols |
| --- | --- | --- |
|  |  |  |

- **State management:** <!-- how state flows; what is a store, what is component-local; hydration rules for backend-loaded state -->
- **API/invoke wrappers:** <!-- where they live, error handling convention, mapping rules -->

## Backend / server layer

| Module | Responsibility | Key symbols |
| --- | --- | --- |
|  |  |  |

- **Startup/shutdown:** <!-- initialization order, unified shutdown path, listener/worker lifecycle: stop signals, join handles, unlisten -->
- **Background workers:** <!-- what runs off the main path, how work is queued/cancelled -->

## Storage

- **Schema owner:** <!-- where schema/migrations live -->
- **Derived data:** <!-- caches, indexes, OCR/derived artifacts — what must be cleaned up when a row is deleted -->
- **Data-safety invariants:** <!-- what must never be silently dropped; migration and cleanup rules -->

## Platform-specific code

<!-- How shared behavior is separated from per-platform implementations. Note the gate: code behind platform cfg/build tags is not compiled locally on another OS; the matching CI job is the only real verification. -->

## Invariants

<!-- Cross-module rules that must hold at all times; each with its source evidence. -->
