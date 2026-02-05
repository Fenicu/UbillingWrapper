import json
import logging
import xml.etree.ElementTree as ET

from pydantic import BaseModel

from pyubilling.exceptions import UbillingParseError

_logger = logging.getLogger(__name__)


def _parse_json(raw: bytes) -> dict | list:
    return json.loads(raw)


def _parse_xml_single(raw: bytes, root_tag: str) -> dict | None:
    root = ET.fromstring(raw)
    for element in root.iter(root_tag):
        result = {}
        for child in element:
            if child.text is not None:
                result[child.tag] = child.text
            result.update(child.attrib)
        return result
    return None


def _parse_xml_list(raw: bytes, root_tag: str) -> list[dict]:
    root = ET.fromstring(raw)
    results = []
    for element in root.iter(root_tag):
        row: dict = {}
        for child in element:
            if child.text is not None:
                row[child.tag] = child.text
            row.update(child.attrib)
        results.append(row)
    return results


def parse_single[T: BaseModel](raw: bytes, model: type[T], *, root_tag: str) -> T | None:
    """Parse response bytes into a single model instance, or None if empty."""
    try:
        data = _parse_json(raw)
    except (json.JSONDecodeError, ValueError):
        try:
            data = _parse_xml_single(raw, root_tag)
        except ET.ParseError as exc:
            _logger.error("XML parse error: %s, raw response: %r", exc, raw[:500])
            raise UbillingParseError(f"Invalid XML: {exc}") from exc

    if not data:
        return None

    if isinstance(data, list):
        data = data[0] if data else None
        if not data:
            return None

    try:
        return model.model_validate(data)
    except Exception as exc:
        raise UbillingParseError(f"Failed to validate {model.__name__}: {exc}") from exc


def parse_list[T: BaseModel](raw: bytes, model: type[T], *, root_tag: str) -> list[T]:
    """Parse response bytes into a list of model instances."""
    try:
        data = _parse_json(raw)
    except (json.JSONDecodeError, ValueError):
        try:
            data = _parse_xml_list(raw, root_tag)
        except ET.ParseError as exc:
            _logger.error("XML parse error: %s, raw response: %r", exc, raw[:500])
            raise UbillingParseError(f"Invalid XML: {exc}") from exc

    if not data:
        return []

    try:
        return [model.model_validate(item) for item in data]
    except Exception as exc:
        raise UbillingParseError(f"Failed to validate {model.__name__}: {exc}") from exc
