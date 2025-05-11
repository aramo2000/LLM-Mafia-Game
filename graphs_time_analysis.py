import matplotlib.pyplot as plt
import json
import math

path = "analysis_data/"
with open(path+"time_analysis_same.json") as f:
    same_time_data = json.load(f)
with open(path+"time_analysis_different.json") as f:
    diff_time_data = json.load(f)

ci_factor = 1.44  # 85% confidence interval
bar_width = 0.35
offset = 0.1

# Re-plotting with increased y-axis limit for better scaling
def plot_response_times_with_ylim(data, title):
    ylim_max = 110
    llms = list(data.keys())
    avg_mafia = [data[llm]["avg_mafia_response_time"] for llm in llms]
    avg_civilian = [data[llm]["avg_civilian_response_time"] for llm in llms]
    mafia_counts = [data[llm]["num_mafia_statements"] for llm in llms]
    civilian_counts = [data[llm]["num_civilian_statements"] for llm in llms]

    ci_factor = 1.44
    mafia_errors = [
        ci_factor * (std := math.sqrt(1)) / math.sqrt(n) if n > 0 else 0
        for n in mafia_counts
    ]
    civilian_errors = [
        ci_factor * (std := math.sqrt(1)) / math.sqrt(n) if n > 0 else 0
        for n in civilian_counts
    ]

    x = range(len(llms))
    plt.figure(figsize=(12, 6))
    bars1 = plt.bar(x, avg_mafia, width=bar_width, label='Mafia Avg Time', color='red')
    bars2 = plt.bar([i + bar_width for i in x], avg_civilian, width=bar_width, label='Civilian Avg Time', color='blue')

    for i, (m, err) in enumerate(zip(avg_mafia, mafia_errors)):
        x_pos = i - offset
        lower, upper = max(m - err, 0), m + err
        plt.plot([x_pos, x_pos], [lower, upper], color='black')
        plt.text(i, m - 5, f'{m:.2f}', ha='center', va='bottom', color='white', fontweight='bold')
        plt.text(x_pos + 0.05, lower, f'{lower:.2f}', ha='right', va='top', fontsize=7)
        plt.text(x_pos + 0.05, upper, f'{upper:.2f}', ha='right', va='bottom', fontsize=7)

    for i, (c, err) in enumerate(zip(avg_civilian, civilian_errors)):
        x_pos = i + bar_width + offset
        lower, upper = max(c - err, 0), c + err
        plt.plot([x_pos, x_pos], [lower, upper], color='black')
        plt.text(i + bar_width, c - 5, f'{c:.2f}', ha='center', va='bottom', color='white', fontweight='bold')
        plt.text(x_pos + 0.05, lower, f'{lower:.2f}', ha='left', va='top', fontsize=7)
        plt.text(x_pos + 0.05, upper, f'{upper:.2f}', ha='left', va='bottom', fontsize=7)

    plt.xlabel('LLMs')
    plt.ylabel('Average Response Time (s)')
    plt.title(title)
    plt.ylim(0, ylim_max)
    plt.xticks([i + bar_width / 2 for i in x], llms)
    plt.legend()
    plt.tight_layout()
    plt.show()


# Call with higher y-limit
plot_response_times_with_ylim(same_time_data, "Response Times by Role (Same-Model Games) with 85% CI")
plot_response_times_with_ylim(diff_time_data, "Response Times by Role (Different-Model Games) with 85% CI")
