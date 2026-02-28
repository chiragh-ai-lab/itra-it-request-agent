resource "aws_api_gateway_rest_api" "main" {
  name        = "${var.project_name}-api"
  description = "IT Request Agent API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_authorizer" "cognito" {
  name          = "${var.project_name}-cognito-authorizer"
  rest_api_id   = aws_api_gateway_rest_api.main.id
  type          = "COGNITO_USER_POOLS"
  provider_arns = [aws_cognito_user_pool.main.arn]
}

# API Gateway deployment with triggers
# CRITICAL: Update ALL 4 sections when adding new endpoints
resource "aws_api_gateway_deployment" "main" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  
  triggers = {
    # Redeployment trigger - update this hash when adding new resources/methods
    redeployment = sha1(jsonencode([
      # Resources
      aws_api_gateway_rest_api.main.root_resource_id,
      aws_api_gateway_resource.health.id,
      aws_api_gateway_resource.requests.id,
      aws_api_gateway_resource.request_id.id,
      aws_api_gateway_resource.request_classify.id,
      aws_api_gateway_resource.request_action.id,
      aws_api_gateway_resource.request_chat.id,
      aws_api_gateway_resource.request_resolve.id,
      # Methods
      module.health_get.method.id,
      module.requests_post.method.id,
      module.requests_get.method.id,
      module.request_id_get.method.id,
      module.request_id_patch.method.id,
      module.request_classify_post.method.id,
      module.request_action_post.method.id,
      module.request_chat_post.method.id,
      module.request_resolve_post.method.id,
      # CORS
      module.health_cors.method.id,
      module.requests_cors.method.id,
      module.request_id_cors.method.id,
      module.request_classify_cors.method.id,
      module.request_action_cors.method.id,
      module.request_chat_cors.method.id,
      module.request_resolve_cors.method.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    module.health_get,
    module.health_cors,
    module.requests_post,
    module.requests_get,
    module.requests_cors,
    module.request_id_get,
    module.request_id_patch,
    module.request_id_cors,
    module.request_classify_post,
    module.request_classify_cors,
    module.request_action_post,
    module.request_action_cors,
    module.request_chat_post,
    module.request_chat_cors,
    module.request_resolve_post,
    module.request_resolve_cors
  ]
}

resource "aws_api_gateway_stage" "main" {
  deployment_id = aws_api_gateway_deployment.main.id
  rest_api_id   = aws_api_gateway_rest_api.main.id
  stage_name    = var.environment
}

# Gateway responses for CORS on errors
resource "aws_api_gateway_gateway_response" "unauthorized" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  response_type = "UNAUTHORIZED"

  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin"  = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
  }
}

resource "aws_api_gateway_gateway_response" "access_denied" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  response_type = "ACCESS_DENIED"

  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin"  = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
  }
}

resource "aws_api_gateway_gateway_response" "default_4xx" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  response_type = "DEFAULT_4XX"

  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin"  = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
  }
}

resource "aws_api_gateway_gateway_response" "default_5xx" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  response_type = "DEFAULT_5XX"

  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin"  = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
  }
}
