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
# Clean Reviews column
# -----------------------
df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')
df = df[df['Reviews'] > 500]

# -----------------------
# Remove app names starting with X Y Z
# -----------------------
df = df[~df['App'].str.startswith(('X','Y','Z'))]

# Remove app names containing S
df = df[~df['App'].str.contains('S', case=False, na=False)]

# -----------------------
# Category filter (E, C, B)
# -----------------------
df = df[df['Category'].str.startswith(('E','C','B'))]

# -----------------------
# Translate Categories
# -----------------------
translations = {
    'BEAUTY': 'सौंदर्य',      # Hindi
    'BUSINESS': 'வணிகம்',    # Tamil
    'DATING': 'Dating (German)'
}

df['Category'] = df['Category'].replace(translations)

# -----------------------
# Convert Date
# -----------------------
df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')
df['Month'] = df['Last Updated'].dt.to_period('M').astype(str)

# -----------------------
# Group installs by Month & Category
# -----------------------
trend = df.groupby(['Month','Category'])['Installs'].sum().reset_index()

# -----------------------
# Calculate Growth %
# -----------------------
trend['Growth'] = trend.groupby('Category')['Installs'].pct_change()
trend['High Growth'] = trend['Growth'] > 0.20

# -----------------------
# Time filter IST (6 PM – 9 PM)
# -----------------------
ist = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(ist).hour

if 18 <= current_time <= 21:
    fig = px.line(
        trend,
        x='Month',
        y='Installs',
        color='Category',
        title='Total Installs Over Time by Category'
    )

    # Highlight high growth points
    high_growth = trend[trend['High Growth'] == True]

    fig.add_scatter(
        x=high_growth['Month'],
        y=high_growth['Installs'],
        mode='markers',
        marker=dict(size=10, color='red'),
        name='High Growth (>20%)'
    )

    fig.show()
else:
    print("This chart works only between 6 PM IST and 9 PM IST")