# Step 4 — Map Salesforce fields to Dynamics columns

**Time:** ~20 minutes (reading + one dry run)

The mapping is the core design work in any CRM migration. Here it lives in one readable file: [`mapping/field_mapping.yaml`](../mapping/field_mapping.yaml).

## Object mapping

| Salesforce | Dynamics 365 (Dataverse) | Load order | Why this order |
|---|---|---|---|
| Account | account | 1 | Parent of contacts and opportunities |
| Contact | contact | 2 | Needs its Account to exist |
| Opportunity | opportunity | 3 | Needs its Account to exist |
| Lead | lead | 4 | Independent |

## Key field mappings

| Salesforce | Dynamics | Note |
|---|---|---|
| Account.Name | account.name | Required |
| Account.Billing* | account.address1_* | Address split across 5 columns on both sides |
| Account.AnnualRevenue | account.revenue | Currency — commas stripped |
| Contact.AccountId | contact.parentcustomerid_account | **Lookup**: Salesforce Id → Dynamics GUID |
| Contact.Title | contact.jobtitle | |
| Opportunity.Amount | opportunity.estimatedvalue | |
| Opportunity.CloseDate | opportunity.estimatedclosedate | Dates normalised to YYYY-MM-DD |
| Opportunity.StageName | opportunity.stepname | Kept as text (see below) |
| Lead.Company | lead.companyname | |
| — | lead.subject ("Topic") | Required in Dynamics, missing in Salesforce → generated as "*Company* (imported from Salesforce)" |
| every `Id` | `<prefix>_salesforceid` | Custom column from Step 2.4 |

## Decisions and trade-offs (good interview material)

| Topic | Decision | Reason |
|---|---|---|
| Re-runs | Upsert on the Salesforce Id column | Safe to fix a problem and run again — no duplicates |
| Relationships | Resolve lookups with an ID map built during the load | Parents are loaded first, so their GUIDs are known |
| Orphans (child points to a missing parent) | Load the record **without** the link and flag it | Better than losing the record silently |
| Missing required name | Skip the record and flag as error | Dynamics would reject it anyway |
| Picklists (Industry, Lead Source, Rating) | Not migrated in v1 | Need a value-by-value option-set mapping |
| Won/Lost opportunities | Loaded as open, stage kept as text | Closing needs the Dynamics *close opportunity* action |
| Owners, activities, files, automation | Out of scope | Users, emails and Flows/Apex are rebuilt, not copied |

## Try it without Dynamics: dry run

```bash
python -m sfdm migrate --dry-run --source data/extract
```

This runs transform → simulated load → validation with no Dynamics connection, and writes `reports/dry_run_report.md`. Read the **Data-quality issues** table and fix anything in Salesforce or the CSVs before the real load.

(Without `--source` it uses the repo's `sample_data/`, which contains one deliberate orphan opportunity so you can see how issues are reported.)

## ✅ Done when

- [ ] Dry run prints `PASS`
- [ ] You understand every row in the data-quality table

Next → [Step 5: Load into Dynamics](05-load-into-dynamics.md)
