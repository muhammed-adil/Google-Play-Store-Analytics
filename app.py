import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

st.title("Google Play Store Analytics Dashboard")

# Load data
df = pd.read_csv("googleplaystore.csv")
reviews_df = pd.read_csv("googleplaystore_user_reviews.csv")

# Merge datasets
df = df.merge(reviews_df[['App', 'Sentiment_Subjectivity']], on='App', how='left')

# Clean Installs
df['Installs'] = df['Installs'].str.replace('+','', regex=False)
df['Installs'] = df['Installs'].str.replace(',','', regex=False)
df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')

# Clean Size
df['Size'] = df['Size'].str.replace('M','', regex=False)
df['Size'] = df['Size'].str.replace('k','', regex=False)
df['Size'] = pd.to_numeric(df['Size'], errors='coerce')

# Clean Reviews
df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')

# Clean Rating
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')

# Remove NaN values
df = df.dropna(subset=['Installs','Size','Rating','Reviews','Sentiment_Subjectivity'])

# Filters (Task 1 conditions)
categories = ['GAME','BEAUTY','BUSINESS','COMICS','COMMUNICATION','DATING','ENTERTAINMENT','SOCIAL','EVENTS']

df = df[
    (df['Rating'] > 3.5) &
    (df['Category'].isin(categories)) &
    (df['Reviews'] > 500) &
    (df['Installs'] > 50000) &
    (df['Sentiment_Subjectivity'] > 0.5)
]

# Remove apps containing letter S
df = df[~df['App'].str.contains('S', na=False)]

# Translate categories
df['Category'] = df['Category'].replace({
    'BEAUTY': 'सौंदर्य',
    'BUSINESS': 'வணிகம்',
    'DATING': 'Partnersuche'
})

# Time condition (5PM–7PM IST)
tz = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(tz).hour

if 17 <= current_time < 19:
    fig = px.scatter(
        df,
        x='Size',
        y='Rating',
        size='Installs',
        color='Category',
        title='Bubble Chart: App Size vs Rating with Installs'
    )

    # Highlight GAME category pink
    fig.for_each_trace(lambda t: t.update(marker_color='pink') if t.name == 'GAME' else ())

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Chart available only between 5 PM and 7 PM IST")