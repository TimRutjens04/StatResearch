import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
df = pd.read_csv("results.csv") 

df["total_goals"] = df["home_score"] + df["away_score"]

# # Select the top 10 most frequent tournament types for readability
top_tournaments = df["tournament"].value_counts()
df_filtered = df[df["tournament"].isin(top_tournaments)]

# Set plot style
sns.set(style="whitegrid")

# Box Plot: Total Goals by Tournament Type
plt.figure(figsize=(14, 7))
sns.boxplot(data=df_filtered, x="tournament", y="total_goals", palette="Set2")
plt.xticks(rotation=90)
plt.xlabel("Tournament Type")
plt.ylabel("Total Goals per Match")
plt.title("Distribution of Total Goals per Match by Tournament Type")
plt.tight_layout()
plt.show()

# Histogram: Distribution of Total Goals
plt.figure(figsize=(10, 5))
sns.histplot(df["total_goals"], bins=15, kde=True, color="blue")
plt.xlabel("Total Goals per Match")
plt.ylabel("Frequency")
plt.title("Histogram of Total Goals per Match")
plt.show()


pd.set_option("display.max_rows", None)
print(top_tournaments)
