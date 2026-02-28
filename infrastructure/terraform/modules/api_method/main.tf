variable "rest_api_id" {
  description = "API Gateway REST API ID"
  type        = string
}

variable "resource_id" {
  description = "API Gateway resource ID"
  type        = string
}

variable "http_method" {
  description = "HTTP method (GET, POST, PUT, DELETE, PATCH)"
  type        = string
}

variable "authorization" {
  description = "Authorization type (NONE, COGNITO_USER_POOLS)"
  type        = string
  default     = "COGNITO_USER_POOLS"
}

variable "authorizer_id" {
  description = "Cognito authorizer ID (required if authorization is COGNITO_USER_POOLS)"
  type        = string
  default     = null
}

variable "lambda_function_name" {
  description = "Lambda function name to invoke"
  type        = string
}

variable "lambda_invoke_arn" {
  description = "Lambda function invoke ARN"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

data "aws_caller_identity" "current" {}

resource "aws_api_gateway_method" "method" {
  rest_api_id   = var.rest_api_id
  resource_id   = var.resource_id
  http_method   = var.http_method
  authorization = var.authorization
  authorizer_id = var.authorizer_id
}

resource "aws_api_gateway_integration" "integration" {
  rest_api_id             = var.rest_api_id
  resource_id             = var.resource_id
  http_method             = aws_api_gateway_method.method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke-${var.http_method}"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${var.rest_api_id}/*/${var.http_method}/*"
}

output "method" {
  value = aws_api_gateway_method.method
}

output "integration" {
  value = aws_api_gateway_integration.integration
}
