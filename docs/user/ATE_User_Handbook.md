# Austin Trading Engine User Handbook

Version: 1.0 Draft  
Applies To: Austin Trading Engine v2.2  
Purpose: Simple user guide for reading ATE on a TradingView chart  

---

# 1. What ATE Is

The Austin Trading Engine, or ATE, is a TradingView market analysis indicator.

It is designed to help you understand what the market is doing.

ATE does **not** place trades.

ATE does **not** connect to a broker.

ATE does **not** manage positions.

ATE does **not** guarantee future price movement.

ATE gives you structured information so you can read the chart more clearly.

---

# 2. The Main Idea

ATE looks at the market through several separate engines:

- TrendEngine
- StructureEngine
- MomentumEngine
- VolatilityEngine
- RiskEngine
- ConfidenceEngine
- DashboardEngine

Each engine looks at a different part of the market.

The dashboard box brings those readings together in one place.

The most important rule is:

> ATE gives information.  
> You make the trading decision.

---

# 3. The Moving Average Lines

ATE plots groups of moving averages on the chart.

These help show the direction and strength of the market.

## Fast Moving Averages

The fast lines react quickly to recent price movement.

They are useful for seeing short-term changes.

Fast lines can change direction quickly, so they should not be used alone.

## Medium Moving Averages

The medium lines give a more balanced view.

They are slower than the fast lines but more responsive than the slow lines.

They help show whether short-term movement is becoming more meaningful.

## Slow Moving Averages

The slow lines show the bigger trend.

They are the most important moving averages for understanding the wider market direction.

When price is above the slow lines and the slow lines are rising, the market often has stronger trend support.

When price is below the slow lines and the slow lines are falling, the market often has weaker trend support.

---

# 4. Line Colours

The moving average lines change colour depending on direction.

A rising line suggests that part of the market trend is improving.

A falling line suggests that part of the market trend is weakening.

Do not judge the whole market from one line.

Look at the group of lines together.

---

# 5. The Dashboard Box

The dashboard box is the main control panel for ATE.

It gives a quick summary of the current market condition.

The dashboard is for reading the market.

It does not tell you to buy or sell.

---

# 6. Trend Score

Trend Score shows how strong the current trend evidence is.

Higher values mean the trend evidence is stronger.

Lower values mean the trend evidence is weaker.

Simple guide:

| Trend Score | Plain meaning |
|---:|---|
| 0–20 | Very weak trend |
| 21–40 | Weak trend |
| 41–60 | Mixed trend |
| 61–80 | Strong trend |
| 81–100 | Very strong trend |

A high Trend Score does not mean price must keep rising.

It means the trend evidence is currently strong.

---

# 7. Market State

Market State turns the Trend Score into a plain label.

Examples:

- Strong Bull
- Bull
- Neutral
- Bear
- Strong Bear

This helps you quickly understand the trend condition.

Market State is not a trade instruction.

---

# 8. Structure Score

Structure Score looks at market structure.

It uses swing highs, swing lows, and break-of-structure behaviour.

It helps answer:

> Is the market structure healthy or weakening?

A strong Structure Score means price structure is supporting the move.

A weak Structure Score means structure is poor or breaking down.

---

# 9. Structure State

Structure State gives the Structure Score a plain label.

Examples:

- Bullish Structure
- Leaning Bullish
- Neutral
- Leaning Bearish
- Bearish Structure

This is useful when Trend Score and Structure Score disagree.

For example:

A market may have a strong trend but weakening structure.

That is worth noticing.

---

# 10. Momentum Score

Momentum Score measures whether movement is strengthening or weakening.

It uses momentum-style evidence such as RSI, MACD, and ADX.

Higher Momentum Score means stronger momentum evidence.

Lower Momentum Score means weaker momentum evidence.

Momentum can change faster than trend.

That means it can give early warning, but it can also be noisy.

---

# 11. Momentum State

Momentum State turns the Momentum Score into a plain label.

Examples:

- Strong Momentum
- Bullish Momentum
- Neutral Momentum
- Bearish Momentum
- Weak Momentum

Momentum State helps you see whether the market is gaining or losing force.

---

# 12. Confidence Score

Confidence Score combines Trend, Structure, and Momentum evidence.

It answers:

> Do the main engines agree?

A high Confidence Score means the evidence is aligned.

A low Confidence Score means the evidence is mixed or weak.

Simple guide:

| Confidence Score | Confidence State label |
|---:|---|
| 81–100 | High Confidence |
| 60–80 | Good Confidence |
| 41–59 | Low / Mixed |
| 21–40 | Bearish Confidence |
| 0–20 | Strong Bearish |

These bands match the dashboard label thresholds used by ATE v2.2.

Important:

High confidence does **not** mean low risk.

A market can be high-confidence and high-risk at the same time.

---

# 13. Confidence State

Confidence State gives the Confidence Score a plain label.

Examples:

- High Confidence
- Good Confidence
- Low / Mixed
- Bearish Confidence
- Strong Bearish

This helps you quickly judge whether the main evidence agrees.

---

# 14. Volatility Score

Volatility Score shows the quality of the current volatility condition.

It does not mean bullish or bearish.

It does not mean buy or sell.

It helps answer:

> Is the market quiet, normal, expanding, unstable, or shock-like?

In ATE v2.2, VolatilityEngine is diagnostic only.

That means it is displayed for information and research.

It does not control trades.

---

# 15. Volatility State

Volatility State describes the current volatility regime.

Possible labels include:

- compressed
- normal
- expanding
- elevated
- unstable
- shock
- unknown

## Compressed

The market is quieter than normal.

This may mean price is resting, ranging, or preparing for a larger move.

Compressed does not tell you direction.

## Normal

Volatility is close to its recent baseline.

This is usually the most orderly condition.

## Expanding

Volatility is increasing.

This can happen during stronger movement, but it still does not tell you direction by itself.

## Elevated

Volatility is above normal.

This can mean more opportunity, but also more uncertainty.

## Unstable

Volatility is very high or erratic.

This can make market readings less reliable.

## Shock

A large-range move has occurred.

Shock conditions should be treated with caution.

## Unknown

There is not enough information yet to classify volatility.

This usually happens near the start of the chart history or when data is insufficient.

---

# 16. Volatility Direction

Volatility Direction describes whether volatility itself is changing.

Possible labels include:

- none
- expanding
- contracting
- stable
- unstable

This is about volatility direction, not price direction.

Expanding volatility does not mean the market is bullish.

Contracting volatility does not mean the market is bearish.

---

# 17. Risk Score

Risk Score is different from most other ATE scores.

A higher Risk Score means the diagnostic environment looks more disordered or pressured, not that the market is in a better state.

RiskEngine answers:

> How risky is the current market environment?

Risk Score does not tell you to buy or sell.

Risk Score does not change position size.

Risk Score does not set stops.

Risk Score does not block or approve trades.

In ATE v2.2, RiskEngine is diagnostic only.

Simple guide:

| Risk Score | Risk State label |
|---:|---|
| 75–100 | Extreme |
| 55–74 | Tense |
| 35–54 | Elevated |
| 15–34 | Normal |
| 0–14 | Calm |

These bands match the Risk State thresholds used by ATE v2.2.

The exact label shown on the dashboard is controlled by Risk State.

---

# 18. Risk State

Risk State gives the Risk Score a plain label.

Possible labels include:

- calm
- normal
- elevated
- tense
- extreme
- unknown

## Calm

Risk components are low.

This does not mean the market is safe.

It only means the RiskEngine currently sees low diagnostic pressure.

## Normal

Risk conditions are within a normal range.

## Elevated

One or more risk components are rising.

This is a sign to pay closer attention.

## Tense

Several risk components may be active.

This suggests the market environment is more difficult.

## Extreme

Risk components are strongly active.

This is a caution condition.

## Unknown

RiskEngine does not have enough information to classify the current bar.

---

# 19. Risk Direction

Risk Direction describes the behaviour of risk.

Possible labels include:

- none
- elevated
- conflict
- stable
- indeterminate

Risk Direction is not price direction.

It does not mean bullish or bearish.

It tells you whether the risk environment is rising, conflicted, stable, or unclear.

---

# 20. Risk Reason

Risk Reason gives a short explanation for the current Risk State.

Examples may include:

- Volatility component dominant
- Extension component dominant
- Structure component dominant
- Conflict component active
- Multiple risk components elevated
- Low component pressure

This is one of the most useful dashboard rows.

It tells you what is driving the RiskEngine reading.

---

# 21. Risk Components

RiskEngine uses four diagnostic components.

## Vol Risk Contribution

This shows how much volatility is contributing to the Risk Score.

High volatility pressure can increase the Risk Score.

## Ext Risk Contribution

This measures extension.

It looks at whether the current bar is stretched compared with ATR.

A high extension reading may mean the market is stretched.

## Struct Risk Contribution

This measures structure-related risk.

It looks at swing distance and structure behaviour.

## Conflict Risk Contribution

This shows when parts of the engine disagree.

For example:

- high confidence but difficult risk conditions
- trend and momentum disagreement
- strong movement with weaker supporting evidence

Conflict is not a trade signal.

It is a warning that the picture is not clean.

---

# 22. Smoothed Risk Score

Smoothed Risk Score is the Risk Score after smoothing.

Smoothing helps reduce flickering from bar to bar.

It is the same diagnostic risk reading, just easier to read on the chart.

---

# 23. Signal Markers on the Chart

ATE can show markers on the chart.

These markers are visual information only.

They are not automatic trading instructions.

## Golden Cross

A Golden Cross marker appears when a faster slow moving average crosses above a slower slow moving average.

This can suggest improving trend conditions.

## Death Cross

A Death Cross marker appears when a faster slow moving average crosses below a slower slow moving average.

This can suggest weakening trend conditions.

## ATE Bull

ATE Bull appears when the Trend Score moves into a strong bullish condition.

## ATE Bear

ATE Bear appears when the Trend Score moves into a strong bearish condition.

## Swing High / Swing Low

Small circles mark detected swing highs and swing lows.

These help show market structure.

## BOS

BOS means Break of Structure.

A bullish BOS means price has broken above a recent swing high.

A bearish BOS means price has broken below a recent swing low.

---

# 24. Alerts

ATE includes existing alert conditions for important events such as:

- Golden Cross
- Death Cross
- Strong Bull
- Strong Bear
- Bullish BOS
- Bearish BOS
- Momentum Bullish
- Momentum Bearish
- High Confidence Bull
- Low Confidence Bear

ATE v2.2 does **not** add RiskEngine alerts.

RiskEngine remains diagnostic only.

These are the only alerts ATE v2.2 produces.

---

# 25. Research Mode

Research Mode displays extra information for review and testing.

It is mainly for development, validation, and Hermes research.

Most users do not need Research Mode turned on during normal chart use.

Research Mode can be useful when checking exactly what ATE is outputting.

---

# 26. Simple Daily Use Workflow

A simple way to read ATE:

1. Check the Market State.
2. Check Trend Score.
3. Check Structure Score.
4. Check Momentum Score.
5. Check Confidence Score.
6. Check Volatility State.
7. Check Risk State.
8. Read Risk Reason.
9. Look at the chart itself.
10. Slow down if readings disagree.

Do not use one dashboard row on its own.

ATE works best when you read the whole picture.

---

# 27. Example Reading

Example:

```text
Trend Score: 84
Market State: Strong Bull
Structure Score: 78
Momentum Score: 82
Confidence Score: 81
Volatility State: expanding
Risk State: tense
Risk Reason: Extension component dominant
```

Plain English reading:

The market trend and momentum are strong.

The main evidence agrees.

Volatility is expanding.

However, RiskEngine is warning that the market may be stretched.

That does not mean sell.

It means the market is strong but the environment may require caution.

---

# 28. Another Example Reading

Example:

```text
Trend Score: 48
Market State: Neutral
Structure Score: 52
Momentum Score: 44
Confidence Score: 49
Volatility State: compressed
Risk State: normal
Risk Reason: Low component pressure
```

Plain English reading:

The market is mixed.

Trend, structure, and momentum do not strongly agree.

Volatility is compressed.

Risk pressure is not high, but there is also no clear strong market evidence.

This may be a market to watch rather than act on.

---

# 29. Common Mistakes

## Mistake 1 — Treating Risk Score as a trade signal

Risk Score is not a buy or sell signal.

It is a caution reading.

## Mistake 2 — Thinking high confidence means low risk

High confidence and high risk can happen together.

## Mistake 3 — Thinking volatility is bullish or bearish

Volatility is not direction.

It only tells you about movement conditions.

## Mistake 4 — Trading every marker

Markers are useful information.

They are not automatic trades.

## Mistake 5 — Ignoring timeframe

Daily and weekly charts can disagree.

Always know which timeframe you are reading.

## Mistake 6 — Looking at one row only

ATE is designed to be read as a full dashboard.

Do not rely on one number.

## Mistake 7 — Forgetting diagnostic-only modules

VolatilityEngine and RiskEngine are currently diagnostic-only.

They provide information.

They do not control trades.

---

# 30. Quick Reference Table

| Dashboard item | Plain meaning |
|---|---|
| Trend Score | Strength of trend evidence |
| Market State | Plain label for trend condition |
| Structure Score | Health of market structure |
| Structure State | Plain label for structure |
| Momentum Score | Strength of movement force |
| Momentum State | Plain label for momentum |
| Confidence Score | Agreement between main engines |
| Confidence State | Plain label for confidence |
| Volatility Score | Quality of volatility condition |
| Volatility State | Current volatility regime |
| Vol Direction | Whether volatility is changing |
| Risk Score | Amount of caution present |
| Risk State | Plain label for market-risk condition |
| Risk Direction | Whether risk is rising, conflicted, stable, or unclear |
| Risk Reason | Main reason for the risk reading |

---

# 31. What ATE Does Not Do

ATE does not:

- guarantee profit
- predict the future
- place trades
- connect to a broker
- manage positions
- calculate account risk
- decide position size
- set stop losses
- issue financial advice
- replace your judgement

ATE is a market analysis tool.

---

# 32. Best Practice

Use ATE as a structured reading tool.

Ask:

```text
What is the trend?
What is the structure?
What is momentum doing?
Do the engines agree?
What is volatility doing?
What is risk doing?
Does the chart confirm the dashboard?
```

If the answers are mixed, slow down.

If the answers are clear, still manage risk carefully.

---

# 33. Final Reminder

ATE is designed to help you read the market more clearly.

It is not designed to make decisions for you.

The dashboard gives evidence.

The trader remains responsible for the decision.