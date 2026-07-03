import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

plt.rcParams.update({
    "figure.dpi": 150,
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#444444",
})

OUT = "/home/claude/funnel_analysis"
df = pd.read_csv(f"{OUT}/funnel_data.csv")

stages = ["visitors", "leads", "mqls", "sqls", "opportunities", "customers"]
stage_labels = ["Visitors", "Leads", "MQLs", "SQLs", "Opportunities", "Customers"]

COLORS = ["#2E5EAA", "#3E7CB1", "#4F9D9D", "#F2A541", "#E0703E", "#C63D4F"]

# ---------------------------------------------------------------
# 1. OVERALL FUNNEL TOTALS + STAGE-TO-STAGE CONVERSION
# ---------------------------------------------------------------
totals = df[stages].sum()
overall_conv = [100.0]
for i in range(1, len(stages)):
    overall_conv.append(round(totals[stages[i]] / totals[stages[i-1]] * 100, 1))

stage_to_stage = [round(totals[stages[i]] / totals[stages[i-1]] * 100, 1) for i in range(1, len(stages))]
biggest_drop_idx = int(np.argmin(stage_to_stage))
biggest_drop_pair = (stage_labels[biggest_drop_idx], stage_labels[biggest_drop_idx+1])
biggest_drop_rate = stage_to_stage[biggest_drop_idx]

print("=== OVERALL FUNNEL ===")
for lbl, val, pct in zip(stage_labels, totals[stages], overall_conv):
    print(f"{lbl:15s} {int(val):>8,}   {pct:>5.1f}% of visitors")
print(f"\nStage-to-stage conversion rates: {dict(zip([f'{stage_labels[i]}->{stage_labels[i+1]}' for i in range(5)], stage_to_stage))}")
print(f"Biggest drop-off: {biggest_drop_pair[0]} -> {biggest_drop_pair[1]} at only {biggest_drop_rate}% conversion")

overall_lead_to_customer = round(totals["customers"] / totals["leads"] * 100, 2)
print(f"\nOverall Lead-to-Customer conversion: {overall_lead_to_customer}%")

# --- Chart 1: Funnel (horizontal bar funnel) ---
fig, ax = plt.subplots(figsize=(9, 5.5))
y = np.arange(len(stages))[::-1]
vals = totals[stages].values
max_val = vals[0]
for i, (v, lbl, c) in enumerate(zip(vals, stage_labels, COLORS)):
    width = v / max_val
    left = (1 - width) / 2
    ax.barh(y[i], width, left=left, height=0.65, color=c, edgecolor="white")
    ax.text(0.5, y[i], f"{lbl}\n{int(v):,}", ha="center", va="center",
             color="white", fontweight="bold", fontsize=10)
    if i > 0:
        pct = stage_to_stage[i-1]
        ax.text(1.02, y[i]+0.5, f"{pct}%", ha="left", va="center", fontsize=9, color="#333")
ax.set_xlim(0, 1.15)
ax.set_yticks([])
ax.set_xticks([])
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_title("Marketing Funnel: Visitor to Customer (6-Month Total)", fontsize=13, fontweight="bold", pad=15)
plt.tight_layout()
plt.savefig(f"{OUT}/chart1_funnel_overview.png", bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------
# 2. CHANNEL PERFORMANCE (totals across 6 months)
# ---------------------------------------------------------------
ch = df.groupby("channel")[["visitors","leads","mqls","sqls","opportunities","customers","spend","revenue"]].sum().reset_index()
ch["visitor_to_lead"] = (ch["leads"] / ch["visitors"] * 100).round(2)
ch["lead_to_customer"] = (ch["customers"] / ch["leads"] * 100).round(2)
ch["cac"] = (ch["spend"] / ch["customers"]).round(0)
ch["roi_pct"] = ((ch["revenue"] - ch["spend"]) / ch["spend"].replace(0, np.nan) * 100).round(0)
ch = ch.sort_values("lead_to_customer", ascending=False)

print("\n=== CHANNEL PERFORMANCE (6-month totals) ===")
print(ch[["channel","visitors","leads","customers","lead_to_customer","cac","roi_pct"]].to_string(index=False))

best_channel = ch.iloc[0]
worst_channel = ch.sort_values("lead_to_customer").iloc[0]
most_efficient_cac = ch.dropna(subset=["cac"]).sort_values("cac").iloc[0]
least_efficient_cac = ch[ch["spend"] > 0].sort_values("cac", ascending=False).iloc[0]

# --- Chart 2: Lead-to-Customer conversion rate by channel ---
fig, ax = plt.subplots(figsize=(9, 5))
ch_sorted = ch.sort_values("lead_to_customer")
bars = ax.barh(ch_sorted["channel"], ch_sorted["lead_to_customer"], color="#2E5EAA")
for b, v in zip(bars, ch_sorted["lead_to_customer"]):
    ax.text(v + 0.1, b.get_y() + b.get_height()/2, f"{v}%", va="center", fontsize=10)
ax.set_xlabel("Lead-to-Customer Conversion Rate (%)")
ax.set_title("Lead-to-Customer Conversion Rate by Channel", fontsize=13, fontweight="bold")
ax.axvline(overall_lead_to_customer, color="#C63D4F", linestyle="--", linewidth=1.2)
ax.text(overall_lead_to_customer, len(ch_sorted)-0.3, f" Overall avg: {overall_lead_to_customer}%",
        color="#C63D4F", fontsize=9, va="bottom")
plt.tight_layout()
plt.savefig(f"{OUT}/chart2_channel_conversion.png", bbox_inches="tight")
plt.close()

# --- Chart 3: CAC vs ROI by channel (bubble = customers) ---
fig, ax = plt.subplots(figsize=(9, 5.5))
ch_spend = ch[ch["spend"] > 0]
sizes = ch_spend["customers"] * 8
sc = ax.scatter(ch_spend["cac"], ch_spend["roi_pct"], s=sizes, c=range(len(ch_spend)),
                 cmap="viridis", alpha=0.75, edgecolor="white", linewidth=1)
for _, r in ch_spend.iterrows():
    ax.annotate(r["channel"], (r["cac"], r["roi_pct"]), textcoords="offset points",
                xytext=(8, 5), fontsize=9)
ax.set_xlabel("Customer Acquisition Cost (CAC, $)")
ax.set_ylabel("ROI (%)")
ax.set_title("Channel Efficiency: CAC vs ROI (bubble size = # customers)", fontsize=13, fontweight="bold")
ax.axhline(0, color="grey", linewidth=0.8)
plt.tight_layout()
plt.savefig(f"{OUT}/chart3_cac_vs_roi.png", bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------
# 3. STAGE DROP-OFF HEATMAP BY CHANNEL
# ---------------------------------------------------------------
conv_matrix = pd.DataFrame(index=ch["channel"])
stage_pairs = [("visitors","leads"),("leads","mqls"),("mqls","sqls"),("sqls","opportunities"),("opportunities","customers")]
pair_labels = ["Visitor→Lead","Lead→MQL","MQL→SQL","SQL→Opp","Opp→Customer"]
ch_full = df.groupby("channel")[stages].sum()
for (a,b), lbl in zip(stage_pairs, pair_labels):
    conv_matrix[lbl] = (ch_full[b] / ch_full[a] * 100).round(1)
conv_matrix = conv_matrix.loc[ch["channel"]]  # keep sort order

print("\n=== STAGE-TO-STAGE CONVERSION BY CHANNEL (%) ===")
print(conv_matrix.to_string())

fig, ax = plt.subplots(figsize=(8.5, 5.5))
im = ax.imshow(conv_matrix.values, cmap="RdYlGn", aspect="auto", vmin=0, vmax=70)
ax.set_xticks(range(len(pair_labels)))
ax.set_xticklabels(pair_labels, rotation=20, ha="right")
ax.set_yticks(range(len(conv_matrix.index)))
ax.set_yticklabels(conv_matrix.index)
for i in range(conv_matrix.shape[0]):
    for j in range(conv_matrix.shape[1]):
        val = conv_matrix.values[i, j]
        ax.text(j, i, f"{val}%", ha="center", va="center", fontsize=9,
                color="white" if val < 20 or val > 55 else "black")
ax.set_title("Stage-to-Stage Conversion Rate Heatmap by Channel", fontsize=13, fontweight="bold")
fig.colorbar(im, ax=ax, label="Conversion Rate (%)", shrink=0.8)
plt.tight_layout()
plt.savefig(f"{OUT}/chart4_dropoff_heatmap.png", bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------
# 4. MONTHLY TREND: Leads, Customers, Lead-to-Customer rate
# ---------------------------------------------------------------
monthly = df.groupby("month")[["leads","customers","spend","revenue"]].sum().reset_index()
monthly["lead_to_customer"] = (monthly["customers"] / monthly["leads"] * 100).round(2)
monthly["roas"] = (monthly["revenue"] / monthly["spend"]).round(2)

print("\n=== MONTHLY TREND ===")
print(monthly.to_string(index=False))

fig, ax1 = plt.subplots(figsize=(9.5, 5))
ax1.bar(monthly["month"], monthly["leads"], color="#3E7CB1", alpha=0.6, label="Leads", width=0.5)
ax1.bar(monthly["month"], monthly["customers"], color="#C63D4F", alpha=0.9, label="Customers", width=0.5)
ax1.set_ylabel("Count")
ax2 = ax1.twinx()
ax2.plot(monthly["month"], monthly["lead_to_customer"], color="#222222", marker="o", linewidth=2, label="Lead→Customer %")
ax2.set_ylabel("Lead-to-Customer Conversion (%)")
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1+lines2, labels1+labels2, loc="upper left", fontsize=9)
ax1.set_title("Monthly Leads, Customers & Conversion Rate Trend", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUT}/chart5_monthly_trend.png", bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------
# Save summary tables for the report
# ---------------------------------------------------------------
ch.round(2).to_csv(f"{OUT}/channel_performance_summary.csv", index=False)
conv_matrix.to_csv(f"{OUT}/dropoff_by_channel.csv")
monthly.round(2).to_csv(f"{OUT}/monthly_trend.csv", index=False)

summary = {
    "overall_lead_to_customer": overall_lead_to_customer,
    "biggest_drop_pair": biggest_drop_pair,
    "biggest_drop_rate": biggest_drop_rate,
    "best_channel": best_channel["channel"],
    "best_channel_rate": best_channel["lead_to_customer"],
    "worst_channel": worst_channel["channel"],
    "worst_channel_rate": worst_channel["lead_to_customer"],
    "most_efficient_cac_channel": most_efficient_cac["channel"],
    "most_efficient_cac": most_efficient_cac["cac"],
    "least_efficient_cac_channel": least_efficient_cac["channel"],
    "least_efficient_cac": least_efficient_cac["cac"],
    "total_spend": totals_spend if (totals_spend := df["spend"].sum()) else 0,
    "total_revenue": df["revenue"].sum(),
}
import json
with open(f"{OUT}/summary.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)

print("\n=== KEY SUMMARY ===")
for k, v in summary.items():
    print(f"{k}: {v}")

print("\nAll charts and CSVs saved to", OUT)
