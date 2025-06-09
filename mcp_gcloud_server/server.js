import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  McpError,
  ErrorCode,
} from '@modelcontextprotocol/sdk/types.js'; // Assuming these are needed based on example
import { exec } from 'child_process';

// Helper function to execute gcloud commands
function executeGcloudCommand(command) {
  return new Promise((resolve, reject) => {
    const gcloudConfigPath = 'C:\\Users\\Michael\\AppData\\Roaming\\gcloud'; // Standard gcloud config path for user Michael on Windows
    const execOptions = {
      env: {
        ...process.env, // Inherit existing env vars
        CLOUDSDK_CONFIG: gcloudConfigPath,
      },
    };
    // Add --quiet flag and explicitly use cmd.exe
    const fullCommand = `cmd.exe /c "gcloud ${command} --quiet --format=json"`;
    exec(fullCommand, execOptions, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error executing: ${fullCommand} with CLOUDSDK_CONFIG=${gcloudConfigPath}`);
        console.error(`stderr: ${stderr}`);
        return reject(new McpError(ErrorCode.InternalError, `Error executing gcloud command: ${stderr || error.message}`));
      }
      try {
        const result = JSON.parse(stdout);
        resolve(result);
      } catch (parseError) {
        console.error(`Error parsing JSON output for: gcloud ${command}`);
        console.error(`stdout: ${stdout}`);
        if (stdout.trim() === "") {
          resolve({ success: true, message: "Command executed successfully, no JSON output." });
        } else {
          // For non-JSON, wrap it to fit tool call expectations (content array)
          resolve({ content: [{ type: 'text', text: stdout.trim() }] });
        }
      }
    });
  });
}

// Define tool execution logic separately
const toolImplementations = {
  list_gcp_projects: async () => {
    // Add --account flag to specify the account directly
    const projects = await executeGcloudCommand('projects list --account=blairmichaelg@gmail.com');
    return { content: [{ type: 'text', text: JSON.stringify(projects, null, 2) }] };
  },
  set_gcp_project: async ({ projectId }) => {
    if (!projectId || typeof projectId !== 'string') {
      throw new McpError(ErrorCode.InvalidParams, 'Missing or invalid projectId parameter.');
    }
    // gcloud config set project does not reliably return JSON
    return new Promise((resolve, reject) => {
      exec(`gcloud config set project ${projectId}`, (error, stdout, stderr) => {
        if (error) {
          console.error(`Error executing: gcloud config set project ${projectId}`);
          console.error(`stderr: ${stderr}`);
          return reject(new McpError(ErrorCode.InternalError, `Error setting GCP project: ${stderr || error.message}`));
        }
        if (stderr.includes(`Updated property [core/project] to [${projectId}].`) || stdout.includes(`Updated property [core/project] to [${projectId}].`)) {
          resolve({ content: [{ type: 'text', text: `Project successfully set to ${projectId}.` }] });
        } else {
          resolve({ content: [{ type: 'text', text: `Attempted to set project to ${projectId}. Output: ${stdout || stderr}`.trim() }] });
        }
      });
    });
  },
  list_vertex_ai_models: async ({ region }) => {
    if (!region || typeof region !== 'string') {
      throw new McpError(ErrorCode.InvalidParams, 'Missing or invalid region parameter.');
    }
    const models = await executeGcloudCommand(`ai models list --region=${region}`);
    return { content: [{ type: 'text', text: JSON.stringify(models, null, 2) }] };
  },
  list_vertex_ai_endpoints: async ({ region }) => {
    if (!region || typeof region !== 'string') {
      throw new McpError(ErrorCode.InvalidParams, 'Missing or invalid region parameter.');
    }
    const endpoints = await executeGcloudCommand(`ai endpoints list --region=${region}`);
    return { content: [{ type: 'text', text: JSON.stringify(endpoints, null, 2) }] };
  },
};

const server = new Server(
  { // ServerInfo
    name: 'gcloud-mcp-server',
    version: '0.1.0',
    description: 'MCP Server for interacting with Google Cloud CLI (gcloud)',
  },
  { // ServerCapabilities
    capabilities: {
      resources: {}, // Not implementing resources for now
      tools: {},     // Tools are defined via request handlers
    },
  }
);

// Handler for ListToolsRequest
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'list_gcp_projects',
        description: 'Lists all accessible Google Cloud projects.',
        inputSchema: { type: 'object', properties: {} },
      },
      {
        name: 'set_gcp_project',
        description: 'Sets the active Google Cloud project.',
        inputSchema: {
          type: 'object',
          properties: { projectId: { type: 'string', description: 'The ID of the project to set as active.' } },
          required: ['projectId'],
        },
      },
      {
        name: 'list_vertex_ai_models',
        description: 'Lists Vertex AI models in a specific region.',
        inputSchema: {
          type: 'object',
          properties: { region: { type: 'string', description: 'The region to list models from (e.g., us-central1).' } },
          required: ['region'],
        },
      },
      {
        name: 'list_vertex_ai_endpoints',
        description: 'Lists Vertex AI endpoints in a specific region.',
        inputSchema: {
          type: 'object',
          properties: { region: { type: 'string', description: 'The region to list endpoints from (e.g., us-central1).' } },
          required: ['region'],
        },
      },
    ],
  };
});

// Handler for CallToolRequest
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const toolName = request.params.name;
  const toolArguments = request.params.arguments;

  if (toolImplementations[toolName]) {
    try {
      const result = await toolImplementations[toolName](toolArguments);
      return result; // Should be { content: [{ type: 'text', text: '...' }] } or { isError: true, content: [...] }
    } catch (error) {
      if (error instanceof McpError) {
        throw error;
      }
      console.error(`Error executing tool ${toolName}:`, error);
      throw new McpError(ErrorCode.InternalError, `Error executing tool ${toolName}: ${error.message}`);
    }
  } else {
    throw new McpError(ErrorCode.MethodNotFound, `Tool "${toolName}" not found.`);
  }
});

server.onerror = (error) => {
  console.error('[MCP Server Error]', error);
};

process.on('SIGINT', async () => {
  console.log('Shutting down gcloud MCP server...');
  await server.close();
  process.exit(0);
});

async function main() {
  try {
    // The example shows `server.run().catch(console.error);` where run instantiates transport and connects.
    // Let's replicate that structure.
    console.log('gcloud-mcp-server v0.1.0 is attempting to start...'); // Corrected log line
    // The SDK doesn't seem to have a generic `start()` or `run()` method on the Server instance itself.
    // The example `WeatherServer` class had its own `run` method.
    // The core is `server.connect(transport)`.
    // For `node server.js` to work as an MCP server, it needs to listen somehow.
    // This is usually done by connecting to a transport like Stdio.
    const { StdioServerTransport } = await import('@modelcontextprotocol/sdk/server/stdio.js');
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error(`gcloud-mcp-server connected to stdio. Ready for MCP requests.`);
    // Keep alive
    process.stdin.resume();

  } catch (error) {
    console.error('Failed to start/connect gcloud MCP server:', error);
    process.exit(1);
  }
}

main();
