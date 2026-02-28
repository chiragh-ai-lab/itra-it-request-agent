# Request intake Lambda functions

# Create Request Lambda
resource "aws_lambda_function" "create_request" {
  filename         = data.archive_file.health_lambda.output_path
  function_name    = "${var.project_name}-create-request"
  role            = aws_iam_role.lambda.arn
  handler         = "itra_create_request.handler"
  source_code_hash = data.archive_file.health_lambda.output_base64sha256
  runtime         = var.lambda_runtime
  timeout         = var.lambda_timeout
  memory_size     = 256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.main.name
      BUCKET_NAME = aws_s3_bucket.main.id
    }
  }

  tags = {
    Name = "${var.project_name}-create-request"
  }
}

resource "aws_cloudwatch_log_group" "create_request" {
  name              = "/aws/lambda/${aws_lambda_function.create_request.function_name}"
  retention_in_days = 7
}

# List Requests Lambda
resource "aws_lambda_function" "list_requests" {
  filename         = data.archive_file.health_lambda.output_path
  function_name    = "${var.project_name}-list-requests"
  role            = aws_iam_role.lambda.arn
  handler         = "itra_list_requests.handler"
  source_code_hash = data.archive_file.health_lambda.output_base64sha256
  runtime         = var.lambda_runtime
  timeout         = var.lambda_timeout
  memory_size     = 256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.main.name
      BUCKET_NAME = aws_s3_bucket.main.id
    }
  }

  tags = {
    Name = "${var.project_name}-list-requests"
  }
}

resource "aws_cloudwatch_log_group" "list_requests" {
  name              = "/aws/lambda/${aws_lambda_function.list_requests.function_name}"
  retention_in_days = 7
}

# Get Request Lambda
resource "aws_lambda_function" "get_request" {
  filename         = data.archive_file.health_lambda.output_path
  function_name    = "${var.project_name}-get-request"
  role            = aws_iam_role.lambda.arn
  handler         = "itra_get_request.handler"
  source_code_hash = data.archive_file.health_lambda.output_base64sha256
  runtime         = var.lambda_runtime
  timeout         = var.lambda_timeout
  memory_size     = 256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.main.name
      BUCKET_NAME = aws_s3_bucket.main.id
    }
  }

  tags = {
    Name = "${var.project_name}-get-request"
  }
}

resource "aws_cloudwatch_log_group" "get_request" {
  name              = "/aws/lambda/${aws_lambda_function.get_request.function_name}"
  retention_in_days = 7
}

# Update Request Lambda
resource "aws_lambda_function" "update_request" {
  filename         = data.archive_file.health_lambda.output_path
  function_name    = "${var.project_name}-update-request"
  role            = aws_iam_role.lambda.arn
  handler         = "itra_update_request.handler"
  source_code_hash = data.archive_file.health_lambda.output_base64sha256
  runtime         = var.lambda_runtime
  timeout         = var.lambda_timeout
  memory_size     = 256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.main.name
      BUCKET_NAME = aws_s3_bucket.main.id
    }
  }

  tags = {
    Name = "${var.project_name}-update-request"
  }
}

resource "aws_cloudwatch_log_group" "update_request" {
  name              = "/aws/lambda/${aws_lambda_function.update_request.function_name}"
  retention_in_days = 7
}
