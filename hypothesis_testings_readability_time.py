import json
from scipy.stats import ttest_ind_from_stats


def reading_ease(diff_data, same_data):
    llms = ['openai', 'deepseek', 'claude', 'gemini', 'grok']

    def run_welch_tests(data):
        results = {}
        for llm in llms:
            mafia_mean = data[llm]['as_mafia']['avg_reading_ease']
            mafia_std = data[llm]['as_mafia']['std_reading_ease']
            mafia_n = data[llm]['as_mafia']['count']
            civ_mean = data[llm]['as_civilian']['avg_reading_ease']
            civ_std = data[llm]['as_civilian']['std_reading_ease']
            civ_n = data[llm]['as_civilian']['count']

            if mafia_n < 2 or civ_n < 2:
                continue

            t_stat = 0
            p_val_two_sided = 1.0
            if mafia_std > 0 and civ_std > 0:
                t_stat, p_val_two_sided = ttest_ind_from_stats(
                    mean1=mafia_mean, std1=mafia_std, nobs1=mafia_n,
                    mean2=civ_mean, std2=civ_std, nobs2=civ_n,
                    equal_var=False
                )
            if p_val_two_sided < 1.0:
                if mafia_mean > civ_mean:
                    p_smaller = p_val_two_sided / 2
                    p_larger = 1 - p_smaller
                else:
                    p_larger = p_val_two_sided / 2
                    p_smaller = 1 - p_larger
                results[llm] = {
                    't-statistic': round(t_stat, 4),
                    'p-value (mafia > civilian)': round(p_larger, 4),
                    'p-value (civilian > mafia)': round(p_smaller, 4)
                }
        return results

    diff_results = run_welch_tests(diff_data)
    same_results = run_welch_tests(same_data)

    output = {
        "different_model_readability_tests": diff_results,
        "same_model_readability_tests": same_results
    }

    filtered_output = {
        "different_model_readability_tests": {
            llm: result for llm, result in diff_results.items()
            if result["p-value (mafia > civilian)"] < 0.01 or result["p-value (civilian > mafia)"] < 0.01
        },
        "same_model_readability_tests": {
            llm: result for llm, result in same_results.items()
            if result["p-value (mafia > civilian)"] < 0.01 or result["p-value (civilian > mafia)"] < 0.01
        }
    }
    with open("hypothesis_testings/reading_ease_hypothesis_results.json", "w") as f:
        json.dump(filtered_output, f, indent=4)


def opinion_time(diff_data, same_data):
    llms = ['openai', 'deepseek', 'claude', 'gemini', 'grok']

    def run_welch_tests(data):
        results = {}
        for llm in llms:
            mafia_mean = data[llm]['avg_mafia_response_time']
            mafia_std = data[llm]['std_mafia_response_time']
            mafia_n = data[llm]['num_mafia_statements']
            civ_mean = data[llm]['avg_civilian_response_time']
            civ_std = data[llm]['std_civilian_response_time']
            civ_n = data[llm]['num_civilian_statements']

            t_stat, p_val_two_sided = ttest_ind_from_stats(
                mean1=mafia_mean, std1=mafia_std, nobs1=mafia_n,
                mean2=civ_mean, std2=civ_std, nobs2=civ_n,
                equal_var=False
            )

            if mafia_mean > civ_mean:
                p_smaller = p_val_two_sided / 2
                p_larger = 1 - p_smaller
            else:
                p_larger = p_val_two_sided / 2
                p_smaller = 1 - p_larger

            results[llm] = {
                't-statistic': round(t_stat, 4),
                'p-value (mafia > civilian)': round(p_larger, 4),
                'p-value (civilian > mafia)': round(p_smaller, 4),
            }
        return results

    diff_results = run_welch_tests(diff_data)
    same_results = run_welch_tests(same_data)

    output = {
        "different_model_time_tests": diff_results,
        "same_model_time_tests": same_results
    }

    filtered_output = {
        "different_model_time_tests": {
            llm: result for llm, result in diff_results.items()
            if result["p-value (mafia > civilian)"] < 0.01 or result["p-value (civilian > mafia)"] < 0.01
        },
        "same_model_time_tests": {
            llm: result for llm, result in same_results.items()
            if result["p-value (mafia > civilian)"] < 0.01 or result["p-value (civilian > mafia)"] < 0.01
        }
    }
    with open("hypothesis_testings/opinion_time_hypothesis_results.json", "w") as f:
        json.dump(filtered_output, f, indent=4)


with open("understandable_sentiment_readability/compact_readability_analysis_different.json") as f:
    diff_data = json.load(f)
with open("understandable_sentiment_readability/compact_readability_analysis_same.json") as f:
    same_data = json.load(f)
reading_ease(diff_data, same_data)

with open("analysis_data/time_analysis_different.json") as f:
    diff_data = json.load(f)
with open("analysis_data/time_analysis_same.json") as f:
    same_data = json.load(f)
opinion_time(diff_data, same_data)
