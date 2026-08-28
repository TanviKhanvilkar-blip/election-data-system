# Data sources

This project loads real results from the **2019 Indian general election**
(17th Lok Sabha) — nothing in the dashboard is simulated.

## `data/LS_2.0.csv`

Candidate-level results for all 543 constituencies (542 loaded successfully
here — one row in the source file was missing its constituency name).
Sourced from candidate affidavits filed with the **Election Commission of
India**, compiled by the **Association for Democratic Reforms** (ADR) /
[myneta.info](https://myneta.info). Covers every candidate's party, votes,
vote share, gender, age, education, declared criminal cases, declared
assets and liabilities, and the constituency's total electors.

## `data/state_turnout_2019.csv`

State-wise actual voter turnout with a male/female/other split of votes
cast, published by the Election Commission of India.

## What's real vs. estimated

Every vote count, victory margin, and candidate attribute (age, gender,
education, criminal cases, assets) in the dashboard comes directly from
the source files above.

The one modeled figure: per-constituency turnout is **exact** (real votes
polled ÷ real electors), but the **gender split within** that turnout is
estimated — using that constituency's state-wide actual male/female vote
share, combined with the commonly cited national average of 52% male /
48% female electors, since the Election Commission does not publish
elector gender at constituency level. This is disclosed in the dashboard
footer.

## A note on the source data's WINNER flag

`LS_2.0.csv` has one known data-entry error: Aurangabad (Bihar) has two
rows flagged as the winner. `populate_data.py` doesn't trust that flag —
it derives `is_winner` from whichever candidate actually received the
most votes in each constituency, which is unambiguous for first-past-the-
post elections and self-corrects this kind of error.

## Re-running the import

```
python populate_data.py
```

Drops and recreates all tables, then reloads everything from the two CSVs
above. Safe to re-run at any time.
