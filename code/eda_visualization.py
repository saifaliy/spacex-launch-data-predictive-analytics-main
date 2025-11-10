# Import required libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Read SpaceX dataset part-2 into the pandas DataFrame
df = pd.read_csv('dataset_part_2.csv')
df.head(5)

# Plot FlightNumber vs. PayloadMass
sns.catplot(y="PayloadMass", x="FlightNumber", hue="Class", data=df, aspect = 5)
plt.xlabel("Flight Number",fontsize=20)
plt.ylabel("Pay load Mass (kg)",fontsize=20)
plt.show()

# FlightNumber vs LaunchSite
sns.catplot(y="LaunchSite", x="FlightNumber", hue="Class", data=df, aspect = 5)
plt.xlabel("Flight Number",fontsize=20)
plt.ylabel("LaunchSite",fontsize=20)
plt.show()

# Plot LaunchSite vs. PayloadMass
sns.catplot(y="LaunchSite", x="PayloadMass", hue="Class", data=df, aspect = 5)
plt.xlabel("PayloadMass",fontsize=20)
plt.ylabel("LaunchSite",fontsize=20)
plt.show()

# Visualize the relationship between success rate of each orbit type
# Group and calculate mean success rate per orbit
success_rate = df.groupby('Orbit')['Class'].mean().sort_values(ascending=False)

# Create figure
plt.figure(figsize=(10,6))

# Create colorful bars
bars = plt.bar(success_rate.index, success_rate.values, color=plt.cm.viridis(success_rate.values / max(success_rate.values)))

# Add chart title and labels
plt.title('SpaceX Launch Success Rate by Orbit Type', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Orbit Type', fontsize=12)
plt.ylabel('Success Rate', fontsize=12)
plt.xticks(rotation=45, ha='right', fontsize=10)

# Add gridlines for clarity
plt.grid(axis='y', linestyle='--', alpha=0.6)

# Add value labels on bars
for bar in bars:
    plt.text(bar.get_x() + bar.get_width()/2,
             bar.get_height() + 0.01,
             f"{bar.get_height():.2f}",
             ha='center', va='bottom', fontsize=10, fontweight='medium')

# Remove unnecessary frame lines for a clean look
for spine in ['top', 'right']:
    plt.gca().spines[spine].set_visible(False)

plt.tight_layout()
plt.show()

# Plot FlightNumber vs. Orbit type
sns.catplot(y="Orbit", x="FlightNumber", hue="Class", data=df, aspect = 5)
plt.xlabel("FlightNumber",fontsize=20)
plt.ylabel("Orbit",fontsize=20)
plt.show()

# Plot Payload Mass vs. Orbit type
sns.catplot(y="Orbit", x="PayloadMass", hue="Class", data=df, aspect = 5)
plt.xlabel("PayloadMass",fontsize=20)
plt.ylabel("Orbit",fontsize=20)
plt.show()

# Visualize the launch success yearly trend
# Create a proper 'Year' column from the 'Date' column.
# Ensure 'Date' is parsed as datetime, then extract the year.
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
# Drop rows where Date couldn't be parsed (optional but safer)
df = df.dropna(subset=['Date']).copy()
df['Year'] = df['Date'].dt.year
df.head()

# Plot a line chart with x axis to be the extracted year and y axis to be the success rate
# Calculate yearly average success rate
yearly_success = df.groupby('Year', as_index=False)['Class'].mean()

# Ensure 'Year' is numeric (sometimes extracted as string)
yearly_success['Year'] = yearly_success['Year'].astype(int)

# Set modern Seaborn style
sns.set_theme(style='whitegrid', context='talk')

# Create figure
plt.figure(figsize=(10,6))

# Line chart with markers and smooth color
sns.lineplot(
    data=yearly_success,
    x='Year',
    y='Class',
    marker='o',
    linewidth=3,
    color='#0077b6'
)

# Add title and axis labels
plt.title('SpaceX Launch Success Rate by Year', fontsize=18, fontweight='bold', pad=20)
plt.xlabel('Launch Year', fontsize=13)
plt.ylabel('Average Success Rate', fontsize=13)

# Make x-axis integers only
plt.xticks(yearly_success['Year'], rotation=45)

# Clean up chart
sns.despine()
plt.tight_layout()
plt.show()

# Features Engineering
features = df[['FlightNumber', 'PayloadMass', 'Orbit', 'LaunchSite', 'Flights', 'GridFins', 'Reused', 'Legs', 'LandingPad', 'Block', 'ReusedCount', 'Serial']]
features.head()

# Create dummy variables to categorical columns
# Create dummy variables for categorical columns
features_one_hot = pd.get_dummies(
    features, 
    columns=['Orbit', 'LaunchSite', 'LandingPad', 'Serial']
)

# Display the first few rows of the new dataframe
features_one_hot.head()

# Cast all columns to float64
features_one_hot = features_one_hot.astype('float64')

# Display the first few rows to verify
features_one_hot.head()

features_one_hot.to_csv('dataset_part_3.csv', index=False)