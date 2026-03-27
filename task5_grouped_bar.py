import pandas as pd
import plotly.graph_objects as go
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
# Clean Reviews, Rating, Size
# -----------------------
df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')

df['Size'] = df['Size'].astype(str)
df['Size'] = df['Size'].str.replace('M','', regex=False)
df['Size'] = pd.to_numeric(df['Size'], errors='coerce')

# -----------------------
# Filter Size >= 10 MB
# -----------------------
df = df[df['Size'] >= 10]

# -----------------------
# Filter Last Updated = January
# -----------------------
df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')
df = df[df['Last Updated'].dt.month == 1]

# -----------------------
# Group by Category
# -----------------------
category_data = df.groupby('Category').agg({
    'Installs':'sum',
    'Rating':'mean',
    'Reviews':'sum'
}).reset_index()

# -----------------------
# Top 10 Categories by Installs
# -----------------------
top10 = category_data.sort_values(by='Installs', ascending=False).head(10)

# Filter Avg Rating >= 4.0
top10 = top10[top10['Rating'] >= 4.0]

# -----------------------
# Time filter IST (3 PM – 5 PM)
# -----------------------
ist = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(ist).hour

if 15 <= current_time <= 17:
    fig = go.Figure()

    fig.add_bar(
        x=top10['Category'],
        y=top10['Rating'],
        name='Average Rating'
    )

    fig.add_bar(
        x=top10['Category'],
        y=top10['Reviews'],
        name='Total Reviews'
    )

    fig.update_layout(
        barmode='group',
        title='Average Rating and Total Reviews for Top 10 Categories'
    )

    fig.show()
else:
    print("Chart available only between 3 PM and 5 PM IST")