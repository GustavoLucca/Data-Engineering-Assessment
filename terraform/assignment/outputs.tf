output "ecr_repository_url" {
  value = module.ecr_repo.repository_url
}

output "lambda_function_name" {
  value = "${local.app_name}-file-processor"
}

output "input_bucket_name" {
  value = aws_s3_bucket.input_s3.bucket
}

output "output_bucket_name" {
  value = aws_s3_bucket.output_s3.bucket
}
