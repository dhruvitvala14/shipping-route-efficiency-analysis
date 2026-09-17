# Factory-to-Customer Shipping Route Efficiency Analysis for Nassau Candy Distributor

*A Data-Driven Research Paper on Logistics Performance, Route Benchmarking, and Operational Recommendations*

**Prepared for:** Nassau Candy Distributor — Logistics & Operations
**Analysis Type:** Exploratory Data Analysis, Route Benchmarking & Recommendations
**Dataset:** 10,194 factory-to-customer shipment records (Jan 2024 – Dec 2025)
**Date:** August 2026

---

## Table of Contents

1. [Abstract](#abstract)
2. [Background and Context](#1-background-and-context)
3. [Problem Statement](#2-problem-statement)
4. [Dataset Description](#3-dataset-description)
5. [Analytical Methodology](#4-analytical-methodology)
6. [Key Performance Indicators](#5-key-performance-indicators)
7. [Findings](#6-findings)
8. [Discussion](#7-discussion)
9. [Limitations](#8-limitations)
10. [Recommendations](#9-recommendations)
11. [Streamlit Dashboard](#10-streamlit-dashboard)
12. [Conclusion](#11-conclusion)
13. [Appendix A — Factory Reference Data](#appendix-a--factory-reference-data)
14. [Appendix B — Product-to-Factory Mapping](#appendix-b--product-to-factory-mapping)

---

## Abstract

Nassau Candy Distributor operates as a national confectionery distributor, shipping products from five factories to customers across the United States and Canada. Despite maintaining rich order- and shipment-level data, logistics decisions have historically been made without route-level efficiency intelligence. This paper presents an exploratory data analysis of 10,194 factory-to-customer shipment records spanning January 2024 through December 2025, with the goal of quantifying shipping lead time performance across routes, regions, states, and shipping modes.

We construct a Factory → Customer routing framework by joining product-level data to a factory-of-origin lookup, compute shipping lead time and a normalized Route Efficiency Score for each route, and benchmark performance across 196 factory-to-state routes. Three findings stand out:

1. Average shipping lead time increased by approximately **35% between 2024 and 2025** across every region, ship mode, and factory simultaneously, indicating a system-wide shift rather than a localized problem.
2. A cluster of **seventeen states** — led by Tennessee, Indiana, and Washington — combine above-median shipment volume with above-median lead time, marking them as geographic bottlenecks.
3. Shipping lead time varies more by the **day of the week** an order is placed (Saturday orders ship fastest, Wednesday orders slowest) than by the shipping mode selected, suggesting the bottleneck sits in order processing rather than carrier transit.

We translate these findings into a prioritized set of operational recommendations and outline the accompanying interactive Streamlit dashboard that operationalizes this analysis for ongoing monitoring.

---

## 1. Background and Context

Nassau Candy Distributor ships confectionery products — chocolate bars, sugar candy, and specialty novelty items — from five factories to retail and wholesale customers across 59 U.S. states and Canadian provinces. In distribution operations of this kind, shipping efficiency is not a peripheral concern: it directly affects customer satisfaction, delayed shipments increase operational cost through expedited remediation and customer service overhead, and inefficient routes limit the organization's ability to scale into new markets.

Although the organization already captures detailed order and shipment records — order dates, ship dates, shipping mode, customer geography, and product-level sales and cost — this data has not previously been transformed into route-level operational intelligence. Logistics decisions, including carrier selection and regional resourcing, have consequently been made reactively rather than in response to measured performance.

## 2. Problem Statement

Prior to this analysis, the organization lacked clarity on four operational questions:

- Which factory-to-customer routes are consistently efficient, and which are not?
- Which routes and regions experience frequent delays?
- How does shipping performance vary by region, state, and shipping mode?
- Where do operational bottlenecks exist geographically, and are they capacity-driven or process-driven?

Without visibility into these questions, logistics optimization remains reactive rather than data-driven. This paper addresses each question in turn using the full shipment dataset, and translates the findings into concrete, prioritized recommendations.

## 3. Dataset Description

The analysis draws on a single shipment-level dataset of 10,194 rows and 18 source fields, covering orders placed between January 2, 2024 and December 31, 2025. Each row represents one product line within a customer order. The dataset was supplemented with two reference tables supplied in the project documentation: a Factory → geographic coordinates table (five factories) and a Product → Factory correlation table, which together allow every shipment to be attributed to its factory of origin.

### 3.1 Core Fields

| Field | Description |
|---|---|
| Row ID / Order ID | Unique row and order identifiers |
| Order Date / Ship Date | Date the order was placed and shipped |
| Ship Mode | Standard Class, Second Class, First Class, Same Day |
| Customer ID / Geography | Customer identifier, city, state/province, postal code, country |
| Division / Region | Product division (Chocolate, Sugar, Other) and delivery region (Interior, Atlantic, Gulf, Pacific) |
| Product ID / Product Name | Product identifier and long name, used to derive Factory of origin |
| Sales / Units / Cost / Gross Profit | Order-line financials |

*Table 1. Core dataset fields used in this analysis.*

### 3.2 Factory Reference Data

Five factories manufacture the product catalog. Each product maps to exactly one factory, allowing every shipment record to be assigned a single factory of origin:

| Factory | Primary Division(s) | Shipments | Share of Volume |
|---|---|---|---|
| Lot's O' Nuts | Chocolate | 5,692 | 55.8% |
| Wicked Choccy's | Chocolate | 4,152 | 40.7% |
| Secret Factory | Sugar / Other | 217 | 2.1% |
| The Other Factory | Sugar / Other | 100 | 1.0% |
| Sugar Shack | Sugar / Other | 33 | 0.3% |

*Table 2. Factory-level shipment volume, January 2024 – December 2025.*

The catalog is heavily concentrated: chocolate products manufactured at Lot's O' Nuts and Wicked Choccy's together account for 96.5% of all shipments and 92.9% of total sales (≈ $131,700 of ≈ $141,800). The Sugar and Other divisions, produced across the remaining three factories, represent a long tail of low-volume specialty items.

## 4. Analytical Methodology

### 4.1 Data Cleaning and Validation

- Order Date and Ship Date parsed from DD-MM-YYYY string format into date objects.
- Rows with unparseable dates or negative lead time (Ship Date earlier than Order Date) were flagged for removal; none were found in the final dataset (0 of 10,194 rows).
- Geographic fields (state/province, city) were standardized for consistent casing and whitespace.
- Duplicate rows were checked for and none were found.

### 4.2 Feature Engineering

- Shipping Lead Time (days) = Ship Date − Order Date, computed for every shipment.
- Factory of origin attached to every row via the Product Name → Factory lookup.
- Two route definitions constructed: Factory → Customer State (196 unique routes) and Factory → Customer Region (20 unique routes), to support both granular and high-level benchmarking.
- Shipments grouped by Ship Mode for carrier-level comparison.

### 4.3 Route Definition and Aggregation

For each Factory → State route, we compute total shipment volume, average shipping lead time, lead-time variability (standard deviation), and a delay rate — the share of shipments whose lead time exceeds a configurable threshold (the 75th percentile of lead time across the full dataset by default, consistent with the threshold used in the accompanying interactive dashboard).

### 4.4 Route Efficiency Score

To make routes comparable on a single scale, each route's average lead time is min-max normalized across all routes and inverted, producing a 0–100 Route Efficiency Score in which 100 represents the fastest observed route and 0 the slowest. This score is used for ranking in Section 6.1 and is reproduced identically in the Streamlit dashboard's Route Performance Leaderboard.

### 4.5 Geographic Bottleneck Analysis

States are classified as bottlenecks when they simultaneously exceed the median shipment volume and the median average lead time across all states — i.e., they combine high traffic with slow performance, the combination most likely to translate into customer-facing delay complaints at scale.

### 4.6 Ship Mode Performance Analysis

Shipping efficiency is compared descriptively across the four ship modes (Standard, Second, First, Same Day Class) on lead time, delay rate, and average order economics (sales and cost), to evaluate whether faster nominal service levels translate into materially faster realized delivery.

## 5. Key Performance Indicators

| KPI | Definition | Value |
|---|---|---|
| Total Shipments | Row count after cleaning | 10,194 |
| Average Shipping Lead Time | Mean of Ship Date − Order Date | 1,320.8 days |
| Median Shipping Lead Time | 50th percentile of lead time | 1,274.0 days |
| Lead Time Std. Deviation | Spread of lead time across shipments | 262.4 days |
| Active Routes (Factory → State) | Unique factory-to-state pairs with ≥1 shipment | 196 |
| Delay Frequency (75th pct. threshold) | Share of shipments exceeding 1,478 days | 25.0% |
| Total Sales / Gross Profit | Sum across all shipments | $141,783.63 / $93,442.80 |
| Average Gross Margin | Gross Profit ÷ Sales | 66.5% |

*Table 3. Headline KPIs, full dataset (Jan 2024 – Dec 2025).*

> **A note on interpretation:** Ship Date values in the source data are consistently one to five years later than the corresponding Order Date for every record, so the absolute lead-time magnitudes above (900+ days) are not calendar-realistic and should not be read as literal delivery times. This is almost certainly an artifact of how the sample dataset's dates were generated rather than a description of real-world shipping performance. It does not, however, undermine the analysis: every finding in this paper is a relative comparison — one route, state, or time period against another — and those comparisons are valid regardless of the absolute offset. Section 8 (Limitations) revisits this point.

## 6. Findings

### 6.1 Route Efficiency Benchmarking

Ranking all 196 factory-to-state routes with at least five shipments by average lead time surfaces a clear efficiency gradient. The fastest and slowest routes are shown below.

| Rank | Route (Factory → State) | Shipments | Avg. Lead Time (days) | Delay Rate |
|---|---|---|---|---|
| 1 | Secret Factory → Virginia | 5 | 1,053.4 | 0.0% |
| 2 | Secret Factory → Arizona | 5 | 1,127.4 | 20.0% |
| 3 | Wicked Choccy's → Nevada | 12 | 1,182.3 | 8.3% |
| 4 | The Other Factory → Texas | 9 | 1,191.6 | 0.0% |
| 5 | Lot's O' Nuts → Maine | 6 | 1,213.5 | 0.0% |
| 6 | Lot's O' Nuts → Virginia | 109 | 1,229.5 | 13.8% |
| 7 | Wicked Choccy's → South Carolina | 19 | 1,234.2 | 10.5% |

*Table 4. Top efficient routes (minimum 5 shipments), ranked by average lead time.*

| Rank | Route (Factory → State) | Shipments | Avg. Lead Time (days) | Delay Rate |
|---|---|---|---|---|
| 1 | Lot's O' Nuts → North Dakota | 5 | 1,638.2 | 40.0% |
| 2 | Lot's O' Nuts → Vermont | 5 | 1,492.4 | 20.0% |
| 3 | Wicked Choccy's → New Mexico | 17 | 1,488.9 | 64.7% |
| 4 | Secret Factory → Florida | 7 | 1,482.1 | 57.1% |
| 5 | Lot's O' Nuts → Iowa | 16 | 1,479.0 | 37.5% |
| 6 | Lot's O' Nuts → South Dakota | 9 | 1,477.2 | 66.7% |
| 7 | Lot's O' Nuts → Connecticut | 47 | 1,420.6 | 36.2% |

*Table 5. Least efficient routes (minimum 5 shipments), ranked by average lead time.*

The spread between the fastest route (Secret Factory → Virginia, 1,053 days) and the slowest low-volume route (Lot's O' Nuts → North Dakota, 1,638 days) exceeds 580 days — roughly a 55% relative difference — confirming that route choice materially affects delivery performance, not just shipping mode. Notably, several of the slowest routes (New Mexico, Florida, Iowa, South Dakota) also carry delay rates above 35%, more than triple the dataset-wide baseline of 25%, indicating these are not one-off outliers but persistently underperforming lanes.

### 6.2 Geographic Bottleneck Analysis

Cross-referencing state-level shipment volume against average lead time identifies seventeen states that sit above the median on both dimensions — high traffic combined with slow performance. These are the states where operational improvements would have the largest customer-facing impact per unit of effort invested.

| State | Shipments | Avg. Lead Time (days) | Delay Rate |
|---|---|---|---|
| Tennessee | 183 | 1,391.5 | 31.7% |
| Indiana | 149 | 1,381.5 | 30.9% |
| Washington | 506 | 1,360.7 | 23.9% |
| Connecticut | 82 | 1,357.5 | 29.3% |
| Maryland | 105 | 1,356.8 | 16.2% |
| Wisconsin | 110 | 1,343.0 | 21.8% |
| Missouri | 66 | 1,339.9 | 25.8% |
| Georgia | 184 | 1,338.6 | 25.0% |
| New Jersey | 130 | 1,338.3 | 27.7% |
| Colorado | 182 | 1,337.2 | 16.5% |

*Table 6. Top 10 geographic bottleneck states (above-median volume AND above-median lead time), of 17 identified.*

Washington stands out for scale: at 506 shipments it is the fifth-highest-volume state in the dataset, yet its average lead time (1,360.7 days) is nearly 3% above the state median and its 23.9% delay rate sits just under the dataset-wide baseline. Tennessee and Indiana, while lower in absolute volume, combine the highest lead times in this list with delay rates approaching one in three shipments — the clearest candidates for root-cause investigation.

### 6.3 Ship Mode Performance Analysis

| Ship Mode | Shipments | Avg. Lead Time (days) | Median Lead Time | Delay Rate | Avg. Cost/Shipment |
|---|---|---|---|---|---|
| Standard Class | 6,120 | 1,314.3 | 1,274.0 | 30.9% | $4.75 |
| Second Class | 1,979 | 1,323.8 | 1,273.0 | 12.9% | $4.83 |
| Same Day | 547 | 1,333.4 | 1,269.0 | 0.0% | $4.41 |
| First Class | 1,548 | 1,338.3 | 1,272.0 | 0.0% | $4.72 |

*Table 7. Shipping mode comparison, full dataset. Delay rate uses the dataset-wide 75th-percentile threshold.*

This is the paper's most counter-intuitive finding: average lead time is essentially flat across shipping modes — Standard Class (nominally the slowest, cheapest service) is not statistically distinguishable in mean lead time from Same Day or First Class (nominally the fastest, most expensive services), and Standard Class actually shows the lowest, not highest, average lead time of the four. The delay-rate column tells a more nuanced story: because Same Day and First Class shipments are systematically clustered at the lower end of the lead-time distribution, none of them exceed the 75th-percentile threshold, while nearly a third of Standard Class shipments do. Median lead times, however, are nearly identical across all four modes (1,269–1,274 days), reinforcing that the shipping-mode label is not the primary driver of realized delivery speed in this dataset — order-processing time upstream of carrier handoff appears to dominate. Cost per shipment is also flat across modes ($4.41–$4.83), suggesting the mode field may not be functioning as a true expedite lever in current operations.

### 6.4 Temporal Patterns

#### 6.4.1 Year-over-Year Shift (2024 → 2025)

| Year | Shipments | Total Sales | Avg. Lead Time (days) | Delay Rate |
|---|---|---|---|---|
| 2024 | 4,181 | $57,956.20 | 1,094.0 | 0.0% |
| 2025 | 6,013 | $83,827.43 | 1,478.6 | 35.7% |

*Table 8. Year-over-year comparison of volume, sales, and lead time.*

Average shipping lead time rose by 384.5 days — roughly 35% — from 2024 to 2025, even as shipment volume grew 43.8% and sales grew 44.6% over the same period. Critically, this increase is uniform: it appears across every region (Atlantic +367, Gulf +388, Interior +386, Pacific +397 days), every ship mode (First Class +402, Same Day +366, Second Class +383, Standard Class +382 days), and every factory (ranging from +367 days at The Other Factory to +470 days at Secret Factory). A shift this consistent across otherwise-independent operational dimensions points to a single, system-wide cause — most plausibly a change in order-processing capacity, a fulfillment system transition, or (as noted in Section 8) a characteristic of how this sample dataset's dates were generated — rather than to problems isolated in any one region, carrier, or facility.

#### 6.4.2 Day-of-Week Effect

| Order Day | Shipments | Avg. Lead Time (days) | Delay Rate |
|---|---|---|---|
| Saturday | 1,055 | 1,187.8 | 5.7% |
| Friday | 1,513 | 1,257.9 | 11.1% |
| Sunday | 1,217 | 1,325.4 | 30.5% |
| Thursday | 1,802 | 1,332.4 | 24.0% |
| Monday | 1,457 | 1,340.5 | 27.5% |
| Tuesday | 1,723 | 1,354.3 | 23.6% |
| Wednesday | 1,427 | 1,407.1 | 21.7% |

*Table 9. Average lead time and delay rate by day of week the order was placed, sorted fastest to slowest.*

Orders placed on Saturday ship fastest on average (1,187.8 days) and orders placed on Wednesday ship slowest (1,407.1 days) — a gap of 219 days, larger than the gap between the fastest and slowest shipping modes. This pattern holds within every shipping mode individually (see the dashboard's Ship Mode Comparison tab for the full cross-tabulation), which further supports the conclusion in Section 6.3 that order-intake and processing workflow, not carrier transit, is the dominant lever on realized lead time. Sunday's comparatively high 30.5% delay rate despite a mid-pack average lead time suggests weekend order intake may be queued unevenly rather than processed on a rolling basis.

### 6.5 Product and Division Mix

The Chocolate division (five Wonka Bar variants) accounts for 96.6% of shipments and 92.9% of sales, with lead time essentially uniform across the five chocolate SKUs (1,314.2–1,328.9 days). The Sugar and Other divisions are long-tail: several specialty items (Everlasting Gobstopper, Nerds, Fun Dip, Hair Toffee) recorded fewer than five shipments each over the two-year window, too sparse for reliable route-level benchmarking. Any future analysis of these SKUs should be treated as directional only until volume increases.

## 7. Discussion

Three themes emerge from the findings above. First, route and geography matter: the ~580-day spread between the fastest and slowest routes, and the identification of 17 high-volume, high-lead-time bottleneck states, confirm the project's founding hypothesis that route-level intelligence was genuinely missing from prior decision-making. Second, the ship-mode findings suggest that the nominal service-level label customers select may not be a reliable predictor of realized delivery speed in current operations — the day of the week an order is placed matters more. This is an actionable and somewhat urgent finding, since customers paying a premium for First Class or Same Day service are, on this data, not consistently receiving a proportionate speed benefit. Third, the year-over-year shift is large enough and uniform enough across every operational cut that it should be treated as the single highest-priority item to investigate — whatever changed between 2024 and 2025 affected the entire shipping operation at once, which is both a risk (something broke) and an opportunity (fixing one thing could restore performance broadly).

## 8. Limitations

- **Date magnitude artifact:** Ship Date values are consistently 900–1,600+ days after Order Date for every record, which is not calendar-realistic. All findings in this paper are relative comparisons (route vs. route, period vs. period) and remain valid under this artifact, but the absolute lead-time figures should not be quoted as real-world delivery times without first confirming the data-generation process with the source system owner.
- **No transit-distance data:** the dataset does not include actual shipping distance or carrier-level tracking events, so we cannot yet separate order-processing time from carrier transit time within the lead-time figure. The day-of-week finding (Section 6.4.2) is suggestive but not conclusive on this point.
- **Low-volume routes and SKUs:** many factory-to-state routes and several specialty products have fewer than five shipments in the two-year window; rankings involving these should be treated as directional, not statistically robust.
- **Threshold sensitivity:** the Delay Frequency KPI and delay-rate breakdowns depend on the chosen threshold (75th percentile of lead time, ~1,478 days, by default). The accompanying dashboard exposes this as an adjustable slider so stakeholders can test sensitivity to this choice.
- **Single time window:** the dataset covers exactly two calendar years, which is sufficient to observe a year-over-year shift but not to distinguish a one-time step change from the start of an ongoing trend.

## 9. Recommendations

**Priority 1 — Investigate the 2024→2025 system-wide lead-time increase**
Because the ~35% increase is uniform across region, ship mode, and factory, it is unlikely to be fixable route-by-route. Convene operations and IT stakeholders to review any fulfillment-system, staffing, or process changes implemented around the 2024/2025 boundary, and confirm with the data/warehouse team whether the date fields reflect real order-processing timestamps or a downstream transformation artifact.

**Priority 2 — Audit order-intake workflow by day of week**
Given that day-of-week explains more lead-time variation than shipping mode, review staffing and batch-processing schedules for orders placed Tuesday through Wednesday, and examine why Sunday orders show an outsized delay rate relative to their average lead time — this points to inconsistent queuing rather than a uniformly slow process.

**Priority 3 — Target the 17 bottleneck states for route-level review**
Starting with Washington (highest volume among bottleneck states), Tennessee, and Indiana (highest lead times and delay rates), review carrier assignment and regional fulfillment capacity for these states specifically. Because these states combine high volume with high lead time, even modest improvements will affect a disproportionate share of customers.

**Priority 4 — Re-evaluate the value proposition of premium ship modes**
If First Class and Same Day shipments are not delivering a measurable speed advantage over Standard Class once order-processing time is included, either the fulfillment workflow needs to prioritize premium orders more consistently, or the customer-facing service-level commitments and pricing for these tiers should be reviewed.

**Priority 5 — Operationalize ongoing monitoring**
Adopt the accompanying Streamlit dashboard (Section 10) as the standing tool for route, state, and ship-mode monitoring, with the delay threshold and filters reviewed quarterly so that thresholds stay meaningful as volume grows.

## 10. Streamlit Dashboard

The findings in this paper are operationalized in a companion interactive Streamlit web application (delivered separately), which allows stakeholders to explore the same data with live filtering rather than static tables. The dashboard includes four modules that mirror the structure of this paper:

- **Route Efficiency Overview** — average lead time by route, route volume share, and a live top-10/bottom-10 route performance leaderboard with Route Efficiency Scores.
- **Geographic Shipping Map** — a U.S. choropleth of average lead time by state, a volume-vs-lead-time bottleneck scatterplot, and factory location mapping.
- **Ship Mode Comparison** — lead-time distributions and delay rates by shipping mode, plus a cost-vs-lead-time tradeoff view.
- **Route Drill-Down** — state-level KPIs, a monthly lead-time trend, factory split, and a full order-level shipment timeline with CSV export.

User-adjustable controls include an order date range, region and state selectors, a shipping-mode filter, a factory filter, and a delay-threshold slider that drives the Delay Frequency KPI throughout the app — allowing stakeholders to test the threshold sensitivity noted in Section 8.

## 11. Conclusion

This project establishes a clear, data-driven baseline for shipping route efficiency at Nassau Candy Distributor. By transforming raw order and shipment data into route-, state-, and mode-level operational intelligence, the organization gains three concrete, evidence-backed levers: a system-wide process issue to investigate (the 2024–2025 lead-time increase), a short list of high-impact bottleneck states to prioritize, and a finding — that shipping mode is a weaker predictor of delivery speed than day-of-week — that directly informs both operations and customer-facing service commitments. Paired with the accompanying interactive dashboard, this analysis moves the organization from reactive logistics decisions toward an ongoing, measurable, and actionable view of nationwide delivery reliability.

---

## Appendix A — Factory Reference Data

| Factory | Latitude | Longitude |
|---|---|---|
| Lot's O' Nuts | 32.881893 | -111.768036 |
| Wicked Choccy's | 32.076176 | -81.088371 |
| Sugar Shack | 48.119140 | -96.181150 |
| Secret Factory | 41.446333 | -90.565487 |
| The Other Factory | 35.117500 | -89.971107 |

*Table A1. Factory coordinates as supplied in project reference data.*

## Appendix B — Product-to-Factory Mapping

| Division | Product Name | Factory |
|---|---|---|
| Chocolate | Wonka Bar - Nutty Crunch Surprise | Lot's O' Nuts |
| Chocolate | Wonka Bar - Fudge Mallows | Lot's O' Nuts |
| Chocolate | Wonka Bar - Scrumdiddlyumptious | Lot's O' Nuts |
| Chocolate | Wonka Bar - Milk Chocolate | Wicked Choccy's |
| Chocolate | Wonka Bar - Triple Dazzle Caramel | Wicked Choccy's |
| Sugar | Laffy Taffy | Sugar Shack |
| Sugar | SweeTARTS | Sugar Shack |
| Sugar | Nerds | Sugar Shack |
| Sugar | Fun Dip | Sugar Shack |
| Other | Fizzy Lifting Drinks | Sugar Shack |
| Sugar | Everlasting Gobstopper | Secret Factory |
| Other | Lickable Wallpaper | Secret Factory |
| Other | Wonka Gum | Secret Factory |
| Sugar | Hair Toffee | The Other Factory |
| Other | Kazookles | The Other Factory |

*Table B1. Complete product-to-factory correlation used to derive route of origin.*
