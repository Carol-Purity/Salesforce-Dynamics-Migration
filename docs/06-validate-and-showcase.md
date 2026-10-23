# Step 6 — Validate the result and showcase it

**Time:** ~30 minutes

## 6.1 Automatic checks

Open `reports/migration_report.md`. For each object it compares:

**Salesforce rows → valid after transform → records actually found in Dynamics**

Every row should say **OK**. The report also lists every data-quality issue and load failure.

## 6.2 Manual spot checks in Sales Hub

Do these checks in the Dynamics app. Each one tests something different.

- [ ] **Accounts → Active Accounts**: your migrated companies are there. Open one: address, phone, revenue are filled in.
- [ ] Inside that account → **Related → Contacts**: its contacts are linked (proves lookups worked).
- [ ] **Opportunities**: estimated revenue and close date match Salesforce.
- [ ] **Leads**: Topic reads "*Company* (imported from Salesforce)".
- [ ] Pick 3 random records and compare them field by field with Salesforce.

Tip: In any list view, **Edit columns → add Salesforce Id** to see the source ID next to each record.

## 6.3 Capture evidence for your portfolio

Save screenshots into `docs/screenshots/` with these names, so the README picks them up:

| File | What to capture |
|---|---|
| `01-salesforce-accounts.png` | Salesforce Accounts list (Step 1) |
| `02-dynamics-column.png` | Salesforce Id column on the Account table (Step 2) |
| `05-terminal-run.png` | Terminal output of `python -m sfdm migrate` |
| `06-dynamics-accounts.png` | Migrated accounts in Sales Hub with the Salesforce Id column |
| `06-related-contacts.png` | An account's related contacts |

> ⚠️ Blur any real email addresses or phone numbers before committing screenshots.

Then copy the reconciliation table from `reports/migration_report.md` into the **Results** section of the README.

## 6.4 Push to GitHub

```bash
git add docs/screenshots README.md
git commit -m "Add migration results and screenshots"
git push
```

## 6.5 Talk about it

A short LinkedIn post or CV bullet:

> Migrated CRM data from Salesforce to Microsoft Dynamics 365 using a Python ETL pipeline (Salesforce REST API → Dataverse Web API). Designed the field mapping, re-ran loads safely with upserts on a source-ID column, resolved parent–child relationships, and validated 100% of records with an automated reconciliation report. CI runs tests and an end-to-end dry run on every push.

## Ideas to extend (optional, before the trial ends)

1. Map the **Industry** picklist to the Dynamics `industrycode` option set.
2. Close Won/Lost opportunities with the `WinOpportunity` / `LoseOpportunity` actions.
3. Migrate **Tasks** (Salesforce) → **tasks** (Dynamics) linked through `regardingobjectid`.
4. Rebuild one Salesforce Flow as a Power Automate flow and document it.
