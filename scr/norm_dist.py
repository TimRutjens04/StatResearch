import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import poisson

# Load dataset
df = pd.read_csv("results.csv")  # Adjust path if needed

# Create a new column for total goals per match
df["total_goals"] = df["home_score"] + df["away_score"]

# Calculate mean (lambda parameter for Poisson)
mean_goals = df["total_goals"].mean()

# Generate x values for Poisson distribution (only integer values make sense for goals)
x = np.arange(0, int(mean_goals*3))  # Up to 3 times the mean should cover most cases
y = poisson.pmf(x, mean_goals)

# Create the plot
plt.figure(figsize=(10, 5))
plt.bar(x, y, alpha=0.8, color='black', label='Poisson Distribution')
plt.plot(x, y, 'r-', linewidth=1)  # Add connecting lines

# Add mean line
plt.axvline(mean_goals, color="black", linestyle="dashed", linewidth=1,
            label=f'Mean = {mean_goals:.2f}')

# Labels and title
plt.xlabel("Total Goals per Match")
plt.ylabel("Probability")
plt.title("Poisson Distribution of Total Goals per Match")
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(x)  # Show all integer values
plt.show()