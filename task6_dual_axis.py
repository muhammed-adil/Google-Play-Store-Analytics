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
# Clean Price and Revenue
# -----------------------
df['Price'] = df['Price'].astype(str)
df['Price'] = df['Price'].str.replace('$','', regex=False)
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

# Revenue calculation
df['Revenue'] = df['Installs'] * df['Price']

# -----------------------
# Clean Size
# -----------------------
df['Size'] = df['Size'].astype(str)
df['Size'] = df['Size'].str.replace('M','', regex=False)
df['Size'] = pd.to_numeric(df['Size'], errors='coerce')

# -----------------------
# Clean Android Version
# -----------------------
df['Android Ver'] = df['Android Ver'].str.extract(r'(\d+\.\d+)')
df['Android Ver'] = pd.to_numeric(df['Android Ver'], errors='coerce')

# -----------------------
# Apply Filters
# -----------------------
df = df[df['Installs'] >= 10000]
df = df[df['Android Ver'] > 4.0]
df = df[df['Size'] > 15]
df = df[df['Content Rating'] == 'Everyone']
df = df[df['App'].str.len() <= 30]

# Revenue filter only for Paid apps
df_paid = df[df['Type'] == 'Paid']
df_paid = df_paid[df_paid['Revenue'] >= 10000]

df_free = df[df['Type'] == 'Free']

df = pd.concat([df_free, df_paid])

# -----------------------
# Top 3 Categories by Installs
# -----------------------
top3 = df.groupby('Category')['Installs'].sum().reset_index()
top3 = top3.sort_values(by='Installs', ascending=False).head(3)

df = df[df['Category'].isin(top3['Category'])]

# -----------------------
# Average Installs & Revenue by Free vs Paid
# -----------------------
result = df.groupby('Type').agg({
    'Installs':'mean',
    'Revenue':'mean'
}).reset_index()

# -----------------------
# Time filter IST (1 PM – 2 PM)
# -----------------------
ist = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(ist).hour

if True:
    fig = go.Figure()

    # Average Installs (Bar)
    fig.add_trace(go.Bar(
        x=result['Type'],
        y=result['Installs'],
        name='Average Installs',
        yaxis='y1'
    ))

    # Average Revenue (Line)
    fig.add_trace(go.Scatter(
        x=result['Type'],
        y=result['Revenue'],
        name='Average Revenue',
        yaxis='y2',
        mode='lines+markers'
    ))

    fig.update_layout(
        title='Average Installs vs Revenue (Free vs Paid)',
        xaxis=dict(title='App Type'),
        yaxis=dict(title='Average Installs'),
        yaxis2=dict(
            title='Average Revenue',
            overlaying='y',
            side='right'
        )
    )

    fig.show()
else:
    print("Chart available only between 1 PM and 2 PM IST")