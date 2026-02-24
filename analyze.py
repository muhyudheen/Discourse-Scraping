"""
IITM Discourse Forum — Community Analysis
==========================================
Loads combine.json, cleans the data, computes summary statistics,
and prints a structured report that feeds the data story.

Run:
    python analyze.py
"""

import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
DATA = ROOT / "data" / "combined.json"
OUT  = ROOT / "output"
OUT.mkdir(exist_ok=True)

# ── 1. Load ───────────────────────────────────────────────────────────────────
with open(DATA, "r", encoding="utf-8") as fh:
    raw = json.load(fh)

items = raw["directory_items"]

# ── 2. Flatten to DataFrame ───────────────────────────────────────────────────
records = []
for item in items:
    u = item.get("user", {})
    records.append({
        "user_id":            item.get("id"),
        "username":           u.get("username", ""),
        "name":               u.get("name", ""),
        "title":              u.get("title"),
        "primary_group":      u.get("primary_group_name"),
        "flair_name":         u.get("flair_name"),
        "trust_level":        u.get("trust_level", 0),
        "solutions":          item.get("solutions", 0),
        "gamification_score": item.get("gamification_score", 0),
        "likes_received":     item.get("likes_received", 0),
        "likes_given":        item.get("likes_given", 0),
        "topic_count":        item.get("topic_count", 0),
        "post_count":         item.get("post_count", 0),
        "topics_entered":     item.get("topics_entered", 0),
        "posts_read":         item.get("posts_read", 0),
        "days_visited":       item.get("days_visited", 0),
        "time_read":          item.get("time_read", 0),   # seconds
    })

df = pd.DataFrame(records)

# ── 3. Clean / Derive ─────────────────────────────────────────────────────────
num_cols = ["solutions","gamification_score","likes_received","likes_given",
            "topic_count","post_count","topics_entered","posts_read",
            "days_visited","time_read"]
df[num_cols] = df[num_cols].fillna(0).astype(int)

df["time_read_hrs"] = (df["time_read"] / 3600).round(2)
df["total_content"] = df["post_count"] + df["topic_count"]

# Composite engagement index (Z-score weighted)
for col in ["post_count", "likes_received", "days_visited", "solutions"]:
    mu, sd = df[col].mean(), df[col].std()
    df[f"z_{col}"] = (df[col] - mu) / (sd if sd > 0 else 1)
df["engagement_index"] = (
    df["z_post_count"]      * 0.30 +
    df["z_likes_received"]  * 0.30 +
    df["z_days_visited"]    * 0.25 +
    df["z_solutions"]       * 0.15
)

# Segment flags
df["is_lurker"]      = (df["total_content"] == 0) & (df["likes_given"] == 0)
df["is_contributor"] = df["total_content"] > 0

trust_map = {0: "New User (0)", 1: "Basic (1)", 2: "Member (2)",
             3: "Regular (3)", 4: "Leader (4)"}
df["trust_label"] = df["trust_level"].map(trust_map).fillna("Unknown")

threshold_95     = df["engagement_index"].quantile(0.95)
df["is_power_user"] = df["engagement_index"] >= threshold_95

N = len(df)

# ── 4. Summary Statistics ─────────────────────────────────────────────────────
community_stats = {
    "total_users":         N,
    "avg_posts":           round(df["post_count"].mean(), 2),
    "avg_time_read_hrs":   round(df["time_read_hrs"].mean(), 2),
    "avg_days_visited":    round(df["days_visited"].mean(), 2),
    "avg_likes_received":  round(df["likes_received"].mean(), 2),
    "avg_likes_given":     round(df["likes_given"].mean(), 2),
    "avg_posts_read":      round(df["posts_read"].mean(), 2),
    "total_posts_created": int(df["post_count"].sum()),
    "total_topics_created":int(df["topic_count"].sum()),
    "total_time_read_hrs": round(df["time_read_hrs"].sum(), 0),
    "total_likes_given":   int(df["likes_given"].sum()),
    "total_solutions":     int(df["solutions"].sum()),
}

trust_dist = df.groupby("trust_label").size().to_dict()

power_users = df[df["is_power_user"]].nlargest(25, "engagement_index")[
    ["username","name","title","trust_level","post_count",
     "likes_received","days_visited","solutions","engagement_index"]
].reset_index(drop=True)

lurker_count        = int(df["is_lurker"].sum())
contributor_count   = int(df["is_contributor"].sum())
silent_reader_count = int((~df["is_lurker"] & ~df["is_contributor"]).sum())

engagement_breakdown = {
    "Power Users":     int(df["is_power_user"].sum()),
    "Contributors":    contributor_count,
    "Silent Readers":  silent_reader_count,
    "Lurkers":         lurker_count,
}

corr_cols    = ["post_count","likes_received","likes_given",
                "days_visited","time_read_hrs","posts_read","solutions"]
corr_matrix  = df[corr_cols].corr().round(3)

top5_users = df.nlargest(5, "gamification_score")[
    ["username","name","gamification_score","post_count",
     "solutions","likes_received","days_visited","trust_level"]
]

# ── 5. Print Report ───────────────────────────────────────────────────────────
sep  = "─" * 65
sep2 = "=" * 65
print(sep2)
print("  IITM DISCOURSE FORUM — DATA ANALYSIS REPORT")
print(sep2)

print(f"\n{sep}\n  COMMUNITY OVERVIEW\n{sep}")
for k, v in community_stats.items():
    print(f"  {k:<30} {v:>12,}")

print(f"\n{sep}\n  TRUST-LEVEL DISTRIBUTION\n{sep}")
for label, cnt in sorted(trust_dist.items()):
    bar = "█" * int(cnt / N * 50)
    pct = cnt / N * 100
    print(f"  {label:<22} {cnt:>4}  ({pct:5.1f}%)  {bar}")

print(f"\n{sep}\n  ENGAGEMENT BREAKDOWN\n{sep}")
for seg, cnt in engagement_breakdown.items():
    pct = cnt / N * 100
    print(f"  {seg:<22} {cnt:>4}  ({pct:5.1f}%)")

print(f"\n{sep}\n  TOP POWER USERS (top 5% by composite engagement index)\n{sep}")
print(power_users.to_string(index=False))

print(f"\n{sep}\n  TOP 5 BY GAMIFICATION SCORE\n{sep}")
print(top5_users.to_string(index=False))

print(f"\n{sep}\n  CORRELATION MATRIX\n{sep}")
print(corr_matrix.to_string())

# ── 6. Visualizations ────────────────────────────────────────────────────────
PALETTE  = ["#4361EE","#3A0CA3","#7209B7","#F72585","#4CC9F0","#4895EF","#560BAD"]
DARK_BG  = "#0d1117"
CARD_BG  = "#161b22"
TEXT_CLR = "#e6edf3"

plt.rcParams.update({
    "figure.facecolor": DARK_BG,
    "axes.facecolor":   CARD_BG,
    "axes.edgecolor":   "#30363d",
    "axes.labelcolor":  TEXT_CLR,
    "text.color":       TEXT_CLR,
    "xtick.color":      TEXT_CLR,
    "ytick.color":      TEXT_CLR,
    "grid.color":       "#21262d",
    "grid.linestyle":   "--",
    "grid.alpha":       0.6,
    "font.family":      "DejaVu Sans",
})

# 6a. Trust-level bar chart
fig, ax = plt.subplots(figsize=(10, 5))
labels  = [k for k, _ in sorted(trust_dist.items())]
counts  = [v for _, v in sorted(trust_dist.items())]
bars    = ax.bar(labels, counts, color=PALETTE[:len(labels)],
                 width=0.55, edgecolor=DARK_BG, linewidth=0.8)
for bar, cnt in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
            str(cnt), ha="center", va="bottom", fontsize=11, fontweight="bold")
ax.set_title("User Distribution by Trust Level", fontsize=14,
             fontweight="bold", pad=14)
ax.set_ylabel("Number of Users")
ax.grid(axis="y")
plt.tight_layout()
plt.savefig(OUT / "trust_level_dist.png", dpi=150, bbox_inches="tight")
plt.close()

# 6b. Engagement pie
fig, ax = plt.subplots(figsize=(7, 7))
seg_labels = list(engagement_breakdown.keys())
seg_vals   = list(engagement_breakdown.values())
wedges, _, autotexts = ax.pie(
    seg_vals, labels=None, autopct="%1.1f%%",
    colors=PALETTE[:len(seg_vals)], explode=[0.04]*len(seg_vals),
    startangle=140, pctdistance=0.78,
    wedgeprops=dict(linewidth=1.5, edgecolor=DARK_BG),
)
for at in autotexts:
    at.set_fontsize(10); at.set_color(TEXT_CLR)
patches = [mpatches.Patch(color=PALETTE[i],
           label=f"{seg_labels[i]}  ({seg_vals[i]})")
           for i in range(len(seg_labels))]
ax.legend(handles=patches, loc="lower center",
          bbox_to_anchor=(0.5, -0.08), ncol=2, frameon=False, fontsize=10)
ax.set_title("Community Engagement Segments", fontsize=14,
             fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig(OUT / "engagement_segments.png", dpi=150, bbox_inches="tight")
plt.close()

# 6c. Correlation heatmap
fig, ax = plt.subplots(figsize=(9, 7))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f",
            cmap="coolwarm", center=0, linewidths=0.5,
            linecolor=DARK_BG, ax=ax, annot_kws={"size": 9},
            cbar_kws={"shrink": 0.8})
ax.set_title("Correlation Heatmap of Engagement Metrics",
             fontsize=13, fontweight="bold", pad=14)
plt.tight_layout()
plt.savefig(OUT / "correlation_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()

# 6d. Post-count distribution
fig, ax = plt.subplots(figsize=(9, 5))
data_plot = df["post_count"][df["post_count"] > 0]
ax.hist(data_plot, bins=40, color=PALETTE[0], edgecolor=DARK_BG, alpha=0.85)
ax.set_xscale("log")
ax.set_title("Distribution of Post Counts (log scale, contributors only)",
             fontsize=13, fontweight="bold", pad=14)
ax.set_xlabel("Posts Created (log scale)")
ax.set_ylabel("Number of Users")
ax.grid(axis="y")
plt.tight_layout()
plt.savefig(OUT / "post_distribution.png", dpi=150, bbox_inches="tight")
plt.close()

# 6e. Time read vs likes received
fig, ax = plt.subplots(figsize=(9, 6))
normal = df[~df["is_power_user"]]
power  = df[df["is_power_user"]]
ax.scatter(normal["time_read_hrs"], normal["likes_received"],
           color=PALETTE[4], alpha=0.45, s=18, label="Regular Users")
ax.scatter(power["time_read_hrs"], power["likes_received"],
           color=PALETTE[3], alpha=0.9, s=60, label="Power Users", zorder=5)
ax.set_title("Time Spent Reading vs. Likes Received",
             fontsize=13, fontweight="bold", pad=14)
ax.set_xlabel("Time Read (hours)")
ax.set_ylabel("Likes Received")
ax.legend(frameon=False)
ax.grid()
plt.tight_layout()
plt.savefig(OUT / "time_vs_likes.png", dpi=150, bbox_inches="tight")
plt.close()

# 6f. Top 15 power users
top15 = df.nlargest(15, "engagement_index")
fig, ax = plt.subplots(figsize=(11, 6))
ax.barh(top15["username"][::-1], top15["engagement_index"][::-1],
        color=PALETTE[2], edgecolor=DARK_BG)
ax.set_title("Top 15 Power Users — Composite Engagement Index",
             fontsize=13, fontweight="bold", pad=14)
ax.set_xlabel("Engagement Index")
ax.grid(axis="x")
plt.tight_layout()
plt.savefig(OUT / "top15_power_users.png", dpi=150, bbox_inches="tight")
plt.close()

# 6g. Days visited vs post count
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(df["days_visited"], df["post_count"],
           c=df["trust_level"], cmap="plasma",
           alpha=0.55, s=20, edgecolors="none")
sm = plt.cm.ScalarMappable(cmap="plasma",
     norm=plt.Normalize(df["trust_level"].min(), df["trust_level"].max()))
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, shrink=0.8)
cbar.set_label("Trust Level", color=TEXT_CLR)
cbar.ax.yaxis.set_tick_params(color=TEXT_CLR)
ax.set_title("Forum Tenure (Days Visited) vs. Posts Created",
             fontsize=13, fontweight="bold", pad=14)
ax.set_xlabel("Days Visited")
ax.set_ylabel("Posts Created")
ax.grid()
plt.tight_layout()
plt.savefig(OUT / "days_vs_posts.png", dpi=150, bbox_inches="tight")
plt.close()

# ── 7. Export summary JSON ────────────────────────────────────────────────────
summary = {
    "community_stats":           community_stats,
    "trust_dist":                trust_dist,
    "engagement_breakdown":      engagement_breakdown,
    "power_users_list":          power_users.head(10).to_dict(orient="records"),
    "top5_users":                top5_users.to_dict(orient="records"),
    "corr_time_likes":           float(corr_matrix.loc["time_read_hrs","likes_received"]),
    "corr_days_posts":           float(corr_matrix.loc["days_visited","post_count"]),
    "corr_likes_given_received": float(corr_matrix.loc["likes_given","likes_received"]),
    "threshold_95":              round(float(threshold_95), 3),
    "lurker_pct":                round(lurker_count / N * 100, 1),
    "contributor_pct":           round(contributor_count / N * 100, 1),
    "power_user_pct":            round(int(df["is_power_user"].sum()) / N * 100, 1),
}

summary_path = OUT / "summary.json"
with open(summary_path, "w", encoding="utf-8") as fh:
    json.dump(summary, fh, indent=2)

print(f"\n{'='*65}")
print(f"  Charts saved  → {OUT}/")
print(f"  Summary JSON  → {summary_path}")
print(f"{'='*65}")
print("  Analysis complete.")
