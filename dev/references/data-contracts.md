# Data Contracts — TEMPLATE

> FILL IN with project facts verified against current source. Delete this
> notice when the template is filled. Every contract surface listed here must
> change together — this is the checklist a cross-layer change is audited
> against.

## API / IPC commands

| Command/endpoint | Arguments | Result | Errors | Tests |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

Contract surfaces that must stay aligned for each: name, arguments/result types, client wrapper, serialization casing, error handling, and tests.

## Types and serialization

- **Shared types:** <!-- where the single source of truth lives; how frontend/backend types stay in sync -->
- **Casing/serialization:** <!-- the convention (e.g. camelCase via serde rename, snake_case) -->
- **Defaults:** <!-- where defaults are defined and how they propagate -->

## Database / persistence

| Table/store | Owner module | Migrations | Derived data to clean up |
| --- | --- | --- | --- |
|  |  |  |  |

- **Migration rules:** <!-- additive-first policy, backfill behavior, rollback expectations -->
- **Recovery expectations:** <!-- what happens on corruption/repair -->

## Configuration / settings

- **Type definition:** <!-- file -->
- **Defaults:** <!-- file -->
- **Normalization/ranges:** <!-- e.g. numeric limits clamped between min/max; 0 and max values forbidden where they would disable or exhaust resources -->
- **Backward compatibility:** <!-- renamed/legacy keys kept as aliases so existing users keep their settings -->
- **UI + persistence + cross-surface application:** <!-- files that must change together -->

## Events / notifications

| Event | Emitted by | Consumed by | Payload |
| --- | --- | --- | --- |
|  |  |  |  |

## i18n

<!-- Locale files and the type definitions that must change together; the mechanism that prevents missing keys (e.g. a test that scans source for keys). -->
