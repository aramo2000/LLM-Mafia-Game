import matplotlib.pyplot as plt
import json
import math

path = "analysis_data/"
with open(path+"deception_detection_different.json") as f:
    diff_data = json.load(f)
with open(path+"deception_detection_same.json") as f:
    same_data = json.load(f)
llms = list(diff_data.keys())


# 1. Stacked Bar Chart: Civilian Votes (Correct, Wrong, No One)
def annotate_stack(bars, values, bottoms):
    for bar, val, bottom in zip(bars, values, bottoms):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, bottom + height / 2,
                 f'{val * 100:.1f}%', ha='center', va='center', fontsize=9, color='white')


def get_vote_ratios_full(data):
    correct_ratios = []
    no_one_ratios = []
    wrong_ratios = []
    for llm in llms:
        correct = data[llm]["civilian_correct_votes"]
        wrong = data[llm]["civilian_wrong_votes"]
        no_one = data[llm]["civilian_no_one"]
        total = correct + wrong + no_one
        correct_ratio = correct / total if total > 0 else 0
        no_one_ratio = no_one / total if total > 0 else 0
        wrong_ratio = wrong / total if total > 0 else 0
        correct_ratios.append(correct_ratio)
        no_one_ratios.append(no_one_ratio)
        wrong_ratios.append(wrong_ratio)
    return correct_ratios, no_one_ratios, wrong_ratios


correct_same, no_one_same, wrong_same = get_vote_ratios_full(same_data)
correct_diff, no_one_diff, wrong_diff = get_vote_ratios_full(diff_data)
x = range(len(llms))
bar_width = 0.35
plt.figure(figsize=(12, 6))
bars1 = plt.bar(x, correct_same, width=bar_width, label='Correct (Same)', color='green')
bars2 = plt.bar(x, no_one_same, width=bar_width, bottom=correct_same, label='No One (Same)', color='gray')
bars3 = plt.bar(x, wrong_same, width=bar_width,
                bottom=[c + n for c, n in zip(correct_same, no_one_same)],
                label='Wrong (Same)', color='salmon')

bars4 = plt.bar([i + bar_width for i in x], correct_diff, width=bar_width, label='Correct (Different)', color='blue')
bars5 = plt.bar([i + bar_width for i in x], no_one_diff, width=bar_width,
                bottom=correct_diff, label='No One (Different)', color='lightgray')
bars6 = plt.bar([i + bar_width for i in x], wrong_diff, width=bar_width,
                bottom=[c + n for c, n in zip(correct_diff, no_one_diff)],
                label='Wrong (Different)', color='indianred')

annotate_stack(bars1, correct_same, [0]*len(llms))
annotate_stack(bars2, no_one_same, correct_same)
annotate_stack(bars3, wrong_same, [c + n for c, n in zip(correct_same, no_one_same)])
annotate_stack(bars4, correct_diff, [0]*len(llms))
annotate_stack(bars5, no_one_diff, correct_diff)
annotate_stack(bars6, wrong_diff, [c + n for c, n in zip(correct_diff, no_one_diff)])

plt.xlabel('LLMs')
plt.ylabel('Vote Ratio')
plt.title('Civilian Voting: Correct, No One, and Wrong Votes (Same vs Different Games)')
plt.xticks([i + bar_width / 2 for i in x], llms)
plt.ylim(0, 1.1)
plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
plt.tight_layout()
plt.show()



# 2. Bar Chart for Mafia Detection (Deception)
same_opportunities = {
    "openai": 1435,
    "gemini": 1336,
    "grok": 1339,
    "claude": 713,
    "deepseek": 653
}
diff_opportunities = {
    "openai": 923,
    "gemini": 1005,
    "grok": 991,
    "claude": 1025,
    "deepseek": 987
}

detection_ratio_same = [
    same_data[llm]["got_civilian_votes_as_mafia"] / same_data[llm]["alive_civilian_voting_opportunities"]
    if same_data[llm]["alive_civilian_voting_opportunities"] > 0 else 0 for llm in llms
]
detection_ratio_diff = [
    diff_data[llm]["got_civilian_votes_as_mafia"] / diff_data[llm]["alive_civilian_voting_opportunities"]
    if diff_data[llm]["alive_civilian_voting_opportunities"] > 0 else 0 for llm in llms
]

# Confidence interval factor for 85%
ci_factor = 1.44

# Calculate standard error bars
same_errors_detect = [
    ci_factor * math.sqrt(p * (1 - p) / same_opportunities[llm]) if same_opportunities[llm] > 0 else 0
    for llm, p in zip(llms, detection_ratio_same)
]
diff_errors_detect = [
    ci_factor * math.sqrt(p * (1 - p) / diff_opportunities[llm]) if diff_opportunities[llm] > 0 else 0
    for llm, p in zip(llms, detection_ratio_diff)
]

# Plotting setup
bar_width = 0.35
x = range(len(llms))
offset = 0.12  # left offset for error bars

plt.figure(figsize=(12, 6))
bars1 = plt.bar(x, detection_ratio_same, width=bar_width, label='Same-Model Games', color='darkred')
bars2 = plt.bar([i + bar_width for i in x], detection_ratio_diff, width=bar_width, label='Different-Model Games', color='orange')

# Annotate values and manual error bars
for i, (val, err) in enumerate(zip(detection_ratio_same, same_errors_detect)):
    lower = max(val - err, 0)
    upper = min(val + err, 1)
    x_pos = i + offset
    plt.plot([x_pos, x_pos], [lower, upper], color='black')
    plt.text(i, val - 0.05, f'{val:.3f}', ha='center', va='bottom', color='white', fontweight='bold')
    plt.text(x_pos + 0.01, lower, f'{lower:.2f}', ha='left', va='top', fontsize=7)
    plt.text(x_pos + 0.01, upper, f'{upper:.2f}', ha='left', va='bottom', fontsize=7)

for i, (val, err) in enumerate(zip(detection_ratio_diff, diff_errors_detect)):
    lower = max(val - err, 0)
    upper = min(val + err, 1)
    x_pos = i + bar_width + offset
    plt.plot([x_pos, x_pos], [lower, upper], color='black')
    plt.text(i + bar_width, val - 0.05, f'{val:.2f}', ha='center', va='bottom', color='white', fontweight='bold')
    plt.text(x_pos + 0.01, lower, f'{lower:.2f}', ha='left', va='top', fontsize=7)
    plt.text(x_pos + 0.01, upper, f'{upper:.2f}', ha='left', va='bottom', fontsize=7)

# Final chart settings
plt.xlabel('LLMs')
plt.ylabel('Detection Ratio')
plt.title('Mafia Detection Ratio (Votes Received / Opportunities) with 85% CI')
plt.xticks([i + bar_width / 2 for i in x], llms)
plt.ylim(0, 0.5)
plt.legend()
plt.tight_layout()
plt.show()
