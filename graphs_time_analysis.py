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

path = "analysis_data/"
with open(path+"time_analysis_same.json") as f:
    same_time_data = json.load(f)
with open(path+"time_analysis_different.json") as f:
    diff_time_data = json.load(f)

bar_width = 0.35

def plot_response_times_no_error_bars(data, title):
    ylim_max = 110
    llms = list(data.keys())
    llms.sort()
    avg_mafia = [data[llm]["avg_mafia_response_time"] for llm in llms]
    avg_civilian = [data[llm]["avg_civilian_response_time"] for llm in llms]

    x = range(len(llms))
    plt.figure(figsize=(12, 6))
    bars1 = plt.bar(x, avg_mafia, width=bar_width, label='Mafia+Don Avg Time', color='red')
    bars2 = plt.bar([i + bar_width for i in x], avg_civilian, width=bar_width, label='Civilian+Detective Avg Time', color='blue')

    # Only add numeric labels to the bars
    for i, m in enumerate(avg_mafia):
        plt.text(i, m - 5, f'{m:.2f}', ha='center', va='bottom', color='white', fontweight='bold')

    for i, c in enumerate(avg_civilian):
        plt.text(i + bar_width, c - 5, f'{c:.2f}', ha='center', va='bottom', color='white', fontweight='bold')

    plt.ylabel('Average Response Time (s)')
    plt.title(title)
    plt.ylim(0, ylim_max)
    plt.xticks([i + bar_width / 2 for i in x], [llm_name_map[llm] for llm in llms])
    plt.legend()
    plt.tight_layout()
    plt.show()


plot_response_times_no_error_bars(same_time_data, "Response Times by Role (Same-Model Games)")
plot_response_times_no_error_bars(diff_time_data, "Response Times by Role (Different-Model Games)")