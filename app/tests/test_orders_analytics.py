'''
This test script exists because I am currently unable to use AWS and I wanted to test in another way to continue working.
'''


import unittest
from pathlib import Path
import sys

import pandas as pd

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root / "app"))

import orders_analytics


class TestOrdersAnalytics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orders_df = pd.read_csv(project_root / "sample_orders.csv")

    def test_calculate_most_profitable_region(self):
        result = orders_analytics.calculate_most_profitable_region(self.orders_df)

        self.assertEqual(result.iloc[0]["Region"], "East")
        self.assertAlmostEqual(float(result.iloc[0]["Profit"]), 2465.5, places=4)

    def test_find_most_common_ship_method(self):
        result = orders_analytics.find_most_common_ship_method(self.orders_df)

        expected = pd.DataFrame(
            [
                {"Category": "Furniture", "Ship Mode": "Same Day", "Order Count": 2},
                {
                    "Category": "Furniture",
                    "Ship Mode": "Standard Class",
                    "Order Count": 2,
                },
                {
                    "Category": "Office Supplies",
                    "Ship Mode": "Standard Class",
                    "Order Count": 4,
                },
                {"Category": "Technology", "Ship Mode": "Same Day", "Order Count": 2},
            ]
        )

        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)

    def test_find_number_of_order_per_category(self):
        result = orders_analytics.find_number_of_order_per_category(self.orders_df)

        expected = pd.DataFrame(
            [
                {"Category": "Furniture", "Sub Category": "Bookcases", "Order Count": 1},
                {"Category": "Furniture", "Sub Category": "Chairs", "Order Count": 1},
                {
                    "Category": "Furniture",
                    "Sub Category": "Furnishings",
                    "Order Count": 1,
                },
                {"Category": "Furniture", "Sub Category": "Tables", "Order Count": 2},
                {
                    "Category": "Office Supplies",
                    "Sub Category": "Appliances",
                    "Order Count": 2,
                },
                {"Category": "Office Supplies", "Sub Category": "Art", "Order Count": 2},
                {
                    "Category": "Office Supplies",
                    "Sub Category": "Binders",
                    "Order Count": 3,
                },
                {
                    "Category": "Office Supplies",
                    "Sub Category": "Labels",
                    "Order Count": 1,
                },
                {
                    "Category": "Office Supplies",
                    "Sub Category": "Paper",
                    "Order Count": 1,
                },
                {
                    "Category": "Office Supplies",
                    "Sub Category": "Storage",
                    "Order Count": 3,
                },
                {"Category": "Technology", "Sub Category": "Phones", "Order Count": 3},
            ]
        )

        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)


if __name__ == "__main__":
    unittest.main()
