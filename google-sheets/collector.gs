/**
 * Google Sheet backup — every laptop sends each finished session here automatically.
 *
 * SET-UP (one person, once, about 5 minutes):
 * 1. Create a new Google Sheet (e.g. "Trust study data"). Extensions → Apps Script.
 * 2. Delete the sample code, paste this whole file, and press Save.
 * 3. Deploy → New deployment → gear icon → "Web app".
 *      Execute as: Me.   Who has access: Anyone.   → Deploy, approve the permissions,
 *      then copy the Web app URL (it ends in /exec).
 * 4. Open that URL in a browser. It should say "Trust study collector is running".
 * 5. Paste the URL into CONFIG.SUBMIT_URL near the top of experiment/experiment.html,
 *    and copy that updated file onto every study laptop.
 * 6. On one laptop, run a real test session (not a pilot), then check that 4 rows appear
 *    in the "trials" tab. Delete those test rows before real data collection starts.
 *
 * If you edit this script later: Deploy → Manage deployments → edit → Version: New version,
 * so the URL stays the same.
 *
 * WHAT IT DOES
 * - A finished session adds one row per trial to the "trials" tab.
 * - A session the Sheet already has is skipped, so a laptop can safely resend.
 * - A withdrawal deletes all of that participant's rows and logs the ID in "withdrawals".
 * - For analysis: File → Download → CSV on the "trials" tab, put the file in data/,
 *   and run analysis/analyze.py as usual. Keep the laptop CSV exports as a second copy.
 *
 * PRIVACY: the URL accepts data from anyone who has it. Only share it inside the group,
 * and don't post it anywhere public (including GitHub).
 */
const COLS = ["pid","station","slot","assistant","ai_gender","item_set","version","started_at","completed_at",
  "position","item_id","confidence","truth","advice","initial","final","trust",
  "rt_initial_ms","rt_final_ms","rt_trust_ms",
  "hypothesis_guess","name_recall","name_correct","gender_perceived","conf_rating_confident","conf_rating_hedged","conf_check_left",
  "received_at"];

function sheet_(name, header) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(name);
  if (!sh) { sh = ss.insertSheet(name); sh.appendRow(header); sh.setFrozenRows(1); }
  return sh;
}

function pidsIn_(sh) {
  const n = sh.getLastRow() - 1;
  if (n < 1) return [];
  return sh.getRange(2, 1, n, 1).getValues().map(r => String(r[0]));
}

function deleteRowsFor_(sh, pid) {
  const pids = pidsIn_(sh);
  for (let i = pids.length - 1; i >= 0; i--) {          // bottom up, so row numbers don't shift
    if (pids[i].toUpperCase() === String(pid).toUpperCase()) sh.deleteRow(i + 2);
  }
}

function doPost(e) {
  const s = JSON.parse(e.postData.contents);
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const trials = sheet_("trials", COLS);
    const now = new Date().toISOString();
    if (s.withdrawn) {
      deleteRowsFor_(trials, s.pid);
      sheet_("withdrawals", ["pid", "withdrawn_at", "received_at"]).appendRow([s.pid, s.withdrawn_at, now]);
    } else {
      const withdrawn = pidsIn_(sheet_("withdrawals", ["pid", "withdrawn_at", "received_at"]));
      if (pidsIn_(trials).includes(String(s.pid)) || withdrawn.includes(String(s.pid))) {
        return ContentService.createTextOutput("duplicate or withdrawn, skipped");
      }
      const rows = s.trials.map(t => {
        const row = Object.assign({}, s, s.checks, t, { received_at: now });
        return COLS.map(c => row[c] === undefined || row[c] === null ? "" : row[c]);
      });
      if (rows.length) trials.getRange(trials.getLastRow() + 1, 1, rows.length, COLS.length).setValues(rows);
    }
  } finally {
    lock.releaseLock();
  }
  return ContentService.createTextOutput("ok");
}

function doGet() {
  return ContentService.createTextOutput("Trust study collector is running.");
}
