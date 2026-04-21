




import streamlit as st
import pandas as pd
import re
from googleapiclient.discovery import build
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import plotly.express as px

api_key ="AIzaSyDClBzan0LTf9rhO4tZpGiWBk-D5U0cmV8"


# ======================
# ⚙️ CONFIG
# ======================
st.set_page_config(page_title="YouTube Analyzer", layout="wide")

# ======================
# 🔴 HEADER
# ======================
st.markdown("""
<div style="display:flex;align-items:center;font-size:40px;font-weight:600;">
<div style="margin-right:12px;">
<svg width="55" height="38" viewBox="0 0 90 60">
  <rect width="90" height="60" rx="14" fill="#FF0000"/>
  <polygon points="35,20 65,30 35,40" fill="white"/>
</svg>
</div>
<span style="color:white;font-weight:700;">
YouTube Comment Analyzer
</span>
</div>
""", unsafe_allow_html=True)

# ======================
# 🎨 BACKGROUND
# ======================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(270deg, #1a0033, #6a00ff, #ff007f);
    background-size: 600% 600%;
    animation: gradientBG 12s ease infinite;
}
@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
</style>
""", unsafe_allow_html=True)

# ======================
# 🔎 INPUT
# ======================
url = st.text_input("🔗 Enter YouTube Video URL")
analyze = st.button("✨ Analyze")

# ======================
# 🔧 FUNCTIONS
# ======================
def get_video_id(url):
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    match = re.search(r"v=([^&]+)", url)
    return match.group(1) if match else None


def get_total_comments(video_id):
    youtube = build("youtube", "v3", developerKey=api_key)
    res = youtube.videos().list(part="statistics", id=video_id).execute()
    return int(res["items"][0]["statistics"].get("commentCount", 0))


def get_comments(video_id):
    youtube = build("youtube", "v3", developerKey=api_key)

    total_comments = get_total_comments(video_id)

    comments = []
    next_page_token = None
    max_fetch = min(total_comments, 500)

    while len(comments) < max_fetch:
        res = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=next_page_token
        ).execute()

        for item in res["items"]:
            text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            text = re.sub(r"<.*?>", "", text)  # clean html
            comments.append(text)

        next_page_token = res.get("nextPageToken")

        if not next_page_token:
            break

    return comments, total_comments


# ======================
# 🚀 ANALYSIS
# ======================
if analyze and url:

    video_id = get_video_id(url)

    if not video_id:
        st.error("❌ Invalid URL")
        st.stop()

    try:
        comments, total_comments = get_comments(video_id)

        if len(comments) == 0:
            st.error("❌ No comments found")
            st.stop()

        df = pd.DataFrame({"clean": comments})

        # ✅ SAVE IN SESSION
        st.session_state.df = df
        st.session_state.total_comments = total_comments

    except Exception as e:
        st.error(f"❌ {e}")
        st.stop()

# ======================
# 🔁 LOAD FROM SESSION
# ======================
if "df" in st.session_state:
    df = st.session_state.df
    total_comments = st.session_state.total_comments
else:
    st.info("👉 Enter URL and click Analyze")
    st.stop()

st.success("✅ Data Loaded Successfully")
# ======================
# 🧠 SENTIMENT
# ======================
positive_words = [
    "good","best","awesome","nice","love","great","amazing","super",
    "excellent","wow","fantastic","congratulations","congrats",
    "🔥","❤️","😍","😘","👍","👏"
]

negative_words = [
    "bad","worst","hate","boring","waste","poor","ugly",
    "disappoint","fake","cringe","annoying"
]

def get_sentiment(text):
    text = text.lower()
    if any(word in text for word in positive_words):
        return "Positive"
    elif any(word in text for word in negative_words):
        return "Negative"
    else:
        return "Neutral"

df["prediction"] = df["clean"].apply(get_sentiment)

# ======================
# 💡 CARDS
# ======================
st.markdown(f"""
<div style="display:flex; gap:20px;">
<div style="flex:1; padding:20px; border-radius:15px;
background: linear-gradient(135deg, #ff4b2b, #ff416c);
text-align:center; color:white;">
<h4>Total</h4>
<h2>{total_comments}</h2>
</div>

<div style="flex:1; padding:20px; border-radius:15px;
background: linear-gradient(135deg, #00c6ff, #0072ff);
text-align:center; color:white;">
<h4>Positive 😊</h4>
<h2>{(df['prediction']=='Positive').sum()}</h2>
</div>

<div style="flex:1; padding:20px; border-radius:15px;
background: linear-gradient(135deg, #ff512f, #dd2476);
text-align:center; color:white;">
<h4>Negative 😡</h4>
<h2>{(df['prediction']=='Negative').sum()}</h2>
</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ======================
# 🍩 + ☁️
# ======================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌀 Sentiment Chart")

    counts = df['prediction'].value_counts().reset_index()
    counts.columns = ['sentiment', 'count']

    fig = px.pie(counts, values='count', names='sentiment', hole=0.6)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("☁️ Word Cloud")

    text = " ".join(df['clean'])
    text = re.sub(r"http\S+", "", text)

    wc = WordCloud(width=800, height=400, colormap="inferno").generate(text)

    fig, ax = plt.subplots()
    ax.imshow(wc)
    ax.axis("off")

    st.pyplot(fig)

st.subheader("💬 Comments")

# Detect column
text_col = None
for col in df.columns:
    if col.lower() in ["comment", "comments", "text", "review", "content", "clean"]:
        text_col = col
        break

if text_col is None:
    st.error("❌ No comment column found")
else:
    option = st.selectbox(
        "Filter Comments",
        ["All", "Positive", "Negative", "Neutral"]
    )

    if option == "All":
        pos_df = df[df["prediction"] == "Positive"].head(3)
        neg_df = df[df["prediction"] == "Negative"].head(3)
        neu_df = df[df["prediction"] == "Neutral"].head(3)

        df_show = pd.concat([pos_df, neg_df, neu_df])

    else:
        df_show = df[df["prediction"] == option].head(3)

# ======================
# 📄 SHOW COMMENTS (ONLY CARDS)
# ======================
if 'df_show' in locals() and not df_show.empty:

    for _, row in df_show.iterrows():

        sentiment = row["prediction"]

        color = {
            "Positive": "#00ff99",
            "Negative": "#ff4b2b",
            "Neutral": "#f1c40f"
        }[sentiment]

        emoji = {
            "Positive": "😊",
            "Negative": "😡",
            "Neutral": "😐"
        }[sentiment]

        st.markdown(f"""
        <div style="
        padding:15px;
        margin:12px 0;
        border-radius:15px;
        background:linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
        border-left:6px solid {color};
        color:white;
        font-size:16px;">
        {row[text_col]} <br><br>
        <b>{sentiment} {emoji}</b>
        </div>
        """, unsafe_allow_html=True)