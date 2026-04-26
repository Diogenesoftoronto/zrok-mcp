FROM python:3.13-slim

WORKDIR /app

COPY src/zrok_mcp/ ./zrok_mcp/
COPY pyproject.toml .

RUN sed -i 's|packages = \["src/zrok_mcp"\]|packages = ["zrok_mcp"]|' pyproject.toml \
    && pip install --no-cache-dir .

ENV ZROK_MCP_TRANSPORT=streamable-http
ENV ZROK_MCP_HOST=0.0.0.0
ENV ZROK_MCP_PORT=8000

EXPOSE 8000

CMD ["zrok-mcp"]
