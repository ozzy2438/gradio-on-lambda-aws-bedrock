#!/usr/bin/env python3
from __future__ import annotations

import os

from aws_cdk import App, CfnOutput, Duration, Environment, Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from constructs import Construct


class GradioLambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        gradio_function = lambda_.DockerImageFunction(
            self,
            "GradioBedrockFunction",
            code=lambda_.DockerImageCode.from_image_asset("."),
            architecture=lambda_.Architecture.X86_64,
            memory_size=2048,
            timeout=Duration.minutes(15),
            environment={
                "AWS_REGION_NAME": self.region,
                "BEDROCK_MODEL": "bedrock/deepseek.v3.2",
                "BEDROCK_MAX_TOKENS": "1024",
                "BEDROCK_TEMPERATURE": "0.7",
                "GRADIO_SERVER_NAME": "0.0.0.0",
                "PORT": "8080",
                "AWS_LWA_INVOKE_MODE": "response_stream",
            },
        )

        gradio_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                resources=["*"],
            )
        )

        function_url = gradio_function.add_function_url(
            auth_type=lambda_.FunctionUrlAuthType.NONE,
            invoke_mode=lambda_.InvokeMode.RESPONSE_STREAM,
        )

        CfnOutput(
            self,
            "GradioFunctionUrl",
            value=function_url.url,
            description="Public URL for the Gradio chat app.",
        )


app = App()
GradioLambdaStack(
    app,
    "GradioLambdaBedrockStack",
    env=Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION")
        or os.getenv("AWS_REGION")
        or os.getenv("AWS_DEFAULT_REGION")
        or "us-east-1",
    ),
)
app.synth()
