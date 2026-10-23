import pytest

from sfdm import config, dataverse, load, transform


@pytest.fixture
def mapping():
    return config.load_mapping()


def test_convert_types():
    assert transform.convert(" 1,050 ", "int") == 1050
    assert transform.convert("18500000", "money") == 18500000.0
    assert transform.convert("15/12/2026", "date") == "2026-12-15"
    assert transform.convert("2026-12-15", "date") == "2026-12-15"
    with pytest.raises(ValueError):
        transform.convert("next spring", "date")


def test_account_fields_are_mapped(mapping):
    row = {"Id": "001X", "Name": "Acme", "Phone": "123", "NumberOfEmployees": "1,050", "Website": ""}
    rec, issues = transform.transform_row("Account", row, mapping["objects"]["Account"], {})
    assert issues == []
    key = mapping["objects"]["Account"]["key_column"]
    assert rec.payload == {key: "001X", "name": "Acme", "telephone1": "123", "numberofemployees": 1050}


def test_lookup_to_known_parent(mapping):
    row = {"Id": "003X", "LastName": "Otieno", "AccountId": "001X"}
    rec, issues = transform.transform_row("Contact", row, mapping["objects"]["Contact"], {"Account": {"001X"}})
    assert issues == []
    assert rec.lookups == {"parentcustomerid_account": ["Account", "001X"]}


def test_orphan_lookup_is_flagged_not_fatal(mapping):
    row = {"Id": "006X", "Name": "Deal", "AccountId": "001MISSING"}
    rec, issues = transform.transform_row("Opportunity", row, mapping["objects"]["Opportunity"], {"Account": set()})
    assert rec is not None and rec.lookups == {}
    assert issues[0].level == "warning" and "not found" in issues[0].message


def test_missing_required_name_skips_record(mapping):
    rec, issues = transform.transform_row("Contact", {"Id": "003Y", "FirstName": "No"},
                                          mapping["objects"]["Contact"], {})
    assert rec is None and issues[0].level == "error"


def test_lead_gets_required_topic(mapping):
    rec, _ = transform.transform_row("Lead", {"Id": "00QX", "LastName": "Mutua", "Company": "Dairy Co"},
                                     mapping["objects"]["Lead"], {})
    assert rec.payload["subject"] == "Dairy Co (imported from Salesforce)"


def test_dry_run_end_to_end_is_idempotent(tmp_path):
    summary, issues = transform.transform(config.SAMPLE_DIR, tmp_path)
    assert summary["Account"] == {"source": 5, "transformed": 5}
    assert any("001SAMPLE0000099AAA" in i.message for i in issues)

    client = dataverse.DryRunClient()
    first, id_map = load.load(client, tmp_path, id_map_file=None)
    assert first["Contact"]["created"] == 7 and first["Contact"]["failed"] == 0

    # contacts are linked to the Dataverse GUID of their account
    amina = next(r for r in client.tables["contacts"].values() if r["firstname"] == "Amina")
    assert amina["parentcustomerid_account@odata.bind"] == f"/accounts({id_map['Account']['001SAMPLE0000001AAA']})"

    # running again updates instead of duplicating
    second, _ = load.load(client, tmp_path, id_map_file=None)
    assert second["Account"] == {"created": 0, "updated": 5, "failed": 0, "errors": []}
    assert len(client.tables["accounts"]) == 5
