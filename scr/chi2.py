import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, kruskal
import matplotlib.pyplot as plt
import seaborn as sns
from categories import world, continental, regional, friendly

# Load the data
df = pd.read_csv("results.csv")
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.width', None)  # Set display width

# Create goal categories
def categorize_goals(goals):
    if goals == 0:
        return '0 goals'
    elif 1 <= goals <= 3:
        return '1-3 goals'
    elif 4 <= goals <= 6:
        return '4-6 goals'
    elif 7 <= goals <= 10:
        return '7-10 goals'
    else:
        return '11+ goals'
    
# Create tournament categories
def categorize_tournament(tournament):
    if tournament in world:
        return 'World'
    elif tournament in continental:
        return 'Continental'
    elif tournament in regional:
        return 'Regional'
    elif tournament in friendly:
        return 'Friendly'
    else:
        return 'Other'

df['goal_category'] = df['total_goals'].apply(categorize_goals)
df['tournament_category'] = df['tournament'].apply(categorize_tournament)

# Create contingency table for tournament vs goal categories
contingency = pd.crosstab(df['tournament_category'], df['goal_category'])

# Perform chi-square test
chi2, p_value, dof, expected = chi2_contingency(contingency)

print("\nContingency Table:")
print(contingency)
print("\nChi-square test results:")
print(f"Chi-square statistic: {chi2:.2f}")
print(f"p-value: {p_value:.2e}")
print(f"Degrees of freedom: {dof}")

# Visualization
plt.figure(figsize=(12, 8))
sns.heatmap(contingency, annot=True, fmt='d', cmap='YlOrRd')
plt.title('Goal Categories by Tournament Type')
plt.ylabel('Tournament Category')
plt.xlabel('Goal Category')
plt.tight_layout()
plt.show()

# Kruskal-Wallis test
tournament_categories = df['tournament_category'].unique()
category_goals = [df[df['tournament_category'] == cat]['total_goals'] for cat in tournament_categories]
h_statistic, p_value = kruskal(*category_goals)

print("\nKruskal-Wallis test results (by tournament category):")
print(f"H-statistic: {h_statistic:.2f}")
print(f"p-value: {p_value:.2e}")

# Descriptive statistics for each category
print("\nDescriptive statistics by tournament category:")
stats_template = """
{category}:
Mean goals: {mean:.2f}
Median goals: {median:.2f}
Standard deviation: {std:.2f}
Number of matches: {count}"""

for cat in tournament_categories:
    cat_goals = df[df['tournament_category'] == cat]['total_goals']
    stats = {
        'category': cat,
        'mean': cat_goals.mean(),
        'median': cat_goals.median(),
        'std': cat_goals.std(),
        'count': len(cat_goals)
    }
    print(stats_template.format(**stats))