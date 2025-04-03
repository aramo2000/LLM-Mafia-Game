import random
from agent2 import Agent
import numpy as np


class MafiaGame:
    def __init__(self, llm_name: str):
        self.num_players = 10
        self.players = []
        self.roles = ["civilian"] * 6 + ["detective"] + ["mafia"] * 2 + ["don"]
        random.shuffle(self.roles)
        self.llm_name = llm_name
        self.night_count = 0
        self.day_count = 0
        self.game_log = "**Mafia Game Starts**\n"
        self.opinion_log = ""
        self.votes_log = ""
        self.winner_log = ""
        self.alive = [True] * self.num_players

        mafia_indices = [i for i, role in  enumerate(self.roles) if role in ["mafia", "don"]]
        for i, role in enumerate(self.roles):
            if role in ["mafia", "don"]:
                self.players.append(Agent(llm_name=llm_name, player_name=f"player_{i}", player_role=role, mafia_player_indices=mafia_indices))
            else:
                self.players.append(Agent(llm_name=llm_name, player_name=f"player_{i}", player_role=role, mafia_players=[]))

    def get_alive_players(self):
        return [i for i, alive in enumerate(self.alive) if alive]

    def night_phase(self):
        self.night_count += 1
        alive_players = self.get_alive_players()
        alive_mafia_indices = [i for i in alive_players if self.roles[i] in ["mafia", "don"]]
        alive_civilian_indices = [i for i in alive_players if self.roles[i] not in ["mafia", "don"]]

        # Mafia choose a target
        mafia_votes = []
        for i in alive_mafia_indices:
            vote = self.players[i].decide_kill(self.game_log, alive_players)
            mafia_votes.append(vote)
        final_target = max(set(mafia_votes), key=mafia_votes.count) #todo change this or handle the case where there is no max

        if "don" in [self.roles[i] for i in alive_mafia_indices]:
            don_index = next(i for i in alive_mafia_indices if self.roles[i] == "don")
            final_target = self.players[don_index].decide_kill(self.game_log, mafia_votes)

        # Detective investigates
        detective_index = next((i for i in alive_players if self.roles[i] == "detective"), None)
        investigation_result = None
        if detective_index is not None:
            investigate_target = self.players[detective_index].investigate(self.game_log, alive_players)
            target, is_mafia = (investigate_target, self.roles[investigate_target] in ["mafia", "don"])
            self.players[detective_index].investigations += f"\nplayer_{target} - Mafia: {is_mafia}"

        # Update state
        self.alive[final_target] = False
        self.game_log += f"\nNight {self.night_count}: Mafia killed player_{final_target}"

    def day_phase(self):
        self.day_count += 1
        alive_players = self.get_alive_players()

        self.game_log += f"\n\nDay {self.day_count} Begins"

        # Each player gives a statement
        for i in alive_players:
            statement = self.players[i].speak_opinion(self.game_log)
            self.opinion_log += f"\nplayer_{i} says: {statement}"
            self.game_log += f"\nplayer_{i} says: {statement}"

        # Voting
        nominees = random.sample(alive_players, k=min(3, len(alive_players))) #todo agents should put the votes
        vote_counts = {n: 0 for n in nominees}
        for i in alive_players:
            vote, reason = self.players[i].vote_day(self.game_log, nominees)
            vote_counts[vote] += 1
            vote_statement = f"player_{i} voted to eliminate player_{vote} - Reason: {reason}"
            self.votes_log += f"\n{vote_statement}"
            self.game_log += f"\n{vote_statement}"

        # Eliminate player with most votes
        eliminated = max(vote_counts, key=vote_counts.get)
        self.alive[eliminated] = False
        self.game_log += f"\nDay: player_{eliminated} was voted out by the town"

    def check_win_condition(self):
        alive_roles = [self.roles[i] for i in self.get_alive_players()]
        mafia_count = sum(1 for r in alive_roles if r in ["mafia", "don"])
        good_count = len(alive_roles) - mafia_count

        if mafia_count == 0:
            self.winner_log = "Good players win!"
            self.game_log += f"\n\n{self.winner_log}"
            return True
        elif mafia_count >= good_count:
            self.winner_log = "Mafia wins!"
            self.game_log += f"\n\n{self.winner_log}"
            return True
        return False

    def run(self):
        while not self.check_win_condition():
            self.night_phase()
            if self.check_win_condition():
                break
            self.day_phase()
        print("\n--- Game Over ---")
        print(self.game_log)
        print("\nAll Player Statements:")
        print(self.opinion_log)
        print("\nAll Votes:")
        print(self.votes_log)
        print("\nWinner:", self.winner_log)
