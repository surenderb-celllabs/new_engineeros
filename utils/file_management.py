# load_file.py

import os
import json
import csv
import yaml
import xml.etree.ElementTree as ET
import pandas as pd
from typing import Any, Dict, List, Union, Optional
from xml.etree.ElementTree import Element


def load_file(file_name: str) -> Any:
    """
    Load a file based on its extension and return its data.

    Supported types:
        - .csv  → List[Dict[str, str]]
        - .json → Dict[str, Any] | List[Any]
        - .txt  → List[str]
        - .xlsx/.xls → pandas.DataFrame
        - .yaml/.yml → Dict[str, Any] | List[Any]
        - .xml  → xml.etree.ElementTree.Element

    Returns:
        Parsed file data in the format corresponding to file type.
    """
    if not os.path.exists(file_name):
        raise FileNotFoundError(f"File not found: {file_name}")

    _, ext = os.path.splitext(file_name)
    ext = ext.lower()

    if ext == ".csv":
        return load_csv(file_name)
    elif ext == ".json":
        return load_json(file_name)
    elif ext == ".txt":
        return load_txt(file_name)
    elif ext in [".xlsx", ".xls"]:
        return load_excel(file_name)
    elif ext in [".yaml", ".yml"]:
        return load_yaml(file_name)
    elif ext == ".xml":
        return load_xml(file_name)
    elif ext == "md":
        return load_md(file_name)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def load_csv(file_name: str) -> List[Dict[str, str]]:
    """Load a CSV file into a list of dictionaries."""
    with open(file_name, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)


def load_json(file_name: str) -> Union[Dict[str, Any], List[Any]]:
    """Load a JSON file into a Python dict or list."""
    with open(file_name, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_txt(file_name: str) -> List[str]:
    """Load a text file as a list of lines (List[str])."""
    with open(file_name, 'r', encoding='utf-8') as f:
        return f.read().splitlines()


def load_excel(file_name: str) -> pd.DataFrame:
    """Load an Excel file into a pandas DataFrame."""
    return pd.read_excel(file_name)


def load_yaml(file_name: str) -> Union[Dict[str, Any], List[Any]]:
    """Load a YAML file into a dict or list."""
    with open(file_name, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_xml(file_name: str) -> Element:
    """Load and parse an XML file into an ElementTree Element."""
    tree = ET.parse(file_name)
    return tree.getroot()

def load_md(file_name):
    """Load the entire Markdown (.md) file as a raw string."""
    with open(file_name, "r", encoding="utf-8") as f:
        return f.read()



def save_file(file_name: str, data: Any) -> None:
    """
    Save data to a file based on its extension.

    Supported types:
        - .csv  → List[Dict[str, Any]] or pandas.DataFrame
        - .json → Dict[str, Any] or List[Any]
        - .txt  → List[str] or str
        - .xlsx/.xls → pandas.DataFrame
        - .yaml/.yml → Dict[str, Any] or List[Any]
        - .xml  → xml.etree.ElementTree.Element

    Args:
        file_name: Name of the output file (with extension)
        data: Data to be saved (type depends on file format)
    """
    _, ext = file_name.lower().rsplit(".", 1)

    if ext == "csv":
        save_csv(file_name, data)
    elif ext == "json":
        save_json(file_name, data)
    elif ext == "txt":
        save_txt(file_name, data)
    elif ext in ["xlsx", "xls"]:
        save_excel(file_name, data)
    elif ext in ["yaml", "yml"]:
        save_yaml(file_name, data)
    elif ext == "xml":
        save_xml(file_name, data)
    elif ext == "md":
        save_md(file_name, data)
    else:
        raise ValueError(f"Unsupported file type: .{ext}")


def save_md(file_name, data):
    """Save a raw string directly into a Markdown (.md) file."""
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(str(data))


def save_csv(file_name: str, data: Union[List[Dict[str, Any]], pd.DataFrame]) -> None:
    """Save data to a CSV file."""
    if isinstance(data, pd.DataFrame):
        data.to_csv(file_name, index=False)
    elif isinstance(data, list) and all(isinstance(row, dict) for row in data):
        with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    else:
        raise TypeError("CSV data must be a pandas.DataFrame or list of dictionaries.")


def save_json(file_name: str, data: Union[Dict[str, Any], List[Any]]) -> None:
    """Save data as a JSON file."""
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def save_txt(file_name: str, data: Union[List[str], str]) -> None:
    """Save text data to a .txt file."""
    with open(file_name, 'w', encoding='utf-8') as f:
        if isinstance(data, list):
            f.write("\n".join(map(str, data)))
        elif isinstance(data, str):
            f.write(data)
        else:
            raise TypeError("TXT data must be a string or list of strings.")


def save_excel(file_name: str, data: pd.DataFrame) -> None:
    """Save a pandas DataFrame to an Excel file."""
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Excel data must be a pandas DataFrame.")
    data.to_excel(file_name, index=False)


def save_yaml(file_name: str, data: Union[Dict[str, Any], List[Any]]) -> None:
    """Save data to a YAML file."""
    with open(file_name, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def save_xml(file_name: str, data: Element) -> None:
    """Save an XML ElementTree Element to an XML file."""
    if not isinstance(data, ET.Element):
        raise TypeError("XML data must be an xml.etree.ElementTree.Element.")
    tree = ET.ElementTree(data)
    tree.write(file_name, encoding='utf-8', xml_declaration=True)

#
# if __name__ == "__main__":
#     # Example usage
#     test_data = {"name": "ChatGPT", "version": "GPT-5"}
#     test_file = "output.json"
#
#     try:
#         save_file(test_file, test_data)
#         print(f"Saved data successfully to {test_file}")
#     except Exception as e:
#         print(f"Error: {e}")


