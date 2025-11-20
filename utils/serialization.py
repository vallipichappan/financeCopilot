import math
from typing import Any, Dict, List, Mapping

import pandas as pd


def maybe_primitive(value: Any) -> Any:
    """Convert pandas/numpy/time values into JSON-serializable primitives."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if hasattr(value, "item"):
        try:
            return maybe_primitive(value.item())
        except Exception:
            pass
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:
            pass
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def format_index_key(key: Any) -> str:
    """Normalize index/column names to strings."""
    if hasattr(key, "isoformat"):
        try:
            return key.isoformat()
        except Exception:
            pass
    return str(key)


def dataframe_to_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Convert a DataFrame to a list of dictionaries with primitive values."""
    if df is None or df.empty:
        return []
    normalised = df.reset_index(drop=False)
    normalised.columns = [format_index_key(col) for col in normalised.columns]
    records: List[Dict[str, Any]] = []
    for record in normalised.to_dict(orient="records"):
        records.append({str(k): maybe_primitive(v) for k, v in record.items()})
    return records


def dataframe_to_nested_dict(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Convert financial statement DataFrame into a nested dict of primitives."""
    if df is None or df.empty:
        return {}
    cleaned = df.copy()
    cleaned.index = [format_index_key(idx) for idx in cleaned.index]
    cleaned.columns = [format_index_key(col) for col in cleaned.columns]
    result: Dict[str, Dict[str, Any]] = {}
    for column, values in cleaned.to_dict().items():
        result[str(column)] = {
            str(idx): maybe_primitive(val) for idx, val in values.items()
        }
    return result


def mapping_to_primitives(mapping: Mapping[str, Any]) -> Dict[str, Any]:
    """Ensure a mapping only contains JSON-friendly primitives."""
    return {str(key): maybe_primitive(value) for key, value in mapping.items()}


