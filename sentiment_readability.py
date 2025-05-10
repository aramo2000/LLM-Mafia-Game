from typing import List, Dict
from transformers import pipeline
import textstat
import config
import os
import json

def sentiment_analyzer(text: str) -> list:
    sa = pipeline(task='sentiment-analysis', model=config.HUGGINGFACE_MODEL)
    return sa(text)


def readability_metrics(text: str) -> list:
    reading_ease = textstat.flesch_reading_ease(text)
    grade_level = textstat.flesch_kincaid_grade(text)
    return [reading_ease, grade_level]


def sentiment_analysis_dict(folder_name: str, json_name: str) -> dict:
    json_paths = [os.path.join(folder_name, fname) for fname in os.listdir(folder_name) if fname.endswith('.json')]

    all_games = []
    for path in json_paths:
        with open(path, 'r') as file:
            all_games.extend(json.load(file))

    llms_used = list({player['llm_name'] for game in all_games for player in game['game_details']['players']})
    results = {llm_name: {"as_civilian": [], "as_mafia": []} for llm_name in llms_used}

    for game in all_games:
        for game_event in game['game_details']['game_log']:
            if "events" in game_event:  # Only day logs
                for event in game_event["events"]:
                    if "statement" in event:
                        player_id = event["player_id"]
                        statement = event["statement"]

                        for player_info in game['game_details']['players']:
                            if player_info['player_id'] == player_id:
                                role = player_info['role']
                                llm_name = player_info['llm_name']
                                sentiment = sentiment_analyzer(statement)
                                if role in {"mafia", "don"}:
                                    results[llm_name]["as_mafia"].append(sentiment)
                                elif role in {"civilian", "detective"}:
                                    results[llm_name]["as_civilian"].append(sentiment)
                                break
        with open(json_name, "w") as f:
            json.dump(results, f, indent=4)
    return results


def compact_sent_analysis_results(sentiment_data: dict, json_name: str) -> dict:
    compact_data = {}
    for llm_name, roles_data in sentiment_data.items():
        compact_data[llm_name] = {}
        for role, sentiment_list in roles_data.items():
            positive_scores = []
            neutral_scores = []
            negative_scores = []
            positive_count = 0
            neutral_count = 0
            negative_count = 0

            for sentiments in sentiment_list:
                for sentiment in sentiments:
                    label = sentiment['label'].lower()
                    score = sentiment['score']

                    if label == 'positive':
                        positive_scores.append(score)
                        positive_count += 1
                    elif label == 'negative':
                        negative_scores.append(score)
                        negative_count += 1
                    elif label == 'neutral':
                        neutral_scores.append(score)
                        neutral_count += 1

            avg_positive_score = sum(positive_scores) / len(positive_scores) if positive_scores else 0
            avg_negative_score = sum(negative_scores) / len(negative_scores) if negative_scores else 0
            avg_neutral_score = sum(neutral_scores) / len(neutral_scores) if neutral_scores else 0

            compact_data[llm_name][role] = {
                "positive_count": positive_count,
                "neutral_count": neutral_count,
                "negative_count": negative_count,
                "positive_avg_score": avg_positive_score,
                "neutral_avg_score": avg_neutral_score,
                "negative_avg_score": avg_negative_score
            }
    with open(json_name, "w") as f:
        json.dump(compact_data, f, indent=4)
    return compact_data


def readability_analysis_dict(folder_name: str, json_name: str) -> dict:
    json_paths = [os.path.join(folder_name, fname) for fname in os.listdir(folder_name) if fname.endswith('.json')]

    all_games = []
    for path in json_paths:
        with open(path, 'r') as file:
            all_games.extend(json.load(file))

    llms_used = list({player['llm_name'] for game in all_games for player in game['game_details']['players']})
    results = {llm_name: {"as_civilian": [], "as_mafia": []} for llm_name in llms_used}

    for game in all_games:
        for game_event in game['game_details']['game_log']:
            if "events" in game_event:  # Only consider day logs with statements
                for event in game_event["events"]:
                    if "statement" in event:
                        player_id = event["player_id"]
                        statement = event["statement"]

                        for player_info in game['game_details']['players']:
                            if player_info['player_id'] == player_id:
                                role = player_info['role']
                                llm_name = player_info['llm_name']
                                readability = readability_metrics(statement)

                                if role in {"mafia", "don"}:
                                    results[llm_name]["as_mafia"].append(readability)
                                elif role in {"civilian", "detective"}:
                                    results[llm_name]["as_civilian"].append(readability)
                                break
        with open(json_name, "w") as f:
            json.dump(results, f, indent=4)
    return results


def compact_readability_analysis_results(readability_data: dict, json_name: str) -> dict:
    compact_data = {}
    for llm_name, roles_data in readability_data.items():
        compact_data[llm_name] = {}
        for role, metrics in roles_data.items():
            count = len(metrics)
            avg_reading_ease = sum([metric[0] for metric in metrics]) / count if count > 0 else 0
            avg_grade_level = sum([metric[1] for metric in metrics]) / count if count > 0 else 0
            compact_data[llm_name][role] = {
                "count": count,
                "avg_reading_ease": avg_reading_ease,
                "avg_grade_level": avg_grade_level
            }
    with open(json_name, "w") as f:
        json.dump(compact_data, f, indent=4)
    return compact_data
