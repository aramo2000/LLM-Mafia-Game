import matplotlib.pyplot as plt
import json
import math


# Load the data
path = "analysis_data/"
with open(path+"win_rates_different.json") as f:
    diff_data = json.load(f)
with open(path+"win_rates_same.json") as f:
    same_data = json.load(f)
llms = list(diff_data["role_win_counts"].keys())
roles = ["mafia", "don", "detective", "civilian"]



# 1. Bar Chart: Win Ratio by Role for Each Model
# Number of games each LLM played in each role
role_game_counts = {
    "mafia": 60,
    "don": 30,
    "detective": 30,
    "civilian": 180
}

ci_factor = 1.44  # For 85% confidence interval

fig, ax = plt.subplots(figsize=(12, 6))
bar_width = 0.2
index = range(len(llms))

for i, role in enumerate(roles):
    role_win_data = [diff_data["llm_role_win_ratios"][llm].get(role, 0) for llm in llms]
    n = role_game_counts[role]
    error_bars = [ci_factor * math.sqrt((p * (1 - p)) / n) if n > 0 else 0 for p in role_win_data]

    bar_positions = [p + bar_width * i for p in index]
    bars = ax.bar(bar_positions, role_win_data, bar_width, yerr=error_bars, capsize=5, label=f"{role} Wins")

    for x, y, err in zip(bar_positions, role_win_data, error_bars):
        # Bar value inside the bar
        ax.text(x, y - 0.05, f'{y:.2f}', ha='center', va='bottom', fontsize=8, color='white', fontweight='bold')

        # Error bar start and end values
        lower = max(y - err, 0)
        upper = min(y + err, 1)
        ax.text(x + 0.01, lower, f'{lower:.2f}', ha='left', va='top', fontsize=7, color='black')
        ax.text(x + 0.01, upper, f'{upper:.2f}', ha='left', va='bottom', fontsize=7, color='black')

# Formatting
ax.set_xlabel('LLMs')
ax.set_ylabel('Win Percentage')
ax.set_title('Win Rates by Role for Each LLM (Different Model Games) with 85% Confidence Interval')
ax.set_xticks([p + bar_width * (len(roles) - 1) / 2 for p in index])
ax.set_xticklabels(llms)
ax.set_ylim(0, 1.1)
ax.legend()
plt.tight_layout()
plt.show()



# 2. Role Wins for Different Models
role_wins_data = diff_data["role_wins"]
llms = list(role_wins_data.keys())
wins = list(role_wins_data.values())

plt.figure(figsize=(10, 6))
plt.bar(llms, wins, color='skyblue')
bars = plt.bar(llms, wins, color='skyblue')

for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height}', ha='center', va='bottom')

plt.xlabel('LLMs')
plt.ylabel('Total Wins (Across All Roles)')
plt.title('Total Wins for Each LLM (Across All Roles)')
plt.tight_layout()
plt.show()



# 3. Mafia Win Rate of Each LLM in Same-Model vs Different-Model Games
same_model_mafia_win_rates = [same_data[llm]["mafia_win_ratio"] for llm in llms]
combined_mafia_don_win_counts = [diff_data["llm_role_combinations_wins"][llm]["mafia_don"] / 90 for llm in llms]

# Sample sizes
same_counts = {
    "openai": 120,
    "gemini": 120,
    "grok": 120,
    "claude": 60,
    "deepseek": 60
}
diff_count = 90

# CI setup
ci_factor = 1.44  # 85% confidence interval

# Compute error bars
same_errors = [
    ci_factor * math.sqrt(p * (1 - p) / same_counts[llm]) if same_counts[llm] > 0 else 0
    for llm, p in zip(llms, same_model_mafia_win_rates)
]
diff_errors = [
    ci_factor * math.sqrt(p * (1 - p) / diff_count) if diff_count > 0 else 0
    for p in combined_mafia_don_win_counts
]

# Plot
fig, ax = plt.subplots(figsize=(12, 6))
bar_width = 0.35
index = range(len(llms))

bars1 = ax.bar(index, same_model_mafia_win_rates, bar_width, yerr=same_errors, capsize=5,
               label='Same-Model Mafia+Don Win Rate', color='red')
bars2 = ax.bar([i + bar_width for i in index], combined_mafia_don_win_counts, bar_width,
               yerr=diff_errors, capsize=5, label='Different-Model Mafia+Don Win Rate', color='blue')

# Annotate values and error bar bounds
for x, y, err in zip(index, same_model_mafia_win_rates, same_errors):
    ax.text(x, y - 0.05, f'{y:.2f}', ha='center', va='bottom', color='white', fontweight='bold')
    ax.text(x + 0.01, max(y - err, 0), f'{max(y - err, 0):.2f}', ha='left', va='top', fontsize=7, color='black')
    ax.text(x + 0.01, min(y + err, 1), f'{min(y + err, 1):.2f}', ha='left', va='bottom', fontsize=7, color='black')

for x, y, err in zip([i + bar_width for i in index], combined_mafia_don_win_counts, diff_errors):
    ax.text(x, y - 0.05, f'{y:.2f}', ha='center', va='bottom', color='white', fontweight='bold')
    ax.text(x + 0.01, max(y - err, 0), f'{max(y - err, 0):.2f}', ha='left', va='top', fontsize=7, color='black')
    ax.text(x + 0.01, min(y + err, 1), f'{min(y + err, 1):.2f}', ha='left', va='bottom', fontsize=7, color='black')

# Final formatting
ax.set_xlabel('LLMs')
ax.set_ylabel('Win Rate')
ax.set_title('Mafia+Don Win Rates of LLMs in Same-Model vs Different-Model Games (85% CI)')
ax.set_xticks([i + bar_width / 2 for i in index])
ax.set_xticklabels(llms)
ax.set_ylim(0, 1.1)
ax.legend()
plt.tight_layout()
plt.show()



# 4. Civilian Win Rate of Each LLM in Same-Model vs Different-Model Games
same_counts_civ = {
    "openai": 280,   # placeholder
    "gemini": 280,
    "grok": 280,
    "claude": 140,
    "deepseek": 140
}
diff_count_civ = 210  # as specified earlier

# Win rates
same_model_civilian_win_rates = [(1 - same_data[llm]["mafia_win_ratio"]) for llm in llms]
combined_civilian_detective_win_counts = [
    diff_data["llm_role_combinations_wins"][llm]["civilian_detective"] / diff_count_civ for llm in llms
]

# Error bars using 85% CI
ci_factor = 1.44
same_errors_civ = [
    ci_factor * math.sqrt(p * (1 - p) / same_counts_civ[llm]) if same_counts_civ[llm] > 0 else 0
    for llm, p in zip(llms, same_model_civilian_win_rates)
]
diff_errors_civ = [
    ci_factor * math.sqrt(p * (1 - p) / diff_count_civ) if diff_count_civ > 0 else 0
    for p in combined_civilian_detective_win_counts
]

# Plot
fig, ax = plt.subplots(figsize=(12, 6))

bars1 = ax.bar(index, same_model_civilian_win_rates, bar_width, yerr=same_errors_civ, capsize=5,
               label='Same-Model Civilians Win Rate', color='red')
bars2 = ax.bar([i + bar_width for i in index], combined_civilian_detective_win_counts, bar_width,
               yerr=diff_errors_civ, capsize=5, label='Different-Model Civilians Win Rate', color='blue')

# Annotate values and error bar bounds
for x, y, err in zip(index, same_model_civilian_win_rates, same_errors_civ):
    ax.text(x, y - 0.05, f'{y:.2f}', ha='center', va='bottom', color='white', fontweight='bold')
    ax.text(x + 0.01, max(y - err, 0), f'{max(y - err, 0):.2f}', ha='left', va='top', fontsize=7, color='black')
    ax.text(x + 0.01, min(y + err, 1), f'{min(y + err, 1):.2f}', ha='left', va='bottom', fontsize=7, color='black')

for x, y, err in zip([i + bar_width for i in index], combined_civilian_detective_win_counts, diff_errors_civ):
    ax.text(x, y - 0.05, f'{y:.2f}', ha='center', va='bottom', color='white', fontweight='bold')
    ax.text(x + 0.01, max(y - err, 0), f'{max(y - err, 0):.2f}', ha='left', va='top', fontsize=7, color='black')
    ax.text(x + 0.01, min(y + err, 1), f'{min(y + err, 1):.2f}', ha='left', va='bottom', fontsize=7, color='black')

# Final formatting
ax.set_xlabel('LLMs')
ax.set_ylabel('Win Rate')
ax.set_title('Civilians Win Rates of LLMs in Same-Model vs Different-Model Games (85% CI)')
ax.set_xticks([i + bar_width / 2 for i in index])
ax.set_xticklabels(llms)
ax.set_ylim(0, 1.1)
ax.legend()
plt.tight_layout()
plt.show()
