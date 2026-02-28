# Health check Lambda function
data "archive_file" "health_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/../../backend/functions"
  output_path = "${path.module}/lambda_functions.zip"
}

resource "aws_lambda_function" "health" {
  filename         = data.archive_file.health_lambda.output_path
  function_name    = "${var.project_name}-health"
  role            = aws_iam_role.lambda.arn
  handler         = "health.handler"
  source_code_hash = data.archive_file.health_lambda.output_base64sha256
  runtime         = var.lambda_runtime
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.main.name
      BUCKET_NAME = aws_s3_bucket.main.id
    }
  }

  tags = {
    Name = "${var.project_name}-health"
  }
}

resource "aws_cloudwatch_log_group" "health" {
  name              = "/aws/lambda/${aws_lambda_function.health.function_name}"
  retention_in_days = 7
}
