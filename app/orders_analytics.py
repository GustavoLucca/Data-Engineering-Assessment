import pandas as pd
"Complete thes functions or write your own to perform the following tasks"

_BASE_REQUIRED_COLUMNS = {
    "Region",
    "Category",
    "Sub Category",
    "Ship Mode",
    "cost price",
    "List Price",
    "Quantity",
    "Discount Percent",
}


def _validate_columns(orders_df: pd.DataFrame, required_columns: set[str]) -> None: #Deals with missing columns in the DataFrame
    missing_columns = sorted(required_columns - set(orders_df.columns))
    if missing_columns:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing_columns)
        )

def calculate_profit_by_order(orders_df):
    "Calculate profit for each order in the DataFrame"

    _validate_columns(orders_df, _BASE_REQUIRED_COLUMNS)

    profit_by_order = orders_df.copy()
    discount_multiplier = 1 - (profit_by_order["Discount Percent"].astype(float) / 100) #Calculates discount beforehand
    gross_revenue = (
        profit_by_order["List Price"].astype(float)
        * profit_by_order["Quantity"].astype(float)
        * discount_multiplier # This is functionally equivalent to Sale Price
    )
    total_cost = (
        profit_by_order["cost price"].astype(float)
        * profit_by_order["Quantity"].astype(float)
    )

    profit_by_order["Profit"] = gross_revenue - total_cost

    return profit_by_order

def calculate_most_profitable_region(orders_df):
    "Calculate the most profitable region and its profit"

    profit_by_order = calculate_profit_by_order(orders_df)
    region_profit = (
        profit_by_order.groupby("Region", as_index=False)["Profit"]
        .sum()
        .sort_values(["Profit", "Region"], ascending=[False, True])
        .head(1)
        .reset_index(drop=True)
    )

    return region_profit

def find_most_common_ship_method(orders_df):
    "Find the most common shipping method for each Category"

    _validate_columns(orders_df, {"Category", "Ship Mode"})

    ship_mode_counts = (
        orders_df.groupby(["Category", "Ship Mode"], as_index=False)
        .size()
        .rename(columns={"size": "Order Count"})
    )

    most_common_ship_methods = (
        ship_mode_counts[
            ship_mode_counts["Order Count"]
            == ship_mode_counts.groupby("Category")["Order Count"].transform("max")
        ]
        .sort_values(["Category", "Ship Mode"])
        .reset_index(drop=True)
    )

    return most_common_ship_methods

def find_number_of_order_per_category( orders_df):
    "find the number of orders for each Category and Sub Category"

    _validate_columns(orders_df, {"Category", "Sub Category"})

    orders_per_category = (
        orders_df.groupby(["Category", "Sub Category"], as_index=False)
        .size()
        .rename(columns={"size": "Order Count"})
        .sort_values(["Category", "Sub Category"])
        .reset_index(drop=True)
    )

    return orders_per_category
