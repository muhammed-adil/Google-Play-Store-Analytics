import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

# Load dataset
df = pd.read_csv("googleplaystore.csv")

# -----------------------
# Clean Installs
# -----------------------
df['Installs'] = df['Installs'].astype(str)
df['Installs'] = df['Installs'].str.replace('+','', regex=False)
df['Installs'] = df['Installs'].str.replace(',','', regex=False)
df = df[df['Installs'].str.isnumeric()]
df['Installs'] = df['Installs'].astype(float)

# -----------------------
# Clean Reviews & Rating
# -----------------------
df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')

# Filters
df = df[df['Rating'] >= 4.2]
df = df[df['Reviews'] > 1000]

# -----------------------
# Remove app names with numbers
# -----------------------
df = df[~df['App'].str.contains(r'\d', regex=True)]

# -----------------------
# Category filter (T or P)
# -----------------------
df = df[df['Category'].str.startswith(('T','P'))]

# -----------------------
# Clean Size
# -----------------------
df['Size'] = df['Size'].astype(str)
df['Size'] = df['Size'].str.replace('M','', regex=False)
df['Size'] = df['Size'].str.replace('k','', regex=False)
df['Size'] = pd.to_numeric(df['Size'], errors='coerce')

df = df[(df['Size'] >= 20) & (df['Size'] <= 80)]

# -----------------------
# Translate Categories
# -----------------------
translations = {
    'TRAVEL_AND_LOCAL': 'Voyage',     # French
    'PRODUCTIVITY': 'Productividad',  # Spanish
    'PHOTOGRAPHY': '写真'              # Japanese
}

df['Category'] = df['Category'].replace(translations)

# -----------------------
# Convert Date
# -----------------------
df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')
df['Month'] = df['Last Updated'].dt.to_period('M').astype(str)

# -----------------------
# Group cumulative installs
# -----------------------
trend = df.groupby(['Month','Category'])['Installs'].sum().reset_index()

trend['Cumulative'] = trend.groupby('Category')['Installs'].cumsum()

# -----------------------
# Growth calculation
# -----------------------
trend['Growth'] = trend.groupby('Category')['Installs'].pct_change()
trend['High Growth'] = trend['Growth'] > 0.25

# -----------------------
# Time filter IST (4 PM – 6 PM)
# -----------------------
ist = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(ist).hour

if 16 <= current_time <= 18:
    fig = px.area(
        trend,
        x='Month',
        y='Cumulative',
        color='Category',
        title='Cumulative Installs Over Time by Category'
    )

    # Highlight high growth months
    high_growth = trend[trend['High Growth'] == True]

    fig.add_scatter(
        x=high_growth['Month'],
        y=high_growth['Cumulative'],
        mode='markers',
        marker=dict(size=8, color='red'),
        name='High Growth (>25%)'
    )

    fig.show()
else:
    print("Chart available only between 4 PM and 6 PM IST")