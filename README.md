# Python LibRML

This is a Python implementation of **LibRML** (Library Rights Machine-readable Language), a model for formal description of permissions and restrictions for digital objects.

LibRML is designed to be low-complexity and tailored for cultural heritage institutions. It focuses on the technical representation of permissions that can be automatically enforced within a system.

## Features

- **LibRML v0.5.0 Support**: Fully compliant with the latest LibRML specification.
- **JSON & XML Support**: Easily convert between Python objects, JSON, and XML.
- **Header & Actions**: Support for general object properties (copyright, commercial use, etc.) and specific usage actions (read, download, print, etc.).
- **Restrictions**: Fine-grained control with restrictions like date ranges, age, location, concurrent sessions, quality (resolution, dimension), and more.
- **Python 3.10+ Modernization**: Uses modern Python features and type hinting.

## Installation

```bash
pip install .
```

## Usage

### Creating a LibRML Object

```python
from datetime import date
from model.librml import LibRML, Action, ActionType, Restriction, RestrictionType

# Create a LibRML object with an ID
librml = LibRML(itemid="id-123456")

# Set general properties
librml.tenant = "https://www.slub-dresden.de/"
librml.copyright = True
librml.commercialuse = False

# Add an action with a restriction
librml.actions.append(
    Action(
        type=ActionType.READ,
        permission=True,
        restrictions=[
            Restriction(
                res_type=RestrictionType.DATE,
                fromdate=date(2026, 2, 11)
            ),
            Restriction(
                res_type=RestrictionType.QUALITY,
                maxdimension=1080
            )
        ]
    )
)
```

### Exporting to JSON and XML

```python
import json

# Export to Dictionary/JSON
print(json.dumps(librml.to_dict(), indent=4))

# Export to XML
print(librml.to_xml())
```

### Loading from JSON or XML

```python
# From JSON string
librml_from_json = LibRML.from_jsonstr(json_string)

# From XML string
librml_obj = LibRML.from_xmlstr(xml_string)
```

## Project Structure

- `model/`: Core LibRML model implementation (`librml.py`, `names.py`).
- `common/`: Common utilities and error definitions.
- `tmpl/`: Template management for LibRML (using Jinja2).
- `examples/`: Example scripts demonstrating how to use the library.
- `sample-templates/`: Sample LibRML templates in Jinja2 format.

## Requirements

- Python >= 3.10
- jinja2

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
