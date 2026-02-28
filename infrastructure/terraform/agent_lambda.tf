# Agent action Lambda functions

# Classify Request Lambda
resource "aws_lambda_function" "classify_request" {
  filename         = data.archive_file.health_lambda.output_path
  function_name    = "${var.project_name}-classify-request"
  role            = aws_iam_role.lambda.arn
  handler         = "itra_classify_request.handler"
  source_code_hash = data.archive_file.health_lambda.output_base64sha256
  runtime         = var.lambda_runtime
  timeout         = 120
  memory_size     = 1024

  environment {
    variables = {
      TABLE_NAME           = aws_dynamodb_table.main.name
      BUCKET_NAME          = aws_s3_bucket.main.id
      CLASSIFICATION_MODEL = "anthropic.claude-3-5-haiku-20241022-v1:0"
    }
  }

  tags = {
    Name = "${var.project_name}-classify-request"
  }
}

resource "aws_cloudwatch_log_group" "classify_request" {
  name              = "/aws/lambda/${aws_lambda_function.classify_request.function_name}"
  retention_in_days = 7
}

# Agent Action Lambda
resource "aws_lambda_function" "agent_action" {
  filename         = data.archive_file.health_lambda.output_path
  function_name    = "${var.project_name}-agent-action"
  role            = aws_iam_role.lambda.arn
  handler         = "itra_agent_action.handler"
  source_code_hash = data.archive_file.health_lambda.output_base64sha256
  runtime         = var.lambda_runtime
  timeout         = 120
  memory_size     = 1024

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.main.name
      BUCKET_NAME = aws_s3_bucket.main.id
    }
  }

  tags = {
    Name = "${var.project_name}-agent-action"
  }
}

resource "aws_cloudwatch_log_group" "agent_action" {
  name              = "/aws/lambda/${aws_lambda_function.agent_action.function_name}"
  retention_in_days = 7
}

# Chat Agent Lambda
resource "aws_lambda_function" "chat_agent" {
  filename         = data.archive_file.health_lambda.output_path
  function_name    = "${var.project_name}-chat-agent"
  role            = aws_iam_role.lambda.arn
  handler         = "itra_chat_agent.handler"
  source_code_hash = data.archive_file.health_lambda.output_base64sha256
  runtime         = var.lambda_runtime
  timeout         = 120
  memory_size     = 1024

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.main.name
      BUCKET_NAME = aws_s3_bucket.main.id
      CHAT_MODEL = "anthropic.claude-3-7-sonnet-20250219-v1:0"
    }
  }

  tags = {
    Name = "${var.project_name}-chat-agent"
  }
}

resource "aws_cloudwatch_log_group" "chat_agent" {
  name              = "/aws/lambda/${aws_lambda_function.chat_agent.function_name}"
  retention_in_days = 7
}

# Send Notification Lambda
resource "aws_lambda_function" "send_notification" {
  filename         = data.archive_file.health_lambda.output_path
  function_name    = "${var.project_name}-send-notification"
  role            = aws_iam_role.lambda.arn
  handler         = "itra_send_notification.handler"
  source_code_hash = data.archive_file.health_lambda.output_base64sha256
  runtime         = var.lambda_runtime
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      SENDER_EMAIL = var.sender_email
    }
  }

  tags = {
    Name = "${var.project_name}-send-notification"
  }
}

resource "aws_cloudwatch_log_group" "send_notification" {
  name              = "/aws/lambda/${aws_lambda_function.send_notification.function_name}"
  retention_in_days = 7
}

# Resolve Request Lambda
resource "aws_lambda_function" "resolve_request" {
  filename         = data.archive_file.health_lambda.output_path
  function_name    = "${var.project_name}-resolve-request"
  role            = aws_iam_role.lambda.arn
  handler         = "itra_resolve_request.handler"
  source_code_hash = data.archive_file.health_lambda.output_base64sha256
  runtime         = var.lambda_runtime
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.main.name
    }
  }

  tags = {
    Name = "${var.project_name}-resolve-request"
  }
}

resource "aws_cloudwatch_log_group" "resolve_request" {
  name              = "/aws/lambda/${aws_lambda_function.resolve_request.function_name}"
  retention_in_days = 7
}
