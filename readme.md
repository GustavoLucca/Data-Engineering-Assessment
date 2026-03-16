## Welcome to your New Math Data assessment.
Please see the [Assessment Instructions](instructions.md)

## Core Data Transformations (Python)

Business logic is implemented in [app/orders_analytics.py](app/orders_analytics.py) and kept separate from the Lambda entry point in [app/lambda.py](app/lambda.py).

### Implemented Transformations

1. **Most Profitable Region** (`calculate_most_profitable_region`)
	- Profit formula per row:
	  - `Profit = (List Price * Quantity * (1 - Discount Percent / 100)) - (cost price * Quantity)`
	- Aggregates profit by `Region` and returns the top region.

2. **Most Common Shipping Method** (`find_most_common_ship_method`)
	- Counts orders by `Category` + `Ship Mode`.
	- Returns the most frequent shipping method per category.
	- Tie handling: returns **all tied winners** for a category.

3. **Order Counts by Category/Sub Category** (`find_number_of_order_per_category`)
	- Groups by `Category` + `Sub Category`.
	- Returns grouped counts in a dataframe.

### Lambda Output Partitioning

The Lambda function writes analytics CSV outputs to the output bucket using date-based partitioning:

- `analytics/run_date=YYYY-MM-DD/most_profitable_region.csv`
- `analytics/run_date=YYYY-MM-DD/most_common_ship_method.csv`
- `analytics/run_date=YYYY-MM-DD/orders_per_category.csv`

This partitioning provides a simple and reliable run-level slice for downstream discovery and reprocessing.

### Local Unit Testing

Tests are located in [app/tests/test_orders_analytics.py](app/tests/test_orders_analytics.py) and use `sample_orders.csv`.

Run tests from repo root:

```sh
python -m unittest discover -s app/tests -p "test_*.py"
```

Covered assertions:
- Most profitable region result and profit value.
- Most common ship method per category including tie behavior.
- Order counts by category and sub-category.
