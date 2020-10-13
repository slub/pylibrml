import json
import logging

from common.errors import TemplateNotValidError
from model.librml import LibRML

logger = logging.getLogger(__name__)


@staticmethod
def from_template(templateid: str, itemid: str, tenant: str = None, **kwargs):
    from tmpl.TemplateManager import TemplateManager
    from jinja2 import Template

    tm = TemplateManager()
    if template := tm.getTemplate(templateid):
        args = {}
        if tr := tm.getFillableRestriction(templateid):
            for pftid, pfttype, pftdesc in tr:
                logger.debug('Found {} as restriction, type is {}'.format(pftid, pfttype))
                if pftid in kwargs:
                    value = kwargs.get(pftid)
                    logger.debug('Found value in args for {}: {}'.format(pftid, value))
                    args[pftid] = value
                else:
                    logger.error('Can''t find a value for {}'.format(pftid))
            tmpl_json = json.dumps(template)
            tmpl = Template(tmpl_json)
            filled = tmpl.render(args)
            template = json.loads(filled)

            ret = LibRML(itemid)
            template.update(id=itemid)
            template.update(tenant=tenant)

            ret.from_dict(template)
        else:
            ret = LibRML(itemid)
            template.update(id=itemid)
            template.update(tenant=tenant)

            ret.from_dict(template)

        return ret

    else:
        raise TemplateNotValidError('No template "{}" found.'.format(templateid))
