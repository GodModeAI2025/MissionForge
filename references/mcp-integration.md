# MCP-Integration — Mission Forge

Inspiriert von claude-codes vollstaendiger MCP-Integration mit 25 Dateien,
OAuth, Transports und Registry.

---

## Konzept

Das Model Context Protocol (MCP) ermoeglicht MissionForge-Agenten den Zugriff
auf externe Systeme ueber standardisierte Schnittstellen — ohne Custom-Scripts.

## MCP als Skill-Typ

Ein MCP-Server wird als spezieller Skill-Typ in MissionForge eingebunden:

```yaml
# .mission-forge/skills/github-api/SKILL.md
---
name: github-api
description: "GitHub API Zugriff via MCP-Server"
version: "1.0.0"
type: mcp                              # NEU: Skill-Typ "mcp"
mcp:
  server: "@modelcontextprotocol/server-github"
  transport: stdio                      # stdio | sse | streamable-http
  env:
    GITHUB_TOKEN: "${GITHUB_TOKEN}"     # Aus Umgebungsvariable
  tools:                                # Verfuegbare MCP-Tools
    - create_issue
    - search_repositories
    - get_file_contents
---

# GitHub API

## Wann verwenden
Wenn ein Agent GitHub-Repositories durchsuchen, Issues erstellen oder
Dateiinhalte lesen muss.

## Verfuegbare Tools
- `create_issue`: Erstellt ein GitHub-Issue
- `search_repositories`: Durchsucht Repositories
- `get_file_contents`: Liest Dateiinhalte aus einem Repository
```

## MCP-Server Konfiguration

In der Projekt- oder User-Config:

```yaml
# .mission-forge/config.yaml
mcp-servers:
  github:
    command: npx
    args: ["@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "${GITHUB_TOKEN}"

  database:
    command: npx
    args: ["@modelcontextprotocol/server-postgres"]
    env:
      DATABASE_URL: "${DATABASE_URL}"

  filesystem:
    command: npx
    args: ["@modelcontextprotocol/server-filesystem"]
    args-extra: ["/path/to/allowed/dir"]
```

## Agent-Zuweisung

Agenten deklarieren MCP-Tool-Abhaengigkeiten in ihrem Manifest:

```yaml
# agents/data-analyst/AGENTS.md
---
skills:
  - database-query          # MCP-Skill
  - code-review             # Regulaerer Skill
metadata:
  tools-allowed: "Read Glob Grep mcp:database:query mcp:database:list_tables"
---
```

**Namenskonvention fuer MCP-Tools**: `mcp:<server-name>:<tool-name>`

## Pre-Flight Validierung

Der Orchestrator prueft vor dem Spawnen:

1. **Server verfuegbar**: Ist der MCP-Server installiert/erreichbar?
2. **Credentials vorhanden**: Sind alle `env`-Variablen gesetzt?
3. **Tools erlaubt**: Sind die angeforderten MCP-Tools im Permission-Profile?
4. **Transport kompatibel**: Ist der Transport-Typ in der Umgebung verfuegbar?

## AuditChain-Integration

MCP-Aufrufe werden in der AuditChain protokolliert:

```json
{
  "event": "MCP_TOOL_CALL",
  "ref": "WP-003",
  "agent": "data-analyst",
  "data": {
    "server": "database",
    "tool": "query",
    "input_hash": "sha256:...",
    "output_hash": "sha256:..."
  }
}
```

## Sicherheit

- MCP-Server laufen in separaten Prozessen
- Credentials werden NICHT in Manifesten gespeichert (nur Env-Referenzen)
- Permission-Profile begrenzen welche MCP-Tools ein Agent nutzen darf
- Im `enterprise`-Modus: Alle MCP-Aufrufe muessen durch Gate-Check
