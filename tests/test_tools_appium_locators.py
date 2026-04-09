import pytest
from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET
from tools.appium_locators import parse_locators, extract_locators


def test_parse_locators_extracts_elements(tmp_path):
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<hierarchy>
  <node resource-id="com.app:id/btn_login" text="Login" class="android.widget.Button" bounds="[0,0][100,50]" content-desc="Login button"/>
  <node resource-id="com.app:id/et_email" text="" class="android.widget.EditText" bounds="[0,60][300,110]" content-desc="Email field"/>
  <node resource-id="" text="" class="android.widget.FrameLayout" bounds="[0,0][1080,1920]" content-desc=""/>
</hierarchy>'''
    xml_file = tmp_path / "ui_dump.xml"
    xml_file.write_text(xml_content)
    locators = parse_locators(str(xml_file))
    assert len(locators) == 2
    assert locators[0]["resource_id"] == "com.app:id/btn_login"
    assert locators[0]["text"] == "Login"
    assert locators[1]["resource_id"] == "com.app:id/et_email"


def test_extract_locators_calls_adb(tmp_path):
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<hierarchy>
  <node resource-id="com.app:id/btn_submit" text="Submit" class="android.widget.Button" bounds="[0,0][100,50]" content-desc=""/>
</hierarchy>'''
    output_path = str(tmp_path / "ui_dump.xml")

    with patch("tools.appium_locators.dump_ui_hierarchy") as mock_dump, \
         patch("tools.appium_locators.parse_locators") as mock_parse:
        mock_dump.return_value = output_path
        mock_parse.return_value = [{"resource_id": "com.app:id/btn_submit", "text": "Submit", "class": "android.widget.Button", "content_desc": "", "bounds": "[0,0][100,50]"}]
        result = extract_locators(output_path)
        mock_dump.assert_called_once_with(output_path)
        mock_parse.assert_called_once_with(output_path)
        assert result[0]["resource_id"] == "com.app:id/btn_submit"
