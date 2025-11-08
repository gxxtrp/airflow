# Standard library imports
import os

# ML library imports
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns

# ==============================================================================
# Define the path to the CSV file
# =============================================================================
data_dir = "data"
file_name = "raw_data.csv"
data_path = os.path.join(data_dir, file_name)
absolute_data_path = os.path.abspath(data_path)

# ==============================================================================
# 1. LOAD DATA
# ==============================================================================
df = pd.read_csv(absolute_data_path)

# ==============================================================================
# DATA VISUALIZATION
# ==============================================================================
TARGET_COL = df.columns[-1]
SYMPTOM_COLS = df.columns[:-1].tolist()
# Get the two most frequent categories for focused plotting
target_counts = df[TARGET_COL].value_counts()
top_categories = target_counts.index[:2].tolist()

print("\n" + "="*50)
print("             3. DATA VISUALIZATION: CORE INSIGHTS (SPLIT)             ")
print("="*50)

# Get the two most frequent categories for focused plotting
top_categories = target_counts.index[:2].tolist()

# --- FIGURE 1: OVERVIEW (Distribution and Correlation) ---
fig1, axes1 = plt.subplots(1, 2, figsize=(20, 10))
fig1.suptitle(f'Figure 1: Data Overview - Distribution & Symptom Correlation', fontsize=18, y=0.98)
plt.subplots_adjust(wspace=0.2)


# Plot 1: Target Variable Distribution
sns.countplot(x=TARGET_COL, data=df, ax=axes1[0], order=target_counts.index)
axes1[0].set_title(f'1. Distribution of Disease Types ({TARGET_COL})', fontsize=14)
axes1[0].set_xlabel('Disease Type')
axes1[0].set_ylabel('Number of Cases')
axes1[0].tick_params(axis='x', rotation=45)


# Plot 2: Symptom Co-occurrence (Correlation Heatmap)
correlation_matrix = df[SYMPTOM_COLS].corr()
# Adjust figure size specifically for the dense heatmap
# We will draw the heatmap directly on the second subplot
sns.heatmap(
    correlation_matrix, 
    ax=axes1[1], 
    cmap='magma', 
    annot=False,  # Set to False to prevent overcrowding labels
    linewidths=0.5, 
    cbar_kws={'label': 'Correlation Coefficient'}
)
axes1[1].set_title('2. Symptom Co-occurrence Correlation Heatmap', fontsize=14)
axes1[1].tick_params(axis='x', rotation=90)
axes1[1].tick_params(axis='y', rotation=0)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()

# --- FIGURE 2: COMPARATIVE SYMPTOM ANALYSIS ---
fig2, axes2 = plt.subplots(1, 2, figsize=(18, 7))
fig2.suptitle(f'Figure 2: Comparative Symptom Frequency (Top Categories)', fontsize=18, y=0.98)
plt.subplots_adjust(wspace=0.3)


# Plot 3: Symptom Frequency for Top Category 1
if len(top_categories) >= 1:
    cat1 = top_categories[0]
    # Filter to show only the Top 10 symptoms for clarity
    cat1_data = df[df[TARGET_COL] == cat1][SYMPTOM_COLS].sum().sort_values(ascending=False).head(10)
    
    sns.barplot(
        x=cat1_data.index, 
        y=cat1_data.values, 
        ax=axes2[0], 
        color=sns.color_palette("viridis")[0]
    )
    axes2[0].set_title(f"3. Symptom Frequency for: {cat1} (Top 10)", fontsize=14)
    axes2[0].set_xlabel('Symptom')
    axes2[0].set_ylabel('Count of Occurrences')
    axes2[0].tick_params(axis='x', rotation=45)
    axes2[0].set_ylim(0, df.shape[0] * 0.7)


# Plot 4: Symptom Frequency for Top Category 2
if len(top_categories) >= 2:
    cat2 = top_categories[1]
    # Filter to show only the Top 10 symptoms for clarity
    cat2_data = df[df[TARGET_COL] == cat2][SYMPTOM_COLS].sum().sort_values(ascending=False).head(10)
    
    sns.barplot(
        x=cat2_data.index, 
        y=cat2_data.values, 
        ax=axes2[1], 
        color=sns.color_palette("viridis")[3]
    )
    axes2[1].set_title(f"4. Symptom Frequency for: {cat2} (Top 10)", fontsize=14)
    axes2[1].set_xlabel('Symptom')
    axes2[1].set_ylabel('Count of Occurrences')
    axes2[1].tick_params(axis='x', rotation=45)
    axes2[1].set_ylim(0, df.shape[0] * 0.7)


plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()

# ==============================================================================
# 4. FINAL SUMMARIES
# ==============================================================================

print("\n" + "="*50)
print("             4. DIAGNOSTIC SUMMARIES (Symptom Differences)             ")
print("="*50)

if len(top_categories) >= 2:
    # Use the top 10 symptoms from the combined data for a cleaner comparison
    combined_symptoms = list(set(cat1_data.index.tolist() + cat2_data.index.tolist()))
    
    # Recalculate difference using the top symptoms across both
    cat1_freq = df[df[TARGET_COL] == cat1][combined_symptoms].sum()
    cat2_freq = df[df[TARGET_COL] == cat2][combined_symptoms].sum()
    
    diff = cat1_freq.sub(cat2_freq, fill_value=0).sort_values(key=abs, ascending=False)
    
    print(f"\n--- Key Symptoms Unique to {cat1} (Positive numbers) vs. {cat2} (Negative numbers) ---")
    print(" (Difference in Raw Count between the two categories, based on top 10 symptoms)")
    print(diff.head(5).to_string())
else:
    print("\nNeed at least two categories to perform a differential symptom analysis.")

# End of EDA Script