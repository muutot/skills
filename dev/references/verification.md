# Verification — TEMPLATE

> FILL IN with project facts verified against current source. Delete this
> notice when the template is filled.

## Command matrix

| Purpose | Command | Notes |
| --- | --- | --- |
| Type check |  |  |
| Frontend/unit tests |  |  |
| Backend tests |  |  |
| Lint |  |  |
| Format check |  |  |
| Full verify gate |  |  |
| Local dev run |  |  |
| Local packaging |  |  |

## Test strategy

- **Bug remediation:** run only the unit tests relevant to each minimal fix; cross-layer fixes use both focused test groups; do not run full suites between fixes.
- **Final gate:** after all requested fixes are complete, run the full verify gate once; do not repeat unless later edits or failures require revalidation.
- **Concurrency limits:** <!-- if the test runner has bounded workers, document why and how to override for an experiment; keep test isolation enabled -->

## Build profile policy

<!-- How local build profiles differ from CI/release builds (e.g. local = fast/unoptimized, CI = cached checks, release = extreme optimization). Never reproduce release-only optimization locally when a workflow enables it remotely. -->

## Platform-gated code

<!-- Which code is only compiled on certain OSes; state that the matching CI job is the only real gate for those halves and a green local run is not coverage. -->

## Runtime / visual verification

| Claim type | Verification method | Script/command | Not covered (manual) |
| --- | --- | --- | --- |
| <!-- e.g. native format handling --> |  |  |  |

Report skipped checks and why. Do not convert missing evidence into a passing claim.

## Pre-release gate

<!-- The local gates that must pass before a release (format + check + lint), what is deliberately NOT built locally, and where the actual release build happens (CI workflow). -->
