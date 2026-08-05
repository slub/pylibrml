import json
from datetime import date
import pytest
import xml.etree.ElementTree as ET

from model.librml import (
    TypedList,
    ActionType,
    RestrictionType,
    Restriction,
    Action,
    LibRML,
)
from common.errors import LibRMLNotValidError


def test_typed_list():
    # Test valid typing and raises on invalid typing
    tl = TypedList(int)
    assert len(tl) == 0

    tl.append(10)
    assert len(tl) == 1
    assert tl[0] == 10

    with pytest.raises(TypeError):
        tl.append("not an int")

    tl.extend([20, 30])
    assert len(tl) == 3
    assert list(tl) == [10, 20, 30]

    tl[1] = 25
    assert tl[1] == 25

    with pytest.raises(TypeError):
        tl[1] = "invalid"

    del tl[0]
    assert list(tl) == [25, 30]

    tl.insert(0, 5)
    assert list(tl) == [5, 25, 30]

    with pytest.raises(TypeError):
        tl.insert(0, "invalid")

    assert str(tl) == "[5, 25, 30]"


def test_action_type_and_restriction_type_enums():
    # Test fname with case-insensitivity
    assert ActionType.fname("READ") == ActionType.READ
    assert ActionType.fname("read") == ActionType.READ
    assert ActionType.fname("Read") == ActionType.READ

    with pytest.raises(ValueError, match='ActionType has no member "UNKNOWN"'):
        ActionType.fname("UNKNOWN")

    # Test getnames
    names = ActionType.getnames()
    assert "read" in names
    assert "download" in names
    assert len(names) == 14

    # Test restriction type enums
    assert RestrictionType.fname("DATE") == RestrictionType.DATE
    assert RestrictionType.fname("date") == RestrictionType.DATE

    with pytest.raises(ValueError, match='RestrictionType has no member "UNKNOWN"'):
        RestrictionType.fname("UNKNOWN")

    res_names = RestrictionType.getnames()
    assert "date" in res_names
    assert "quality" in res_names
    assert len(res_names) == 12


def test_restriction_various_types():
    # RestrictionType.PARTS
    r_parts = Restriction(RestrictionType.PARTS, percentage=80)
    d_parts = r_parts.to_dict()
    assert d_parts == {"type": "parts", "percentage": 80}
    x_parts = r_parts.to_xml()
    assert x_parts.attrib.get("percentage") == "80"

    # RestrictionType.GROUP
    r_group = Restriction(RestrictionType.GROUP, groups=["admin", "editor"])
    d_group = r_group.to_dict()
    assert d_group == {"type": "group", "groups": ["admin", "editor"]}
    x_group = r_group.to_xml()
    assert x_group.attrib.get("groups") == "admin editor"

    # RestrictionType.AGE
    r_age = Restriction(RestrictionType.AGE, minage=18, maxage=99)
    d_age = r_age.to_dict()
    assert d_age == {"type": "age", "minage": 18, "maxage": 99}
    x_age = r_age.to_xml()
    assert x_age.attrib.get("minage") == "18"
    assert x_age.attrib.get("maxage") == "99"

    # RestrictionType.LOCATION
    r_loc = Restriction(RestrictionType.LOCATION, inside="inside-loc", outside="outside-loc", subnet="127.0.0.1")
    d_loc = r_loc.to_dict()
    assert d_loc == {"type": "location", "inside": "inside-loc", "outside": "outside-loc", "subnet": "127.0.0.1"}
    x_loc = r_loc.to_xml()
    assert x_loc.attrib.get("inside") == "inside-loc"
    assert x_loc.attrib.get("outside") == "outside-loc"
    assert x_loc.attrib.get("subnet") == "127.0.0.1"

    # RestrictionType.DATE
    r_date = Restriction(RestrictionType.DATE, fromdate=date(2026, 2, 11), todate=date(2026, 2, 20))
    d_date = r_date.to_dict()
    assert d_date == {"type": "date", "fromdate": "2026-02-11", "todate": "2026-02-20"}
    x_date = r_date.to_xml()
    assert x_date.attrib.get("fromdate") == "2026-02-11"
    assert x_date.attrib.get("todate") == "2026-02-20"

    # RestrictionType.DURATION
    r_dur = Restriction(RestrictionType.DURATION, maxduration=120, percentage=50)
    d_dur = r_dur.to_dict()
    assert d_dur == {"type": "duration", "maxduration": 120, "percentage": 50}
    x_dur = r_dur.to_xml()
    assert x_dur.attrib.get("maxduration") == "120"
    assert x_dur.attrib.get("percentage") == "50"

    # RestrictionType.COUNT
    r_count = Restriction(RestrictionType.COUNT, count=5)
    d_count = r_count.to_dict()
    assert d_count == {"type": "count", "count": 5}
    x_count = r_count.to_xml()
    assert x_count.attrib.get("count") == "5"

    # RestrictionType.CONCURRENT
    r_con = Restriction(RestrictionType.CONCURRENT, sessions=3)
    d_con = r_con.to_dict()
    assert d_con == {"type": "concurrent", "sessions": 3}
    x_con = r_con.to_xml()
    assert x_con.attrib.get("sessions") == "3"

    # RestrictionType.WATERMARK
    r_wm = Restriction(RestrictionType.WATERMARK, watermarkvalue="COPY")
    d_wm = r_wm.to_dict()
    assert d_wm == {"type": "watermark", "watermarkvalue": "COPY"}
    x_wm = r_wm.to_xml()
    assert x_wm.attrib.get("watermarkvalue") == "COPY"

    # RestrictionType.COMMERCIALUSE
    r_comm = Restriction(RestrictionType.COMMERCIALUSE, commercialuse=True, noncommercialuse=False)
    d_comm = r_comm.to_dict()
    assert d_comm == {"type": "commercialuse", "commercialuse": True, "noncommercialuse": False}
    x_comm = r_comm.to_xml()
    assert x_comm.attrib.get("commercialuse") == "true"
    assert x_comm.attrib.get("noncommercialuse") == "false"

    # RestrictionType.QUALITY
    r_qual = Restriction(RestrictionType.QUALITY, maxresolution=1080, maxbitrate=5000, maxdimension=1920)
    d_qual = r_qual.to_dict()
    assert d_qual == {"type": "quality", "maxresolution": 1080, "maxbitrate": 5000, "maxdimension": 1920}
    x_qual = r_qual.to_xml()
    assert x_qual.attrib.get("maxresolution") == "1080"
    assert x_qual.attrib.get("maxbitrate") == "5000"
    assert x_qual.attrib.get("maxdimension") == "1920"

    # RestrictionType.AGREEMENT
    r_agree = Restriction(RestrictionType.AGREEMENT, agreement_required=True)
    d_agree = r_agree.to_dict()
    assert d_agree == {"type": "agreement", "required": True}
    x_agree = r_agree.to_xml()
    assert x_agree.attrib.get("required") == "true"


def test_restriction_from_dict_and_xml():
    # Dict parsing
    r = Restriction(RestrictionType.DATE)
    r.from_dict({
        "fromdate": "2026-02-11",
        "todate": "2026-02-20",
        "minage": 18,
        "percentage": 10,
        "groups": ["g1"],
        "maxage": 99,
        "inside": "in",
        "outside": "out",
        "subnet": "sub",
        "maxduration": 100,
        "count": 5,
        "sessions": 2,
        "watermarkvalue": "wm",
        "commercialuse": True,
        "noncommercialuse": False,
        "maxresolution": 720,
        "maxbitrate": 3000,
        "maxdimension": 1280,
        "required": True
    })
    assert r.fromdate == date(2026, 2, 11)
    assert r.todate == date(2026, 2, 20)
    assert r.minage == 18
    assert r.percentage == 10
    assert r.groups == ["g1"]
    assert r.maxage == 99
    assert r.inside == "in"
    assert r.outside == "out"
    assert r.subnet == "sub"
    assert r.maxduration == 100
    assert r.count == 5
    assert r.sessions == 2
    assert r.watermarkvalue == "wm"
    assert r.commercialuse is True
    assert r.noncommercialuse is False
    assert r.maxresolution == 720
    assert r.maxbitrate == 3000
    assert r.maxdimension == 1280
    assert r.agreement_required is True

    # XML parsing
    node = ET.Element("restriction", {
        "percentage": "45",
        "groups": "admin editor",
        "minage": "21",
        "maxage": "65",
        "inside": "inside-val",
        "outside": "outside-val",
        "subnet": "10.0.0.1",
        "fromdate": "2026-05-01",
        "todate": "2026-05-15",
        "maxduration": "300",
        "count": "10",
        "sessions": "4",
        "watermarkvalue": "DRAFT",
        "commercialuse": "true",
        "noncommercialuse": "false",
        "maxbitrate": "128",
        "maxresolution": "480",
        "maxdimension": "640",
        "required": "true"
    })

    for rtype in RestrictionType:
        rx = Restriction(rtype)
        rx.from_xml(node)
        if rtype == RestrictionType.PARTS:
            assert rx.percentage == 45
        elif rtype == RestrictionType.GROUP:
            assert rx.groups == ["admin", "editor"]
        elif rtype == RestrictionType.AGE:
            assert rx.minage == 21
            assert rx.maxage == 65
        elif rtype == RestrictionType.LOCATION:
            assert rx.inside == "inside-val"
            assert rx.outside == "outside-val"
            assert rx.subnet == "10.0.0.1"
        elif rtype == RestrictionType.DATE:
            assert rx.fromdate == date(2026, 5, 1)
            assert rx.todate == date(2026, 5, 15)
        elif rtype == RestrictionType.DURATION:
            assert rx.maxduration == 300
            assert rx.percentage == 45
        elif rtype == RestrictionType.COUNT:
            assert rx.count == 10
        elif rtype == RestrictionType.CONCURRENT:
            assert rx.sessions == 4
        elif rtype == RestrictionType.WATERMARK:
            assert rx.watermarkvalue == "DRAFT"
        elif rtype == RestrictionType.COMMERCIALUSE:
            assert rx.commercialuse is True
            assert rx.noncommercialuse is False
        elif rtype == RestrictionType.QUALITY:
            assert rx.maxbitrate == 128
            assert rx.maxresolution == 480
            assert rx.maxdimension == 640
        elif rtype == RestrictionType.AGREEMENT:
            assert rx.agreement_required is True


def test_action_serialization_and_deserialization():
    act = Action(ActionType.READ, permission=True)
    act.restrictions.append(Restriction(RestrictionType.AGE, minage=18))

    # to_json / dict
    d = act.to_json()
    assert d["type"] == "read"
    assert d["permission"] is True
    assert len(d["restrictions"]) == 1
    assert d["restrictions"][0]["minage"] == 18

    # to_xml
    x = act.to_xml()
    assert x.attrib.get("type") == "read"
    assert x.attrib.get("permission") == "true"
    assert len(x.findall("{*}restriction")) == 1

    # from_dict
    act2 = Action(ActionType.DOWNLOAD)
    act2.from_dict(d)
    assert act2.permission is True
    assert len(act2.restrictions) == 1
    assert act2.restrictions[0].minage == 18

    # from_jsonstr
    json_str = json.dumps(d)
    act3 = Action.from_jsonstr(json_str)
    assert act3.type == ActionType.READ
    assert act3.permission is True
    assert act3.restrictions[0].minage == 18

    # from_xmlstr
    xml_str = """
    <action type="print" permission="false" xmlns="http://librml.org/schema">
        <restriction type="date" fromdate="2026-01-01"/>
    </action>
    """
    act4 = Action.from_xmlstr(xml_str)
    assert act4.type == ActionType.PRINT
    assert act4.permission is False
    assert len(act4.restrictions) == 1
    assert act4.restrictions[0].fromdate == date(2026, 1, 1)


def test_action_xml_invalid():
    # If restriction doesn't have type
    xml_str = """
    <action type="print" permission="false" xmlns="http://librml.org/schema">
        <restriction fromdate="2026-01-01"/>
    </action>
    """
    with pytest.raises(LibRMLNotValidError, match='Restriction inside Action has no attribute "type"'):
        Action.from_xmlstr(xml_str)


def test_librml_full_workflow():
    librml = LibRML(
        itemid="id-999",
        tenant="https://test.tenant.org/",
        copyright=True,
        commercialuse=False,
        mention=True,
        sharealike=True,
        template="CCBY",
        usageguide="https://guide.org"
    )

    assert librml.id == "id-999"
    assert librml.tenant == "https://test.tenant.org/"
    assert librml.copyright is True
    assert librml.commercialuse is False
    assert librml.mention is True
    assert librml.sharealike is True
    assert librml.template == "CCBY"
    assert librml.usageguide == "https://guide.org"

    act = Action(ActionType.DISPLAYMETADATA, permission=True)
    librml.actions.append(act)

    # Dict conversion
    d = librml.to_dict()
    assert d["id"] == "id-999"
    assert d["tenant"] == "https://test.tenant.org/"
    assert d["copyright"] is True
    assert d["commercialuse"] is False
    assert d["mention"] is True
    assert d["sharealike"] is True
    assert d["template"] == "CCBY"
    assert d["usageguide"] == "https://guide.org"
    assert len(d["actions"]) == 1

    # XML conversion
    xml_str = librml.to_xml()
    assert "version=\"0.5.0\"" in xml_str
    assert "id=\"id-999\"" in xml_str
    assert "tenant=\"https://test.tenant.org/\"" in xml_str

    # Deserialization from JSON dict
    librml2 = LibRML()
    librml2.from_dict(d)
    assert librml2.id == "id-999"
    assert len(librml2.actions) == 1

    # Deserialization from JSON string
    librml3 = LibRML.from_jsonstr(json.dumps(d))
    assert librml3.id == "id-999"

    # Deserialization from XML string
    librml4 = LibRML.from_xmlstr(xml_str)
    assert librml4.id == "id-999"
    assert librml4.tenant == "https://test.tenant.org/"
    assert librml4.copyright is True
    assert librml4.commercialuse is False
    assert librml4.mention is True
    assert librml4.sharealike is True
    assert librml4.template == "CCBY"
    assert librml4.usageguide == "https://guide.org"
    assert len(librml4.actions) == 1
    assert librml4.actions[0].type == ActionType.DISPLAYMETADATA

    assert "read" in librml.allactionnames()


def test_librml_invalid_inputs():
    with pytest.raises(LibRMLNotValidError, match="JSON has no attribute id"):
        LibRML().from_dict({"tenant": "foo"})

    # Invalid root element in XML
    with pytest.raises(LibRMLNotValidError, match="There is no root element named \"libRML\""):
        LibRML.from_xmlstr("<notLibRML></notLibRML>")

    # Missing item node inside libRML XML
    with pytest.raises(LibRMLNotValidError, match="Can't find element \"item\""):
        LibRML.from_xmlstr("<libRML xmlns=\"http://librml.org/schema\"></libRML>")

    # Action missing type attribute in XML
    xml_no_action_type = """
    <libRML xmlns="http://librml.org/schema">
        <item id="id-123">
            <action permission="true" />
        </item>
    </libRML>
    """
    with pytest.raises(LibRMLNotValidError, match='Action inside Item has no attribute "type"'):
        LibRML.from_xmlstr(xml_no_action_type)
