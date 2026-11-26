# Airtel Telecom Analytics — Viva Study Guide

**Scope note:** This study sheet was prepared from the project notebooks, SQL runbook checkpoints, and validation files. The supplied `Class_A_Group_3_Network_Usage_Professional_Dashboard_Guide.pdf` is the assignment reference; its text could not be extracted with the PDF utilities available in this workspace, so any exact viva questions printed there should be checked directly against that handout.

## Project in one minute

The project analyses a 22,000-subscriber Airtel dataset covering customer attributes, plans, circles, daily network use, recharges, and complaints. The business question is which observable customer and service patterns are associated with churn and where the company can investigate retention. The dashboard has two tabs: **Usage & demand** and **Service quality**. It is descriptive and should not be presented as proving that usage, complaints, or any other feature causes churn.

## Data model and grain

- `customers` is one row per subscriber (`customer_id`); it contains activation, segment, plan, ARPU, and churn fields.
- `circles` maps `circle_id` to circle and region. One circle may link to many customers.
- `plans` maps `plan_id` to plan characteristics. A plan may be current for many customers and appear on many recharges.
- `usage_daily` is one subscriber-day record, linked to a customer by `customer_id`.
- `recharges` is one transaction per row, linked to a customer and plan.
- `complaints` is one ticket per row, linked to a customer.
- `customer_features` is a prepared one-row-per-subscriber analytical table. It combines customer-level aggregates; it is not a raw event table.

Central viva point: identify the unit of analysis before calculating a metric. Customer churn must be counted at customer grain. Ticket counts are at complaint grain, and usage averages may be at usage-record grain unless explicitly aggregated per customer first.

## Key numbers to remember

| Topic | Project checkpoint |
|---|---:|
| Subscribers | 22,000 |
| Churned subscribers | 5,226 (23.75%) |
| Complaint tickets | 26,841 |
| Customers with a complaint | 15,369; churn 25.36% |
| Customers without a complaint | 6,631; churn 20.03% |
| Usage records | 1,326,739, 1 Jan–30 Jun 2025 |
| May mean data per usage record | 1,767.9 MB |
| June mean data per usage record | 1,790.0 MB |
| Churn by recharge-spend quartile | 34.85%, 24.53%, 20.65%, 14.98% from lowest to highest |
| First six circles' cumulative recharge revenue | 36.7% |

The complaint/non-complaint comparison is subscriber-level, using an existence test. Joining customers directly to multiple complaint tickets duplicates subscribers and changes the weighting; the ticket-level churn percentage is not the customer churn rate.

## SQL topics

- **JOIN:** combines related rows; use the correct keys and check whether a one-to-many join changes row count.
- **LEFT JOIN:** preserves all rows on the left, including customers with no usage or no complaint.
- **GROUP BY:** aggregates rows by a category or entity. Aggregate events to customer level before comparing customers.
- **EXISTS:** tests whether at least one matching row exists without multiplying the customer row.
- **CTE:** names a subquery (`WITH ...`) to make a multi-step query easier to read.
- **Window functions:** `ROW_NUMBER`, `NTILE`, and cumulative `SUM() OVER (...)` calculate ranks/bands/running totals while retaining rows.
- **Date functions:** `strftime` groups dates by month; `julianday` supports elapsed-day calculations.
- **Index and query plan:** an index can speed up key lookups; `EXPLAIN QUERY PLAN` reveals a `SEARCH` versus a table `SCAN`. A scan may be reasonable for a condition that matches many rows.
- **NULL handling:** `COUNT(column)` ignores NULL while `COUNT(*)` counts rows. Use `COALESCE` only when zero is the correct meaning; a missing observation is not always zero.

## Statistics and validation

- **Null hypothesis:** no population difference/association for the selected comparison. **Alternative:** a difference/association exists.
- **Significance level:** alpha 0.05 is the decision threshold used in the project. A small p-value is evidence against the null under the model assumptions, not a measure of business importance or the probability that the null is true.
- **Welch t-test:** compares two means without assuming equal variances. Use independent customer-level observations for subscriber comparisons.
- **Two-proportion z-test:** compares two proportions such as churn rates, with adequate counts and independent customer units.
- **F-test:** checks equality of variances; it is sensitive to non-normal data. Follow the project test plan when selecting the corresponding mean test.
- **Randomized A/B test:** preserve the randomized unit (subscriber), define the offer period, and exclude pre-offer churn when estimating post-offer outcomes. A test on 912,820 subscriber-day rows is pseudoreplication if treatment was assigned to 21,993 subscribers.
- **Effect size and uncertainty:** report the magnitude and context alongside p-values; statistical significance does not imply practical impact.
- **Association versus causation:** observational churn differences may reflect confounding, reverse timing, selection, or exposure opportunity.

## Dashboard interpretation and limitations

- Monthly traffic totals, active subscribers, weekday average use, and usage spread answer demand questions. Each chart's filters select region, connection type, and device type.
- Complaint matrix compares resolved and unresolved ticket counts; the ECDF shows the fraction of resolved tickets closed by each elapsed day. The scatter summarizes volume and average resolution time by region and complaint category.
- A ticket-weighted statistic can give heavy complainants more influence. Clarify whether a chart's unit is a subscriber, ticket, transaction, or usage record.
- May/June usage increases are an open question in the runbook. Do not invent a cause from these data alone.
- Observed usage and churn cover a limited six-month window; late-period events and customers with sparse activity can have different exposure. Plan allowances and “actual ARPU” are constructed measures with assumptions documented in the analysis notebook.
- Dashboard filters show segment comparisons, not causal effects. Small subgroups and missing observations need careful interpretation.

## Likely viva prompts

1. What business question does the project answer, and who would use the results?
2. What is the grain of each table? How do you prevent double-counting churn after a join?
3. Explain the relationships among customers, circles, plans, usage, recharges, and complaints.
4. Why use `EXISTS` to identify subscribers with complaints?
5. What is the difference between average data per usage row and average usage per subscriber?
6. How would you explain the May/June data-usage increase without claiming an unsupported cause?
7. What does a p-value mean? How is it different from effect size?
8. Why is subscriber-day pseudoreplication a problem in a subscriber-randomized test?
9. Which assumptions and limitations affect the churn comparisons?
10. What does the complaint ECDF show, and why is a ticket-level rate not the same as a subscriber-level rate?
11. Why use multiple chart forms and filters? How can a viewer avoid drawing a causal conclusion?
12. What additional data or follow-up experiment would strengthen the business recommendation?

## Short presentation sequence

1. Business question and dataset scope.
2. ER model and correct analysis grain.
3. Data quality and preparation decisions.
4. Main descriptive findings and careful interpretation.
5. Dashboard tour: two tabs, filters, and chart reading.
6. Statistical validation, limitations, and proposed next action.
