## Gradio Chat on Amazon Bedrock

This app runs a Gradio `ChatInterface` backed by DeepSeek V3.2 on Amazon
Bedrock through the LiteLLM Python SDK.

### Local Run

```bash
uv run src/gradio_on_lambda_bedrock_aws/app.py
```

By default, the app calls:

```text
bedrock/deepseek.v3.2
```

and uses the first available AWS region from:

```text
AWS_REGION_NAME
AWS_REGION
AWS_DEFAULT_REGION
```

If none are set, it defaults to `us-east-1`.

### Authentication

Use normal AWS credentials for Bedrock Runtime, for example an AWS profile,
environment variables, or a Lambda execution role with Bedrock invoke access.

For Bedrock API key authentication, set:

```bash
export AWS_BEARER_TOKEN_BEDROCK="your-bedrock-api-key"
```

To use the Bedrock Mantle OpenAI-compatible endpoint instead, set:

```bash
export BEDROCK_MANTLE_API_KEY="your-bedrock-api-key"
```

When `BEDROCK_MANTLE_API_KEY` is present, the default model switches to:

```text
bedrock_mantle/deepseek.v3.2
```

### Configuration

```bash
export BEDROCK_MODEL="bedrock/deepseek.v3.2"
export AWS_REGION_NAME="us-east-1"
export BEDROCK_TEMPERATURE="0.7"
export BEDROCK_MAX_TOKENS="1024"
export SYSTEM_PROMPT="You are a concise, helpful assistant."
export GRADIO_SERVER_PORT="7860"
```

`LITELLM_MODEL` can also be used to override the model route directly.

### Troubleshooting

If botocore reports that the login credential provider needs
`botocore[crt]`, install the locked dependencies again:

```bash
uv sync
```

## Deploy With CDK

The CDK app in `infra.py` builds this project as a Lambda container image,
uses the AWS Lambda Web Adapter to run Gradio on port `8080`, grants the
function permission to invoke Bedrock, and exposes the app with a public Lambda
Function URL.

```bash
uv sync
aws login
cdk bootstrap
cdk deploy
```

Docker must be running because CDK builds the Lambda image from `Dockerfile`.

If CDK cannot resolve the AWS account, refresh your AWS CLI session first:

```bash
aws login
aws sts get-caller-identity
```

For non-default profiles, run CDK with the same profile:

```bash
AWS_PROFILE=your-profile cdk bootstrap
AWS_PROFILE=your-profile cdk deploy
```
