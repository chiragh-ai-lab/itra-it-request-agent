# ITRA Infrastructure

AWS serverless infrastructure for the IT Request Agent, deployed via Terraform.

## Architecture

- **DynamoDB**: Single-table design with tenant isolation
- **S3**: KMS-encrypted storage with organized paths
- **Cognito**: User authentication with JWT tokens
- **API Gateway**: REST API with Cognito authorizer
- **Lambda**: Python 3.12 functions with shared IAM role
- **Bedrock**: AI capabilities (classification, chat, actions)

## Prerequisites

- AWS CLI configured with credentials
- Terraform 1.5.0+
- Python 3.12 (for local Lambda testing)

## Deployment

### Initial Setup

The S3 backend and DynamoDB lock table are already created:
- S3 bucket: `itra-terraform-state-734883380404`
- DynamoDB table: `itra-terraform-locks`

### Deploy Infrastructure

```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

### Outputs

After deployment, Terraform outputs:
- `api_endpoint`: API Gateway URL for frontend
- `cognito_user_pool_id`: For frontend auth configuration
- `cognito_user_pool_client_id`: For frontend auth configuration
- `s3_bucket_name`: For file uploads
- `dynamodb_table_name`: Main data table

## Adding New API Endpoints

When adding a new endpoint, follow these steps to avoid CORS issues:

1. Create Lambda function in `backend/functions/`
2. Add Lambda resource in appropriate `*_lambda.tf` file
3. Create API resource and method in `*_api.tf` file
4. Add CORS module for the resource
5. **CRITICAL**: Update ALL 4 sections in `api_gateway.tf`:
   - Add resource to `triggers` block
   - Add method to `triggers` block
   - Add CORS to `triggers` block
   - Add method + CORS to `depends_on` list

### Example: Adding a /health endpoint

```hcl
# In health_api.tf
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

# Then update api_gateway.tf triggers and depends_on
```

## Testing CORS

Before building more endpoints, test CORS:

```bash
curl -X OPTIONS https://your-api-url/health \
  -H "Origin: https://your-frontend.com" \
  -H "Access-Control-Request-Method: GET" -v
```

Expected response headers:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET,POST,PUT,PATCH,DELETE,OPTIONS`
- `Access-Control-Allow-Headers: Content-Type,Authorization,...`

## Lambda Development

All Lambda functions should:
1. Import `utils.py` for standard patterns
2. Use `get_tenant_id(event)` for tenant isolation
3. Use `success()` and `error()` for responses
4. Use `get_s3_client()` for S3 operations (SigV4)
5. Use `convert_decimals()` for DynamoDB responses

Example Lambda:

```python
import os
from utils import success, error, get_tenant_id, get_dynamodb_resource

TABLE_NAME = os.environ['TABLE_NAME']

def handler(event, context):
    try:
        tenant_id = get_tenant_id(event)
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(TABLE_NAME)
        
        # Your logic here
        
        return success({'message': 'Success'})
    except Exception as e:
        print(f"Error: {str(e)}")
        return error(str(e), 500)
```

## Troubleshooting

### CORS errors in browser
- Verify OPTIONS method exists for the endpoint
- Check all 4 sections in `api_gateway.tf` are updated
- Delete and recreate API Gateway deployment if needed

### Lambda code changes not taking effect
```bash
rm backend/lambda_functions.zip
terraform apply
```

### DynamoDB Decimal errors in frontend
- Ensure `convert_decimals()` is used in Lambda response
- Check `utils.py` is imported correctly

### S3 signature errors
- Verify `get_s3_client()` is used (includes SigV4)
- Check KMS key permissions in Lambda IAM role

## CI/CD

GitHub Actions automatically:
- Runs `terraform plan` on PRs
- Runs `terraform apply` on merge to main

Required GitHub secrets:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
