import json
from datetime import date

from model.librml import LibRML, Action, ActionType, Restriction, RestrictionType

if __name__ == '__main__':
    id = 'id-123456'
    # create empty LibRML-Object with a id
    librml = LibRML(itemid=id)

    # set some attributes
    librml.tenant = 'http://slub-dresden.de'
    librml.sharealike = True
    librml.mention = True

    print('Output after creation and setting some attributes:')
    print(json.dumps(librml.to_dict(), indent=4))

    # Add a action and a restriction
    librml.actions.append(
        Action(
            type=ActionType.READ,
            restrictions=[
                Restriction(
                    res_type=RestrictionType.DATE,
                    fromdate=date(year=2026, month=2, day=11))
            ],
        )
    )

    print('Output after a action with a restriction:')
    print(json.dumps(librml.to_dict(), indent=4))

    # The same works with a json
    download_restriction = {
        "type": "download",
        "restrictions": [
            {
                "type": "date",
                "fromdate": "2026-02-11"
            }
        ]
    }
    librml.actions.append(Action.from_dict(download_restriction))

    print('Output after a json:')
    print(json.dumps(librml.to_dict(), indent=4))
