from typing import Dict, Any, List

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


async def businessInsight(
    input_csv_path: str = "data/output.csv",
    top_n: int = 5,
) -> Dict[str, Any]:
    """
    Step 4: Business Insights & Plots 

    Reads the enriched, exploded CSV (with columns including `general_topic_l1`, `topic_discussed`,
    `product`, `channel`, `Date`, `state`, `customer_sentiment`) and produces four plots:
      1) Top N Customer Pain Points (bar)
      2) Pain Points by Product (heatmap of counts)
      3) Theme Severity (100% stacked bar by sentiment share)
      4) Theme Trends Over Time (line chart by month for top N themes)

    Saves PNGs to the data/ directory and returns their file paths.
    """
    df = pd.read_csv(input_csv_path)

    # 1) Top N Customer Pain Points
    top_counts = (
        df.groupby("general_topic_l1").size().sort_values(ascending=False).head(top_n)
    )
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    top_counts.iloc[::-1].plot(kind="barh", ax=ax1, color="#4C78A8")
    ax1.set_title(f"Top {top_n} Customer Pain Points")
    ax1.set_xlabel("Count")
    ax1.set_ylabel("Theme (general_topic_l1)")
    fig1.tight_layout()
    p1 = "data/plot_top_pain_points.png"
    fig1.savefig(p1, dpi=150)
    plt.close(fig1)

    # 2) Pain Points by Product (heatmap)
    cross = df.pivot_table(index="general_topic_l1", columns="product", values="topic_discussed", aggfunc="count", fill_value=0)
    fig2, ax2 = plt.subplots(figsize=(max(8, 0.6 * (cross.shape[1] + 4)), max(6, 0.4 * (cross.shape[0] + 4))))
    im = ax2.imshow(cross.values, aspect="auto", cmap="Blues")
    ax2.set_yticks(range(cross.shape[0]))
    ax2.set_yticklabels(cross.index.tolist())
    ax2.set_xticks(range(cross.shape[1]))
    ax2.set_xticklabels(cross.columns.tolist(), rotation=45, ha="right")
    ax2.set_title("Pain Points by Product (Counts)")
    fig2.colorbar(im, ax=ax2, label="Count")
    fig2.tight_layout()
    p2 = "data/heatmap_pain_points_by_product.png"
    fig2.savefig(p2, dpi=150)
    plt.close(fig2)

    # 3) Theme Severity (Negative Share) - 100% stacked bar by sentiment
    sentiment_counts = df.groupby(["general_topic_l1", "customer_sentiment"]).size().unstack(fill_value=0)
    sentiment_counts = sentiment_counts.reindex(columns=["Negative", "Neutral", "Positive"], fill_value=0)
    sentiment_props = sentiment_counts.div(sentiment_counts.sum(axis=1), axis=0).fillna(0)
    # limit to top N themes by volume for readability
    top_themes = top_counts.index.tolist()
    sentiment_props_top = sentiment_props.loc[[t for t in sentiment_props.index if t in top_themes]]
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    bottom = np.zeros(len(sentiment_props_top))
    colors = {"Negative": "#E45756", "Neutral": "#F2CF5B", "Positive": "#72B7B2"}
    for sent in ["Negative", "Neutral", "Positive"]:
        vals = sentiment_props_top[sent].values
        ax3.bar(sentiment_props_top.index, vals, bottom=bottom, label=sent, color=colors[sent])
        bottom += vals
    ax3.set_title("Theme Severity by Sentiment (Share)")
    ax3.set_ylabel("Share of Mentions")
    ax3.set_xlabel("Theme (Top)")
    ax3.legend(title="Sentiment")
    plt.setp(ax3.get_xticklabels(), rotation=30, ha="right")
    fig3.tight_layout()
    p3 = "data/theme_severity_stacked.png"
    fig3.savefig(p3, dpi=150)
    plt.close(fig3)

    # 4) Theme Trends Over Time (monthly counts by theme for top N)
    dft = df.copy()
    dft["Date"] = pd.to_datetime(dft["Date"], errors="coerce")
    dft = dft.dropna(subset=["Date"])  # minimal; no extra handling
    dft["month"] = dft["Date"].dt.to_period("M").dt.to_timestamp()
    dft_top = dft[dft["general_topic_l1"].isin(top_themes)]
    trend = dft_top.groupby(["month", "general_topic_l1"]).size().reset_index(name="count")
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    for theme in top_themes:
        sub = trend[trend["general_topic_l1"] == theme]
        ax4.plot(sub["month"], sub["count"], marker="o", label=theme)
    ax4.set_title("Theme Trends Over Time (Top Themes)")
    ax4.set_ylabel("Mentions per Month")
    ax4.set_xlabel("Month")
    ax4.legend(title="Theme", bbox_to_anchor=(1.04, 1), loc="upper left")
    fig4.tight_layout()
    p4 = "data/theme_trends_over_time.png"
    fig4.savefig(p4, dpi=150)
    plt.close(fig4)

    return {
        "status": "success",
        "plots": [p1, p2, p3, p4],
        "top_n": int(top_n),
        "input_path": input_csv_path,
    }
