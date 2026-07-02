# DashboardEngine

## Purpose

Render the full state of the Austin Trading Engine on the chart for human inspection.

## Status

Specification draft. Implementation pending.

## Inputs

- Outputs from every other engine
- Dashboard layout preferences
- Theme and information density settings

## Outputs

- On-chart panels and labels
- Status table summarising engine reads
- Optional alert condition exports

## Method (placeholder)

A composite of small tables and coloured cells. No data is invented by the dashboard — every cell reflects a value produced by another engine.

## Constraints

- No repainting.
- Bar-close only.
- Read-only: never publishes decisions, only displays them.

## Version

`0.1.0-spec`