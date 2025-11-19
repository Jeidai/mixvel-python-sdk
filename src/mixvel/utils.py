# -*- coding: utf-8 -*-

"""General utility helpers used across the SDK."""

from __future__ import annotations

from xml.etree import ElementTree as ET


def strip_namespaces(root: ET.Element) -> ET.Element:
    """Remove XML namespaces in-place so XPath-like queries stay simple."""

    for elem in root.iter():
        if not isinstance(elem.tag, str):
            continue
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]
    return root


# Backwards compatibility for third-party code that relied on the old helper.
def lxml_remove_namespaces(root: ET.Element) -> ET.Element:
    """Deprecated alias that now calls :func:`strip_namespaces`."""

    return strip_namespaces(root)
