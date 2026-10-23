# Step 3 — Export data from Salesforce

**Time:** ~15 minutes

Goal: four CSV files in `data/extract/` — `Account.csv`, `Contact.csv`, `Opportunity.csv`, `Lead.csv` — with Salesforce API field names as headers. Pick **one** option.

## Option A — Scripted export (recommended, shows API skills)

1. In `.env`, fill in `SF_USERNAME`, `SF_PASSWORD` and `SF_SECURITY_TOKEN` (from Step 1.3).
2. Run:

   ```bash
   python -m sfdm extract
   ```

   Expected output:

   ```
   Extracting from Salesforce...
     Account          12 records -> data/extract/Account.csv
     Contact          20 records -> data/extract/Contact.csv
     ...
   ```

The script builds its SOQL queries from `mapping/field_mapping.yaml`, so it only pulls the fields that will be migrated.

**If login fails** (`INVALID_LOGIN`): check the password + security token, and that `SF_DOMAIN=login`. Some orgs block API username-password login. If so, use Option B.

## Option B — No-code export with Workbench

1. Open <https://workbench.developerforce.com>, choose **Production**, log in.
2. **Queries → SOQL Query**, choose **Bulk CSV**, and run each query below. Download each result and save it as `data/extract/<Object>.csv`.

```sql
SELECT Id, Name, Phone, Website, BillingStreet, BillingCity, BillingState, BillingPostalCode, BillingCountry, NumberOfEmployees, AnnualRevenue, Description FROM Account
SELECT Id, FirstName, LastName, Email, Phone, MobilePhone, Title, MailingCity, MailingCountry, AccountId FROM Contact
SELECT Id, Name, Amount, CloseDate, Probability, StageName, Description, AccountId FROM Opportunity
SELECT Id, FirstName, LastName, Company, Email, Phone, Title, City, Country FROM Lead
```

## Check the export

Open each CSV and confirm the row counts match what you noted in Step 1.2.

> 🔒 `data/` is git-ignored, so exported customer data never reaches GitHub. Only the fictional `sample_data/` is committed.

## ✅ Done when

- [ ] Four CSVs are in `data/extract/`
- [ ] Row counts match Salesforce

Next → [Step 4: Map the fields](04-map-fields.md)
