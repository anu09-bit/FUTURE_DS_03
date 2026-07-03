"""
Generate a synthetic B2B marketing funnel dataset.
Funnel stages: Visitors -> Leads -> MQL -> SQL -> Opportunity -> Customer
Channels: Organic Search, Paid Search, Paid Social, Email, Referral, Direct, Content/Blog
6 months of monthly data.
"""
import numpy as np
import pandas as pd

np.random.seed(42)

months = pd.date_range("2026-01-01", periods=6, freq="MS").strftime("%Y-%m").tolist()

channels = {
    # channel: (base_visitors_per_month, visitor->lead, lead->mql, mql->sql, sql->opp, opp->customer, spend_per_month)
    "Organic Search": (18000, 0.038, 0.55, 0.42, 0.55, 0.32, 3500),
    "Paid Search":    (12000, 0.065, 0.48, 0.38, 0.50, 0.28, 22000),
    "Paid Social":    (20000, 0.022, 0.35, 0.25, 0.40, 0.18, 18000),
    "Email":          (9000,  0.085, 0.60, 0.50, 0.60, 0.35, 2000),
    "Referral":       (3000,  0.120, 0.70, 0.60, 0.68, 0.45, 500),
    "Direct":         (7000,  0.045, 0.50, 0.40, 0.52, 0.30, 0),
    "Content/Blog":   (10000, 0.030, 0.45, 0.30, 0.45, 0.22, 4000),
}

rows = []
for m_idx, month in enumerate(months):
    growth = 1 + m_idx * 0.03  # slight organic growth over time
    for ch, (base_v, v2l, l2m, m2s, s2o, o2c, spend) in channels.items():
        visitors = int(base_v * growth * np.random.normal(1, 0.06))
        leads = int(visitors * v2l * np.random.normal(1, 0.08))
        mqls = int(leads * l2m * np.random.normal(1, 0.08))
        sqls = int(mqls * m2s * np.random.normal(1, 0.08))
        opps = int(sqls * s2o * np.random.normal(1, 0.08))
        customers = int(opps * o2c * np.random.normal(1, 0.08))
        monthly_spend = spend * np.random.normal(1, 0.05)

        rows.append({
            "month": month,
            "channel": ch,
            "visitors": max(visitors, 0),
            "leads": max(leads, 0),
            "mqls": max(mqls, 0),
            "sqls": max(sqls, 0),
            "opportunities": max(opps, 0),
            "customers": max(customers, 0),
            "spend": round(max(monthly_spend, 0), 2),
        })

df = pd.DataFrame(rows)

# Derive avg deal value per channel (customers pay different amounts by channel/segment)
deal_value = {
    "Organic Search": 4200, "Paid Search": 3800, "Paid Social": 2600,
    "Email": 3200, "Referral": 5200, "Direct": 4600, "Content/Blog": 3600,
}
df["avg_deal_value"] = df["channel"].map(deal_value) * np.random.normal(1, 0.05, len(df))
df["revenue"] = (df["customers"] * df["avg_deal_value"]).round(2)
df["avg_deal_value"] = df["avg_deal_value"].round(2)

df.to_csv("/home/claude/funnel_analysis/funnel_data.csv", index=False)
print(df.shape)
print(df.head(10))
print("\nTotals:")
print(df[["visitors","leads","mqls","sqls","opportunities","customers","spend","revenue"]].sum())
