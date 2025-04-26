import json
from typing import List, Dict
from transformers import pipeline
import textstat
import config
from pprint import pprint

def llms_vote_stats(game_records: List[Dict]) -> dict :
    llms_used = list({player['llm_name'] for game in game_records for player in game['game_details']['players']})

    stats = {llm_name:{"civilian_correct_votes":0, "got_civilian_votes_as_mafia":0, "civilian_no_one":0} for llm_name in llms_used}

    for game in game_records:
        players_info = {player["player_id"]:player for player in game["game_details"]["players"]}
        mafia_names = [player["player_id"] for player in game["game_details"]["players"] if player["role"] in {"mafia","don"}]
        for log in game["game_details"]["game_log"]:
            if "day" in log:
                for event in log["events"]:
                    if "vote" in event:
                        voter_name = event["player_id"]
                        voted_on_name = event["vote"]

                        if voted_on_name in mafia_names and players_info[voter_name]["role"] == "civilian" and event["vote"] != "no one":
                            stats[players_info[voter_name]["llm_name"]]["civilian_correct_votes"] +=1
                            stats[players_info[voted_on_name]["llm_name"]]["got_civilian_votes_as_mafia"] +=1

                        if players_info[voter_name]["role"] == "civilian" and event["vote"] == "no one":
                            stats[players_info[voter_name]["llm_name"]]["civilian_no_one"] += 1

    return stats


def sentiment_analyzer(text: str) -> list :
    sa = pipeline(task ='sentiment-analysis', model=config.HUGGINGFACE_MODEL)
    return sa(text)

def readability_metrics(text: str) -> list :
    reading_ease = textstat.flesch_reading_ease(text)
    grade_level = textstat.flesch_kincaid_grade(text)
    return [reading_ease, grade_level]


def sentiment_analysis_dict(game_records: List[Dict]) -> dict :
    llms_used = list({player['llm_name'] for game in game_records for player in game['game_details']['players']})
    results = {llm_name:{"as_civilian":[], "as_mafia":[]} for llm_name in llms_used}
    for game in game_records:
        for game_event in game['game_details']['game_log']:
            if "events" in game_event:  # Only check for Day events that contain player statements
                for event in game_event["events"]:
                    if "statement" in event:
                        player_id = event["player_id"]
                        statement = event["statement"]
                        for player_info in game['game_details']['players']:
                            if player_info['player_id'] == player_id:
                                role = player_info['role']
                                llm_name = player_info['llm_name']
                                sentiment = sentiment_analyzer(statement)
                                if role == "mafia" or role == "don":
                                    results[llm_name]["as_mafia"].append(sentiment)
                                elif role == "civilian" or role == "detective":
                                    results[llm_name]["as_civilian"].append(sentiment)
        return results

def compact_sent_analysis_results(sentiment_data: dict) -> dict:
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
    return compact_data

def readability_analysis_dict(game_records: List[Dict]) -> dict :
    llms_used = list({player['llm_name'] for game in game_records for player in game['game_details']['players']})

    results = {llm_name:{"as_civilian":[], "as_mafia":[]} for llm_name in llms_used}
    for game in game_records:
        for game_event in game['game_details']['game_log']:
            if "events" in game_event:  # Only check for Day events that contain player statements
                for event in game_event["events"]:
                    if "statement" in event:
                        player_id = event["player_id"]
                        statement = event["statement"]
                        for player_info in game['game_details']['players']:
                            if player_info['player_id'] == player_id:
                                role = player_info['role']
                                llm_name = player_info['llm_name']
                                readability = readability_metrics(statement)
                                if role == "mafia" or role == "don":
                                    results[llm_name]["as_mafia"].append(readability)
                                elif role == "civilian" or role == "detective":
                                    results[llm_name]["as_civilian"].append(readability)
        return results

def compact_readability_analysis_results(readability_data: dict) -> dict:
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
    return compact_data



with open("game_results.json", "r") as file:
    games_total_record = json.load(file)

# pprint(llms_vote_stats(games_total_record))
# pprint(sentiment_analysis_dict(games_total_record))
# pprint(compact_sent_analysis_results(sentiment_analysis_dict(games_total_record)))
# pprint(readability_analysis_dict(games_total_record))
pprint(compact_readability_analysis_results(readability_analysis_dict(games_total_record)))