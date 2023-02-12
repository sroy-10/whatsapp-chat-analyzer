from io import StringIO

import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

import helper
from preprocesser import do_preprocess

st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="📬",
    layout="wide",
)
st.sidebar.title("WhatsApp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    string_data = StringIO(
        uploaded_file.getvalue().decode("utf-8")
    ).read()

    df = do_preprocess(string_data)
    # st.dataframe(df, use_container_width=True)

    # Fetch unique users
    user_list = df["user"].unique().tolist()
    try:
        user_list.remove("Group Notifications")
    except:
        pass
    user_list.sort()
    user_list.insert(0, "Overall")

    # Display the list of users in Dropdown
    selected_user = st.sidebar.selectbox(
        "Show analysis w.r.t", user_list
    )

    if st.sidebar.button("Show Analysis"):
        # Stats: Total Messages, Total Words, Media Shared, Links Shared
        st.title("Top Statistics")
        stats = helper.get_stats(df, selected_user)
        col = st.columns(len(stats))
        for idx, d in enumerate(stats.items()):
            with col[idx]:
                st.title(d[1])
                st.subheader(d[0])

        # Monthly Timeline
        st.title("Monthly Timeline")
        monthly_timeline = helper.monthly_timeline(df, selected_user)
        fig, ax = plt.subplots()
        ax.plot(
            monthly_timeline["time"],
            monthly_timeline["message"],
            color="green",
        )
        plt.xticks(rotation="vertical")
        st.pyplot(fig)

        # Daily Timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(df, selected_user)
        fig, ax = plt.subplots()
        ax.plot(
            daily_timeline["date"],
            daily_timeline["message"],
            color="red",
        )
        plt.xticks(rotation="vertical")
        st.pyplot(fig)

        # Finding the busiest users in the group(Group Level)
        # This will work only in case of 'Overall'
        if selected_user == "Overall":
            st.title("Most Busy User")
            busy_user_list, df_percent = helper.get_most_busy_users(df)
            col2 = st.columns(2)
            with col2[0]:
                # Graph Plot
                fig, ax = plt.subplots()
                ax.bar(
                    busy_user_list.index,
                    busy_user_list.values,
                    color="red",
                )
                plt.xticks(rotation="vertical")
                st.pyplot(fig)

            with col2[1]:
                st.dataframe(df_percent, use_container_width=True)

        col3 = st.columns(2)
        # Word Cloud
        with col3[0]:
            df_wc = helper.create_wordcloud(df, selected_user)
            st.title("Word Cloud")
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)

        # Most Common Words
        with col3[1]:
            st.title("Most Common Words")
            most_common_words = helper.get_most_type_words(
                df, selected_user
            )
            fig, ax = plt.subplots()
            ax.barh(
                most_common_words["words"],
                most_common_words["frequency"],
            )
            plt.xticks(rotation="vertical")
            st.pyplot(fig)

        # Emoji Analysis
        st.title("Emoji Analysis")
        emoji_df = helper.emoji_helper(df)
        col4 = st.columns(2)
        with col4[0]:
            st.dataframe(emoji_df)
        with col4[1]:
            fig, ax = plt.subplots()
            # create pie chart
            ax.pie(
                x=emoji_df["frequency"][:5],
                labels=emoji_df["emoji"][:5],
                colors=sns.color_palette("pastel"),
                autopct="%.0f%%",
            )
            st.pyplot(fig)
