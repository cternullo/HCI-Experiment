"""
Would You Trust Her? — analysis script (Group 9, Human Centred AI)

Usage:
    pip install -r requirements.txt
    python analysis/analyze.py data/*.csv
    python analysis/analyze.py data/*.csv --exclude-failed-checks

Outputs (in ./results/):
    report.md            descriptives, ANOVA tables, manipulation checks
    participant_means.csv one row per participant x confidence (what the ANOVA uses)
    fig_woa.png, fig_trust.png   2x2 bar charts, means ± SD

What it does (matches the pre-registered plan in the design deck):
  * WOA per trial = (final - initial) / (advice - initial), capped to [0, 1];
    trials where initial == advice are dropped.
  * Averages WOA and trust per participant for confident and for hedged trials.
  * 2x2 mixed ANOVA: assistant (Eve/Adam, between) x confidence (within),
    on WOA (tests H1a, H2a, H3a), then on trust (H1b, H2b, H3b).
  * alpha = .025 per ANOVA (Bonferroni for 2 DVs).
  * Aligned Rank Transform (ART) ANOVA as the non-parametric version; it is the
    deciding test when residuals are skewed (capped WOA usually is).
  * If the interaction is significant: confident vs hedged tested separately
    for Eve and for Adam.
"""
import argparse
import os
import re
import sys

import numpy as np
import pandas as pd
from scipy import stats
import pingouin as pg
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "results"
ALPHA = 0.025   # Bonferroni: .05 / 2 dependent variables (WOA, trust), per the design slides


# ----------------------------------------------------------------- loading
def load(paths):
    frames = [pd.read_csv(p) for p in paths]
    d = pd.concat(frames, ignore_index=True)
    d = d.drop_duplicates(subset=["pid", "item_id"])          # same file exported twice
    d = d[d["completed_at"].notna()].copy()
    return d


def compute_woa(d):
    same = d["initial"] == d["advice"]
    raw = (d["final"] - d["initial"]) / (d["advice"] - d["initial"])
    d["woa_raw"] = raw.where(~same)
    d["woa"] = d["woa_raw"].clip(0, 1)
    return d


# ----------------------------------------------------------------- checks
def manipulation_checks(d):
    p = d.drop_duplicates("pid")[
        ["pid", "assistant", "ai_gender", "item_set", "name_correct", "gender_perceived",
         "conf_rating_confident", "conf_rating_hedged", "hypothesis_guess"]].copy()
    p["name_correct"] = p["name_correct"].astype(str).str.lower().eq("true")
    p["gender_match"] = p["gender_perceived"] == p["ai_gender"]
    return p


# Whole words only, so "human", "manage" or "humanity" are NOT flagged.
# Word stems (confiden-, hedg-, gender-) also match their longer forms.
GUESS_PATTERN = re.compile(
    r"\b(gender\w*|female|male|woman|women|man|men|sex|confiden\w*|hedg\w*|certain\w*|names?)\b")


def guessed_hypothesis(text):
    """Flags guesses that mention the manipulated factors. Read them by hand too."""
    if pd.isna(text):
        return False
    return bool(GUESS_PATTERN.search(str(text).lower()))


# ----------------------------------------------------------------- ART ANOVA
def art_mixed_anova(df, dv, between, within, subject):
    """Aligned Rank Transform for a 2-factor mixed design (Wobbrock et al., 2011).
    For each effect: strip all effects from the response (residual = y - cell mean),
    add back only the effect of interest, rank, run the mixed ANOVA on the ranks
    and keep only the row for that effect."""
    y = df[dv]
    grand = y.mean()
    cell = df.groupby([between, within])[dv].transform("mean")
    a_mean = df.groupby(between)[dv].transform("mean")
    b_mean = df.groupby(within)[dv].transform("mean")
    resid = y - cell
    aligned = {
        between: resid + (a_mean - grand),
        within: resid + (b_mean - grand),
        "Interaction": resid + (cell - a_mean - b_mean + grand),
    }
    rows = []
    for effect, al in aligned.items():
        tmp = df[[between, within, subject]].copy()
        tmp["r"] = stats.rankdata(al)
        res = pg.mixed_anova(data=tmp, dv="r", between=between, within=within, subject=subject)
        res["Source"] = res["Source"].replace({f"{between} * {within}": "Interaction"})
        rows.append(res[res["Source"] == effect])
    return pd.concat(rows, ignore_index=True)


# ----------------------------------------------------------------- figures
def bar_chart(cell_stats, dv, ylabel, path, ylim=None):
    fig, ax = plt.subplots(figsize=(6, 4.2), dpi=150)
    conf_levels = ["confident", "hedged"]
    assistants = ["Eve", "Adam"]
    colors = {"confident": "#f07c45", "hedged": "#7a8699"}
    w = 0.36
    x = np.arange(len(assistants))
    for k, c in enumerate(conf_levels):
        sub = cell_stats.set_index(["assistant", "confidence"])
        m = [sub.loc[(a, c), "mean"] if (a, c) in sub.index else np.nan for a in assistants]
        s = [sub.loc[(a, c), "sd"] if (a, c) in sub.index else np.nan for a in assistants]
        ax.bar(x + (k - 0.5) * w, m, w, yerr=s, capsize=4, label=c.capitalize(), color=colors[c])
    ax.set_xticks(x)
    ax.set_xticklabels(assistants)
    ax.set_ylabel(ylabel)
    if ylim:
        ax.set_ylim(*ylim)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, title="Wording")
    ax.set_title(f"{ylabel} by assistant and wording (mean ± SD)", fontsize=10)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def pcol(df):
    """pingouin renamed 'p-unc' to 'p_unc' in newer versions; normalise to 'p'."""
    return df.rename(columns={"p-unc": "p", "p_unc": "p"})


def fmt_table(df):
    return df.to_markdown(index=False, floatfmt=".3f")


# ----------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", nargs="+")
    ap.add_argument("--exclude-failed-checks", action="store_true",
                    help="drop participants who got the name wrong or guessed the hypothesis")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    d = compute_woa(load(args.csv))
    checks = manipulation_checks(d)
    checks["guessed"] = checks["hypothesis_guess"].map(guessed_hypothesis)
    lines = ["# Would You Trust Her? — results\n"]

    n_total = checks["pid"].nunique()
    lines.append(f"Participants with complete data: **{n_total}** "
                 f"(Eve {sum(checks.assistant == 'Eve')}, Adam {sum(checks.assistant == 'Adam')})\n")

    # ---- manipulation checks
    lines.append("## Manipulation & demand checks\n")
    lines.append(f"- Recalled assistant name correctly: {checks.name_correct.sum()}/{n_total}")
    gp = pd.crosstab(checks["assistant"], checks["gender_perceived"])
    lines.append(f"- Perceived gender by condition:\n\n{gp.to_markdown()}\n")
    cc, ch = checks["conf_rating_confident"], checks["conf_rating_hedged"]
    if len(checks) >= 2:
        t = stats.ttest_rel(cc, ch)
        w = stats.wilcoxon(cc, ch) if (cc != ch).any() else None
        lines.append(f"- Confidence check: confident M = {cc.mean():.2f} (SD {cc.std():.2f}), "
                     f"hedged M = {ch.mean():.2f} (SD {ch.std():.2f}); paired t({len(cc) - 1}) = "
                     f"{t.statistic:.2f}, p = {t.pvalue:.4f}"
                     + (f"; Wilcoxon W = {w.statistic:.1f}, p = {w.pvalue:.4f}" if w else ""))
    lines.append(f"- Hypothesis guess mentions gender/confidence/name (auto-flag, **check by hand**): "
                 f"{checks.guessed.sum()}/{n_total}\n")
    flagged = checks[checks.guessed][["pid", "assistant", "hypothesis_guess"]]
    if len(flagged):
        lines.append(fmt_table(flagged) + "\n")

    if args.exclude_failed_checks:
        bad = checks[(~checks.name_correct) | checks.guessed]["pid"]
        d = d[~d["pid"].isin(bad)]
        lines.append(f"**Excluded {len(bad)} participant(s)** for failed name check or hypothesis guess.\n")

    # ---- trial-level summary
    dropped = d["woa"].isna().sum()
    raw = d["woa_raw"].dropna()
    lines.append("## Trials\n")
    lines.append(f"- Trials: {len(d)}; dropped from WOA because initial = advice: {dropped}")
    lines.append(f"- Raw WOA outside [0, 1] before capping: {((raw < 0) | (raw > 1)).sum()} of {len(raw)} "
                 f"(<0 = moved away from AI, >1 = overshot AI)")
    lines.append(f"- WOA exactly 0 (ignored AI): {(d.woa == 0).sum()}; exactly 1 (copied AI): {(d.woa == 1).sum()}\n")

    # ---- per participant x confidence
    pm = (d.groupby(["pid", "assistant", "confidence"], as_index=False)
            .agg(woa=("woa", "mean"), trust=("trust", "mean"), n_woa_trials=("woa", "count")))
    pm.to_csv(os.path.join(OUT, "participant_means.csv"), index=False)

    for dv, label, ylim in [("woa", "Weight of Advice", (0, 1.05)), ("trust", "Trust (1–7)", (1, 7.5))]:
        sub = pm.dropna(subset=[dv])
        # listwise: keep participants with both confidence levels
        complete = sub.groupby("pid")["confidence"].nunique()
        sub = sub[sub["pid"].isin(complete[complete == 2].index)]
        lost = pm["pid"].nunique() - sub["pid"].nunique()

        lines.append(f"## {label}\n")
        if lost:
            lines.append(f"_{lost} participant(s) excluded from this analysis: no usable trial in one confidence level._\n")
        cs = (sub.groupby(["assistant", "confidence"])[dv]
                 .agg(n="count", mean="mean", sd="std", median="median").reset_index())
        lines.append(fmt_table(cs) + "\n")
        bar_chart(cs, dv, label, os.path.join(OUT, f"fig_{dv}.png"), ylim)

        if sub["pid"].nunique() < 4 or sub["assistant"].nunique() < 2:
            lines.append("_Not enough participants for ANOVA yet._\n")
            continue

        suffix = "a" if dv == "woa" else "b"
        hyp = {"confidence": f"H1{suffix}", "assistant": f"H2{suffix}", "Interaction": f"H3{suffix}"}

        aov = pcol(pg.mixed_anova(data=sub, dv=dv, between="assistant", within="confidence", subject="pid"))
        aov["Source"] = aov["Source"].replace({"assistant * confidence": "Interaction"})
        art = pcol(art_mixed_anova(sub, dv, "assistant", "confidence", "pid"))

        # Normality of residuals decides which ANOVA is the deciding test (slides: skewed -> ART)
        resid = sub[dv] - sub.groupby(["assistant", "confidence"])[dv].transform("mean")
        use_art = False
        if len(resid) >= 3 and resid.std() > 0:
            sw = stats.shapiro(resid)
            use_art = sw.pvalue < .05
            lines.append(f"Shapiro–Wilk on residuals: W = {sw.statistic:.3f}, p = {sw.pvalue:.4f} → "
                         + ("skewed/non-normal, so the **ART ANOVA decides** the hypotheses."
                            if use_art else "no strong evidence against normality, so the **mixed ANOVA decides** the hypotheses.") + "\n")

        for name, tab, is_main in [("Mixed ANOVA", aov, not use_art), ("Aligned Rank Transform ANOVA", art, use_art)]:
            t = tab.copy()
            t.insert(0, "Hypothesis", t["Source"].map(hyp))
            if is_main:
                t["Decision"] = np.where(t["p"] < ALPHA, f"reject H0 (p < {ALPHA})", "retain H0")
            keep = [c for c in ["Hypothesis", "Source", "DF1", "DF2", "F", "p", "np2", "Decision"] if c in t.columns]
            lines.append(f"**{name}**{' (deciding test)' if is_main else ' (robustness check)'}\n")
            lines.append(fmt_table(t[keep]) + "\n")

        # Effect size for H1 (paired, pooled over assistant)
        wide = sub.pivot(index="pid", columns="confidence", values=dv)
        diff = wide["confident"] - wide["hedged"]
        dz = diff.mean() / diff.std() if diff.std() > 0 else np.nan
        lines.append(f"Confident − hedged (all participants): mean difference = {diff.mean():.3f}, Cohen's d_z = {dz:.2f}\n")

        # Follow-up: only if the interaction is significant in the deciding test
        main_tab = art if use_art else aov
        p_int = float(main_tab.loc[main_tab["Source"] == "Interaction", "p"].iloc[0])
        if p_int < ALPHA:
            lines.append(f"**Follow-up for H3{suffix}** (interaction p = {p_int:.4f} < {ALPHA}): "
                         f"confident vs hedged tested separately for Eve and for Adam, α = {ALPHA}\n")
            rows = []
            for a in ["Eve", "Adam"]:
                w = wide[wide.index.isin(sub.loc[sub.assistant == a, "pid"])]
                dd = w["confident"] - w["hedged"]
                if len(dd) < 2:
                    continue
                if use_art:
                    st = stats.wilcoxon(w["confident"], w["hedged"]) if (dd != 0).any() else None
                    test, stat, pv = "Wilcoxon W", (st.statistic if st else np.nan), (st.pvalue if st else 1.0)
                else:
                    st = stats.ttest_rel(w["confident"], w["hedged"])
                    test, stat, pv = f"paired t({len(dd) - 1})", st.statistic, st.pvalue
                rows.append({"Assistant": a, "n": len(dd), "Confident M": w["confident"].mean(),
                             "Hedged M": w["hedged"].mean(), "Test": test, "Statistic": stat, "p": pv,
                             "d_z": dd.mean() / dd.std() if dd.std() > 0 else np.nan,
                             "Decision": "significant" if pv < ALPHA else "not significant"})
            lines.append(fmt_table(pd.DataFrame(rows)) + "\n")
        else:
            lines.append(f"Interaction not significant (p = {p_int:.4f}), so no follow-up tests (as planned).\n")
        lines.append(f"![{label}](fig_{dv}.png)\n")

    with open(os.path.join(OUT, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))
    print(f"\nSaved to ./{OUT}/")


if __name__ == "__main__":
    sys.exit(main())
