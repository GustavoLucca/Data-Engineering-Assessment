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

The suite now includes mocked Lambda integration tests in [app/tests/test_lambda.py](app/tests/test_lambda.py), which validate S3 event parsing and S3 read/write behavior without requiring live AWS infrastructure.

Covered assertions:
- Most profitable region result and profit value.
- Most common ship method per category including tie behavior.
- Order counts by category and sub-category.

## Deployment (Terraform + Docker + AWS)

### Prerequisites

- AWS CLI configured with the profile in `terraform/assignment/vars.tfvars`.
- Docker installed and running.
- Terraform installed.

### 1) Configure Terraform variables

Edit `terraform/assignment/vars.tfvars` and confirm:

- `candidate_name`
- `aws_profile`

### 2) Initialize Terraform

From repository root:

```sh
cd terraform/assignment
terraform init -backend-config="key=nmd-assignment-<candidate-name>.tfstate"
```

### 3) Create ECR first (bootstrap apply)

The Lambda image must exist in ECR before full infrastructure apply.

```sh
terraform apply -target=module.ecr_repo -var-file="vars.tfvars"
```

### 4) Build and push Lambda image

```sh
AWS_PROFILE=$(terraform console -var-file="vars.tfvars" <<'EOF' | tr -d '"'
var.aws_profile
EOF
)
REGION=$(terraform console -var-file="vars.tfvars" <<'EOF' | tr -d '"'
var.region_name
EOF
)
ECR_URI=$(terraform output -raw ecr_repository_url)
LOCAL_IMAGE_NAME="nmd-assignment-file-processor"

docker build --platform linux/arm64 -t "$LOCAL_IMAGE_NAME" ../..
aws ecr get-login-password --region "$REGION" --profile "$AWS_PROFILE" \
	| docker login --username AWS --password-stdin "${ECR_URI%/*}"
docker tag "$LOCAL_IMAGE_NAME:latest" "$ECR_URI:latest"
docker push "$ECR_URI:latest"
```

### 5) Apply full infrastructure

```sh
terraform apply -var-file="vars.tfvars"
```

### 6) Optional: force Lambda image refresh

If you pushed a new image tag and want immediate rollout:

```sh
LAMBDA_FUNCTION_NAME=$(terraform output -raw lambda_function_name)
aws lambda update-function-code \
	--function-name "$LAMBDA_FUNCTION_NAME" \
	--image-uri "$ECR_URI:latest" \
	--region "$REGION" \
	--profile "$AWS_PROFILE"
```

## Testing Instructions

### Local unit tests

From repository root:

```sh
python -m unittest discover -s app/tests -p "test_*.py"
```

### End-to-end test in AWS

From `terraform/assignment`:

```sh
INPUT_BUCKET=$(terraform output -raw input_bucket_name)
OUTPUT_BUCKET=$(terraform output -raw output_bucket_name)
```

Upload sample input:

```sh
aws s3 cp ../../sample_orders.csv "s3://$INPUT_BUCKET/sample_orders.csv" \
	--region "$REGION" \
	--profile "$AWS_PROFILE"
```

Validate output files:

```sh
aws s3 ls "s3://$OUTPUT_BUCKET/analytics/" --recursive \
	--region "$REGION" \
	--profile "$AWS_PROFILE"
```

Expected output paths:

- `analytics/run_date=YYYY-MM-DD/most_profitable_region.csv`
- `analytics/run_date=YYYY-MM-DD/most_common_ship_method.csv`
- `analytics/run_date=YYYY-MM-DD/orders_per_category.csv`
