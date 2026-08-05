import json
import logging

from common.errors import TemplateNotValidError
from model.librml import LibRML

logger = logging.getLogger(__name__)


@staticmethod
def from_template(templateid: str, itemid: str, tenant: str = None, **kwargs):
    from tmpl.TemplateManager import TemplateManager
    from jinja2 import Template
    import re
    import json

    tm = TemplateManager()
    if templateid not in tm.templates:
        raise TemplateNotValidError('No template "{}" found.'.format(templateid))

    raw_source = tm.templates[templateid].get("raw_source")
    if not raw_source:
        raise TemplateNotValidError('No template "{}" source found.'.format(templateid))

    args = {}
    if tr := tm.getFillableRestriction(templateid):
        for pftid, pfttype, pftdesc in tr:
            logger.debug("Found {} as restriction, type is {}".format(pftid, pfttype))
            if pftid in kwargs:
                value = kwargs.get(pftid)
                logger.debug("Found value in args for {}: {}".format(pftid, value))
                args[pftid] = value
            else:
                logger.error("Cant find a value for {}".format(pftid))
                args[pftid] = [] if pfttype == "list" else ""

    tmpl = Template(raw_source)
    filled = tmpl.render(args)
    # Clean up trailing commas from Jinja loops to ensure valid JSON
    filled = re.sub(r",\s*\]", "]", filled)
    filled = re.sub(r",\s*\}", "}", filled)

    template = json.loads(filled)

    def clean_empty(data):
        if isinstance(data, dict):
            return {
                k: clean_empty(v) for k, v in data.items() if v is not None and v != ""
            }
        elif isinstance(data, list):
            return [clean_empty(x) for x in data if x is not None and x != ""]
        return data

    template = clean_empty(template)

    ret = LibRML(itemid)
    template.update(id=itemid)
    template.update(tenant=tenant)

    ret.from_dict(template)
    return ret
