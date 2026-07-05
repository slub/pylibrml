import collections.abc
import json
import logging
import xml.etree.ElementTree as ET
from datetime import date
from enum import Enum, unique

from common.errors import LibRMLNotValidError
from model.names import SUBNET, GROUPS, PERCENTAGE, MINAGE, MAXAGE, INSIDE, OUTSIDE, FROMDATE, TODATE, \
    MAXDURATION, COUNT, SESSIONS, WATERMARK, COMMERCIAL, NONCOMMERCIAL, MAXRES, MAXBIT, MAXDIMENSION, \
    AGREEMENTREQ, TYPE, XRESTRICTION, XPART, XGROUP, XSUBNET, PERMISSION, RESTRICTIONS, XACTION, TENANT, \
    MENTION, SHARE, USAGEGUIDE, ACTIONS, LIBRML, ITEM, ID, VERSION, TEMPLATE, COPYRIGHT, RELATEDIDS, RELATEDID

logger = logging.getLogger(__name__)


class TypedList(collections.abc.MutableSequence):
    def __init__(self, oktypes, *args):
        self.oktypes = oktypes
        self.list = list()
        self.extend(list(args))

    def check(self, v):
        if not isinstance(v, self.oktypes):
            raise TypeError(v)

    def __len__(self):
        return len(self.list)

    def __getitem__(self, i):
        return self.list[i]

    def __delitem__(self, i):
        del self.list[i]

    def __setitem__(self, i, v):
        self.check(v)
        self.list[i] = v

    def insert(self, i, v):
        self.check(v)
        self.list.insert(i, v)

    def __str__(self):
        return str(self.list)


@unique
class ActionType(Enum):
    DISPLAYMETADATA = 1
    READ = 2
    RUN = 3
    LEND = 4
    DOWNLOAD = 5
    PRINT = 6
    REPRODUCE = 7
    MODIFY = 8
    REUSE = 9
    DISTRIBUTE = 10
    PUBLISH = 11
    ARCHIVE = 12
    INDEX = 13
    MOVE = 14

    @classmethod
    def fname(cls, name):
        try:
            return [member for membername, member in cls.__members__.items()
                    if member.name.lower() == name.lower()].pop()
        except IndexError:
            raise ValueError('ActionType has no member "{}"'.format(name))

    @classmethod
    def getnames(cls):
        return [name.lower() for name, member in cls.__members__.items()]


@unique
class RestrictionType(Enum):
    PARTS = 1
    GROUP = 2
    AGE = 3
    LOCATION = 4
    DATE = 5
    DURATION = 6
    COUNT = 7
    CONCURRENT = 8
    WATERMARK = 9
    COMMERCIALUSE = 10
    QUALITY = 11
    AGREEMENT = 12

    @classmethod
    def fname(cls, name):
        try:
            return [member for membername, member in cls.__members__.items()
                    if member.name.lower() == name.lower()].pop()
        except IndexError:
            raise ValueError('RestrictionType has no member "{}"'.format(name))

    @classmethod
    def getnames(cls):
        return [name.lower() for name, member in cls.__members__.items()]


class Restriction:
    def __init__(self, res_type: RestrictionType, subnet: list[str] | None = None, groups: list[str] | None = None,
                 percentage: int | None = None, minage: int | None = None, maxage: int | None = None,
                 inside: str | None = None, outside: str | None = None, 
                 fromdate: date | None = None, todate: date | None = None, maxduration: int | None = None,
                 count: int | None = None, sessions: int | None = None,
                 watermarkvalue: str | None = None, commercialuse: bool | None = None,
                 noncommercialuse: bool | None = None, maxresolution: int | None = None,
                 maxbitrate: int | None = None, maxdimension: int | None = None,
                 agreement_required: bool | None = None):

        if res_type in RestrictionType:
            self.type = res_type
        else:
            raise TypeError()

        self.subnet = subnet if subnet is not None else []
        self.groups = groups if groups is not None else []
        self.percentage = percentage
        self.minage = minage
        self.maxage = maxage
        self.inside = inside
        self.outside = outside
        self.fromdate = fromdate
        self.todate = todate
        self.maxduration = maxduration
        self.count = count
        self.sessions = sessions
        self.watermarkvalue = watermarkvalue
        self.commercialuse = commercialuse
        self.noncommercialuse = noncommercialuse
        self.maxresolution = maxresolution
        self.maxbitrate = maxbitrate
        self.maxdimension = maxdimension
        self.agreement_required = agreement_required

    def to_dict(self):
        if self.type == RestrictionType.PARTS:
            if self.percentage:
                return {TYPE: self.type.name.lower(), PERCENTAGE: int(self.percentage)}
        elif self.type == RestrictionType.GROUP:
            if len(self.groups) > 0:
                return {TYPE: self.type.name.lower(), GROUPS: self.groups}
        elif self.type == RestrictionType.AGE:
            out = {TYPE: self.type.name.lower()}
            if self.minage:
                out[MINAGE] = self.minage
            if self.maxage:
                out[MAXAGE] = self.maxage
            if self.minage or self.maxage:
                return out
        elif self.type == RestrictionType.LOCATION:
            out = {TYPE: self.type.name.lower()}
            if self.inside:
                out[INSIDE] = self.inside
            if self.outside:
                out[OUTSIDE] = self.outside
            if len(self.subnet) > 0:
                out[SUBNET] = self.subnet
            if self.inside or self.outside or len(self.subnet) > 0:
                return out
        elif self.type == RestrictionType.DATE:
            out = {TYPE: self.type.name.lower()}
            if self.fromdate:
                out[FROMDATE] = str(self.fromdate)
            if self.todate:
                out[TODATE] = str(self.todate)
            if self.todate or self.fromdate:
                return out
        elif self.type == RestrictionType.DURATION:
            if self.maxduration:
                return {TYPE: self.type.name.lower(), MAXDURATION: int(self.maxduration)}
        elif self.type == RestrictionType.COUNT:
            if self.count:
                return {TYPE: self.type.name.lower(), COUNT: int(self.count)}
        elif self.type == RestrictionType.CONCURRENT:
            if self.sessions:
                return {TYPE: self.type.name.lower(), SESSIONS: int(self.sessions)}
        elif self.type == RestrictionType.WATERMARK:
            if self.watermarkvalue:
                return {TYPE: self.type.name.lower(), WATERMARK: self.watermarkvalue}
        elif self.type == RestrictionType.COMMERCIALUSE:
            out = {TYPE: self.type.name.lower()}
            if self.commercialuse is not None:
                out[COMMERCIAL] = self.commercialuse
            if self.noncommercialuse is not None:
                out[NONCOMMERCIAL] = self.noncommercialuse
            if self.commercialuse is not None or self.noncommercialuse is not None:
                return out
        elif self.type == RestrictionType.QUALITY:
            out = {TYPE: self.type.name.lower()}
            if self.maxresolution:
                out[MAXRES] = int(self.maxresolution)
            if self.maxbitrate:
                out[MAXBIT] = int(self.maxbitrate)
            if self.maxdimension:
                out[MAXDIMENSION] = int(self.maxdimension)
            if self.maxresolution or self.maxbitrate or self.maxdimension:
                return out
        elif self.type == RestrictionType.AGREEMENT:
            if self.agreement_required is not None:
                return {TYPE: self.type.name.lower(), AGREEMENTREQ: self.agreement_required}

    def to_xml(self):
        x = ET.Element(XRESTRICTION, {TYPE: self.type.name.lower()})

        if self.type == RestrictionType.PARTS:
            if self.percentage:
                x.set(PERCENTAGE, str(self.percentage))
            for part in self.parts:
                p = ET.SubElement(x, XPART)
                p.text = part
        elif self.type == RestrictionType.GROUP:
            for group in self.groups:
                g = ET.SubElement(x, XGROUP)
                g.text = group
        elif self.type == RestrictionType.AGE:
            if self.minage:
                x.set(MINAGE, str(self.minage))
            if self.maxage:
                x.set(MAXAGE, str(self.maxage))
        elif self.type == RestrictionType.LOCATION:
            if self.inside:
                x.set(INSIDE, self.inside)
            if self.outside:
                x.set(OUTSIDE, self.outside)
            for n in self.subnet:
                xn = ET.SubElement(x, XSUBNET)
                xn.text = str(n)
        elif self.type == RestrictionType.DATE:
            if self.todate:
                x.set(TODATE, str(self.todate))
            if self.fromdate:
                x.set(FROMDATE, str(self.fromdate))
        elif self.type == RestrictionType.DURATION:
            if self.maxduration:
                x.set(MAXDURATION, str(self.maxduration))
        elif self.type == RestrictionType.COUNT:
            if self.count:
                x.set(COUNT, str(self.count))
        elif self.type == RestrictionType.CONCURRENT:
            if self.sessions:
                x.set(SESSIONS, str(self.sessions))
        elif self.type == RestrictionType.WATERMARK:
            if self.watermarkvalue:
                x.set(WATERMARK, self.watermarkvalue)
        elif self.type == RestrictionType.COMMERCIALUSE:
            if self.commercialuse is not None:
                x.set(COMMERCIAL, str(self.commercialuse).lower())
            if self.noncommercialuse is not None:
                x.set(NONCOMMERCIAL, str(self.noncommercialuse).lower())
        elif self.type == RestrictionType.QUALITY:
            if self.maxbitrate:
                x.set(MAXBIT, str(self.maxbitrate))
            if self.maxresolution:
                x.set(MAXRES, str(self.maxresolution))
            if self.maxdimension:
                x.set(MAXDIMENSION, str(self.maxdimension))
        elif self.type == RestrictionType.AGREEMENT:
            if self.agreement_required is not None:
                x.set(AGREEMENTREQ, str(self.agreement_required).lower())
        else:
            return None

        return x

    def from_dict(self, restriction):
        if PERCENTAGE in restriction:
            self.percentage = int(restriction[PERCENTAGE])
        if GROUPS in restriction:
            self.groups = restriction[GROUPS]
        if MINAGE in restriction:
            self.minage = int(restriction[MINAGE])
        if MAXAGE in restriction:
            self.maxage = int(restriction[MAXAGE])
        if INSIDE in restriction:
            self.inside = restriction[INSIDE]
        if OUTSIDE in restriction:
            self.outside = restriction[OUTSIDE]
        if SUBNET in restriction:
            self.subnet = restriction[SUBNET]
        if FROMDATE in restriction:
            self.fromdate = date.fromisoformat(restriction[FROMDATE])
        if TODATE in restriction:
            self.todate = date.fromisoformat(restriction[TODATE])
        if MAXDURATION in restriction:
            self.maxduration = int(restriction[MAXDURATION])
        if COUNT in restriction:
            self.count = int(restriction[COUNT])
        if SESSIONS in restriction:
            self.sessions = int(restriction[SESSIONS])
        if WATERMARK in restriction:
            self.watermarkvalue = restriction[WATERMARK]
        if COMMERCIAL in restriction:
            self.commercialuse = restriction[COMMERCIAL]
        if NONCOMMERCIAL in restriction:
            self.noncommercialuse = restriction[NONCOMMERCIAL]
        if MAXRES in restriction:
            self.maxresolution = int(restriction[MAXRES])
        if MAXBIT in restriction:
            self.maxbitrate = int(restriction[MAXBIT])
        if MAXDIMENSION in restriction:
            self.maxdimension = int(restriction[MAXDIMENSION])
        if AGREEMENTREQ in restriction:
            self.agreement_required = restriction[AGREEMENTREQ]

    def from_xml(self, restriction_node):
        if self.type == RestrictionType.PARTS:
            if restriction_node.attrib.get(PERCENTAGE):
                self.percentage = int(restriction_node.attrib.get(PERCENTAGE))
            for part in restriction_node.iterfind(XPART):
                self.parts.append(part.text)
        if self.type == RestrictionType.GROUP:
            for group in restriction_node.iterfind(XGROUP):
                self.groups.append(group.text)
        if self.type == RestrictionType.AGE:
            if restriction_node.attrib.get(MINAGE):
                self.minage = int(restriction_node.attrib.get(MINAGE))
            if restriction_node.attrib.get(MAXAGE):
                self.maxage = int(restriction_node.attrib.get(MAXAGE))
        if self.type == RestrictionType.LOCATION:
            self.inside = restriction_node.attrib.get(INSIDE)
            self.outside = restriction_node.attrib.get(OUTSIDE)
            for subnet in restriction_node.iterfind(XSUBNET):
                self.subnet.append(subnet.text)
        if self.type == RestrictionType.DATE:
            if restriction_node.attrib.get(FROMDATE):
                self.fromdate = date.fromisoformat(restriction_node.attrib.get(FROMDATE))
            if restriction_node.attrib.get(TODATE):
                self.todate = date.fromisoformat(restriction_node.attrib.get(TODATE))
        if self.type == RestrictionType.DURATION:
            self.maxduration = int(restriction_node.attrib.get(MAXDURATION))
        if self.type == RestrictionType.COUNT:
            self.count = int(restriction_node.attrib.get(COUNT))
        if self.type == RestrictionType.CONCURRENT:
            self.sessions = int(restriction_node.attrib.get(SESSIONS))
        if self.type == RestrictionType.WATERMARK:
            self.watermarkvalue = restriction_node.attrib.get(WATERMARK)
        if self.type == RestrictionType.COMMERCIALUSE:
            if restriction_node.attrib.get(COMMERCIAL):
                self.commercialuse = restriction_node.attrib.get(COMMERCIAL) == 'true'
            if restriction_node.attrib.get(NONCOMMERCIAL):
                self.noncommercialuse = restriction_node.attrib.get(NONCOMMERCIAL) == 'true'
        if self.type == RestrictionType.QUALITY:
            if restriction_node.attrib.get(MAXBIT):
                self.maxbitrate = int(restriction_node.attrib.get(MAXBIT))
            if restriction_node.attrib.get(MAXRES):
                self.maxresolution = int(restriction_node.attrib.get(MAXRES))
            if restriction_node.attrib.get(MAXDIMENSION):
                self.maxdimension = int(restriction_node.attrib.get(MAXDIMENSION))
        if self.type == RestrictionType.AGREEMENT:
            self.agreement_required = restriction_node.attrib.get(AGREEMENTREQ) == 'true'


class Action:
    def __init__(self, actiontype: ActionType, permission: bool | None = None, restrictions: list[Restriction] | None = None):
        self.permission = permission
        if restrictions is not None:
            self.restrictions = restrictions
        else:
            self.restrictions = TypedList(Restriction)

        if actiontype in ActionType:
            self.type = actiontype
        else:
            raise TypeError

    def to_json(self):
        output = dict(type=self.type.name.lower())
        if self.permission:
            output[PERMISSION] = self.permission

        if len(self.restrictions) > 0:
            rstring = []
            for restriction in self.restrictions:
                rs = restriction.to_dict()
                if rs:
                    rstring.append(rs)

            output[RESTRICTIONS] = rstring
        return output

    def to_xml(self):
        a = ET.Element(XACTION, {TYPE: self.type.name.lower()})
        if self.permission:
            a.set(PERMISSION, str(self.permission).lower())

        if len(self.restrictions) > 0:
            for restriction in self.restrictions:
                a.append(restriction.to_xml())
        return a

    def from_dict(self, action):
        if PERMISSION in action:
            self.permission = action[PERMISSION]
        if RESTRICTIONS in action:
            restrictions = action[RESTRICTIONS]
            for restriction in restrictions:
                r = Restriction(RestrictionType.fname(restriction[TYPE]))
                r.from_dict(restriction)
                self.restrictions.append(r)

    @staticmethod
    def from_jsonstr(actionjson: str):
        d = json.loads(actionjson)
        t = ActionType.fname(d[TYPE])
        p = d[PERMISSION]
        action = Action(actiontype=t, permission=p)
        action.from_dict(d)
        return action

    def from_xml(self, action_node):
        if PERMISSION in action_node.attrib:
            self.permission = action_node.attrib.get(PERMISSION) == 'true'
        for restriction_node in action_node.iterfind(XRESTRICTION):
            if TYPE in restriction_node.attrib:
                r = Restriction(RestrictionType.fname(restriction_node.attrib.get(TYPE)))
                r.from_xml(restriction_node)
                self.restrictions.append(r)
            else:
                raise LibRMLNotValidError('Restriction inside Action has no attribute "{}".'.format(TYPE))

    @staticmethod
    def from_xmlstr(actionxml: str):
        x = ET.fromstring(actionxml)
        t = ActionType.fname(x.attrib.get(TYPE))
        p = x.attrib.get(PERMISSION) == 'true'
        action = Action(actiontype=t, permission=p)
        action.from_xml(x)
        return action


class LibRML(object):
    def __init__(self,
                 itemid: str | None = None,
                 relatedids: list[str] | None = None,
                 tenant: str | None = None,
                 mention: bool = False,
                 sharealike: bool = False,
                 commercialuse: bool = False,
                 usageguide: str | None = None,
                 template: str | None = None,
                 copyright: bool = False,
                 actions: list[Action] | None = None):
        self.id = itemid
        if relatedids is not None:
            self.relatedids = relatedids
        else:
            self.relatedids = []
        self.tenant = tenant
        self.mention = mention
        self.sharealike = sharealike
        self.usageguide = usageguide
        self.template = template
        self.copyright = copyright
        self.commercialuse = commercialuse
        if actions is not None:
            self.actions = actions
        else:
            self.actions = TypedList(Action)

    def to_dict(self):
        output = {ID: self.id}
        if len(self.relatedids) > 0:
            output[RELATEDIDS] = self.relatedids
        if self.tenant:
            output[TENANT] = self.tenant
        if self.mention:
            output[MENTION] = self.mention
        if self.sharealike:
            output[SHARE] = self.sharealike
        if self.usageguide:
            output[USAGEGUIDE] = self.usageguide
        if self.template:
            output[TEMPLATE] = self.template
        if self.copyright:
            output[COPYRIGHT] = self.copyright
        if self.commercialuse is not None:
            output[COMMERCIAL] = self.commercialuse
        if len(self.actions) > 0:
            astring = []
            for action in self.actions:
                astring.append(action.to_json())
            output[ACTIONS] = astring
        return output

    def to_xml(self):
        root = ET.Element(LIBRML)
        root.set('version', VERSION)
        root.append(ET.Comment(' This XML is created using the libRML Python code '))
        item = ET.SubElement(root, ITEM, {ID: self.id})

        if len(self.relatedids) > 0:
            for rid in self.relatedids:
                ET.SubElement(item, RELATEDID, {ID: rid})
        if self.tenant:
            item.set(TENANT, str(self.tenant))
        if self.mention:
            item.set(MENTION, str(self.mention).lower())
        if self.sharealike:
            item.set(SHARE, str(self.sharealike).lower())
        if self.usageguide:
            item.set(USAGEGUIDE, str(self.usageguide))
        if self.template:
            item.set(TEMPLATE, str(self.template))
        if self.copyright:
            item.set(COPYRIGHT, str(self.copyright).lower())
        if self.commercialuse is not None:
            item.set(COMMERCIAL, str(self.commercialuse).lower())
        if len(self.actions) > 0:
            for action in self.actions:
                item.append(action.to_xml())

        return ET.tostring(root, encoding='unicode', method='xml', xml_declaration=True)

    def from_json(self, json_obj):
        data = json.loads(json_obj)
        self.from_dict(data)

    @staticmethod
    def from_jsonstr(librmljson: str):
        librmldict = json.loads(librmljson)
        itemid = librmldict[ID]
        librml = LibRML(itemid=itemid)
        librml.from_dict(librmldict)
        return librml

    def from_dict(self, data):
        if ID in data:
            self.id = data[ID]
        else:
            raise LibRMLNotValidError('JSON has no attribute {}!'.format(ID))
        if RELATEDIDS in data:
            self.relatedids = data[RELATEDIDS]
        if TENANT in data:
            self.tenant = data[TENANT]
        if MENTION in data:
            self.mention = data[MENTION]
        if SHARE in data:
            self.sharealike = data[SHARE]
        if USAGEGUIDE in data:
            self.usageguide = data[USAGEGUIDE]
        if TEMPLATE in data:
            self.template = data[TEMPLATE]
        if COPYRIGHT in data:
            self.copyright = data[COPYRIGHT]
        if COMMERCIAL in data:
            self.commercialuse = data[COMMERCIAL]
        if ACTIONS in data:
            actions = data[ACTIONS]
            for action in actions:
                a = Action(ActionType.fname(action[TYPE]))
                self.actions.append(a)
                a.from_dict(action)

    @staticmethod
    def from_xmlstr(xmlstr: str):
        xml_tree = ET.ElementTree(ET.fromstring(xmlstr))
        root = xml_tree.getroot()
        if root.tag == LIBRML:
            ie = root.find(ITEM)
            if ie is not None and (ID in ie.attrib or TENANT in ie.attrib):
                librml = LibRML(itemid=ie.attrib.get(ID, ''))
                librml.tenant = ie.attrib.get(TENANT)
                if MENTION in ie.attrib:
                    librml.mention = ie.attrib.get(MENTION) == 'true'
                if SHARE in ie.attrib:
                    librml.sharealike = ie.attrib.get(SHARE) == 'true'
                if USAGEGUIDE in ie.attrib:
                    librml.usageguide = ie.attrib.get(USAGEGUIDE)
                if TEMPLATE in ie.attrib:
                    librml.template = ie.attrib.get(TEMPLATE)
                if COPYRIGHT in ie.attrib:
                    librml.copyright = ie.attrib.get(COPYRIGHT) == 'true'
                if COMMERCIAL in ie.attrib:
                    librml.commercialuse = ie.attrib.get(COMMERCIAL) == 'true'
                for action_node in ie.iter(XACTION):
                    if TYPE in action_node.attrib:
                        action = Action(actiontype=ActionType.fname(action_node.attrib.get(TYPE)))
                        action.from_xml(action_node)
                        librml.actions.append(action)
                    else:
                        raise LibRMLNotValidError('Action inside Item has no attribute "{}".'.format(TYPE))
            else:
                raise LibRMLNotValidError(
                    'Can\'t find element "{}", or the {} has no "{}" or "{}".'
                        .format(ITEM, ITEM, ID, TENANT))
        else:
            raise LibRMLNotValidError('There is no root element named "{}". Go away!'.format(LIBRML))
        return librml

    def allactionnames(self):
        return ActionType.getnames()


if __name__ == '__main__':
    pass
