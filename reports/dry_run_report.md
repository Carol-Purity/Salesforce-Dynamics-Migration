# Migration report

- **Run:** 2026-10-23 08:28 UTC
- **Mode:** dry run (no Dynamics connection)
- **Result:** PASS - every transformed record is in Dynamics

## Reconciliation

| Object | Salesforce rows | Valid after transform | In Dynamics | Created | Updated | Failed | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| Account | 5 | 5 | 5 | 5 | 0 | 0 | OK |
| Contact | 7 | 7 | 7 | 7 | 0 | 0 | OK |
| Opportunity | 6 | 6 | 6 | 6 | 0 | 0 | OK |
| Lead | 4 | 4 | 4 | 4 | 0 | 0 | OK |

## Data-quality issues (1)

| Object | Salesforce Id | Field | Level | Detail |
|---|---|---|---|---|
| Opportunity | 006SAMPLE0000006AAA | AccountId | warning | parent Account 001SAMPLE0000099AAA not found in export - loaded without link |
