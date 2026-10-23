# Step 5 — Load the data into Dynamics 365

**Time:** ~10 minutes

## 5.1 Run the migration

```bash
python -m sfdm migrate
```

The first time, you will see something like:

```
To sign in, use a web browser to open the page https://microsoft.com/devicelogin
and enter the code ABCD-EFGH to authenticate.
```

Open that page, enter the code, and sign in with your **Dynamics trial account** (not your Gmail). The sign-in is cached in `.token_cache.bin` (git-ignored), so the next runs don't ask again.

Expected output:

```
[1/3] Transform
  Account        12 rows ->   12 records
  ...
[2/3] Load
  Account      created   12  updated    0  failed    0
  Contact      created   20  updated    0  failed    0
  ...
[3/3] Validate
      PASS -> reports/migration_report.md
```

## 5.2 Prove it is safe to re-run

Run `python -m sfdm migrate` again. This time every line should show **updated** instead of **created**, and no duplicates appear in Dynamics. Mention this in your write-up: it is what makes a migration safe in production.

## Troubleshooting

| Message | Fix |
|---|---|
| `Missing setting DATAVERSE_URL` | Fill in `.env` (Step 2.5) |
| `... 400: ... property 'cr8a1_salesforceid' does not exist` | `SF_ID_COLUMN` in `.env` doesn't match the logical name from Step 2.4, or the column is missing on one of the 4 tables |
| `401` / `403` | You signed in with the wrong account. Delete `.token_cache.bin` and run again |
| `Sign-in failed: AADSTS...` | Your trial account needs to finish setup — log in to Sales Hub once in the browser first |
| Some records `failed` | Their exact error is listed in `reports/migration_report.md` under *Load failures* |

Next → [Step 6: Validate and showcase](06-validate-and-showcase.md)
