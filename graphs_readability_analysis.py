import matplotlib.pyplot as plt
import json
import math

llm_name_map = {
    "openai": "OpenAI o4-mini",
    "gemini": "Gemini 2.5 Flash",
    "grok": "Grok-3 mini beta",
    "claude": "Claude 3.7 Sonnet",
    "deepseek": "DeepSeek Reasoner (R1)"
}

# Load data
with open("understandable_sentiment_readability/compact_readability_analysis_same.json") as f:
    same_data = json.load(f)
with open("understandable_sentiment_readability/compact_readability_analysis_different.json") as f:
    diff_data = json.load(f)

llms = list(same_data.keys())
llms.sort()
bar_width = 0.35
ci_factor = 1.44  # for ~85% confidence interval
offset = 0.1

def plot_reading_ease(data, title):
    x = range(len(llms))
    mafia_means = [data[llm]["as_mafia"]["avg_reading_ease"] for llm in llms]
    civ_means = [data[llm]["as_civilian"]["avg_reading_ease"] for llm in llms]

    mafia_counts = [data[llm]["as_mafia"]["count"] for llm in llms]
    civ_counts = [data[llm]["as_civilian"]["count"] for llm in llms]

    mafia_stds = [data[llm]["as_mafia"]["std_reading_ease"] for llm in llms]
    civ_stds = [data[llm]["as_civilian"]["std_reading_ease"] for llm in llms]

    mafia_errors = [ci_factor * std / math.sqrt(n) if n > 1 else 0 for std, n in zip(mafia_stds, mafia_counts)]
    civ_errors = [ci_factor * std / math.sqrt(n) if n > 1 else 0 for std, n in zip(civ_stds, civ_counts)]

    plt.figure(figsize=(12, 6))
    bars1 = plt.bar(x, mafia_means, width=bar_width, label='Mafia+Don Avg Reading Ease', color='salmon')
    bars2 = plt.bar([i + bar_width for i in x], civ_means, width=bar_width, label='Civilian+Detective Avg Reading Ease', color='skyblue')

    for i, (m, err) in enumerate(zip(mafia_means, mafia_errors)):
        x_pos = i - offset
        lower, upper = max(m - err, 0), m + err
        plt.plot([x_pos, x_pos], [lower, upper], color='black')
        plt.text(i, m - 5, f'{m:.2f}', ha='center', va='bottom', color='black')
        plt.text(x_pos + 0.05, lower, f'{lower:.2f}', ha='right', va='top', fontsize=8)
        plt.text(x_pos + 0.05, upper, f'{upper:.2f}', ha='right', va='bottom', fontsize=8)

    for i, (c, err) in enumerate(zip(civ_means, civ_errors)):
        x_pos = i + bar_width + offset
        lower, upper = max(c - err, 0), c + err
        plt.plot([x_pos, x_pos], [lower, upper], color='black')
        plt.text(i + bar_width, c - 5, f'{c:.2f}', ha='center', va='bottom', color='black')
        plt.text(x_pos + 0.05, lower, f'{lower:.2f}', ha='left', va='top', fontsize=8)
        plt.text(x_pos + 0.05, upper, f'{upper:.2f}', ha='left', va='bottom', fontsize=8)

    # plt.xlabel("LLMs")
    plt.ylabel("Flesch Reading Ease")
    plt.title(title)
    plt.xticks([i + bar_width / 2 for i in x], [llm_name_map[llm] for llm in llms])
    plt.ylim(0, 70)
    plt.legend()
    plt.tight_layout()
    plt.show()

# Plot both settings
plot_reading_ease(same_data, "Flesch Reading Ease by Role (Same-Model Games) with 85% CI")
plot_reading_ease(diff_data, "Flesch Reading Ease by Role (Different-Model Games) with 85% CI")
