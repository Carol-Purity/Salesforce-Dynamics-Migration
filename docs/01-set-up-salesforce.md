# Step 1 — Set up the Salesforce source org

**Time:** ~20 minutes · **Cost:** free

You need a Salesforce org with some data to migrate. A free **Developer Edition** never expires and already contains sample Accounts, Contacts and Opportunities.

## 1.1 Sign up

1. Go to <https://developer.salesforce.com/signup>.
2. Fill in the form. The **Username** must look like an email but does not need to be a real inbox — use something like `carol@sfdm-demo.dev`.
3. Open the activation email, set a password, and log in.

## 1.2 Look at the data you will migrate

1. Click the **App Launcher** (9 dots, top left) → **Sales**.
2. Open the **Accounts**, **Contacts**, **Opportunities** and **Leads** tabs. Change each list view to **All …** to see every record.
3. Write down how many records each object has — you will compare against these numbers at the end.

> **Optional — add the project's sample data.** If you want the same Kenyan-company test data used in this repo, import `sample_data/Account.csv` and `sample_data/Contact.csv` with **Setup → Data Import Wizard**. Not required: the org's built-in data works fine.

## 1.3 Get your security token (only needed for the scripted export)

1. Click your avatar (top right) → **Settings**.
2. Left menu → **My Personal Information → Reset My Security Token** → **Reset Security Token**.
3. The token arrives by email. Keep it for Step 3.

## ✅ Done when

- [ ] You can log in to your Developer Edition org
- [ ] You noted record counts for Accounts, Contacts, Opportunities, Leads
- [ ] 📸 Screenshot of the Accounts list saved to `docs/screenshots/01-salesforce-accounts.png`

Next → [Step 2: Set up Dynamics 365](02-set-up-dynamics.md)
