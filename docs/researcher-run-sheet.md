# Would You Trust Her? — Researcher Run Sheet

## Before the session day

Each laptop needs about 10 minutes of setup. Do this the day before, not with a participant waiting.

1. **Copy `experiment/experiment.html` onto every laptop you'll use.** Open it by double-clicking the file, in Chrome, Edge or Firefox. Don't open it inside a preview, email or chat window, because the data is saved in that browser.
2. **Check the home screen.** It says "Ready for the next participant". If you see a yellow storage warning, the browser can't save data: close it and open the file directly.
3. **Give each laptop its own station letter.** Go to **Data & settings → Station & slot**. Set A, B, C and so on, then press Save. Each station has its own balanced list, and its participant IDs start with that letter.
4. **Run one pilot of each condition.** Go to **Data & settings → Pilot as Eve**, then **Pilot as Adam**, and click through the whole study. Pilot runs save nothing and don't use up a slot.
5. **Turn on the Google Sheet backup.** One person sets up the Sheet once (steps at the top of `google-sheets/collector.gs`) and pastes the URL into `SUBMIT_URL` in `experiment.html` *before* the file is copied onto the laptops. On each laptop the home screen should then say "Google Sheet backup: on". Pilot runs never upload, so test it with one normal session per laptop: check its 4 rows appear in the Sheet, then press **Withdraw my data** on the debrief screen and check the rows disappear. That removes the test from the laptop and the Sheet, and gives the slot back.
6. **Set the withdrawal contact.** The consent and debrief screens tell participants to contact "a member of Group 9". If you want a named person or email, change `CONTACT` at the top of the file on every laptop.
7. **Prepare the laptop.** Charge it, close other tabs, turn off notifications, and set browser zoom so that the whole dot image fits on screen.
8. **Prepare the room.** Run one participant at a time, and make sure people waiting can't see the screen. Have the printed participant sheets ready.

**Agree on these rules as a group:**

- Every researcher uses the same cover story: "We're testing an AI that helps with estimates."
- Never say "Eve", "Adam", gender, confidence or wording to anyone before their debrief.
- Participants must be classmates aged 18 or over.
- If two researchers each run their own laptop, each one keeps a separate log (see Session log, below).

## Running one participant

Each participant takes about 5 minutes. You only touch the laptop at the start and the end.

1. **Check the home screen.** It shows the station, the next slot number and how many have been completed. The condition is not shown here. If you need it, it is under **Data & settings → Next participant's condition**; only open that when no participant can see the screen.
2. **Greet them and use the cover story.** Say: *"Thanks for helping. We're testing an AI assistant that helps people make quick estimates. It takes about five minutes, and everything you need is on screen. Here's a sheet with the steps."*
3. **Press "Hand over to participant →"**, then give them the laptop and the participant sheet.
4. **Consent.** They read the information and tick the box. If they press **I do not want to take part**, nothing is saved. Thank them and press **Researcher: return**.
5. **Step back.** Sit to the side where you can't see the screen. Don't comment on their answers or on the assistant.
6. **The study runs on its own.** It shows the assistant intro, then 4 tasks, then 4 short questions, then the debrief. Each task goes: Show image → 6 s of dots → estimate → 2 s wait → the assistant's answer → final estimate → 1–7 trust rating.
7. **Debrief.** Make sure they read it. If they might want their data deleted later, they can photograph their participant ID on that screen. They press **Finish**, or **Withdraw my data**.
8. **Take the laptop back** on the "All done" screen and press **Researcher: next participant**. Check that the completed count went up by 1. Then write a log line (see below).
9. **Close the session.** Say: *"Please don't talk about the study with anyone who hasn't done it yet. It would change their answers."*

**What to say if a participant asks a question during the study:**

| They ask | You say |
| --- | --- |
| "Can I count the dots?" | "There isn't time. Just give your best estimate." |
| "Is the AI real? Is it any good?" | "I can explain everything at the end." |
| "Should I go with its answer?" | "Do whatever you think is most accurate." |
| "What's this study really about?" | "I'll tell you all about it at the end." |
| "I typed the wrong number." | "That's okay, just carry on." (Note it in the log.) |

## If something goes wrong

Rule of thumb: never re-run the same person, and never edit their data. Abandon the session or delete it, then write it in the log.

| Situation | What to do |
| --- | --- |
| Participant wants to stop part-way | Press **Ctrl + Shift + X**. The partial data is deleted and the slot is reused by the next person. |
| Participant declines consent | They press **I do not want to take part**. Nothing is saved. |
| Participant withdraws at the debrief | They press **Withdraw my data**, then confirm. Their data is deleted and the slot is returned. |
| Participant asks to withdraw later | Ask for their ID (e.g. A007-K3). Go to **Data & settings → Sessions**, type the ID and press Delete. Do it on the laptop they used. This also deletes their rows from the Google Sheet automatically (check the Sheet afterwards). |
| Laptop freezes, or the page is refreshed mid-study | The session can't be resumed. Reopen the file. The unfinished session is excluded from the export and the slot is not used up. Don't run that person again, because they've already seen the images. |
| Home screen says "waiting to upload" and the number keeps growing | The laptop can't reach Google (no Wi-Fi). Carry on: the data is safe on the laptop and uploads by itself once it's back online. Export the CSV at the end of the block as usual. |
| Storage warning on the home screen | Data isn't being saved. Close the browser and open `experiment.html` directly by double-clicking it. |
| A participant already knows what the study is about | Run them as normal and note it in the log. Their hypothesis-guess answer will usually flag it. |
| A participant saw the condition (e.g. in **Data & settings**) | Carry on, but note it in the log so the group can decide whether to exclude them. |

### Session log

Keep one log per laptop. Copy this table into your own notes or a shared sheet.

| Date | Participant ID | Researcher | Notes (problems, mistyped numbers, prior knowledge) |
| --- | --- | --- | --- |
|  |  |  |  |

## After every block of sessions, and at the end of the day

The data exists only in that laptop's browser until you export it. Export after every block of sessions.

1. Go to **Data & settings → Download CSV**. The file is named like `trust_study_A_2026-11-20.csv`.
2. Also press **Download raw JSON (backup)**.
3. If downloads don't work, press **Show CSV to copy**, then paste the text into a file ending in `.csv`.
4. Upload both files to the group's shared drive the same day. Keep one CSV per laptop per day, and don't merge them by hand. **Don't commit participant data to this repo.**
5. If the Google Sheet backup is on, check **Data & settings → Google Sheet backup** says "waiting to upload: 0". If not, press **Retry uploads now** once you're on Wi-Fi.
6. Check the **Balance** table. Each Eve/Adam × set 1/2 cell should be about equal.
7. Only use **Clear all data** once the backup is safely in the shared drive. Never clear the browser's history or site data on a study laptop.

**When data collection is finished:**

1. Put every CSV in the `data/` folder of your local copy of this repo. You can use the laptop CSVs, the Google Sheet's "trials" tab (File → Download → CSV), or both: the script removes duplicates.
2. Run `pip install pandas numpy scipy matplotlib pingouin tabulate` once.
3. Run `python analysis/analyze.py data/*.csv`, then open `results/report.md` and the two charts.
4. Read every hypothesis guess yourselves, then decide which exclusions to make. Run `python analysis/analyze.py data/*.csv --exclude-failed-checks` as the sensitivity check, and report both runs.
