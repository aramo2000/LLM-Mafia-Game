import json
from statsmodels.stats.proportion import proportions_ztest
import numpy as np


def roles_win_rate_different(diff_data):
    llms = ['openai', 'deepseek', 'claude', 'gemini', 'grok']

    wins_mafia = [diff_data["role_win_counts"][llm]["mafia"] for llm in llms]
    games_mafia = [diff_data["llm_role_counts"][llm]["mafia"] for llm in llms]

    wins_civilian = [diff_data["role_win_counts"][llm]["civilian"] for llm in llms]
    games_civilian = [diff_data["llm_role_counts"][llm]["civilian"] for llm in llms]

    wins_don = [diff_data["role_win_counts"][llm]["don"] for llm in llms]
    games_don = [diff_data["llm_role_counts"][llm]["don"] for llm in llms]

    wins_detective = [diff_data["role_win_counts"][llm]["detective"] for llm in llms]
    games_detective = [diff_data["llm_role_counts"][llm]["detective"] for llm in llms]

    def pairwise_comparison(wins, games, alternative):
        role_results = {}
        for i in range(len(llms)):
            for j in range(len(llms)):
                if i != j:
                    stat, pval = proportions_ztest([wins[i], wins[j]], [games[i], games[j]], alternative=alternative)
                    role_results[f'{llms[i]} vs {llms[j]}'] = {'z-statistic': stat, 'p-value': pval}
        return role_results

    role_comparison_results_smaller = {}
    role_comparison_results_smaller['Mafia'] = pairwise_comparison(wins_mafia, games_mafia, 'smaller')
    role_comparison_results_smaller['Civilian'] = pairwise_comparison(wins_civilian, games_civilian, 'smaller')
    role_comparison_results_smaller['Don'] = pairwise_comparison(wins_don, games_don, 'smaller')
    role_comparison_results_smaller['Detective'] = pairwise_comparison(wins_detective, games_detective, 'smaller')

    significant_results_smaller = {}
    for role, comparisons in role_comparison_results_smaller.items():
        significant_results_smaller[role] = {k: v for k, v in comparisons.items() if v['p-value'] < 0.15}

    final_results = {
        "smaller_comparisons": significant_results_smaller
    }

    output_path = "hypothesis_testings/roles_win_rate_different_hypothesis_results.json"
    with open(output_path, "w") as f:
        json.dump(final_results, f, indent=4)


def mafia_different_same(diff_data, same_data):
    llms = ['openai', 'deepseek', 'claude', 'gemini', 'grok']

    mafia_don_diff = {
        llm: diff_data["llm_role_combinations_wins"][llm]["mafia_don"] for llm in llms
    }

    mafia_don_same = {
        llm: same_data[llm]["mafia_win"] for llm in llms
    }

    def pairwise_ztest(wins_1, games_1, wins_2, games_2, alternative):
        stat, pval = proportions_ztest([np.array(wins_1), np.array(wins_2)], [games_1, games_2],
                                       alternative=alternative)
        return stat, pval

    same_vs_diff_results = {}
    for llm in llms:
        same_model_win_count = mafia_don_same[llm] * 3
        diff_model_win_count = mafia_don_diff[llm]

        same_model_games = 120 if llm in ['openai', 'gemini', 'grok'] else 60
        diff_model_games = 90

        stat_larger, pval_larger = pairwise_ztest([same_model_win_count], [same_model_games],
                                                  [diff_model_win_count], [diff_model_games],
                                                  alternative='larger')
        stat_smaller, pval_smaller = pairwise_ztest([same_model_win_count], [same_model_games],
                                                    [diff_model_win_count], [diff_model_games],
                                                    alternative='smaller')

        same_vs_diff_results[llm] = {
            'larger': {'z-statistic': float(stat_larger[0]), 'p-value': float(pval_larger[0])},
            'smaller': {'z-statistic': float(stat_smaller[0]), 'p-value': float(pval_smaller[0])}
        }

    diff_model_comparisons = {}
    for i in range(len(llms)):
        for j in range(len(llms)):
            if i != j:
                stat_smaller, pval_smaller = pairwise_ztest([mafia_don_diff[llms[i]]], [90],
                                                            [mafia_don_diff[llms[j]]], [90],
                                                            alternative='smaller')
                diff_model_comparisons[f'{llms[i]} vs {llms[j]}'] = {
                    'smaller': {'z-statistic': float(stat_smaller[0]), 'p-value': float(pval_smaller[0])}
                }

    same_model_comparisons = {}
    for i in range(len(llms)):
        for j in range(len(llms)):
            if i != j:
                stat_smaller, pval_smaller = pairwise_ztest([mafia_don_same[llms[i]] * 3], [120 if llms[i] in ['openai', 'gemini', 'grok'] else 60],
                                                            [mafia_don_same[llms[j]] * 3], [120 if llms[j] in ['openai', 'gemini', 'grok'] else 60],
                                                            alternative='smaller')
                same_model_comparisons[f'{llms[i]} vs {llms[j]}'] = {
                    'smaller': {'z-statistic': float(stat_smaller[0]), 'p-value': float(pval_smaller[0])}
                }

    final_results = {
        'same_vs_diff_comparisons': {
            llm: {key: value for key, value in result.items() if value['p-value'] < 0.15}
            for llm, result in same_vs_diff_results.items()
        },
        'different_model_comparisons': {
            comparison: {key: value for key, value in result.items() if value['p-value'] < 0.15}
            for comparison, result in diff_model_comparisons.items()
        },
        'same_model_comparisons': {
            comparison: {key: value for key, value in result.items() if value['p-value'] < 0.15}
            for comparison, result in same_model_comparisons.items()
        }
    }
    output_path = "hypothesis_testings/mafia_different_same_hypothesis_results.json"
    with open(output_path, "w") as f:
        json.dump(final_results, f, indent=4)


def civilian_different_same(diff_data, same_data):
    llms = ['openai', 'deepseek', 'claude', 'gemini', 'grok']

    civ_det_diff = {
        llm: diff_data["llm_role_combinations_wins"][llm]["civilian_detective"] for llm in llms
    }

    civ_det_same = {
        llm: same_data[llm]["civilians_win"] for llm in llms
    }

    def pairwise_ztest(wins_1, games_1, wins_2, games_2, alternative):
        stat, pval = proportions_ztest([np.array(wins_1), np.array(wins_2)], [games_1, games_2],
                                       alternative=alternative)
        return stat, pval

    same_vs_diff_results = {}
    for llm in llms:
        same_model_win_count = civ_det_same[llm] * 7
        diff_model_win_count = civ_det_diff[llm]

        same_model_games = 280 if llm in ['openai', 'gemini', 'grok'] else 140
        diff_model_games = 210

        stat_larger, pval_larger = pairwise_ztest([same_model_win_count], [same_model_games],
                                                  [diff_model_win_count], [diff_model_games],
                                                  alternative='larger')
        stat_smaller, pval_smaller = pairwise_ztest([same_model_win_count], [same_model_games],
                                                    [diff_model_win_count], [diff_model_games],
                                                    alternative='smaller')

        same_vs_diff_results[llm] = {
            'larger': {'z-statistic': float(stat_larger[0]), 'p-value': float(pval_larger[0])},
            'smaller': {'z-statistic': float(stat_smaller[0]), 'p-value': float(pval_smaller[0])}
        }

    diff_model_comparisons = {}
    for i in range(len(llms)):
        for j in range(len(llms)):
            if i != j:
                stat_smaller, pval_smaller = pairwise_ztest([civ_det_diff[llms[i]]], [210],
                                                            [civ_det_diff[llms[j]]], [210],
                                                            alternative='smaller')
                diff_model_comparisons[f'{llms[i]} vs {llms[j]}'] = {
                    'smaller': {'z-statistic': float(stat_smaller[0]), 'p-value': float(pval_smaller[0])}
                }

    same_model_comparisons = {}
    for i in range(len(llms)):
        for j in range(len(llms)):
            if i != j:
                stat_smaller, pval_smaller = pairwise_ztest([civ_det_same[llms[i]] * 7], [280 if llms[i] in ['openai', 'gemini', 'grok'] else 140],
                                                            [civ_det_same[llms[j]] * 7], [280 if llms[j] in ['openai', 'gemini', 'grok'] else 140],
                                                            alternative='smaller')
                same_model_comparisons[f'{llms[i]} vs {llms[j]}'] = {
                    'smaller': {'z-statistic': float(stat_smaller[0]), 'p-value': float(pval_smaller[0])}
                }

    final_results = {
        'same_vs_diff_comparisons': {
            llm: {key: value for key, value in result.items() if value['p-value'] < 0.15}
            for llm, result in same_vs_diff_results.items()
        },
        'different_model_comparisons': {
            comparison: {key: value for key, value in result.items() if value['p-value'] < 0.15}
            for comparison, result in diff_model_comparisons.items()
        },
        'same_model_comparisons': {
            comparison: {key: value for key, value in result.items() if value['p-value'] < 0.15}
            for comparison, result in same_model_comparisons.items()
        }
    }
    output_path = "hypothesis_testings/civilian_different_same_hypothesis_results.json"
    with open(output_path, "w") as f:
        json.dump(final_results, f, indent=4)


path = "analysis_data/"
with open(path+"win_rates_different.json") as f:
    diff_data = json.load(f)
with open(path+"win_rates_same.json") as f:
    same_data = json.load(f)

roles_win_rate_different(diff_data)
mafia_different_same(diff_data, same_data)
civilian_different_same(diff_data, same_data)