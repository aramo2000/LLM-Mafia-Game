import json
import os
from pprint import pprint


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
    # Initialize dictionaries to store wins, losses, and total games per LLM
    mafia_wins = {}
    mafia_losses = {}
    llm_total_games = {}

    # Loop through the files in the folder
    json_files = [f for f in os.listdir(folder_name) if f.endswith('.json')]

    # Process each JSON file
    for file_name in json_files:
        llm_name = file_name.split('_')[0]  # Get the LLM's name (before the first '_')
        file_path = os.path.join(folder_name, file_name)

        with open(file_path, 'r') as file:
            games = json.load(file)

        # Initialize LLM stats if not already present
        if llm_name not in mafia_wins:
            mafia_wins[llm_name] = 0
            mafia_losses[llm_name] = 0
            llm_total_games[llm_name] = 0

        # Process each game
        for game in games:
            winner = game['game_details']['game_outcome']['winner']
            llm_total_games[llm_name] += 1  # Count this game for the LLM

            # Check if the LLM won or lost
            if winner == "Mafia wins!":
                mafia_wins[llm_name] += 1
            else:
                mafia_losses[llm_name] += 1

    # Calculate win ratios for each LLM
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

    # Save the result to a JSON file
    with open(json_name, "w") as file:
        json.dump(llm_win_ratios, file, indent=4)

    return llm_win_ratios
