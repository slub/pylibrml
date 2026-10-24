import json
from pathlib import Path

from model.librml import LibRML

librml_path = Path(__file__).parent.parent.parent / "librml"

xmls = librml_path.glob("examples/*.xml")

for xml in xmls:
    xmlstr = xml.read_text()
    try:
        librml = LibRML.from_xmlstr(xmlstr)
        json_dump = json.dumps(librml.to_dict(), indent=2)
        xml.with_suffix(".json").write_text(json_dump + "\n")
    except Exception as e:
        print(f"Error occurred while processing {xml}: {e}")
