# Would You Trust Her?

**How an AI assistant's perceived gender and confidence affect trust in its advice.**
Group 9 · Human Centred AI · Group Empirical Study.
Team: Cole Ternullo, Danny Dowling, Felim Sullivan, Laura Gonzalez, Liam Maher.

This is a Wizard-of-Oz experiment. Participants answer 6 estimation questions (how many sweets are in a jar, how far Dublin is from Paris, and so on; four come with a photo). For each one they give an estimate, see a pre-scripted "AI" answer that is always 10% off the truth, then give a final estimate and a trust rating. The assistant is shown by name only (no picture), and the confident and hedged sentences are both 11 words. There are two factors:

- **Assistant gender:** Eve (female) or Adam (male), between-subjects.
- **Wording confidence:** confident or hedged, within-subjects (4 trials each).

| Hypothesis | Weight of Advice (a) | Trust rating (b) |
|---|---|---|
| H1 Confidence | H1a | H1b |
| H2 Gender | H2a | H2b |
| H3 Interaction | H3a | H3b |

The analysis is a 2×2 mixed design on each DV, with α = .025 (Bonferroni correction for 2 DVs). The deciding test is fixed in advance: an aligned rank transform (ART) ANOVA for Weight of Advice (capping it at 0–1 makes it skewed) and an ordinary mixed ANOVA for trust. The other test is always reported as a robustness check. If the interaction is significant, confident vs hedged is followed up separately for Eve and for Adam. The full design is in [`docs/design/`](docs/design/).

## Repo layout

```
experiment/experiment.html    the study app, works offline
experiment/images/            the photos for the questions (must stay next to experiment.html)
stimulus-sources/             where each photo and true answer comes from (never shown to participants)
analysis/analyze.py           WOA, ANOVAs, ART, follow-up tests, charts → results/
google-sheets/collector.gs    Google Sheet backup: every laptop uploads each session automatically
docs/researcher-run-sheet.md  how to run a session (for us)
docs/participant-instructions.md  printable handout (cover story only)
docs/design/                  experimental design slides (v1 original, v3 current)
data/                         put exported CSVs here locally (git-ignored)
```

## Quick start

**To run the study:** follow [`docs/researcher-run-sheet.md`](docs/researcher-run-sheet.md). In short, copy the whole `experiment` folder to the laptop, double-click `experiment.html` inside it, pilot it, then hand the laptop to participants and export the CSV afterwards.

**To back up data to Google Sheets:** one person sets up the Sheet once (steps at the top of [`google-sheets/collector.gs`](google-sheets/collector.gs)) and pastes its URL into `SUBMIT_URL`. After that, every laptop uploads each finished session on its own and retries if the Wi-Fi drops. The researcher screen shows whether the backup is on and how many sessions are waiting. Keep the URL inside the group: don't commit it to GitHub.

**To analyse the data:**

```bash
pip install -r requirements.txt
python analysis/analyze.py data/*.csv
python analysis/analyze.py data/*.csv --exclude-failed-checks   # sensitivity analysis
```

## Changing the experiment

Everything you might change is in the `CONFIG` block at the top of `experiment/experiment.html`: the advice delay, the image exposure time, the confident and hedged wording, the items, and the withdrawal contact.

- **Items:** each item has a `question`, a `unit`, a `truth` and an `adviceDir` (+1 = advice 10% above the truth, −1 = 10% below). Confidence alternates down the list: in set 1 list positions 1, 3, 5 are confident and 2, 4, 6 are hedged; set 2 swaps them. With 3 items per group the + and − items can't split evenly, so each group has 2 of one and 1 of the other, and the item sets reverse this. Add or remove items in pairs.
- **Photos:** `type: "image"` with `src: "images/x.jpg"` shows a photo, and `type: "text"` shows the question on its own. You need a verified true value for every item: record the source in [`stimulus-sources/SOURCES.md`](stimulus-sources/SOURCES.md). Answers must be whole numbers.
- **Exposure time:** `EXPOSURE_MS: 0` keeps the photo on screen while the participant answers. A value such as `6000` shows it for 6 seconds and then hides it.
- **Version tag:** if you change anything participants see, bump `STUDY_VERSION`. It is saved with every session.

## Working on this together

- Make your changes on a branch and open a pull request. Don't push straight to `main` once data collection has started.
- **Never commit participant data.** `data/`, `*.csv` and `results/` are git-ignored. Keep the data on the group's shared drive.
- Don't change the study after the first real participant unless the whole group agrees. If you do, bump `STUDY_VERSION`.
