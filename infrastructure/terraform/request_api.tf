# Request intake API endpoints

# /requests resource
resource "aws_api_gateway_resource" "requests" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "requests"
}

# POST /requests - Create request
module "requests_post" {
  source = "./modules/api_method"
  
  rest_api_id          = aws_api_gateway_rest_api.main.id
  resource_id          = aws_api_gateway_resource.requests.id
  http_method          = "POST"
  authorization        = "COGNITO_USER_POOLS"
  authorizer_id        = aws_api_gateway_authorizer.cognito.id
  lambda_function_name = aws_lambda_function.create_request.function_name
  lambda_invoke_arn    = aws_lambda_function.create_request.invoke_arn
  aws_region           = var.aws_region
}

# GET /requests - List requests
module "requests_get" {
  source = "./modules/api_method"
  
  rest_api_id          = aws_api_gateway_rest_api.main.id
  resource_id          = aws_api_gateway_resource.requests.id
  http_method          = "GET"
  authorization        = "COGNITO_USER_POOLS"
  authorizer_id        = aws_api_gateway_authorizer.cognito.id
  lambda_function_name = aws_lambda_function.list_requests.function_name
  lambda_invoke_arn    = aws_lambda_function.list_requests.invoke_arn
  aws_region           = var.aws_region
}

# CORS for /requests
module "requests_cors" {
  source = "./modules/api_cors"
  
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.requests.id
}

# /requests/{id} resource
resource "aws_api_gateway_resource" "request_id" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.requests.id
  path_part   = "{id}"
}

# GET /requests/{id} - Get single request
module "request_id_get" {
  source = "./modules/api_method"
  
  rest_api_id          = aws_api_gateway_rest_api.main.id
  resource_id          = aws_api_gateway_resource.request_id.id
  http_method          = "GET"
  authorization        = "COGNITO_USER_POOLS"
  authorizer_id        = aws_api_gateway_authorizer.cognito.id
  lambda_function_name = aws_lambda_function.get_request.function_name
  lambda_invoke_arn    = aws_lambda_function.get_request.invoke_arn
  aws_region           = var.aws_region
}

# PATCH /requests/{id} - Update request
module "request_id_patch" {
  source = "./modules/api_method"
  
  rest_api_id          = aws_api_gateway_rest_api.main.id
  resource_id          = aws_api_gateway_resource.request_id.id
  http_method          = "PATCH"
  authorization        = "COGNITO_USER_POOLS"
  authorizer_id        = aws_api_gateway_authorizer.cognito.id
  lambda_function_name = aws_lambda_function.update_request.function_name
  lambda_invoke_arn    = aws_lambda_function.update_request.invoke_arn
  aws_region           = var.aws_region
}

# CORS for /requests/{id}
module "request_id_cors" {
  source = "./modules/api_cors"
  
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.request_id.id
}
