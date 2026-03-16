# You will need to modify the key value in the backend block to a unique value for your assignment.

provider "aws" {
  region = var.region_name
  profile = var.aws_profile
}
data "aws_caller_identity" "current" {}


# By default, we use a local backend so you can work without AWS backend credentials.
# To switch to the provided shared S3/Dynamo backend, uncomment the block below and
# ensure your profile has permissions to read/write the configured bucket/table.

terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}

# terraform {
#   backend "s3" {
#     bucket         = "nmd-training-tf-states-706146613458"
#     key            = "nmd-assignment-gustavo-lucca-padilla.tfstate"
#     region         = "us-west-2"
#     dynamodb_table = "nmd-training-tf-state-lock-table"    
#     encrypt        = true                   # Encrypts the state file at rest
#     profile        = "GustavoLucca"         # Change depending on profile
#   }
#}
