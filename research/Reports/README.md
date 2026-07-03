# Austin Trading Research Reports

This folder stores human-readable Austin Trading research outputs.

Reports are written for Paul Austin, ChatGPT, Hermes, and future Austin Trading Team agents.

## Folder Structure

```text
research/Reports/
├── RDR/
├── Asset_Qualification/
│   ├── Gold/
│   ├── Silver/
│   ├── Equities/
│   ├── FX/
│   ├── Bonds/
│   └── Commodities/
├── Version_Comparisons/
├── Market_DNA/
└── Negative_Findings/
```

## Report Types

| Folder | Purpose |
|---|---|
| `RDR/` | Research Decision Records. |
| `Asset_Qualification/` | Asset suitability grading reports. |
| `Version_Comparisons/` | ATE version-vs-version comparisons. |
| `Market_DNA/` | Market behaviour and structure research. |
| `Negative_Findings/` | Weak, failed, falsified, inconclusive, or operationally rejected research. |

## Reading Order

For a major research result, read in this order:

1. Human report dashboard block.
2. Executive summary.
3. Core metrics and asset ranking tables.
4. Negative findings and limitations.
5. Recommendation.
6. Linked manifest and summary CSV.
7. RDR if the result changed project direction.

## Rules

- Reports must separate evidence, interpretation, recommendation, and decision.
- Negative results must be preserved when they prevent future rework.
- Performance claims must link to a run manifest and summary CSV.
- Hermes may recommend; Paul Austin approves final governance/release decisions.
- No report in this folder authorises live trading, broker connectivity, paper-trading APIs, or autonomous execution.
