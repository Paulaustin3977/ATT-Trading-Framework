# Coding Standards

## Scope

These standards apply to all Pine Script v6 code in this repository. They exist to keep the codebase auditable, explainable, and regression-safe.

## Language and Version

- **Language:** Pine Script v6
- **Style guide basis:** TradingView Pine Script v6 conventions
- **Indentation:** 4 spaces, no tabs

## Naming

| Construct        | Convention             | Example              |
|------------------|------------------------|----------------------|
| Variables        | `snake_case`           | `atr_period`         |
| Constants        | `UPPER_SNAKE_CASE`     | `MAX_BARS_BACK`      |
| Functions        | `camelCase`            | `trendRead()`        |
| User-defined types | `PascalCase`         | `EngineState`        |
| Inputs           | `snake_case`           | `length`             |

## File Layout

Every `.pine` file follows this order:

1. `//@version=6` and `indicator(...)` or `strategy(...)`
2. Imports
3. Constants
4. Inputs
5. Functions
6. Calculations
7. Plots and visuals
8. Alerts

## Hard Rules

1. **No repainting.** `lookahead`, future references, and `barmerge.lookahead_on` are forbidden.
2. **No `security()` calls at lower timeframes for daily decisions.** Higher-timeframe requests must use `request.security()` with explicit tuple returns and never use `barmerge.lookahead_on`.
3. **No magic numbers.** Every numeric literal in a calculation must be a named constant or input.
4. **No silent fallbacks.** If a function can fail, it returns a documented default and logs the condition.
5. **Bar-close only.** Signals are emitted at the close of the bar that produced them.

## Functions

- Each function has a one-line purpose comment.
- Each function has a return-type comment when the type is not obvious.
- Functions do not call `plot()` or `alertcondition()`.

## Comments

- Comments explain **why**, not **what**.
- Comments are in English.
- Each engine block in a file starts with a section header comment.

## Inputs

- Inputs are grouped using `group=`.
- Every input has a sensible default.
- Every input has a tooltip or comment describing its effect.

## Performance

- Avoid recomputing expensive values per bar inside loops.
- Cache rolling calculations in a single pass.

## Testing

- Every behavioural change is paired with at least one regression case in `tests/Regression/`.
- Negative results are recorded, not hidden.