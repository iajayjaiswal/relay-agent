import subprocess
import xml.etree.ElementTree as ET


def dump_ui_hierarchy(output_path: str = "/tmp/ui_dump.xml") -> str:
    """Dumps UI hierarchy from connected Android device via adb."""
    subprocess.run(
        ["adb", "shell", "uiautomator", "dump", "/sdcard/ui_dump.xml"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["adb", "pull", "/sdcard/ui_dump.xml", output_path],
        check=True,
        capture_output=True,
    )
    return output_path


def parse_locators(xml_path: str) -> list[dict]:
    """Parses UI dump XML and extracts element locators."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    locators = []
    for node in root.iter("node"):
        resource_id = node.get("resource-id", "")
        content_desc = node.get("content-desc", "")
        text = node.get("text", "")
        class_name = node.get("class", "")
        bounds = node.get("bounds", "")
        if resource_id or content_desc or text:
            locators.append({
                "resource_id": resource_id,
                "content_desc": content_desc,
                "text": text,
                "class": class_name,
                "bounds": bounds,
            })
    return locators


def extract_locators(output_path: str = "/tmp/ui_dump.xml") -> list[dict]:
    """Full flow: adb dump -> parse -> return locator list."""
    dump_ui_hierarchy(output_path)
    return parse_locators(output_path)
