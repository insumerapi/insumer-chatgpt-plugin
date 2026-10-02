# InsumerAPI plugin for ChatGPT and Codex

The InsumerAPI plugin for the ChatGPT and Codex plugin directory: six skills plus a connection to the hosted InsumerAPI MCP server at `https://api.insumermodel.com/mcp`.

InsumerAPI is condition-based access infrastructure for blockchain wallets. Send a wallet and conditions, get a signed boolean across 37 chains, never the balance. Wallet auth is how it works: read, evaluate, sign.

## Layout

```
plugin.json                     Agent Plugins 1.0.0 manifest with the OpenAI listing metadata
mcp.json                        the hosted MCP server (streamable HTTP, no key)
skills/insumer-hosted-tools/    how to use the ten hosted tools and the shared daily allowance
skills/insumer-auth/            the five REST skills, vendored from insumer-agent-skills
skills/insumer-attest/
skills/insumer-trust/
skills/insumer-trust-batch/
skills/insumer-jwks-verify/
assets/icon.png                 512 x 512
SKILLS_SOURCE                   the insumer-agent-skills commit the skills were vendored from
```

## Build

```bash
./build.sh
```

Vendors the five REST skills from a sibling checkout of [insumer-agent-skills](https://github.com/insumerapi/insumer-agent-skills), validates the manifest limits, scans everything that will ship for secrets and internal names, and writes `dist/insumer-plugin-<version>.zip`. The ZIP is what gets uploaded to the plugin directory.

## The hosted server

The MCP server is the same code as the [mcp-server-insumer](https://github.com/insumerapi/mcp-server-insumer) npm package, served over MCP streamable HTTP on a shared key. It serves ten tools that need no caller identity; the tools that produce signed results share one free daily allowance. For your own allowance, run the package locally with your own key.

Server card: https://insumermodel.com/.well-known/mcp-server-card

## License

MIT. See [LICENSE](LICENSE).
