import sys
import json
import os
from datetime import datetime, timezone
from io import BytesIO
from urllib.parse import unquote_plus
import pandas as pd

import orders_analytics

"""
Modify this lambda function to perform the following questions

1. Find the most profitable Region, and its profit
2. What shipping method is most common for each Category
3. Output a glue table containing the number of orders for each Category and Sub Category
"""


def get_s3_path_from_event(event : dict) -> str:
    "Returns the S3 path from the lambda event record"

    try:
        first_record = event["Records"][0]
        bucket_name = first_record["s3"]["bucket"]["name"]
        object_key = unquote_plus(first_record["s3"]["object"]["key"])
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError("Invalid S3 event format") from error

    return f"s3://{bucket_name}/{object_key}"

def lambda_handler(event, context):
    "Lambda function to process S3 events and perform analytics on orders data"

    import boto3

    s3_client = boto3.client("s3")
    source_path = get_s3_path_from_event(event)

    _, path_without_scheme = source_path.split("s3://", 1)
    source_bucket, source_key = path_without_scheme.split("/", 1)

    output_bucket = os.environ.get("OUTPUT_BUCKET")
    if not output_bucket:
        raise ValueError("Environment variable OUTPUT_BUCKET is required")

    output_prefix = os.environ.get("OUTPUT_PREFIX", "analytics").rstrip("/")
    run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    partition_prefix = f"{output_prefix}/run_date={run_date}"

    input_object = s3_client.get_object(Bucket=source_bucket, Key=source_key)
    orders_df = pd.read_csv(input_object["Body"])

    reports = {
        "most_profitable_region.csv": orders_analytics.calculate_most_profitable_region(orders_df),
        "most_common_ship_method.csv": orders_analytics.find_most_common_ship_method(orders_df),
        "orders_per_category.csv": orders_analytics.find_number_of_order_per_category(orders_df),
    }

    written_files = []
    for file_name, report_df in reports.items():
        output_key = f"{partition_prefix}/{file_name}"
        csv_buffer = BytesIO(report_df.to_csv(index=False).encode("utf-8"))
        s3_client.put_object(
            Bucket=output_bucket,
            Key=output_key,
            Body=csv_buffer.getvalue(),
            ContentType="text/csv",
        )
        written_files.append(f"s3://{output_bucket}/{output_key}")

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "source": source_path,
                "outputs": written_files,
            }
        ),
    }

