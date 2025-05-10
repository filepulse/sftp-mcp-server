from multiprocessing import Value
from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager

import os
import stat
import paramiko


class SftpClient:
    def __init__(self):
        self._sftp = None
        self._error = None
        self._setup_connection()

    def _setup_connection(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(
                hostname=os.environ["SFTP_HOST"],
                username=os.environ["SFTP_USERNAME"],
                password=os.environ["SFTP_PASSWORD"],
            )

            sftp = ssh.open_sftp()

            self._sftp = sftp

        except KeyError as e:
            raise ValueError(f"Missing environment variable: {e}")
        except Exception as e:
            raise ValueError(f"Connection error: {e}")

    def connected(self):
        return self._sftp and not self._error

    def listdir(self, path: str):
        return self._sftp.listdir(path)

    def rename(self, oldpath: str, newpath: str):
        self._sftp.rename(oldpath, newpath)

    def get(self, path: str):
        fo = self._sftp.file(path, "rb")
        return fo
    
    def open(self, path: str):
        fo = self._sftp.file(path, "wb")
        return fo
    
    def delete(self, path: str):
        if stat.S_ISDIR(self._sftp.stat(path).st_mode):
            self._sftp.rmdir(path)
        else:
            self._sftp.remove(path)

    def mkdir(self, path: str):
        self._sftp.mkdir(path)

    def write(self, path: str, content: str):
        fo = self._sftp.file(path, "wb")
        fo.write(content.encode())
        fo.close()


@asynccontextmanager
async def app_lifespan(server: FastMCP):
    try:
        sftp = SftpClient()

        yield sftp
    finally:
        await sftp.close()


# Create an MCP server
mcp = FastMCP("SFTP", lifespan=app_lifespan)



@mcp.tool(name="retrieve-objects")
def retrieve_files_and_folders(path: str, ctx: Context) -> list[str]:
    """
    Retrieves a list of files and folders from the specified path.
    Args:
        path (str): The path to the directory.
    """
    sftp = ctx.request_context.lifespan_context

    if not sftp.connected:
        raise ValueError(f"SFTP connection not established:" f"{sftp._error}")

    return sftp.listdir(path)


@mcp.tool(name="rename-object")
def rename_object(oldpath: str, newpath: str, ctx: Context) -> bool:
    """
    Renames a file from oldpath to newpath.
    Args:
        oldpath (str): The current path of the file or folder.
        newpath (str): The new path for the file or folder.
    """
    sftp = ctx.request_context.lifespan_context

    if not sftp.connected:
        raise ValueError(f"SFTP connection not established:" f"{sftp._error}")

    sftp.rename(oldpath, newpath)


@mcp.tool(name="delete-object")
def delete_object(path: str, ctx: Context) -> str:
    """
    Deletes a file or folder
    Args: 
        path (str)
    """
    sftp = ctx.request_context.lifespan_context

    if not sftp.connected:
        raise ValueError(f"SFTP connection not established:" f"{sftp._error}")

    # Download the file

    fo = sftp.delete(path)

    return "Item deleted successfully"


@mcp.tool(name="download-file")
def download_file(path: str, ctx: Context) -> str:
    """
    Downloads a file from the specified path.
    Args:
        path (str): The path to the file.
    """
    sftp = ctx.request_context.lifespan_context

    if not sftp.connected:
        raise ValueError(f"SFTP connection not established:" f"{sftp._error}")

    # Download the file

    fo = sftp.get(path)

    return fo.read()

@mcp.tool(name="create-directory")
def create_directory(path: str, ctx: Context) -> str:
    """
    Args:
        path (str): Path to create, system will create non-existing subdirectories.
    """
    sftp = ctx.request_context.lifespan_context

    if not sftp.connected:
        raise ValueError(f"SFTP connection not established:" f"{sftp._error}")
    
    sftp.mkdir(path)

    return "Directory created."


@mcp.tool(name="write-to-file")
def write_to_file(path: str, content: str, ctx: Context) -> bool:
    """
    Writes content to a file at the specified path.
    Args:
        path (str): The path to the file.
        content (str): The content to write to the file.
    """
    sftp = ctx.request_context.lifespan_context

    if not sftp.connected:
        raise ValueError(f"SFTP connection not established:" f"{sftp._error}")

    # Download the file
    fo = sftp.open(path)

    # Write the content to the file
    fo.write(content.encode())

    return "File written successfully"


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
