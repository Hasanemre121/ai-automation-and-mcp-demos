FROM python:3.12-slim
WORKDIR /app
COPY mcp_business_tools_server.py /app/mcp_business_tools_server.py
ENTRYPOINT ["python", "/app/mcp_business_tools_server.py"]
