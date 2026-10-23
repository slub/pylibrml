import pytest
import pathlib
from model.exceptions import TemplateNotValidError
from tmpl.TemplateManager import TemplateManager, MetaInformation
from tmpl.templateutils import from_template


def test_meta_information_and_missing_file(tmp_path):
    # Test that missing meta sidecar file raises TemplateNotValidError
    jinja_file = tmp_path / "test_template.jinja"
    jinja_file.touch()

    with pytest.raises(TemplateNotValidError, match="has no metainformation sidecar-file"):
        MetaInformation(jinja_file)


def test_template_manager_basics():
    tm = TemplateManager()

    # Test list templates
    tpl_list = tm.getTemplateList()
    assert len(tpl_list) > 0
    assert "CC0" in tpl_list
    assert "Group-Embargo" in tpl_list

    # Test getTemplateMeta
    meta_cc0 = tm.getTemplateMeta("CC0")
    assert meta_cc0["id"] == "CC0"
    assert "vars" in meta_cc0
    assert len(meta_cc0["vars"]) == 0

    meta_embargo = tm.getTemplateMeta("Group-Embargo")
    assert meta_embargo["id"] == "Group-Embargo"
    assert len(meta_embargo["vars"]) == 2

    # Check variables in embargo
    vars_dict = {v["variable"]: v for v in meta_embargo["vars"]}
    assert "embargodate" in vars_dict
    assert vars_dict["embargodate"]["datatype"] == "date"
    assert "groups" in vars_dict
    assert vars_dict["groups"]["datatype"] == "list"


def test_get_template_and_fillable_restrictions():
    tm = TemplateManager()

    # Test static template (valid JSON)
    cc0_tpl = tm.getTemplate("CC0")
    assert cc0_tpl is not None
    assert cc0_tpl["template"] == "CC0"

    # Test loop template (non-valid JSON originally)
    embargo_tpl = tm.getTemplate("Group-Embargo")
    assert embargo_tpl is not None
    assert embargo_tpl["template"] == "Group-Embargo"

    # Test invalid template
    assert tm.getTemplate("NON_EXISTENT") is None

    # Test getFillableRestriction
    res_cc0 = tm.getFillableRestriction("CC0")
    assert res_cc0 == []

    res_embargo = tm.getFillableRestriction("Group-Embargo")
    assert len(res_embargo) == 2
    vars_list = [v[0] for v in res_embargo]
    assert "embargodate" in vars_list
    assert "groups" in vars_list


def test_from_template_success():
    # Test CC0
    obj_cc0 = from_template("CC0", "id-cc0", tenant="https://slub-dresden.de/")
    assert obj_cc0.id == "id-cc0"
    assert obj_cc0.tenant == "https://slub-dresden.de/"
    assert obj_cc0.template == "CC0"
    assert len(obj_cc0.actions) == 12

    # Test Group-Embargo with variables
    obj_emb = from_template(
        "Group-Embargo",
        "id-emb",
        tenant="https://slub-dresden.de/",
        embargodate="2026-02-11",
        groups=["admin", "special-users"]
    )

    assert obj_emb.id == "id-emb"
    assert obj_emb.tenant == "https://slub-dresden.de/"
    assert obj_emb.template == "Group-Embargo"
    assert len(obj_emb.actions) == 12

    # Check that read action is restricted by date and group correctly
    read_action = [a for a in obj_emb.actions if a.type.name.lower() == "read"][0]
    assert len(read_action.restrictions) == 2

    rest_types = {r.type.name.lower(): r for r in read_action.restrictions}
    assert "date" in rest_types
    assert "group" in rest_types

    assert str(rest_types["date"].fromdate) == "2026-02-11"
    assert rest_types["group"].groups == ["admin", "special-users"]


def test_from_template_fallback_defaults():
    # Test rendering Group-Embargo when arguments are missing
    # Missing groups (defaults to empty list) and missing embargodate (defaults to empty string)
    obj_emb = from_template("Group-Embargo", "id-emb")

    # The read action should still parse, but its date might be empty string or invalid ISO for parsing.
    # Actually, if date is empty string, Restriction.from_dict() won't load fromdate because FROMDATE is missing or empty.
    # Let's see if it parses correctly.
    read_action = [a for a in obj_emb.actions if a.type.name.lower() == "read"][0]
    rest_types = {r.type.name.lower(): r for r in read_action.restrictions}
    assert "group" in rest_types
    assert rest_types["group"].groups == []


def test_from_template_invalid():
    with pytest.raises(TemplateNotValidError, match='No template "NON_EXISTENT" found'):
        from_template("NON_EXISTENT", "id-123")
