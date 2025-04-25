import pandas as pd
import plotly.express as px
from helpers import ROOT_CAUSE_CATEGORIES, TECHNICAL_DOMAIN_CATEGORIES, ACCESS_CONTEXT_CATEGORIES

df = pd.read_csv("data/transformed_data.csv")

# Group by 'rootCauseCategory' and then by 'technicalDomain' to get counts
grouped_df = df.groupby(['rootCauseCategory', 'technicalDomain']).size().reset_index(name='counts')

# Remove values of `rootCauseCategory` if not in the list of ROOT_CAUSE_CATEGORIES
grouped_df = grouped_df[grouped_df['rootCauseCategory'].isin(ROOT_CAUSE_CATEGORIES.keys())]
# Remove values of `technicalDomain` if not in the list of TECHNICAL_DOMAIN_CATEGORIES
grouped_df = grouped_df[grouped_df['technicalDomain'].isin(TECHNICAL_DOMAIN_CATEGORIES.keys())]
# # Remove values of `accessContext` if not in the list of ACCESS_CONTEXT_CATEGORIES
# grouped_df = grouped_df[grouped_df['accessContext'].isin(ACCESS_CONTEXT_CATEGORIES.keys())]

# Pivot the DataFrame to get 'technicalDomain' as columns and 'rootCauseCategory' as rows
pivot_df = grouped_df.pivot(index='rootCauseCategory', columns='technicalDomain', values='counts').fillna(0)

# Reset the index to make 'rootCauseCategory' a column again
pivot_df.reset_index(inplace=True)

# Print the pivoted DataFrame
print(pivot_df)

# Print the heatmap with plotly, with x axis as technicalDomain and y axis as rootCauseCategory
# Create the heatmap with plotly
fig = px.imshow(
    pivot_df.set_index('rootCauseCategory'),
    labels=dict(x="Technical Domain", y="Root Cause Category", color="Count"),
    x=pivot_df.columns[1:],  # Use all columns except the first one (rootCauseCategory)
    y=pivot_df['rootCauseCategory'],
    color_continuous_scale="YlOrRd",
    aspect="auto",
    title="Heatmap of Root Cause Categories by Technical Domain"
)

# Customize the layout
fig.update_layout(
    xaxis=dict(side="bottom"),
    yaxis=dict(tickmode="linear"),
    coloraxis_colorbar=dict(title="Count")
)

# Show the plot
fig.show()

pivot_df.to_csv("data/heatmap_data.csv", index=False)

