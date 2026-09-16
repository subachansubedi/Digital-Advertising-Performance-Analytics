"""Python analysis for the Digital Advertising Performance project.

The code uses pandas, matplotlib, and seaborn to analyze the provided CSV files and answer 15 questions about the advertising data. The results are saved as charts in the "outputs" folder and a CSV file with the answers.
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


# Change these two folders when running the script on another computer.
DATA_FOLDER = "/Raw Data File"
OUTPUT_FOLDER = "/output"


def save_chart(file_name):
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_FOLDER, file_name), dpi=150)
    plt.close()


def add_answer(answers, question, topic, answer):
    answers.append([question, topic, answer])


def main():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    sns.set_style("whitegrid")

    events = pd.read_csv(os.path.join(DATA_FOLDER, "ad_events.csv"))
    ads = pd.read_csv(os.path.join(DATA_FOLDER, "ads.csv"))
    campaigns = pd.read_csv(os.path.join(DATA_FOLDER, "campaigns.csv"))
    users = pd.read_csv(os.path.join(DATA_FOLDER, "users.csv"))

    events["timestamp"] = pd.to_datetime(events["timestamp"])
    events["date"] = events["timestamp"].dt.date
    events["month"] = events["timestamp"].dt.to_period("M").astype(str)
    events = events.merge(ads, on="ad_id")
    events = events.merge(users, on="user_id", how="left")
    ads_with_campaigns = ads.merge(campaigns, on="campaign_id")

    answers = []

    # Q01: What is in the data?
    event_counts = events["event_type"].value_counts()
    add_answer(
        answers, "Q01", "Data overview",
        f"{len(events):,} events across {events['ad_id'].nunique():,} ads and "
        f"{len(users):,} user records",
    )
    plt.figure(figsize=(8, 4.5))
    sns.barplot(x=event_counts.index, y=event_counts.values, color="#457b9d")
    plt.title("Q01 - Event types in the dataset")
    plt.ylabel("Number of events")
    plt.xticks(rotation=25)
    save_chart("q01_event_mix.png")

    # Q02: What does the advertising funnel look like?
    funnel_order = ["Impression", "Click", "Like", "Comment", "Share", "Purchase"]
    funnel = event_counts.reindex(funnel_order).fillna(0)
    add_answer(
        answers, "Q02", "Advertising funnel",
        f"{int(funnel['Click']):,} clicks and {int(funnel['Purchase']):,} purchases from "
        f"{int(funnel['Impression']):,} impressions",
    )
    plt.figure(figsize=(8, 4.5))
    sns.barplot(x=funnel.index, y=funnel.values, color="#1877f2")
    plt.title("Q02 - From impressions to purchases")
    plt.ylabel("Events")
    save_chart("q02_funnel.png")

    # Q03-Q05: Platform comparison.
    platform_events = events.groupby(["ad_platform", "event_type"]).size().unstack(fill_value=0)
    platform_summary = platform_events.copy()
    platform_summary["ctr"] = platform_summary["Click"] / platform_summary["Impression"] * 100
    platform_summary["engagement_rate"] = (
        platform_summary[["Like", "Comment", "Share"]].sum(axis=1)
        / platform_summary["Impression"] * 100
    )
    platform_summary["purchase_rate"] = platform_summary["Purchase"] / platform_summary["Click"] * 100
    best_ctr = platform_summary["ctr"].idxmax()
    best_purchase = platform_summary["purchase_rate"].idxmax()
    add_answer(answers, "Q03", "Platform reach", f"{platform_events['Impression'].idxmax()} generated more impressions")
    add_answer(answers, "Q04", "Platform click-through rate", f"{best_ctr} had the higher CTR at {platform_summary.loc[best_ctr, 'ctr']:.2f}%")
    add_answer(answers, "Q05", "Platform purchase rate", f"{best_purchase} had the higher click-to-purchase rate at {platform_summary.loc[best_purchase, 'purchase_rate']:.2f}%")
    platform_chart = platform_summary[["ctr", "engagement_rate", "purchase_rate"]].reset_index()
    platform_chart = platform_chart.melt(id_vars="ad_platform", var_name="metric", value_name="percent")
    plt.figure(figsize=(9, 4.5))
    sns.barplot(data=platform_chart, x="metric", y="percent", hue="ad_platform")
    plt.title("Q03-Q05 - Facebook and Instagram comparison")
    plt.ylabel("Rate (%)")
    save_chart("q03_q05_platform_comparison.png")

    # Q06-Q08: Ad format comparison.
    format_events = events.groupby(["ad_type", "event_type"]).size().unstack(fill_value=0)
    format_events["ctr"] = format_events["Click"] / format_events["Impression"] * 100
    format_events["purchase_rate"] = format_events["Purchase"] / format_events["Click"] * 100
    format_events["engagement_rate"] = (
        format_events[["Like", "Comment", "Share"]].sum(axis=1)
        / format_events["Impression"] * 100
    )
    top_format_impressions = format_events["Impression"].idxmax()
    top_format_ctr = format_events["ctr"].idxmax()
    top_format_purchase = format_events["purchase_rate"].idxmax()
    add_answer(answers, "Q06", "Ad format reach", f"{top_format_impressions} received the most impressions")
    add_answer(answers, "Q07", "Ad format CTR", f"{top_format_ctr} had the highest CTR at {format_events.loc[top_format_ctr, 'ctr']:.2f}%")
    add_answer(answers, "Q08", "Ad format purchase rate", f"{top_format_purchase} had the highest click-to-purchase rate at {format_events.loc[top_format_purchase, 'purchase_rate']:.2f}%")
    format_chart = format_events[["ctr", "engagement_rate", "purchase_rate"]].reset_index()
    format_chart = format_chart.melt(id_vars="ad_type", var_name="metric", value_name="percent")
    plt.figure(figsize=(10, 5))
    sns.barplot(data=format_chart, x="ad_type", y="percent", hue="metric")
    plt.title("Q06-Q08 - Performance by ad format")
    plt.ylabel("Rate (%)")
    save_chart("q06_q08_ad_formats.png")

    # Q09-Q10: Audience gender and age group.
    gender = events.groupby(["target_gender", "event_type"]).size().unstack(fill_value=0)
    gender["ctr"] = gender["Click"] / gender["Impression"] * 100
    gender["purchase_rate"] = gender["Purchase"] / gender["Click"] * 100
    age = events.groupby(["target_age_group", "event_type"]).size().unstack(fill_value=0)
    age["ctr"] = age["Click"] / age["Impression"] * 100
    age["purchase_rate"] = age["Purchase"] / age["Click"] * 100
    best_gender = gender["purchase_rate"].idxmax()
    best_age = age["purchase_rate"].idxmax()
    add_answer(answers, "Q09", "Target gender", f"{best_gender} targeting had the higher click-to-purchase rate at {gender.loc[best_gender, 'purchase_rate']:.2f}%")
    add_answer(answers, "Q10", "Target age group", f"{best_age} had the highest click-to-purchase rate at {age.loc[best_age, 'purchase_rate']:.2f}%")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    sns.barplot(data=gender.reset_index(), x="target_gender", y="purchase_rate", ax=axes[0], color="#e76f51")
    axes[0].set_title("Q09 - Purchase rate by target gender")
    axes[0].set_ylabel("Purchase rate (%)")
    sns.barplot(data=age.reset_index(), x="target_age_group", y="purchase_rate", ax=axes[1], color="#2a9d8f")
    axes[1].set_title("Q10 - Purchase rate by target age")
    axes[1].set_ylabel("Purchase rate (%)")
    axes[1].tick_params(axis="x", rotation=35)
    save_chart("q09_q10_audience.png")

    # Q11-Q12: Timing.
    time_summary = events.groupby(["time_of_day", "event_type"]).size().unstack(fill_value=0)
    time_summary["ctr"] = time_summary["Click"] / time_summary["Impression"] * 100
    time_summary["purchase_rate"] = time_summary["Purchase"] / time_summary["Click"] * 100
    day_summary = events.groupby(["day_of_week", "event_type"]).size().unstack(fill_value=0)
    day_summary["ctr"] = day_summary["Click"] / day_summary["Impression"] * 100
    day_summary["purchase_rate"] = day_summary["Purchase"] / day_summary["Click"] * 100
    best_time = time_summary["purchase_rate"].idxmax()
    best_day = day_summary["purchase_rate"].idxmax()
    add_answer(answers, "Q11", "Time of day", f"{best_time} had the highest click-to-purchase rate at {time_summary.loc[best_time, 'purchase_rate']:.2f}%")
    add_answer(answers, "Q12", "Day of week", f"{best_day} had the highest click-to-purchase rate at {day_summary.loc[best_day, 'purchase_rate']:.2f}%")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    sns.barplot(data=time_summary.reset_index(), x="time_of_day", y="purchase_rate", ax=axes[0], color="#457b9d")
    axes[0].set_title("Q11 - Purchase rate by time of day")
    axes[0].set_ylabel("Purchase rate (%)")
    sns.barplot(data=day_summary.reset_index(), x="day_of_week", y="purchase_rate", ax=axes[1], color="#f4a261")
    axes[1].set_title("Q12 - Purchase rate by day")
    axes[1].set_ylabel("Purchase rate (%)")
    axes[1].tick_params(axis="x", rotation=35)
    save_chart("q11_q12_timing.png")

    # Q13: Geography.
    country = events.groupby(["country", "event_type"]).size().unstack(fill_value=0)
    country["purchase_rate"] = country["Purchase"] / country["Click"] * 100
    country = country[country["Click"] >= 100].sort_values("purchase_rate", ascending=False)
    best_country = country.iloc[0]
    add_answer(answers, "Q13", "Country performance", f"{country.index[0]} had the highest purchase rate among countries with at least 100 clicks: {best_country['purchase_rate']:.2f}%")
    plt.figure(figsize=(9, 5))
    sns.barplot(data=country.head(10).reset_index(), y="country", x="purchase_rate", color="#6a4c93")
    plt.title("Q13 - Top country purchase rates")
    plt.xlabel("Purchase rate (%)")
    save_chart("q13_country_performance.png")

    # Q14: Campaign context.
    campaign_summary = ads_with_campaigns.groupby("campaign_id", as_index=False).agg(
        campaign_name=("name", "first"), budget=("total_budget", "first"), duration=("duration_days", "first")
    )
    campaign_events = events.groupby("campaign_id").size().reset_index(name="events")
    campaign_summary = campaign_summary.merge(campaign_events, on="campaign_id")
    campaign_summary["events_per_budget_dollar"] = campaign_summary["events"] / campaign_summary["budget"]
    efficient_campaign = campaign_summary.loc[campaign_summary["events_per_budget_dollar"].idxmax()]
    add_answer(answers, "Q14", "Campaign activity", f"{efficient_campaign['campaign_name']} generated the most events per budget dollar in this dataset")
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=campaign_summary, x="budget", y="events", size="duration", hue="duration", palette="viridis", legend=False, sizes=(40, 300))
    plt.title("Q14 - Campaign budget and recorded event volume")
    plt.xlabel("Campaign budget ($)")
    plt.ylabel("Recorded events")
    save_chart("q14_campaign_budget.png")

    # Q15: Weekly trend.
    weekly = events.set_index("timestamp").resample("W")["event_id"].count().reset_index()
    peak_week = weekly.loc[weekly["event_id"].idxmax()]
    add_answer(answers, "Q15", "Weekly activity", f"The busiest week began {peak_week['timestamp'].strftime('%Y-%m-%d')} with {int(peak_week['event_id']):,} events")
    plt.figure(figsize=(10, 4))
    sns.lineplot(data=weekly, x="timestamp", y="event_id", marker="o", color="#1877f2")
    plt.title("Q15 - Weekly advertising activity")
    plt.xlabel("Week")
    plt.ylabel("Events")
    save_chart("q15_weekly_activity.png")

    answer_table = pd.DataFrame(answers, columns=["question", "topic", "answer"])
    answer_table.to_csv(os.path.join(OUTPUT_FOLDER, "15_question_results.csv"), index=False)
    print(answer_table.to_string(index=False))


if __name__ == "__main__":
    main()
