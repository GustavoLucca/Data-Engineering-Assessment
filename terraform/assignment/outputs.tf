output "ecr_repository_url" {
  value = module.ecr_repo.repository_url
}

output "lambda_function_name" {
  value = "${local.app_name}-file-processor"
}
