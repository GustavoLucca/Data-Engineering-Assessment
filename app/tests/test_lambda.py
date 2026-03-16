import importlib
import json
import os
import sys
import unittest
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root / "app"))

lambda_module = importlib.import_module("lambda")


class TestLambdaHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_csv_bytes = (project_root / "sample_orders.csv").read_bytes()

    def test_get_s3_path_from_event(self):
        event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "my-input-bucket"},
                        "object": {"key": "incoming%2Fsample_orders.csv"},
                    }
                }
            ]
        }

        result = lambda_module.get_s3_path_from_event(event)
        self.assertEqual(result, "s3://my-input-bucket/incoming/sample_orders.csv")

    def test_get_s3_path_from_event_invalid(self):
        with self.assertRaises(ValueError):
            lambda_module.get_s3_path_from_event({"bad": "event"})

    def test_lambda_handler_processes_and_writes_reports(self):
        mock_s3 = MagicMock()
        mock_s3.get_object.return_value = {"Body": BytesIO(self.sample_csv_bytes)}
        mock_boto3 = MagicMock()
        mock_boto3.client.return_value = mock_s3

        event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "input-bucket"},
                        "object": {"key": "sample_orders.csv"},
                    }
                }
            ]
        }

        with patch.dict(sys.modules, {"boto3": mock_boto3}):
            with patch.dict(os.environ, {"OUTPUT_BUCKET": "output-bucket", "OUTPUT_PREFIX": "analytics"}, clear=False):
                result = lambda_module.lambda_handler(event, context={})

        self.assertEqual(result["statusCode"], 200)
        body = json.loads(result["body"])
        self.assertEqual(body["source"], "s3://input-bucket/sample_orders.csv")
        self.assertEqual(len(body["outputs"]), 3)

        run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        expected_prefix = f"analytics/run_date={run_date}/"

        mock_s3.get_object.assert_called_once_with(Bucket="input-bucket", Key="sample_orders.csv")
        self.assertEqual(mock_s3.put_object.call_count, 3)

        put_keys = {call.kwargs["Key"] for call in mock_s3.put_object.call_args_list}
        expected_keys = {
            f"{expected_prefix}most_profitable_region.csv",
            f"{expected_prefix}most_common_ship_method.csv",
            f"{expected_prefix}orders_per_category.csv",
        }
        self.assertSetEqual(put_keys, expected_keys)

        for call in mock_s3.put_object.call_args_list:
            self.assertEqual(call.kwargs["Bucket"], "output-bucket")
            self.assertEqual(call.kwargs["ContentType"], "text/csv")
            self.assertIsInstance(call.kwargs["Body"], (bytes, bytearray))

    def test_lambda_handler_requires_output_bucket(self):
        mock_boto3 = MagicMock()
        mock_boto3.client.return_value = MagicMock()
        event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "input-bucket"},
                        "object": {"key": "sample_orders.csv"},
                    }
                }
            ]
        }

        with patch.dict(sys.modules, {"boto3": mock_boto3}):
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(ValueError):
                    lambda_module.lambda_handler(event, context={})


if __name__ == "__main__":
    unittest.main()