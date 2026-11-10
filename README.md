# Would You Trust Her?

**How an AI assistant's perceived gender and confidence affect trust in its advice.**
Group 9 · Human Centred AI · Group Empirical Study.
Team: Cole Ternullo, Danny Dowling, Felim Sullivan, Laura Gonzalez, Liam Maher.

This is a Wizard-of-Oz experiment. Participants make 4 estimates, see a pre-scripted "AI" answer that is always 10% off the truth, then give a final estimate and a trust rating. There are two factors:

- **Assistant gender:** Eve (female) or Adam (male), between-subjects.
- **Wording confidence:** confident or hedged, within-subjects (2 trials each).

| Hypothesis | Weight of Advice (a) | Trust rating (b) |
|---|---|---|
| H1 Confidence | H1a | H1b |
| H2 Gender | H2a | H2b |
| H3 Interaction | H3a | H3b |

The analysis is a 2×2 mixed ANOVA on each DV, with α = .025 (Bonferroni correction for 2 DVs). If the data is skewed, an aligned rank transform (ART) ANOVA is used instead. If the interaction is significant, confident vs hedged is followed up separately for Eve and for Adam. The full design is in [`docs/design/`](docs/design/).

## Repo layout

```
experiment/experiment.html    the whole study app: one file, works offline
analysis/analyze.py           WOA, ANOVAs, ART, follow-up tests, charts → results/
google-sheets/collector.gs    optional: send data from every laptop to one Google Sheet
docs/researcher-run-sheet.md  how to run a session (for us)
docs/participant-instructions.md  printable handout (cover story only)
docs/design/                  experimental design slides (v1 original, v3 current)
data/                         put exported CSVs here locally (git-ignored)
```

## Quick start

**To run the study:** follow [`docs/researcher-run-sheet.md`](docs/researcher-run-sheet.md). In short, double-click `experiment/experiment.html`, pilot it, then hand the laptop to participants and export the CSV afterwards.

**To analyse the data:**

```bash
pip install -r requirements.txt
python analysis/analyze.py data/*.csv
python analysis/analyze.py data/*.csv --exclude-failed-checks   # sensitivity analysis
```

## Changing the experiment

Everything you might change is in the `CONFIG` block at the top of `experiment/experiment.html`: the advice delay, the image exposure time, the confident and hedged wording, the items, and the withdrawal contact.

- **Items:** each item has `truth` and `adviceDir` (+1 = advice 10% above the truth, −1 = 10% below). Set 1 makes the first half confident; set 2 swaps them. Keep one + item and one − item in each half. Add items in pairs.
- **Photos instead of dots:** set `type: "image"` and `src: "images/x.jpg"`. You need a verified true value for every photo.
- **Version tag:** if you change anything participants see, bump `STUDY_VERSION`. It is saved with every session.

## Working on this together

- Make your changes on a branch and open a pull request. Don't push straight to `main` once data collection has started.
- **Never commit participant data.** `data/`, `*.csv` and `results/` are git-ignored. Keep the data on the group's shared drive.
- Don't change the study after the first real participant unless the whole group agrees. If you do, bump `STUDY_VERSION`.
