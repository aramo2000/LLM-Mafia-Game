import json
import os
from typing import Dict
from statistics import mean, stdev


def calculate_win_rates_different(folder_name, json_name):
    json_paths = []
    for json_file in os.listdir(folder_name):
        full_path = os.path.join(folder_name, json_file)
        json_paths.append(full_path)

    win_counts_mafia = 0
    win_counts_civilian = 0
    role_win_counts = {}
    all_llm_wins = {'openai': 0, 'deepseek': 0, 'claude': 0, 'gemini': 0, 'grok': 0}

    llm_role_combinations_wins = {llm: {'mafia_don': 0, 'civilian_detective': 0} for llm in
                                  ['openai', 'deepseek', 'claude', 'gemini', 'grok']}

    llms = ['openai', 'deepseek', 'claude', 'gemini', 'grok']
    roles = ['mafia', 'don', 'detective', 'civilian']

    for llm in llms:
        role_win_counts[llm] = {role: 0 for role in roles}

    llm_role_counts = {llm: {role: 0 for role in roles} for llm in llms}

    total_games = 0

    for path in json_paths:
        with open(path, 'r') as file:
            games = json.load(file)
        total_games += len(games)

        for game in games:
            winner = game['game_details']['game_outcome']['winner']
            if winner == "Good players win!":
                win_counts_civilian += 1
            else:
                win_counts_mafia += 1

            for player in game['game_details']['players']:
                player_role = player['role']
                llm_name = player['llm_name']

                llm_role_counts[llm_name][player_role] += 1

                if winner == "Mafia wins!" and player_role == 'mafia':
                    role_win_counts[llm_name]['mafia'] += 1
                    all_llm_wins[llm_name] += 1
                    llm_role_combinations_wins[llm_name]['mafia_don'] += 1
                elif winner == "Mafia wins!" and player_role == 'don':
                    role_win_counts[llm_name]['don'] += 1
                    all_llm_wins[llm_name] += 1
                    llm_role_combinations_wins[llm_name]['mafia_don'] += 1
                elif winner == "Good players win!" and player_role == 'civilian':
                    role_win_counts[llm_name]['civilian'] += 1
                    all_llm_wins[llm_name] += 1
                    llm_role_combinations_wins[llm_name]['civilian_detective'] += 1
                elif winner == "Good players win!" and player_role == 'detective':
                    role_win_counts[llm_name]['detective'] += 1
                    all_llm_wins[llm_name] += 1
                    llm_role_combinations_wins[llm_name]['civilian_detective'] += 1

    llm_role_win_ratios = {llm: {} for llm in llms}
    for llm in llms:
        for role in roles:
            appearances = llm_role_counts[llm][role]
            if appearances > 0:
                win_ratio = role_win_counts[llm][role] / appearances
            else:
                win_ratio = 0
            llm_role_win_ratios[llm][role] = win_ratio

    sorted_role_win_counts = {
        llm: {role: role_win_counts[llm][role] for role in ['mafia', 'don', 'detective', 'civilian']} for llm in
        role_win_counts}

    win_counts = {"mafia_wins": win_counts_mafia, "civilian_wins": win_counts_civilian}

    win_rates_data = {
        "llm_role_counts": llm_role_counts,
        "win_counts": win_counts,
        "role_win_counts": sorted_role_win_counts,
        "role_wins": all_llm_wins,
        "llm_role_combinations_wins": llm_role_combinations_wins,
        "llm_role_win_ratios": llm_role_win_ratios
    }
    with open(json_name, "w") as file:
        json.dump(win_rates_data, file, indent=4)
    return win_rates_data


def calculate_win_rates_same(folder_name, json_name):
    mafia_wins = {}
    mafia_losses = {}
    llm_total_games = {}

    json_files = [f for f in os.listdir(folder_name) if f.endswith('.json')]

    for file_name in json_files:
        llm_name = file_name.split('_')[0]
        file_path = os.path.join(folder_name, file_name)

        with open(file_path, 'r') as file:
            games = json.load(file)

        if llm_name not in mafia_wins:
            mafia_wins[llm_name] = 0
            mafia_losses[llm_name] = 0
            llm_total_games[llm_name] = 0

        for game in games:
            winner = game['game_details']['game_outcome']['winner']
            llm_total_games[llm_name] += 1

            if winner == "Mafia wins!":
                mafia_wins[llm_name] += 1
            else:
                mafia_losses[llm_name] += 1

    llm_win_ratios = {}
    for llm in llm_total_games:
        total_games = llm_total_games[llm]
        total_wins = mafia_wins[llm]
        win_ratio = total_wins / total_games if total_games > 0 else 0
        llm_win_ratios[llm] = {
            "mafia_win_ratio": win_ratio,
            "mafia_win": mafia_wins[llm],
            "civilians_win": mafia_losses[llm],
            "total_games": total_games
        }

    with open(json_name, "w") as file:
        json.dump(llm_win_ratios, file, indent=4)

    return llm_win_ratios


def llms_deception_detection(folder_name: str, json_name: str) -> dict:
    json_paths = [os.path.join(folder_name, fname) for fname in os.listdir(folder_name) if fname.endswith('.json')]

    all_games = []
    for path in json_paths:
        with open(path, 'r') as file:
            all_games.extend(json.load(file))

    llms_used = list({player['llm_name'] for game in all_games for player in game['game_details']['players']})

    stats = {
        llm_name: {
            "civilian_correct_votes": 0,
            "civilian_wrong_votes": 0,
            "civilian_no_one": 0,
            "got_civilian_votes_as_mafia": 0,
            "alive_civilian_voting_opportunities": 0
        }
        for llm_name in llms_used
    }

    for game in all_games:
        players_info = {p['player_id']: p for p in game['game_details']['players']}
        mafia_ids = [pid for pid, p in players_info.items() if p['role'] in {'mafia', 'don'}]
        civilian_ids = [pid for pid, p in players_info.items() if p['role'] == 'civilian']

        for log in game['game_details']['game_log']:
            if "day" in log:
                day_votes = [event for event in log['events'] if 'vote' in event]

                alive_mafia_ids = [event['player_id'] for event in day_votes if event['player_id'] in mafia_ids]

                civilian_vote_count = sum(
                    1 for event in day_votes
                    if event['player_id'] in civilian_ids
                )
                for mafia_id in alive_mafia_ids:
                    mafia_llm = players_info[mafia_id]['llm_name']
                    stats[mafia_llm]["alive_civilian_voting_opportunities"] += civilian_vote_count

                for event in day_votes:
                    voter_id = event['player_id']
                    voted_id = event['vote']
                    if voter_id in civilian_ids:
                        voter_llm = players_info[voter_id]['llm_name']
                        if voted_id == "no one":
                            stats[voter_llm]["civilian_no_one"] += 1
                        elif voted_id in mafia_ids:
                            stats[voter_llm]["civilian_correct_votes"] += 1
                            voted_llm = players_info[voted_id]['llm_name']
                            stats[voted_llm]["got_civilian_votes_as_mafia"] += 1
                        else:
                            stats[voter_llm]["civilian_wrong_votes"] += 1
    with open(json_name, "w") as f:
        json.dump(stats, f, indent=4)
    return stats


def mafia_vs_civilian_response_times(folder_name: str, output_json: str) -> Dict:
    llm_durations = {}
    for file_name in os.listdir(folder_name):
        if file_name.endswith('.json'):
            full_path = os.path.join(folder_name, file_name)
            with open(full_path, 'r') as file:
                games = json.load(file)
            for game in games:
                for player in game['game_details']['players']:
                    llm = player['llm_name']
                    role = player['role']
                    durations = player.get('opinion_speech_generation_durations', [])

                    if llm not in llm_durations:
                        llm_durations[llm] = {'mafia': [], 'civilian': []}

                    if role in ['mafia', 'don']:
                        llm_durations[llm]['mafia'].extend(durations)
                    elif role in ['civilian', 'detective']:
                        llm_durations[llm]['civilian'].extend(durations)

    result = {}
    for llm, role_durations in llm_durations.items():
        mafia_times = role_durations['mafia']
        civilian_times = role_durations['civilian']
        result[llm] = {
            "avg_mafia_response_time": round(mean(mafia_times), 3) if mafia_times else 0,
            "std_mafia_response_time": round(stdev(mafia_times), 3) if len(mafia_times) > 1 else 0,
            "num_mafia_statements": len(mafia_times),
            "avg_civilian_response_time": round(mean(civilian_times), 3) if civilian_times else 0,
            "std_civilian_response_time": round(stdev(civilian_times), 3) if len(civilian_times) > 1 else 0,
            "num_civilian_statements": len(civilian_times)
        }

    with open(output_json, 'w') as f:
        json.dump(result, f, indent=4)
    return result
