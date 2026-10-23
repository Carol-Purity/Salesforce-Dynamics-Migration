# Step 2 — Set up the Dynamics 365 target

**Time:** ~30 minutes · **Cost:** free 30-day trial

> ⏰ **The trial runs for 30 days.** Finish Step 1 first and have Python working (README → *Before you start*) so the trial days are spent migrating, not setting up.

## 2.1 Start the trial

1. Go to the [Dynamics 365 Sales free trial page](https://dynamics.microsoft.com/en-gb/sales/sales/free-trial/) and choose **Try for free**.
2. Follow the prompts. If it asks for a *work* account and you only have Gmail, let it create a new Microsoft 365 account for you (it will look like `carol@yourcompany.onmicrosoft.com`). **Write down that sign-in and password.**
3. When setup finishes, click **Launch trial**. You land in the **Sales Hub** app.

## 2.2 Find your environment URL

Look at your browser's address bar while in Sales Hub. It looks like:

```
https://org1a2b3c4d.crm4.dynamics.com/main.aspx?appid=...
```

The part up to `.com` is your **environment URL** → `https://org1a2b3c4d.crm4.dynamics.com`. Save it.

## 2.3 Why we need one custom column

Dynamics gives every record its own ID (a GUID), so the original Salesforce IDs would be lost. We add a **Salesforce Id** column to each table. It lets us:

- re-run the migration without creating duplicates (update instead of create),
- link Contacts and Opportunities to the right Account,
- trace any Dynamics record back to its Salesforce origin.

## 2.4 Add the "Salesforce Id" column (repeat for 4 tables)

1. Go to <https://make.powerapps.com>. Top right, make sure your **trial environment** is selected.
2. Left menu → **Tables** → open **Account**.
3. **+ New → Column**:
   - **Display name:** `Salesforce Id`
   - **Data type:** Single line of text
   - Expand **Advanced options** and note the **Schema/Logical name** — something like `cr8a1_salesforceid`.
4. **Save**.
5. Repeat for **Contact**, **Opportunity** and **Lead**, using the exact same display name. The logical name will have the same prefix on every table.

## 2.5 Fill in your settings file

In the project folder:

```bash
cp .env.example .env        # Windows: copy .env.example .env
```

Open `.env` and set:

```ini
DATAVERSE_URL=https://org1a2b3c4d.crm4.dynamics.com
SF_ID_COLUMN=cr8a1_salesforceid      # the logical name from 2.4
```

Leave `TENANT_ID`, `CLIENT_ID` and `CLIENT_SECRET` blank. The tool will ask you to sign in with your trial account in the browser (a "device code" sign-in).

<details>
<summary>Option B (advanced): app registration for unattended runs</summary>

1. <https://entra.microsoft.com> → **App registrations → New registration** → name it `sfdm` → Register. Copy the **Application (client) ID** and **Directory (tenant) ID**.
2. **Certificates & secrets → New client secret** → copy the value.
3. <https://admin.powerplatform.microsoft.com> → your environment → **Settings → Users + permissions → Application users → New app user** → pick `sfdm` → security role **System Administrator** (trial only).
4. Put the three values in `TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET`.

This is how real migrations authenticate — worth mentioning in interviews.
</details>

## ✅ Done when

- [ ] Sales Hub opens with your trial account
- [ ] `Salesforce Id` column exists on Account, Contact, Opportunity, Lead
- [ ] `.env` has `DATAVERSE_URL` and `SF_ID_COLUMN`
- [ ] 📸 Screenshot of the new column on the Account table → `docs/screenshots/02-dynamics-column.png`

Next → [Step 3: Export from Salesforce](03-export-from-salesforce.md)
