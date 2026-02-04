import streamlit as st
from gnews import GNews
import requests
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="AI Daily Brief", page_icon="🗞️")
HF_TOKEN = st.secrets.get("HF_TOKEN")
# Using a faster, more reliable summarization model
API_URL = "https://api-inference.huggingface.co/models/slauw87/bart_summarisation"

# --- LOGIC ---
@st.cache_data(ttl=3600)
def fetch_news(topic):
    return GNews(language='en', period='1d', max_results=3).get_news(topic)

def get_ai_summary(text):
    if not HF_TOKEN: return "Token missing."
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": text, 
        "parameters": {"max_length": 60, "min_length": 20},
        "options": {"wait_for_model": True} # Critical for free tier
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
        return response.json()[0]['summary_text']
    except:
        return "AI is preparing the summary... refresh in a moment."

# --- UI ---
st.title("🗞️ Your AI Daily News Brief")
st.caption(f"Personalized Feed • {datetime.now().strftime('%d %b %Y')}")

with st.sidebar:
    st.header("Preferences")
    segments = st.multiselect("Topics:", ["Technology", "Business", "Sports", "Politics"], default=["Technology"])

if segments:
    for topic in segments:
        st.subheader(f"🔹 {topic}")
        articles = fetch_news(topic)
        for art in articles:
            with st.container(border=True):
                st.markdown(f"**{art['title']}**")
                summary = get_ai_summary(art['description'] or art['title'])
                st.write(f"✨ {summary}")
                st.caption(f"Source: {art['publisher']['title']}")
                st.link_button("Read More", art['url'])


