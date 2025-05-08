<p align="center">
  <img src="https://www.filepulse.io/assets/img/filepulse-dark.png" alt="SFTP MCP Server" width="200"/>
</p>

<h1 align="center">SFTP MCP Server</h1>

<p align="center">
  MCP (ModelContextProtcol) Server to connect an SFTP Server
</p>

---

## 🚀 Overview

Supported features
- Download/Upload files
- List files/folders
- Rename files
- Delete files/folders
- Create directories
- Move files/folders

---

## 📚 Documentation

👉 Full documentation is available at:  
**[https://your-documentation-url.com](https://your-documentation-url.com)**

The documentation covers the setup and integration in Claude desktop.

---

## 🛠️ Running in development mode

If UV is not yet installed, run;

```bash
On MAC: curl -LsSf https://astral.sh/uv/install.sh | sh

On Windows: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Install the necessary packages with; 

```bash
uv sync
```



Lastly, use the configuration below in the Claude desktop config file;

```json
{
  "mcpServers": {
    "sftp": {
      "command": "uv",
      "args": [
        "--directory",
        "PATH_TO_REPOSITORY/sftp-mcp-server",
        "run",
        "main.py"
      ],
      "env": {
        "SFTP_HOST": "",
        "SFTP_USERNAME": "",
        "SFTP_PASSWORD": ""
      }
    }
  }
}
```