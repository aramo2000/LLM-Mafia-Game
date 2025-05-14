import json
from statsmodels.stats.proportion import proportions_ztest
import numpy as np


def mafia_detection_ratio(diff_data, same_data):
    llms = ['openai', 'deepseek', 'claude', 'gemini', 'grok']

    mafia_votes_diff = {llm: diff_data[llm]["got_civilian_votes_as_mafia"] for llm in llms}
    opportunities_diff = {llm: diff_data[llm]["alive_civilian_voting_opportunities"] for llm in llms}

    mafia_votes_same = {llm: same_data[llm]["got_civilian_votes_as_mafia"] for llm in llms}
    opportunities_same = {llm: same_data[llm]["alive_civilian_voting_opportunities"] for llm in llms}

    def pairwise_ztest(wins_1, games_1, wins_2, games_2, alternative):
        stat, pval = proportions_ztest([np.array(wins_1), np.array(wins_2)], [games_1, games_2], alternative=alternative)
        return stat, pval

    same_vs_diff_results = {}
    for llm in llms:
        same_model_votes = mafia_votes_same[llm]
        diff_model_votes = mafia_votes_diff[llm]

        same_model_opportunities = opportunities_same[llm]
        diff_model_opportunities = opportunities_diff[llm]

        stat_larger, pval_larger = pairwise_ztest([same_model_votes], [same_model_opportunities],
                                                  [diff_model_votes], [diff_model_opportunities],
                                                  alternative='larger')
        stat_smaller, pval_smaller = pairwise_ztest([same_model_votes], [same_model_opportunities],
                                                    [diff_model_votes], [diff_model_opportunities],
                                                    alternative='smaller')

        same_vs_diff_results[llm] = {
            'larger': {'z-statistic': float(stat_larger[0]), 'p-value': float(pval_larger[0])},
            'smaller': {'z-statistic': float(stat_smaller[0]), 'p-value': float(pval_smaller[0])}
        }

    diff_model_comparisons = {}
    for i in range(len(llms)):
        for j in range(len(llms)):
            if i != j:
                stat_smaller, pval_smaller = pairwise_ztest([mafia_votes_diff[llms[i]]], [opportunities_diff[llms[i]]],
                                                            [mafia_votes_diff[llms[j]]], [opportunities_diff[llms[j]]],
                                                            alternative='smaller')
                diff_model_comparisons[f'{llms[i]} vs {llms[j]}'] = {
                    'smaller': {'z-statistic': float(stat_smaller[0]), 'p-value': float(pval_smaller[0])}
                }

    same_model_comparisons = {}
    for i in range(len(llms)):
        for j in range(len(llms)):
            if i != j:
                stat_smaller, pval_smaller = pairwise_ztest([mafia_votes_same[llms[i]]], [opportunities_same[llms[i]]],
                                                            [mafia_votes_same[llms[j]]], [opportunities_same[llms[j]]],
                                                            alternative='smaller')
                same_model_comparisons[f'{llms[i]} vs {llms[j]}'] = {
                    'smaller': {'z-statistic': float(stat_smaller[0]), 'p-value': float(pval_smaller[0])}
                }

    final_results = {
        'same_vs_diff_comparisons': {
            llm: {key: value for key, value in result.items() if value['p-value'] < 0.05}
            for llm, result in same_vs_diff_results.items()
        },
        'different_model_comparisons': {
            comparison: {key: value for key, value in result.items() if value['p-value'] < 0.05}
            for comparison, result in diff_model_comparisons.items()
        },
        'same_model_comparisons': {
            comparison: {key: value for key, value in result.items() if value['p-value'] < 0.05}
            for comparison, result in same_model_comparisons.items()
        }
    }
    output_path = "hypothesis_testings/mafia_detection_ratio_hypothesis_results.json"
    with open(output_path, "w") as f:
        json.dump(final_results, f, indent=4)
    return final_results


def civilian_correct_votes_ratio(diff_data, same_data):
    # LLMs
    llms = ['openai', 'deepseek', 'claude', 'gemini', 'grok']

    correct_votes_diff = {
        llm: diff_data[llm]["civilian_correct_votes"] for llm in llms
    }
    no_one_votes_diff = {
        llm: diff_data[llm]["civilian_no_one"] for llm in llms
    }
    wrong_votes_diff = {
        llm: diff_data[llm]["civilian_wrong_votes"] for llm in llms
    }

    correct_votes_same = {
        llm: same_data[llm]["civilian_correct_votes"] for llm in llms
    }
    no_one_votes_same = {
        llm: diff_data[llm]["civilian_no_one"] for llm in llms
    }
    wrong_votes_same = {
        llm: same_data[llm]["civilian_wrong_votes"] for llm in llms
    }

    def pairwise_ztest(wins_1, games_1, wins_2, games_2, alternative):
        stat, pval = proportions_ztest([np.array(wins_1), np.array(wins_2)], [games_1, games_2],
                                       alternative=alternative)

        return stat, pval

    same_vs_diff_results = {}
    for llm in llms:
        same_model_correct_votes = correct_votes_same[llm]
        diff_model_correct_votes = correct_votes_diff[llm]

        same_model_no_one_votes = no_one_votes_same[llm]
        diff_model_no_one_votes = no_one_votes_diff[llm]

        same_model_wrong_votes = wrong_votes_same[llm]
        diff_model_wrong_votes = wrong_votes_diff[llm]

        same_total_games = same_model_correct_votes + same_model_no_one_votes + same_model_wrong_votes
        diff_total_games = diff_model_correct_votes + diff_model_no_one_votes + diff_model_wrong_votes

        stat_larger, pval_larger = pairwise_ztest([same_model_correct_votes], [same_total_games],
                                                  [diff_model_correct_votes], [diff_total_games],
                                                  alternative='larger')
        stat_smaller, pval_smaller = pairwise_ztest([same_model_correct_votes], [same_total_games],
                                                    [diff_model_correct_votes], [diff_total_games],
                                                    alternative='smaller')

        same_vs_diff_results[llm] = {
            'larger': {'z-statistic': float(stat_larger[0]), 'p-value': float(pval_larger[0])},
            'smaller': {'z-statistic': float(stat_smaller[0]), 'p-value': float(pval_smaller[0])}
        }

    diff_model_comparisons = {}
    for i in range(len(llms)):
        for j in range(len(llms)):
            if i != j:
                diff_model_correct_votes_1 = correct_votes_diff[llms[i]]
                diff_model_no_one_votes_1 = no_one_votes_diff[llms[i]]
                diff_model_wrong_votes_1 = wrong_votes_diff[llms[i]]

                diff_model_correct_votes_2 = correct_votes_diff[llms[j]]
                diff_model_no_one_votes_2 = no_one_votes_diff[llms[j]]
                diff_model_wrong_votes_2 = wrong_votes_diff[llms[j]]

                total_games_1 = diff_model_correct_votes_1 + diff_model_no_one_votes_1 + diff_model_wrong_votes_1
                total_games_2 = diff_model_correct_votes_2 + diff_model_no_one_votes_2 + diff_model_wrong_votes_2

                stat_smaller, pval_smaller = pairwise_ztest([diff_model_correct_votes_1], [total_games_1],
                                                            [diff_model_correct_votes_2], [total_games_2],
                                                            alternative='smaller')
                diff_model_comparisons[f'{llms[i]} vs {llms[j]}'] = {
                    'smaller': {'z-statistic': float(stat_smaller[0]), 'p-value': float(pval_smaller[0])}
                }

    same_model_comparisons = {}
    for i in range(len(llms)):
        for j in range(len(llms)):
            if i != j:
                same_model_correct_votes_1 = correct_votes_same[llms[i]]
                same_model_no_one_votes_1 = no_one_votes_same[llms[i]]
                same_model_wrong_votes_1 = wrong_votes_same[llms[i]]
                same_model_correct_votes_2 = correct_votes_same[llms[j]]
                same_model_no_one_votes_2 = no_one_votes_same[llms[j]]
                same_model_wrong_votes_2 = wrong_votes_same[llms[j]]

                total_games_1 = same_model_correct_votes_1 + same_model_no_one_votes_1 + same_model_wrong_votes_1
                total_games_2 = same_model_correct_votes_2 + same_model_no_one_votes_2 + same_model_wrong_votes_2

                stat_smaller, pval_smaller = pairwise_ztest([same_model_correct_votes_1], [total_games_1],
                                                            [same_model_correct_votes_2], [total_games_2],
                                                            alternative='smaller')
                same_model_comparisons[f'{llms[i]} vs {llms[j]}'] = {
                    'smaller': {'z-statistic': float(stat_smaller[0]), 'p-value': float(pval_smaller[0])}
                }

    final_results = {
        'same_vs_diff_comparisons': {
            llm: {key: value for key, value in result.items() if value['p-value'] < 0.05}
            for llm, result in same_vs_diff_results.items()
        },
        'different_model_comparisons': {
            comparison: {key: value for key, value in result.items() if value['p-value'] < 0.05}
            for comparison, result in diff_model_comparisons.items()
        },
        'same_model_comparisons': {
            comparison: {key: value for key, value in result.items() if value['p-value'] < 0.05}
            for comparison, result in same_model_comparisons.items()
        }
    }

    output_path = "hypothesis_testings/civilian_correct_votes_ratio_hypothesis_results.json"
    with open(output_path, "w") as f:
        json.dump(final_results, f, indent=4)


def civilian_wrong_votes_ratio(diff_data, same_data):
    # LLMs
    llms = ['openai', 'deepseek', 'claude', 'gemini', 'grok']

    correct_votes_diff = {
        llm: diff_data[llm]["civilian_correct_votes"] for llm in llms
    }
    no_one_votes_diff = {
        llm: diff_data[llm]["civilian_no_one"] for llm in llms
    }
    wrong_votes_diff = {
        llm: diff_data[llm]["civilian_wrong_votes"] for llm in llms
    }

    correct_votes_same = {
        llm: same_data[llm]["civilian_correct_votes"] for llm in llms
    }
    no_one_votes_same = {
        llm: diff_data[llm]["civilian_no_one"] for llm in llms
    }
    wrong_votes_same = {
        llm: same_data[llm]["civilian_wrong_votes"] for llm in llms
    }

    def pairwise_ztest(wins_1, games_1, wins_2, games_2, alternative):
        # Perform the z-test for proportions
        stat, pval = proportions_ztest([np.array(wins_1), np.array(wins_2)], [games_1, games_2],
                                       alternative=alternative)

        return stat, pval

    same_vs_diff_results = {}
    for llm in llms:
        same_model_correct_votes = correct_votes_same[llm]
        diff_model_correct_votes = correct_votes_diff[llm]

        same_model_no_one_votes = no_one_votes_same[llm]
        diff_model_no_one_votes = no_one_votes_diff[llm]

        same_model_wrong_votes = wrong_votes_same[llm]
        diff_model_wrong_votes = wrong_votes_diff[llm]

        same_total_games = same_model_correct_votes + same_model_no_one_votes + same_model_wrong_votes
        diff_total_games = diff_model_correct_votes + diff_model_no_one_votes + diff_model_wrong_votes

        stat_larger, pval_larger = pairwise_ztest([same_model_wrong_votes], [same_total_games],
                                                  [diff_model_wrong_votes], [diff_total_games],
                                                  alternative='larger')
        stat_smaller, pval_smaller = pairwise_ztest([same_model_wrong_votes], [same_total_games],
                                                    [diff_model_wrong_votes], [diff_total_games],
                                                    alternative='smaller')

        same_vs_diff_results[llm] = {
            'larger': {'z-statistic': float(stat_larger[0]), 'p-value': float(pval_larger[0])},
            'smaller': {'z-statistic': float(stat_smaller[0]), 'p-value': float(pval_smaller[0])}
        }

    diff_model_comparisons = {}
    for i in range(len(llms)):
        for j in range(len(llms)):
            if i != j:
                diff_model_correct_votes_1 = correct_votes_diff[llms[i]]
                diff_model_no_one_votes_1 = no_one_votes_diff[llms[i]]
                diff_model_wrong_votes_1 = wrong_votes_diff[llms[i]]

                diff_model_correct_votes_2 = correct_votes_diff[llms[j]]
                diff_model_no_one_votes_2 = no_one_votes_diff[llms[j]]
                diff_model_wrong_votes_2 = wrong_votes_diff[llms[j]]

                total_games_1 = diff_model_correct_votes_1 + diff_model_no_one_votes_1 + diff_model_wrong_votes_1
                total_games_2 = diff_model_correct_votes_2 + diff_model_no_one_votes_2 + diff_model_wrong_votes_2

                stat_smaller, pval_smaller = pairwise_ztest([diff_model_wrong_votes_1], [total_games_1],
                                                            [diff_model_wrong_votes_2], [total_games_2],
                                                            alternative='smaller')
                diff_model_comparisons[f'{llms[i]} vs {llms[j]}'] = {
                    'smaller': {'z-statistic': float(stat_smaller[0]), 'p-value': float(pval_smaller[0])}
                }

    same_model_comparisons = {}
    for i in range(len(llms)):
        for j in range(len(llms)):
            if i != j:
                same_model_correct_votes_1 = correct_votes_same[llms[i]]
                same_model_no_one_votes_1 = no_one_votes_same[llms[i]]
                same_model_wrong_votes_1 = wrong_votes_same[llms[i]]
                same_model_correct_votes_2 = correct_votes_same[llms[j]]
                same_model_no_one_votes_2 = no_one_votes_same[llms[j]]
                same_model_wrong_votes_2 = wrong_votes_same[llms[j]]

                total_games_1 = same_model_correct_votes_1 + same_model_no_one_votes_1 + same_model_wrong_votes_1
                total_games_2 = same_model_correct_votes_2 + same_model_no_one_votes_2 + same_model_wrong_votes_2

                stat_smaller, pval_smaller = pairwise_ztest([same_model_wrong_votes_1], [total_games_1],
                                                            [same_model_wrong_votes_2], [total_games_2],
                                                            alternative='smaller')
                same_model_comparisons[f'{llms[i]} vs {llms[j]}'] = {
                    'smaller': {'z-statistic': float(stat_smaller[0]), 'p-value': float(pval_smaller[0])}
                }

    final_results = {
        'same_vs_diff_comparisons': {
            llm: {key: value for key, value in result.items() if value['p-value'] < 0.05}
            for llm, result in same_vs_diff_results.items()
        },
        'different_model_comparisons': {
            comparison: {key: value for key, value in result.items() if value['p-value'] < 0.05}
            for comparison, result in diff_model_comparisons.items()
        },
        'same_model_comparisons': {
            comparison: {key: value for key, value in result.items() if value['p-value'] < 0.05}
            for comparison, result in same_model_comparisons.items()
        }
    }
    output_path = "hypothesis_testings/civilian_wrong_votes_ratio_hypothesis_results.json"
    with open(output_path, "w") as f:
        json.dump(final_results, f, indent=4)


path = "analysis_data/"
with open(path+"deception_detection_different.json") as f:
    diff_data = json.load(f)
with open(path+"deception_detection_same.json") as f:
    same_data = json.load(f)

mafia_detection_ratio(diff_data, same_data)
civilian_correct_votes_ratio(diff_data, same_data)
civilian_wrong_votes_ratio(diff_data, same_data)
