"""
Group 9 - "Would You Trust Her?"
Works out every number, table and graph in the Results, Statistical Tests
and Conclusions sections of our report.

How to run (from the repo root, with the laptop CSVs in data/):
    pip install -r requirements.txt
    python analysis/make_results.py data/trust_study_A_2026-11-12.csv data/trust_study_C_2026-11-12.csv

It prints all the results (saved copy: analysis/results_output.txt) and saves the
five figures as PNGs in analysis/figures/.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pingouin as pg
from scipy import stats
from statsmodels.stats.power import TTestIndPower, TTestPower

ALPHA = 0.025  # .05 split across our two measures (Bonferroni)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)


# ------------------------------------------------------------------ load data
files = sys.argv[1:]
if not files:
    sys.exit("Give the CSV file(s) from the laptops, e.g. python make_results.py trust_study_A.csv trust_study_C.csv")
d = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
d = d.drop_duplicates(["pid", "item_id"])          # in case the same file was loaded twice
people = d.drop_duplicates("pid").copy()           # one row per participant

# Weight of Advice per trial: how far they moved towards the AI, capped to 0-1.
# (The laptops already save this as "woa", but we recalculate it to be sure.)
raw = (d["final"] - d["initial"]) / (d["advice"] - d["initial"])
d["woa"] = raw.clip(0, 1)
d.loc[d["initial"] == d["advice"], "woa"] = np.nan  # can't be calculated, so dropped

# One score per person per wording: the mean of their 3 confident and 3 hedged trials
pm = (d.groupby(["pid", "assistant", "confidence"], as_index=False)
        .agg(woa=("woa", "mean"), trust=("trust", "mean")))


def p_col(t):
    # pingouin calls the p-value column 'p-unc' or 'p_unc' depending on the version
    return t.rename(columns={"p-unc": "p", "p_unc": "p"})


def mixed_anova(data, dv):
    t = p_col(pg.mixed_anova(data=data, dv=dv, between="assistant", within="confidence", subject="pid"))
    t["Source"] = t["Source"].replace({"assistant * confidence": "Interaction"})
    return t


def art_anova(data, dv):
    """Aligned Rank Transform ANOVA (Wobbrock et al., 2011) for our 2x2 mixed design.
    For each effect: take out every effect, put back only the one being tested,
    rank the result, and run the normal mixed ANOVA on the ranks."""
    y = data[dv]
    grand = y.mean()
    cell = data.groupby(["assistant", "confidence"])[dv].transform("mean")
    a = data.groupby("assistant")[dv].transform("mean")
    b = data.groupby("confidence")[dv].transform("mean")
    resid = y - cell
    aligned = {"assistant": resid + (a - grand),
               "confidence": resid + (b - grand),
               "Interaction": resid + (cell - a - b + grand)}
    rows = []
    for effect, values in aligned.items():
        tmp = data[["pid", "assistant", "confidence"]].copy()
        tmp["rank"] = stats.rankdata(values)
        t = mixed_anova(tmp, "rank")
        rows.append(t[t["Source"] == effect])
    return pd.concat(rows, ignore_index=True)


def show(t, title):
    print(f"\n{title}")
    for r in t.itertuples():
        print(f"  {r.Source:<12} F({r.DF1:.0f}, {r.DF2:.0f}) = {r.F:5.2f}   p = {r.p:.3f}   np2 = {r.np2:.2f}")


# ------------------------------------------------------------------ the sample
print(f"Participants: {len(people)}  ({people.assistant.value_counts().to_dict()})")
print(f"Trials: {len(d)}")
mins = (pd.to_datetime(people.completed_at) - pd.to_datetime(people.started_at)).dt.total_seconds() / 60
print(f"Session length: median {mins.median():.1f} min (range {mins.min():.1f} to {mins.max():.1f})")
print(f"Raw WOA outside 0-1 (capped): {((raw < 0) | (raw > 1)).sum()}")
print(f"WOA = 0 (ignored AI): {(d.woa == 0).sum()}   WOA = 1 (copied AI): {(d.woa == 1).sum()}")

# ------------------------------------------------------------------ manipulation checks
c, h = people.conf_rating_confident, people.conf_rating_hedged
t = stats.ttest_rel(c, h)
print(f"\nConfidence check: confident M = {c.mean():.2f} (SD {c.std():.2f}), "
      f"hedged M = {h.mean():.2f} (SD {h.std():.2f}); t({len(c) - 1}) = {t.statistic:.2f}, p = {t.pvalue:.4f}; "
      f"Wilcoxon p = {stats.wilcoxon(c, h).pvalue:.4f}; rated confident higher: {(c > h).sum()}/{len(c)}")

people["name_ok"] = people.name_correct.astype(str).str.lower().eq("true")
print("\nRecalled the name:", people.groupby("assistant").name_ok.sum().to_dict())
print(pd.crosstab(people.assistant, people.gender_perceived))
tab = pd.crosstab(people.assistant, people.name_ok)
print(f"Fisher's exact test on name recall: p = {stats.fisher_exact(tab.values).pvalue:.2f}")

# ------------------------------------------------------------------ descriptives (Table 2)
print("\nMean (SD) per condition:")
print(pm.groupby(["assistant", "confidence"])[["woa", "trust"]].agg(["mean", "std"]).round(2))
print(pm.groupby("confidence")[["woa", "trust"]].agg(["mean", "std"]).round(2))
print(pm.groupby(["pid", "assistant"])[["woa", "trust"]].mean().groupby("assistant").mean().round(2))

# ------------------------------------------------------------------ checks done before the tests
print(f"\nControls: advice exactly 10% off on every trial: "
      f"{np.allclose(d.advice, np.round(d.truth * np.where(d.advice > d.truth, 1.1, 0.9)))}")
print("Advice too high (+1) / too low (-1) per wording:\n", pd.crosstab(d.confidence, np.sign(d.advice - d.truth)))
print("Item set per assistant:\n", pd.crosstab(people.assistant, people.item_set))
print(f"Trials where own estimate = AI's answer (can't be scored): {(d.initial == d.advice).sum()}")
for dv in ["woa", "trust"]:
    resid = pm[dv] - pm.groupby(["assistant", "confidence"])[dv].transform("mean")
    sw = stats.shapiro(resid)
    print(f"Shapiro-Wilk on {dv} residuals: W = {sw.statistic:.3f}, p = {sw.pvalue:.2f}")

# ------------------------------------------------------------------ main tests (Table 2)
# The presentation planned a mixed ANOVA on each measure, with an ART ANOVA if the data were skewed.
# We report both for both measures. assistant = H2, confidence = H1, interaction = H3; a = WOA, b = trust.
show(mixed_anova(pm, "woa"), "WOA - mixed ANOVA (H1a, H2a, H3a)")
show(art_anova(pm, "woa"), "WOA - ART ANOVA")
show(mixed_anova(pm, "trust"), "Trust - mixed ANOVA (H1b, H2b, H3b)")
show(art_anova(pm, "trust"), "Trust - ART ANOVA")
print("H1 predicted a direction, so a one-tailed p is half the two-tailed p (the means went the predicted way).")

wide = pm.pivot(index="pid", columns="confidence", values=["woa", "trust"])
for dv in ["woa", "trust"]:
    diff = wide[dv, "confident"] - wide[dv, "hedged"]
    print(f"Effect size of wording on {dv}: d_z = {diff.mean() / diff.std():.2f}")
print(f"People with higher WOA after confident advice: {(wide['woa', 'confident'] > wide['woa', 'hedged']).sum()}/{len(wide)}")

# ------------------------------------------------------------------ extra (exploratory) analyses
named = people[people.name_ok].pid
show(art_anova(pm[pm.pid.isin(named)], "woa"), "WOA without the people who forgot the name")
show(mixed_anova(pm[pm.pid.isin(named)], "trust"), "Trust without the people who forgot the name")
guessed = people[people.hypothesis_guess.str.contains(r"\b(?:gender|female|male|confiden\w*)\b", case=False, na=False)].pid
show(art_anova(pm[pm.pid.isin(named) & ~pm.pid.isin(guessed)], "woa"),
     f"WOA without those AND without people who guessed the hypothesis ({list(guessed)})")

for g in ["Eve", "Adam"]:
    s = pm[pm.assistant == g].pivot(index="pid", columns="confidence", values="woa")
    w = stats.wilcoxon(s.confident, s.hedged)
    print(f"{g}: confident vs hedged WOA, Wilcoxon W = {w.statistic:.0f}, p = {w.pvalue:.3f}; "
          f"{(s.confident > s.hedged).sum()} of {len(s)} went up")

r = pg.rm_corr(data=d.dropna(subset=["woa"]), x="woa", y="trust", subject="pid")
print(f"\nWOA vs trust (repeated-measures correlation): r = {r.r.iloc[0]:.2f}, "
      f"95% CI {r['CI95%' if 'CI95%' in r else 'CI95'].iloc[0]}, p = {r.pval.iloc[0]:.4f}")
print("WOA per question:", d.groupby("item_id").woa.mean().round(2).to_dict())

n = len(people)
print(f"\nPower: with n = {n}, 80% power at alpha = {ALPHA} needs d_z = "
      f"{TTestPower().solve_power(nobs=n, alpha=ALPHA, power=.8):.2f} (wording) and d = "
      f"{TTestIndPower().solve_power(nobs1=n // 2, alpha=ALPHA, power=.8):.2f} (gender)")
print(f"People needed to detect d_z = 0.42 for wording: {TTestPower().solve_power(effect_size=.42, alpha=ALPHA, power=.8):.0f}")
print(f"People per group needed for d = 0.5 for gender: {TTestIndPower().solve_power(effect_size=.5, alpha=ALPHA, power=.8):.0f}")

# ------------------------------------------------------------------ figures
BLUE, ORANGE, INK, GREY, GRID, BG = "#2a78d6", "#eb6834", "#2b2b29", "#6b6a63", "#e4e3de", "#fcfcfb"
COL = {"confident": BLUE, "hedged": ORANGE}
plt.rcParams.update({"font.size": 11, "axes.edgecolor": GREY, "ytick.color": GREY,
                     "figure.facecolor": BG, "axes.facecolor": BG})
rng = np.random.default_rng(3)  # only used to spread the dots sideways so they don't overlap


def tidy(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.yaxis.grid(True, color=GRID)
    ax.set_axisbelow(True)


def bar_chart(dv, ylabel, ylim, fname, title):
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    w = 0.36
    for j, conf in enumerate(["confident", "hedged"]):
        for i, g in enumerate(["Eve", "Adam"]):
            v = pm[(pm.assistant == g) & (pm.confidence == conf)][dv]
            x = i + (j - 0.5) * w * 1.06
            ax.bar(x, v.mean(), w, color=COL[conf], label=conf.capitalize() if i == 0 else None, zorder=2)
            ax.errorbar(x, v.mean(), yerr=v.std(), color=INK, capsize=5, lw=1.4, zorder=3)  # error bar = 1 SD
            ax.scatter(x + rng.uniform(-.07, .07, len(v)), v, s=22, facecolor="white", edgecolor=INK, zorder=4)
            ax.text(x, ylim[0] + (ylim[1] - ylim[0]) * .03, f"{v.mean():.2f}", ha="center",
                    color="white", fontsize=10, fontweight="bold", zorder=5)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Eve (female name)\nn = 6", "Adam (male name)\nn = 6"])
    ax.set_ylim(*ylim)
    ax.set_ylabel(ylabel)
    tidy(ax)
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold", color=INK)
    ax.legend(title="Advice wording", frameon=False, loc="upper left", bbox_to_anchor=(1, 1))
    fig.text(.01, .01, "Bars = means; error bars = ±1 SD; dots = individual participants.", fontsize=9, color=GREY)
    fig.tight_layout(rect=(0, .04, 1, 1))
    fig.savefig(os.path.join(OUT, fname), dpi=200)
    plt.close(fig)


bar_chart("woa", "Weight of Advice (0 = ignored, 1 = copied)", (0, 1.12), "fig1_woa.png",
          "Figure 1. Weight of Advice by assistant and wording")
bar_chart("trust", "Trust rating (1–7)", (0, 7.6), "fig2_trust.png",
          "Figure 2. Trust rating by assistant and wording")

# Figure 3: did people hear the difference between the two wordings?
fig, ax = plt.subplots(figsize=(6.2, 4.4))
for i, (col, conf) in enumerate([("conf_rating_confident", "confident"), ("conf_rating_hedged", "hedged")]):
    v = people[col]
    ax.bar(i, v.mean(), .55, color=COL[conf], zorder=2)
    ax.errorbar(i, v.mean(), yerr=v.std(), color=INK, capsize=6, lw=1.4, zorder=3)
    ax.text(i, .25, f"{v.mean():.2f}", ha="center", color="white", fontweight="bold", zorder=5)
for a, b in zip(people.conf_rating_confident, people.conf_rating_hedged):
    ax.plot([0, 1], [a + rng.uniform(-.08, .08), b + rng.uniform(-.08, .08)], color=GREY, lw=.8, alpha=.6, zorder=4)
ax.set_xticks([0, 1])
ax.set_xticklabels(['"I\'m certain the answer\nis 450…" (confident)', '"I think it\'s probably\naround 450…" (hedged)'])
ax.set_ylim(0, 7.8)
ax.set_ylabel("How confident it sounds (1–7)")
tidy(ax)
ax.set_title("Figure 3. Perceived confidence of each wording", loc="left", fontsize=12, fontweight="bold", color=INK)
fig.text(.01, .01, f"n = {len(people)}. Bars = means; error bars = ±1 SD; grey lines = individual participants.",
         fontsize=9, color=GREY)
fig.tight_layout(rect=(0, .04, 1, 1))
fig.savefig(os.path.join(OUT, "fig3_confidence_check.png"), dpi=200)
plt.close(fig)

# Figure 4: did people notice the gender?
order = ["female", "male", "neither", "didnt_think"]
labels = {"female": "Female", "male": "Male", "neither": "Neither", "didnt_think": "Didn't think about it"}
shades = {"female": "#8e2f57", "male": "#24578a", "neither": "#a8a7a0", "didnt_think": "#d6d5cf"}
counts = pd.crosstab(people.assistant, people.gender_perceived).reindex(index=["Eve", "Adam"], columns=order, fill_value=0)
fig, ax = plt.subplots(figsize=(7.2, 3.0))
for i, g in enumerate(counts.index):
    left = 0
    for cat in order:
        n_ = counts.loc[g, cat]
        if n_:
            ax.barh(i, n_, left=left, color=shades[cat], edgecolor=BG, lw=2, label=labels[cat] if i == 0 or g == "Adam" else None)
            ax.text(left + n_ / 2, i, str(n_), ha="center", va="center",
                    color="white" if cat in ("female", "male") else INK, fontweight="bold")
            left += n_
    recalled = people[people.assistant == g].name_ok.sum()
    ax.text(6.15, i, f"name recalled: {recalled}/6", va="center", fontsize=10, color=INK)
ax.set_yticks([0, 1])
ax.set_yticklabels(["Eve", "Adam"])
ax.invert_yaxis()
ax.set_xlim(0, 8.2)
ax.set_xticks(range(7))
ax.set_xlabel("Number of participants")
ax.spines[["top", "right"]].set_visible(False)
h, l = ax.get_legend_handles_labels()
seen = dict(zip(l, h))
ax.legend([seen[labels[c]] for c in order if labels[c] in seen], [labels[c] for c in order if labels[c] in seen],
          frameon=False, ncol=4, loc="upper left", bbox_to_anchor=(0, -0.32), fontsize=9)
ax.set_title('Figure 4. "Did you think of the assistant as…?"', loc="left", fontsize=12, fontweight="bold", color=INK)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig4_gender_check.png"), dpi=200)
plt.close(fig)

# Figure 5: each person's WOA for hedged vs confident advice
fig, axs = plt.subplots(1, 2, figsize=(7.2, 4.2), sharey=True)
for ax, g in zip(axs, ["Eve", "Adam"]):
    s = pm[pm.assistant == g].pivot(index="pid", columns="confidence", values="woa")
    for _, r in s.iterrows():
        up = r.confident > r.hedged
        ax.plot([0, 1], [r.hedged, r.confident], color=INK if up else GREY, lw=1.6 if up else 1.2,
                ls="-" if up else "--", marker="o", ms=6, mfc="white", zorder=3)
    ax.plot([0, 1], [s.hedged.mean(), s.confident.mean()], color=BLUE, lw=3.5, marker="o", ms=8, zorder=4)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Hedged", "Confident"])
    ax.set_xlim(-.3, 1.3)
    ax.set_ylim(-.05, 1.08)
    ax.set_title(f"{g}: {(s.confident > s.hedged).sum()} of {len(s)} rose", fontsize=11, color=INK)
    tidy(ax)
axs[0].set_ylabel("Weight of Advice (participant mean)")
fig.suptitle("Figure 5. Each participant's WOA, hedged vs confident", x=.01, ha="left",
             fontsize=12, fontweight="bold", color=INK)
fig.text(.01, .01, "Solid black = higher after confident advice; dashed grey = lower; thick blue = group mean.",
         fontsize=9, color=GREY)
fig.tight_layout(rect=(0, .04, 1, .95))
fig.savefig(os.path.join(OUT, "fig5_woa_per_participant.png"), dpi=200)
plt.close(fig)

print(f"\nFigures saved in {OUT}")
