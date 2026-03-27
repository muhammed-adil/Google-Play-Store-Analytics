import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

# Load dataset
df = pd.read_csv("googleplaystore.csv")

# ---------------------------
# Clean Installs column
# ---------------------------
df['Installs'] = df['Installs'].astype(str)
df['Installs'] = df['Installs'].str.replace('+','', regex=False)
df['Installs'] = df['Installs'].str.replace(',','', regex=False)

# Keep only numeric values
df = df[df['Installs'].str.isnumeric()]

# Convert to float
df['Installs'] = df['Installs'].astype(float)

# ---------------------------
# Remove categories starting with A, C, G, S
# ---------------------------
df = df[~df['Category'].str.startswith(('A','C','G','S'))]

# ---------------------------
# Map categories to countries (for choropleth)
# ---------------------------
country_map = {
    'GAME':'India',
    'BUSINESS':'United States',
    'BEAUTY':'France',
    'ENTERTAINMENT':'United Kingdom',
    'EVENTS':'Canada',
    'SOCIAL':'Germany',
    'DATING':'Brazil',
    'COMMUNICATION':'Australia',
    'COMICS':'Japan'
}

df['Country'] = df['Category'].map(country_map)

# Remove rows without country
df = df.dropna(subset=['Country'])

# ---------------------------
# Group installs by country
# ---------------------------
country_installs = df.groupby('Country')['Installs'].sum().reset_index()

# ---------------------------
# Top 5 categories by installs
# ---------------------------
top5 = country_installs.sort_values(by='Installs', ascending=False).head(5)

# ---------------------------
# Highlight installs > 1,000,000
# ---------------------------
top5['Highlight'] = top5['Installs'] > 1000000

# ---------------------------
# Time filter IST (6 PM – 8 PM)
# ---------------------------
ist = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(ist).hour

if 18 <= current_time <= 20:
    fig = px.choropleth(
        top5,
        locations="Country",
        locationmode="country names",
        color="Installs",
        hover_name="Country",
        color_continuous_scale="Viridis",
        title="Global Installs by Category (Top 5)"
    )
    fig.show()
else:
    print("Map available only between 6 PM and 8 PM IST")