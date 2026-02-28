# Health check API endpoint
resource "aws_api_gateway_resource" "health" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "health"
}

module "health_get" {
  source = "./modules/api_method"
  
  rest_api_id          = aws_api_gateway_rest_api.main.id
  resource_id          = aws_api_gateway_resource.health.id
  http_method          = "GET"
  authorization        = "NONE"
  lambda_function_name = aws_lambda_function.health.function_name
  lambda_invoke_arn    = aws_lambda_function.health.invoke_arn
  aws_region           = var.aws_region
}

module "health_cors" {
  source = "./modules/api_cors"
  
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.health.id
}
