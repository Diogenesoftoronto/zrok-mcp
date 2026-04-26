FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir .

ENV ZROK_MCP_TRANSPORT=streamable-http
ENV ZROK_MCP_HOST=0.0.0.0

EXPOSE 8000

CMD ["zrok-mcp"]
