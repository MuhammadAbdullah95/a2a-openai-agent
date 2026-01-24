from mcp.server.fastmcp import FastMCP
import os

mcp = FastMCP("filesystem_server")
DEFAULT_WORKSPACE = os.path.expanduser("~/mcp/content_workspace")


@mcp.tool("write_file")
async def write_file(filepath: str, content: str) -> str:
    """
    Write content to a file in the workspace.

    Args:
        filepath (str): Relative path within the workspace to write to.
        content (str): The content to write to the file.

    Returns:
        str: Confirmation message with the full path written.
    """
    full_path = os.path.join(DEFAULT_WORKSPACE, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File written successfully: {full_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@mcp.tool("read_file")
async def read_file(filepath: str) -> str:
    """
    Read content from a file in the workspace.

    Args:
        filepath (str): Relative path within the workspace to read from.

    Returns:
        str: The content of the file, or an error message.
    """
    full_path = os.path.join(DEFAULT_WORKSPACE, filepath)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"File not found: {full_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@mcp.tool("list_files")
async def list_files(directory: str = "") -> str:
    """
    List files in a directory within the workspace.

    Args:
        directory (str): Relative path within the workspace to list.
            Defaults to the workspace root.

    Returns:
        str: Newline-separated list of files, or an error message.
    """
    full_path = os.path.join(DEFAULT_WORKSPACE, directory)
    try:
        if not os.path.exists(full_path):
            os.makedirs(full_path, exist_ok=True)
            return "(empty directory)"
        entries = os.listdir(full_path)
        if not entries:
            return "(empty directory)"
        return "\n".join(entries)
    except Exception as e:
        return f"Error listing files: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
