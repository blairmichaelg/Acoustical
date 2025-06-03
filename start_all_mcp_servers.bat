@echo off
REM Script to start all MCP servers

REM github.com.modelcontextprotocol.servers.tree.main.src.github
set GITHUB_PERSONAL_ACCESS_TOKEN=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
start "MCP Server: GitHub" cmd /k npx -y @modelcontextprotocol/server-github

REM github.com.modelcontextprotocol/servers/tree/main/src/filesystem
start "MCP Server: Filesystem" cmd /k npx -y @modelcontextprotocol/server-filesystem "C:\Users\Michael\Documents\Cline\MCP"

REM github.com/AgentDeskAI/browser-tools-mcp
start "MCP Server: Browser Tools" cmd /k npx -y @agentdeskai/browser-tools-mcp@latest

REM github.com.modelcontextprotocol/servers/tree/main/src/sequentialthinking
start "MCP Server: Sequential Thinking" cmd /k npx -y @modelcontextprotocol/server-sequential-thinking

REM github.com/upstash/context7-mcp
start "MCP Server: Context7" cmd /k cmd /c npx -y @upstash/context7-mcp@latest

REM github.com/zcaceres/fetch-mcp
start "MCP Server: Fetch MCP" cmd /k node "C:\Users\Michael\Documents\Cline\MCP\fetch-mcp\dist\index.js"
