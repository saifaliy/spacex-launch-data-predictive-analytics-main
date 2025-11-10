# Import required libraries
import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv('dataset_part_1.csv')
df.head(5)

# Identify and calculate the percentage of the missing values in each attribute
df.isnull().sum()/len(df)*100

# Identify numerical and categorical variables
df.dtypes

# Let's see the number of launches on each site
df['LaunchSite'].value_counts()

# Apply value_counts on Orbit column.
# Ignore GTO as it is a transfer orbit and not itself geostationary
df['Orbit'].value_counts()

# landing_outcomes = values on Outcome column
landing_outcomes = df['Outcome'].value_counts()

for i,outcome in enumerate(landing_outcomes.keys()):
    print(i,outcome)

# Create a set of outcomes where the second stage did not land successfully
bad_outcomes=set(landing_outcomes.keys()[[1,3,5,6,7]])
bad_outcomes

# Create a landing outcome label from Outcome column
landing_class = np.where(df['Outcome'].isin(bad_outcomes) | df['Outcome'].isna(), 0, 1)
df['Class']=landing_class
df[['Class']].head() # Should match 90 successful landings from Outcome column
df.head(5)

# Determine the success rate
df['Class'].mean()

# Save as CSV
df.to_csv("dataset_part_2.csv", index=False)