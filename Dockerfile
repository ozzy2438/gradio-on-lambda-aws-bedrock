FROM public.ecr.aws/docker/library/python:3.13-slim

COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:1.0.0 /lambda-adapter /opt/extensions/lambda-adapter

WORKDIR /var/task

ENV GRADIO_SERVER_NAME=0.0.0.0 \
    PORT=8080 \
    AWS_LWA_INVOKE_MODE=response_stream \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev

EXPOSE 8080

CMD ["/var/task/.venv/bin/python", "src/gradio_on_lambda_bedrock_aws/app.py"]

# force rebuild Mon Apr 27 18:44:04 AEST 2026
