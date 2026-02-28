# Agent action API endpoints

# POST /requests/{id}/classify - Trigger classification
resource "aws_api_gateway_resource" "request_classify" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.request_id.id
  path_part   = "classify"
}

module "request_classify_post" {
  source = "./modules/api_method"
  
  rest_api_id          = aws_api_gateway_rest_api.main.id
  resource_id          = aws_api_gateway_resource.request_classify.id
  http_method          = "POST"
  authorization        = "COGNITO_USER_POOLS"
  authorizer_id        = aws_api_gateway_authorizer.cognito.id
  lambda_function_name = aws_lambda_function.classify_request.function_name
  lambda_invoke_arn    = aws_lambda_function.classify_request.invoke_arn
  aws_region           = var.aws_region
}

module "request_classify_cors" {
  source = "./modules/api_cors"
  
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.request_classify.id
}

# POST /requests/{id}/action - Execute agent action
resource "aws_api_gateway_resource" "request_action" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.request_id.id
  path_part   = "action"
}

module "request_action_post" {
  source = "./modules/api_method"
  
  rest_api_id          = aws_api_gateway_rest_api.main.id
  resource_id          = aws_api_gateway_resource.request_action.id
  http_method          = "POST"
  authorization        = "COGNITO_USER_POOLS"
  authorizer_id        = aws_api_gateway_authorizer.cognito.id
  lambda_function_name = aws_lambda_function.agent_action.function_name
  lambda_invoke_arn    = aws_lambda_function.agent_action.invoke_arn
  aws_region           = var.aws_region
}

module "request_action_cors" {
  source = "./modules/api_cors"
  
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.request_action.id
}

# POST /requests/{id}/chat - Chat with agent
resource "aws_api_gateway_resource" "request_chat" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.request_id.id
  path_part   = "chat"
}

module "request_chat_post" {
  source = "./modules/api_method"
  
  rest_api_id          = aws_api_gateway_rest_api.main.id
  resource_id          = aws_api_gateway_resource.request_chat.id
  http_method          = "POST"
  authorization        = "COGNITO_USER_POOLS"
  authorizer_id        = aws_api_gateway_authorizer.cognito.id
  lambda_function_name = aws_lambda_function.chat_agent.function_name
  lambda_invoke_arn    = aws_lambda_function.chat_agent.invoke_arn
  aws_region           = var.aws_region
}

module "request_chat_cors" {
  source = "./modules/api_cors"
  
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.request_chat.id
}

# POST /requests/{id}/resolve - Resolve request
resource "aws_api_gateway_resource" "request_resolve" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.request_id.id
  path_part   = "resolve"
}

module "request_resolve_post" {
  source = "./modules/api_method"
  
  rest_api_id          = aws_api_gateway_rest_api.main.id
  resource_id          = aws_api_gateway_resource.request_resolve.id
  http_method          = "POST"
  authorization        = "COGNITO_USER_POOLS"
  authorizer_id        = aws_api_gateway_authorizer.cognito.id
  lambda_function_name = aws_lambda_function.resolve_request.function_name
  lambda_invoke_arn    = aws_lambda_function.resolve_request.invoke_arn
  aws_region           = var.aws_region
}

module "request_resolve_cors" {
  source = "./modules/api_cors"
  
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.request_resolve.id
}
