import streamlit as st
import preprocessor,helper
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import plotly.express as px

#from wordcloud import WordCloud

# from helper import most_common_words

st.sidebar.title("Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
        df = preprocessor.preprocess(data)

        #Fetch unique users
        user_list = df['users'].unique().tolist()
        if 'group_notification' in user_list:
            user_list.remove('group_notification')
        user_list.sort()
        user_list.insert(0,'Overall')

        selected_user = st.sidebar.selectbox("Show Analysis wrt", user_list)

        # ----------- DATE FILTER ------------
        st.sidebar.subheader("Filter by Date Range")

        start_date = st.sidebar.date_input("From Date", df['only_date'].min())
        end_date = st.sidebar.date_input("To Date", df['only_date'].max())

        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Apply filtering
        df = df[(df['only_date'] >= start_date) & (df['only_date'] <= end_date)]
        # -------------------------------------

        if st.sidebar.button("Show Analysis"):

            #Stats Area
            num_messages, words, num_media, links = helper.fetch_stats(selected_user,df)
            st.title("Top Statistics")
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1], gap = "large")

            with col1:
                st.header("Total Message")
                st.title(num_messages)
            with col2:
                st.header("Total Word")
                st.title(words)
            with col3:
                st.header("Media Shared")
                st.title(num_media)
            with col4:
                st.header("Link Shared")
                st.title(links)

            #Monthly timeline
            st.title("Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user, df)

            fig, ax = plt.subplots()
            ax.plot(
                timeline['time'],
                timeline['messages'],
                color = 'red'
            )

            plt.xticks(rotation = 90)
            st.pyplot(fig)

            #Daily Timeline
            st.title("Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_user, df)

            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['messages'], color='black')

            # ax.xaxis.set_major_locator(mdates.DayLocator(interval = 20))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y'))

            plt.xticks(rotation = 90)
            st.pyplot(fig)

            #Activity Map
            st.title('Activity Map')

            col1, col2 = st.columns([1,1], gap = "large")

            with col1:
                st.header("Most busy day")
                busy_day = helper.week_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values)
                plt.xticks(rotation = 90)
                st.pyplot(fig)

            with col2:
                st.header("Most busy month")
                busy_month = helper.month_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values, color = 'orange')
                plt.xticks(rotation = 90)
                st.pyplot(fig)

            st.title("Weekly Activity Map")
            my_heatmap = helper.activity_heatmap(selected_user, df)
            fig, ax = plt.subplots(figsize = (10,6))
            sns.heatmap(my_heatmap, ax = ax)
            st.pyplot(fig)


            #finding the busiest users in the group(Group Level)
            if selected_user == 'Overall':
                st.title("Most Busy Users")
                x, new_df = helper.most_busy_user(df)
                fig, ax = plt.subplots()

                col1, col2 = st.columns([1,1], gap = "large")

                with col1:
                    ax.bar(x.index, x.values)
                    plt.xticks(rotation = 90)
                    st.pyplot(fig)
                with col2:
                    st.dataframe(new_df)

            #WordCloud
            st.title("Wordcloud")
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            ax.axis("off")
            st.pyplot(fig)

            #Most Common Words
            st.title("Most Common words")
            most_common_df = helper.most_common_words(selected_user, df)
            fig, ax = plt.subplots()
            ax.barh(most_common_df[0],most_common_df[1], color = 'green')
            # plt.xticks(rotation = "vertical")
            st.pyplot(fig)
            # st.dataframe(most_common_df)

            #Emoji Analysis
            emoji_df = helper.emoji_analysis(selected_user, df)
            st.title("Emoji Analysis")

            col1, col2 = st.columns([1,1], gap = "large")

            with col1:
                st.dataframe(emoji_df)

            with col2:
                fig = px.pie(
                    emoji_df.head(),
                    values='count',
                    names='emoji'
                )

                fig.update_traces(
                    textposition='auto',
                    textinfo='percent+label',
                    insidetextfont=dict(
                        size=22,
                        color = 'white'
                    ),
                    outsidetextfont=dict(
                        size=28
                    ),
                    hoverinfo = 'skip',
                    pull=[0.02] * len(emoji_df.head())
                )

                fig.update_layout(
                    showlegend=False,
                    uniformtext_minsize=16,
                    uniformtext_mode='hide'
                )

                st.plotly_chart(fig, use_container_width=True)
