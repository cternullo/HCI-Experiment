/**
 * OPTIONAL — collect sessions from several laptops into one Google Sheet.
 *
 * 1. Create a Google Sheet. Extensions → Apps Script. Paste this file. Save.
 * 2. Deploy → New deployment → type "Web app".
 *    Execute as: Me.  Who has access: Anyone.  Deploy, then copy the /exec URL.
 * 3. Paste that URL into CONFIG.SUBMIT_URL in experiment.html.
 *
 * Every finished session adds 4 rows (one per trial) to the "trials" tab.
 * A withdrawal adds a row to the "withdrawals" tab — delete that participant's rows by hand.
 * Still export the CSV from each laptop as a backup: the upload is fire-and-forget.
 */
const COLS = ["pid","station","slot","assistant","ai_gender","item_set","version","started_at","completed_at",
  "position","item_id","confidence","truth","advice","initial","final","trust",
  "rt_initial_ms","rt_final_ms","rt_trust_ms",
  "hypothesis_guess","name_recall","name_correct","gender_perceived","conf_rating_confident","conf_rating_hedged","conf_check_left"];

function sheet_(name, header) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(name);
  if (!sh) { sh = ss.insertSheet(name); sh.appendRow(header); }
  return sh;
}

function doPost(e) {
  const s = JSON.parse(e.postData.contents);
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    if (s.withdrawn) {
      sheet_("withdrawals", ["pid", "withdrawn_at"]).appendRow([s.pid, s.withdrawn_at]);
    } else {
      const sh = sheet_("trials", COLS);
      s.trials.forEach(t => {
        const row = Object.assign({}, s, s.checks, t);
        sh.appendRow(COLS.map(c => row[c] === undefined ? "" : row[c]));
      });
    }
  } finally {
    lock.releaseLock();
  }
  return ContentService.createTextOutput("ok");
}
