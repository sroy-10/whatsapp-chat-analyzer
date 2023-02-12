import re

import pandas as pd


def do_preprocess(data):
    # Extracting the data through RegEX
    pattern = "\d{1,2}\/\d{1,2}\/\d{2,4},\s\d{1,2}:\d{2}\s\S{2}\s-\s"
    messages = re.split(pattern, data)[1:]

    dates = [i.split("-")[0] for i in re.findall(pattern, data)]
    user = []
    for idx, msg in enumerate(messages):
        name = re.findall(".*:\s", msg)
        if len(name) == 0:
            user.append("Group Notifications")
        else:
            messages[idx] = messages[idx].replace(name[0], "")
            user.append(name[0].split(":")[0].strip())

    # Creating new dataframe to store the data
    df = pd.DataFrame(
        {"timestamp": dates, "user": user, "message": messages}
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date
    df["year"] = df["timestamp"].dt.year
    df["month"] = df["timestamp"].dt.month_name()
    df["month_num"] = df["timestamp"].dt.month
    df["day"] = df["timestamp"].dt.day
    df["hour"] = df["timestamp"].dt.hour
    df["minute"] = df["timestamp"].dt.minute
    df.head(3)
    return df
