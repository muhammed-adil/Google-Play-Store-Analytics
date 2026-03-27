import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

# -----------------------------
# Time restriction (5 PM to 7 PM IST)
# -----------------------------
ist = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(ist)

if not (17 <= current_time.hour < 21):
    print("Chart available only between 5 PM and 7 PM IST")
    exit()

# -----------------------------
# Load datasets
# -----------------------------
df = pd.read_csv("googleplaystore.csv")
reviews_df = pd.read_csv("googleplaystore_user_reviews.csv")

# -----------------------------
# Clean Size column
# -----------------------------
df['Size'] = df['Size'].str.replace('M', '')
df['Size'] = df['Size'].str.replace('k', '')
df['Size'] = df['Size'].replace('Varies with device', None)
df['Size'] = pd.to_numeric(df['Size'], errors='coerce')

# -----------------------------
# Clean Installs column
# -----------------------------
df['Installs'] = df['Installs'].str.replace('+', '')
df['Installs'] = df['Installs'].str.replace(',', '')
df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')

# -----------------------------
# Convert Reviews & Rating
# -----------------------------
df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')

# -----------------------------
# Merge Sentiment Subjectivity
# -----------------------------
reviews_df = reviews_df[['App', 'Sentiment_Subjectivity']]
reviews_df = reviews_df.dropna()

df = pd.merge(df, reviews_df, on='App', how='inner')

# -----------------------------
# Apply Filters
# -----------------------------
categories = [
    'GAME','BEAUTY','BUSINESS','COMICS','COMMUNICATION',
    'DATING','ENTERTAINMENT','SOCIAL','EVENTS'
]

df = df[
    (df['Rating'] > 3.5) &
    (df['Reviews'] > 500) &
    (df['Installs'] > 50000) &
    (df['Sentiment_Subjectivity'] > 0.5) &
    (df['Category'].isin(categories)) &
    (~df['App'].str.contains('S', case=False, na=False))
]

# -----------------------------
# Translate Categories
# -----------------------------
translation = {
    'BEAUTY': 'सुंदरता',      # Hindi
    'BUSINESS': 'வணிகம்',     # Tamil
    'DATING': 'Partnersuche' # German
}

df['Category'] = df['Category'].replace(translation)

# -----------------------------
# Bubble Chart
# -----------------------------
fig = px.scatter(
    df,
    x='Size',
    y='Rating',
    size='Installs',
    color='Category',
    hover_name='App',
    title='Bubble Chart: App Size vs Rating with Installs'
)

# -----------------------------
# Highlight Game category in Pink
# -----------------------------
for trace in fig.data:
    if trace.name == 'GAME':
        trace.marker.color = 'pink'
        trace.marker.line.width = 2
        trace.marker.line.color = 'black'

# -----------------------------
# Dropdown Filter for Categories
# -----------------------------
unique_categories = df['Category'].unique()
buttons = []

# Show All button
buttons.append(dict(
    label="All",
    method="update",
    args=[{"visible": [True] * len(fig.data)}]
))

# Category buttons
for cat in unique_categories:
    visible = [cat == trace.name for trace in fig.data]
    buttons.append(dict(
        label=cat,
        method="update",
        args=[{"visible": visible}]
    ))

fig.update_layout(
    updatemenus=[
        dict(
            buttons=buttons,
            direction="down",
            showactive=True,
            x=1.15,
            y=1
        )
    ],
    xaxis_title="App Size (MB)",
    yaxis_title="Average Rating",
    legend_title="Category"
)

fig.show()