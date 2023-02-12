from collections import Counter

import emoji
import pandas as pd
from urlextract import URLExtract
from wordcloud import WordCloud


def filter_df(
    df, selected_user="", flg_rmv_grp_notif="", flg_rmv_media=""
):
    if selected_user != "" and selected_user != "Overall":
        df = df[df["user"] == selected_user]

    if flg_rmv_grp_notif == "X":
        df = df[df["user"] != "Group Notifications"]

    if flg_rmv_media == "X":
        df = df[df["message"] != "<Media omitted>\n"]
    return df


def get_stats(df, selected_user):
    df = filter_df(df, selected_user=selected_user)
    result = dict()

    # Get the total number of messages
    result["Total Messages"] = "{:,.0f}".format(df.shape[0])

    # Get the total number of words
    # Filtering out the Group Notifications and the media messages
    words = []
    word_df = filter_df(df, flg_rmv_grp_notif="X", flg_rmv_media="X")

    for msg in word_df["message"]:
        words.extend(msg.split())
    result["Total Words"] = "{:,.0f}".format(len(words))

    # Get the total Media Messages
    media_df = df[df["message"].str.find("<Media omitted>") == 0]
    result["Media Shared"] = "{:,.0f}".format(media_df.shape[0])

    # Return the result in dictionary format
    links = []
    for msg in df["message"]:
        links.extend(URLExtract().find_urls(msg))
    result["Links Shared"] = "{:,.0f}".format(len(links))

    return result


def get_most_busy_users(df, top=5):
    busy_user_list = df["user"].value_counts().head(top)
    df_percent = (
        round(((df["user"].value_counts() / df.shape[0]) * 100), 2)
        .reset_index()
        .rename(columns={"index": "name", "user": "percent"})
    )

    return busy_user_list, df_percent


def remove_stop_words(message):
    word_list = []
    stop_words = open("stop_hinglish.txt", "r").read()
    for word in message.lower().split():
        if word not in stop_words:
            word_list.append(word)
    return " ".join(word_list)


def create_wordcloud(df, selected_user):
    df = filter_df(
        df,
        selected_user=selected_user,
        flg_rmv_grp_notif="X",
        flg_rmv_media="X",
    )
    df["message"] = df["message"].apply(remove_stop_words)
    wc = WordCloud(
        width=500,
        height=500,
        min_font_size=10,
        background_color="white",
        colormap="Paired",
    )
    # df_wc = wc.generate(df["message"].str.cat(sep=" "))
    df_wc = wc.generate(" ".join(df["message"]))
    return df_wc


def get_most_type_words(df, selected_user):
    df = filter_df(
        df,
        selected_user=selected_user,
        flg_rmv_grp_notif="X",
        flg_rmv_media="X",
    )
    df["message"] = df["message"].apply(remove_stop_words)

    word_list = []
    for msg in df["message"]:
        word_list.extend(msg.split())

    res_df = pd.DataFrame(Counter(word_list).most_common(20)).rename(
        columns={0: "words", 1: "frequency"}
    )
    return res_df


def emoji_helper(df, top=10):
    emoji_list = []
    for msg in df["message"]:
        emoji_list.extend([i for i in msg if i in emoji.EMOJI_DATA])

    return pd.DataFrame(Counter(emoji_list).most_common(top)).rename(
        columns={0: "emoji", 1: "frequency"}
    )


def monthly_timeline(df, selected_user):
    df = filter_df(df, selected_user=selected_user)    
    timeline = (
        df.groupby(["year", "month_num", "month"]).count()["message"]
    ).reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(
            timeline["month"][i] + "-" + str(timeline["year"][i])
        )
    timeline["time"] = time
    return timeline

def daily_timeline(df, selected_user):
    df = filter_df(df, selected_user=selected_user)    
    daily_timeline = pd.DataFrame(df.groupby('date').count()['message'].reset_index())
    return daily_timeline
