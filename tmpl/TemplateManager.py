import json
import logging
import pathlib

from config import Config
from jinja2 import FileSystemLoader, meta
from jinja2.nativetypes import NativeEnvironment

from common.errors import TemplateNotValidError

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MetaInformation():
    templateid = None
    templatename = None
    description = None
    variables = {}

    def __init__(self, template_name: pathlib.Path):
        metafilename = template_name.stem + ".meta.json"
        p = template_name.parent
        metafile = pathlib.Path(p.resolve() / metafilename)
        if metafile.is_file():
            with metafile.open(encoding='utf-8') as file:
                self.data = json.load(file)
                logger.debug('Read metainfo from {}'.format(metafile.resolve()))
                self.templateid = self.data['template']
                self.templatename = self.data['readablename']
                self.description = self.data['description']
                if 'variables' in self.data:
                    self.variables = {}
                    for var in self.data['variables']:
                        name = var['name'] if 'name' in var else None
                        datatype = var['datatype'] if 'datatype' in var else None
                        readablename = var['readablename'] if 'readablename' in var else None
                        description = var['description'] if 'description' in var else None
                        source = var['source'] if 'source' in var else None
                        self.variables[name] = dict(datatype=datatype,
                                                    readablename=readablename,
                                                    description=description,
                                                    source=source)
        else:
            logger.warning('Could not find {}, no metainformation for {} available!'.format(metafile, template_name))
            raise TemplateNotValidError('Template ``{}`` has no metainformation sidecar-file.'.format(metafile))

    def getVarInfo(self, varname: str):
        if self.variables[varname]:
            return self.variables[varname]['readablename'], \
                   self.variables[varname]['datatype'], \
                   self.variables[varname]['description'], \
                   self.variables[varname]['source']

    def getInfo(self):
        return self.templateid, self.templatename, self.description

    def getID(self):
        return self.templateid


class TemplateManager(object):
    __instance = None

    def __init__(self):
        self.templates = {}
        T_PATH = Config.TEMPLATE_PATH
        env = NativeEnvironment(loader=FileSystemLoader(T_PATH))
        templates = env.list_templates('.jinja')
        for template_name in templates:
            try:
                template_source = env.loader.get_source(env, template_name)[0]
                parsed_content = env.parse(template_source)
                vars = meta.find_undeclared_variables(parsed_content)
                logger.info('Template: {}'.format(template_name))
                metainfo = MetaInformation(pathlib.Path(T_PATH / template_name))
                variables = []
                for var in vars:
                    logger.info('.. Variable: {}'.format(var))
                    if metainfo:
                        readablename, datatype, description, source = metainfo.getVarInfo(var)
                        variables.append(
                            dict(variable=var,
                                 readablename=readablename,
                                 datatype=datatype,
                                 description=description,
                                 source=source))
                tid, tname, description = metainfo.getInfo()
                if tname is None:
                    tname = template_name
                if description is None:
                    description = 'No metainfo-file for this template, create one!'
                self.templates[tid] = dict(id=tid,
                                           templatename=tname,
                                           description=description,
                                           vars=variables)
            except TemplateNotValidError as error:
                logger.error('Can not load template from filesystem: {}'.format(template_name))

    def __new__(cls, *args, **kwargs):
        if TemplateManager.__instance == None:
            logger.debug("TemplateManager init.")
            TemplateManager.__instance = object.__new__(cls)
            TemplateManager.__instance.__init__()
        else:
            logger.debug("TemplateManager reuse.")
        return TemplateManager.__instance

    def getTemplateList(self):
        return list(self.templates.keys())

    def getTemplateMeta(self, template):
        return self.templates.get(template)


if __name__ == '__main__':
    pass
