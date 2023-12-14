import json
from typing import List


def html_chunker(rows: List, chunk_size: int = 10) -> List[List]:
    """
    Chunk a list of rows into smaller lists with a specified chunk size.

    Parameters:
    - rows (List): The list of rows to be chunked.
    - chunk_size (int): The size of each chunk. Default is 10.

    Returns:
    - List[List]: A list of lists, each containing a chunk of rows.
    """
    header_row = [rows[0]]
    chunks = [
        header_row + rows[i : i + chunk_size] for i in range(1, len(rows), chunk_size)
    ]

    return chunks


def html_to_str(chunk: List) -> str:
    """
    Convert a chunk of HTML rows to a formatted string.

    Parameters:
    - chunk (List): A chunk of HTML rows.

    Returns:
    - str: A formatted string representation of the chunk.
    """
    return "\n\n".join(list(map(str, chunk)))


def save_json(output, filepath: str = "../output.json") -> None:
    """
    Save JSON-formatted data to a file.

    Parameters:
    - output: The JSON-formatted data to be saved.
    - filepath (str): The file path where the JSON data will be saved. Default is "../output.json".
    """
    with open(filepath, "w") as f:
        json.dump(json.loads(output), f, indent=4)
