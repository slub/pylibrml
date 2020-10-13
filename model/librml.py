import collections
import json
import logging
import xml.etree.ElementTree as ET
from datetime import date
from enum import Enum, unique
from typing import List

from common.errors import LibRMLNotValidError, TemplateNotValidError, ZHSerError
from model.names import SUBNET, GROUPS, PARTS, MINAGE, INSIDE, OUTSIDE, MACHINES, FROMDATE, TODATE, DURATION, COUNT, \
    SESSIONS, WATERMARK, COMMERCIAL, NONCOMMERCIAL, MAXRES, MAXBIT, TYPE, XRESTRICTION, XPART, XGROUP, XSUBNET, \
    PERMISSION, RESTRICTIONS, XACTION, TENANT, MENTION, SHARE, USAGEGUIDE, ACTIONS, LIBRML, ITEM, ID, VERSION, XMACHINE, \
    TEMPLATE

logger = logging.getLogger(__name__)


class TypedList(collections.MutableSequence):
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
    def from_name(cls, name):
        for action_name, action in ActionType.__members__.items():
            if action_name == name.upper():
                return action
        raise Exception('Not a member of ActionType: {}'.format(name))


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

    @classmethod
    def from_name(cls, name):
        for restriction_name, restriction in RestrictionType.__members__.items():
            if restriction_name == name.upper():
                return restriction
        raise ZHSerError('Not a member of RestrictionType: {}'.format(name))


class Restriction:
    def __init__(self, res_type, subnet: List[str] = None, groups: List[str] = None, parts: List[str] = None,
                 minage: int = None, inside: str = None, outside: str = None, machines: List[str] = None,
                 fromdate: date = None, todate: date = None, duration: int = None, count: int = None,
                 sessions: int = None, watermarkvalue: str = None, commercialuse: bool = None,
                 noncommercialuse: bool = None, maxresolution: int = None, maxbitrate: int = None):

        if res_type in RestrictionType:
            self.type = res_type
        else:
            raise TypeError()

        self.subnet = subnet if subnet is not None else []
        self.groups = groups if groups is not None else []
        self.parts = parts if parts is not None else []
        self.minage = minage
        self.inside = inside
        self.outside = outside
        self.machines = machines if machines is not None else []
        self.fromdate = fromdate
        self.todate = todate
        self.duration = duration
        self.count = count
        self.sessions = sessions
        self.watermarkvalue = watermarkvalue
        self.commercialuse = commercialuse
        self.noncommercialuse = noncommercialuse
        self.maxresolution = maxresolution
        self.maxbitrate = maxbitrate

    def to_dict(self):
        if self.type == RestrictionType.PARTS:
            if len(self.parts) > 0:
                return {TYPE: self.type.name.lower(), PARTS: self.parts}
        elif self.type == RestrictionType.GROUP:
            if len(self.groups) > 0:
                return {TYPE: self.type.name.lower(), GROUPS: self.groups}
        elif self.type == RestrictionType.AGE:
            if self.minage:
                return {TYPE: self.type.name.lower(), MINAGE: self.minage}
        elif self.type == RestrictionType.LOCATION:
            out = {TYPE: self.type.name.lower()}
            if self.inside:
                out[INSIDE] = self.inside
            if self.outside:
                out[OUTSIDE] = self.outside
            if len(self.subnet) > 0:
                out[SUBNET] = self.subnet
            if len(self.machines) > 0:
                out[MACHINES] = self.machines
            if self.inside or self.outside or len(self.subnet) > 0 or len(self.machines) > 0:
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
            if self.duration:
                return {TYPE: self.type.name.lower(), DURATION: int(self.duration)}
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
            if self.commercialuse:
                out[COMMERCIAL] = self.commercialuse
            if self.noncommercialuse:
                out[NONCOMMERCIAL] = self.noncommercialuse
            if self.commercialuse or self.noncommercialuse:
                return out
        elif self.type == RestrictionType.QUALITY:
            out = {TYPE: self.type.name.lower()}
            if self.maxresolution:
                out[MAXRES] = int(self.maxresolution)
            if self.maxbitrate:
                out[MAXBIT] = int(self.maxbitrate)
            if self.maxresolution or self.maxbitrate:
                return out

    def to_xml(self):
        x = ET.Element(XRESTRICTION, {TYPE: self.type.name.lower()})

        if self.type == RestrictionType.PARTS:
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
        elif self.type == RestrictionType.LOCATION:
            if self.inside:
                x.set(INSIDE, self.inside)
            if self.outside:
                x.set(OUTSIDE, self.outside)
            for n in self.subnet:
                xn = ET.SubElement(x, XSUBNET)
                xn.text = str(n)
            for m in self.machines:
                xm = ET.SubElement(x, XMACHINE)
                xm.text = str(m)
        elif self.type == RestrictionType.DATE:
            if self.todate:
                x.set(TODATE, str(self.todate))
            if self.fromdate:
                x.set(FROMDATE, str(self.fromdate))
        elif self.type == RestrictionType.DURATION:
            if self.duration:
                x.set(DURATION, str(self.duration))
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
            if self.commercialuse:
                x.set(COMMERCIAL, str(self.commercialuse).lower())
            if self.noncommercialuse:
                x.set(NONCOMMERCIAL, str(self.noncommercialuse).lower())
        elif self.type == RestrictionType.QUALITY:
            if self.maxbitrate:
                x.set(MAXBIT, str(self.maxbitrate))
            if self.maxresolution:
                x.set(MAXRES, str(self.maxresolution))
        else:
            return None

        return x

    def from_dict(self, restriction):
        if PARTS in restriction:
            self.parts = restriction[PARTS]
        if GROUPS in restriction:
            self.groups = restriction[GROUPS]
        if MINAGE in restriction:
            self.minage = restriction[MINAGE]
        if INSIDE in restriction:
            self.inside = restriction[INSIDE]
        if OUTSIDE in restriction:
            self.outside = restriction[OUTSIDE]
        if SUBNET in restriction:
            self.subnet = restriction[SUBNET]
        if MACHINES in restriction:
            self.machines = restriction[MACHINES]
        if FROMDATE in restriction:
            self.fromdate = date.fromisoformat(restriction[FROMDATE])
        if TODATE in restriction:
            self.todate = date.fromisoformat(restriction[TODATE])
        if DURATION in restriction:
            self.duration = int(restriction[DURATION])
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
            self.maxresolution = restriction[MAXRES]
        if MAXBIT in restriction:
            self.maxbitrate = restriction[MAXBIT]

    def from_xml(self, restriction_node):
        if self.type == RestrictionType.PARTS:
            for part in restriction_node.iterfind(XPART):
                self.parts.append(part.text)
        if self.type == RestrictionType.GROUP:
            for group in restriction_node.iterfind(XGROUP):
                self.groups.append(group.text)
        if self.type == RestrictionType.AGE:
            self.minage = restriction_node.attrib.get(MINAGE)
        if self.type == RestrictionType.LOCATION:
            self.inside = restriction_node.attrib.get(INSIDE)
            self.outside = restriction_node.attrib.get(OUTSIDE)
            for subnet in restriction_node.iterfind(XSUBNET):
                self.subnet.append(subnet.text)
            for machine in restriction_node.iterfind(XMACHINE):
                self.machines.append(machine.text)
        if self.type == RestrictionType.DATE:
            self.fromdate = date.fromisoformat(restriction_node.attrib.get(FROMDATE))
            self.todate = date.fromisoformat(restriction_node.attrib.get(TODATE))
        if self.type == RestrictionType.DURATION:
            self.duration = int(restriction_node.attrib.get(DURATION))
        if self.type == RestrictionType.COUNT:
            self.count = int(restriction_node.attrib.get(COUNT))
        if self.type == RestrictionType.CONCURRENT:
            self.sessions = int(restriction_node.attrib.get(SESSIONS))
        if self.type == RestrictionType.WATERMARK:
            self.watermarkvalue = restriction_node.attrib.get(WATERMARK)
        if self.type == RestrictionType.COMMERCIALUSE:
            self.commercialuse = restriction_node.attrib.get(COMMERCIAL) == "true"
            self.noncommercialuse = restriction_node.attrib.get(NONCOMMERCIAL) == "true"
        if self.type == RestrictionType.QUALITY:
            self.maxbitrate = restriction_node.attrib.get(MAXBIT)
            self.maxresolution = restriction_node.attrib.get(MAXRES)


class Action:
    def __init__(self, type: ActionType, permission: bool = None, restrictions: List[Restriction] = None):
        self.permission = permission
        if restrictions is not None:
            self.restrictions = restrictions
        else:
            self.restrictions = TypedList(Restriction)

        if type in ActionType:
            self.type = type
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
            self.permission = action[PERMISSION] == 'true'
        if RESTRICTIONS in action:
            restrictions = action[RESTRICTIONS]
            for restriction in restrictions:
                r = Restriction(RestrictionType.from_name(restriction[TYPE]))
                r.from_dict(restriction)
                self.restrictions.append(r)

    def from_xml(self, action_node):
        if PERMISSION in action_node.attrib:
            self.permission = action_node.attrib.get(PERMISSION) == 'true'
        for restriction_node in action_node.iterfind(XRESTRICTION):
            if TYPE in restriction_node.attrib:
                r = Restriction(RestrictionType.from_name(restriction_node.attrib.get(TYPE)))
                r.from_xml(restriction_node)
                self.restrictions.append(r)
            else:
                raise LibRMLNotValidError('Restriction inside Action has no attribute "{}".'.format(TYPE))


class LibRML(object):
    def __init__(self, itemid: str, tenant: str = None, mention: bool = False, sharealike: bool = False,
                 usageguide: str = None, template: str = None, actions: List[Action] = None):
        self.id = itemid
        self.tenant = tenant
        self.mention = mention
        self.sharealike = sharealike
        self.usageguide = usageguide
        self.template = template
        if actions is not None:
            self.actions = actions
        else:
            self.actions = TypedList(Action)

    def to_dict(self):
        output = {ID: self.id}

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
        if len(self.actions) > 0:
            for action in self.actions:
                item.append(action.to_xml())

        return ET.tostring(root, encoding='unicode', method='xml', xml_declaration=True)

    def from_json(self, json_obj):
        data = json.loads(json_obj)
        self.from_dict(data)

    def from_dict(self, data):
        if ID in data:
            self.id = data[ID]
        else:
            raise LibRMLNotValidError('JSON has no attribute {}!'.format(ID))
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
        if ACTIONS in data:
            actions = data[ACTIONS]
            for action in actions:
                a = Action(ActionType.from_name(action[TYPE]))
                self.actions.append(a)
                a.from_dict(action)

    def from_xml(self, xml):
        xml_tree = ET.ElementTree(ET.fromstring(xml))
        root = xml_tree.getroot()
        if root.tag == LIBRML:
            ie = root.find(ITEM)
            if ie is not None and ID in ie.attrib and TENANT in ie.attrib:
                self.id = ie.attrib.get(ID)
                self.tenant = ie.attrib.get(TENANT)
                if MENTION in ie.attrib:
                    self.mention = ie.attrib.get(MENTION) == 'true'
                if SHARE in ie.attrib:
                    self.sharealike = ie.attrib.get(SHARE) == 'true'
                if USAGEGUIDE in ie.attrib:
                    self.usageguide = ie.attrib.get(USAGEGUIDE)
                if TEMPLATE in ie.attrib:
                    self.template = ie.attrib.get(TEMPLATE)
                for action_node in ie.iter(XACTION):
                    if TYPE in action_node.attrib:
                        action = Action(type=ActionType.from_name(action_node.attrib.get(TYPE)))
                        action.from_xml(action_node)
                        self.actions.append(action)
                    else:
                        raise LibRMLNotValidError('Action inside Item has no attribute "{}".'.format(TYPE))
            else:
                raise LibRMLNotValidError(
                    'Can\'t find element "{}", or the {} has no "{}", or the {} has no "{}".'
                        .format(ITEM, ITEM, ID, ITEM, TENANT))
        else:
            raise LibRMLNotValidError('There is no root element named "{}". Go away!'.format(LIBRML))

    def getActions(self, type):
        ret = []
        for action in self.actions:
            if action.type == type:
                ret.append(action)
        return ret

if __name__ == '__main__':
    pass
