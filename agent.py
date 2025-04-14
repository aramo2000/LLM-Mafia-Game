import random
from typing import List
import config
import prompts_constants
from token_utils import count_openai_input_tokens, count_openai_output_tokens
import json

class Agent:
    def __init__(self, llm_name: str, player_name: str, player_role: str, mafia_player_indices: List[int]):
        self.llm_name = llm_name
        self.player_name = player_name
        self.role = player_role
        self.input_tokens_used = 0
        self.output_tokens_used = 0
        if self.role  in ["mafia", "don"]:
            self.mafia_players ="These are the mafia players in the game including you " + str([f"player_{i}" for i in mafia_player_indices])
        else:
            self.mafia_players = []

        self.investigations = ""


    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        if self.llm_name == "openai":
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            input_tokens = count_openai_input_tokens(messages, model=config.OPENAI_MODEL)
            llm_response = config.OPENAI_CLIENT.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=messages,
                temperature=0.3,
            )
            output_text = llm_response.choices[0].message.content.strip()
            output_tokens = count_openai_output_tokens(output_text, model=config.OPENAI_MODEL)

            self.input_tokens_used += input_tokens
            self.output_tokens_used += output_tokens
            return output_text
        else:
            raise NotImplementedError(f"LLM {self.llm_name} not supported yet.")

    def _build_system_prompt(self):
        rules = prompts_constants.SYSTEM_PROMPTS["rules"]
        role_prompt = prompts_constants.SYSTEM_PROMPTS.get(self.role, "")
        return f"{rules}\n\n{role_prompt}\n\nYou are {self.player_name}. Your role is {self.role}. {self.mafia_players}"

    def speak_opinion(self, game_log: str) -> str:
        system_prompt = self._build_system_prompt()

        # Provide more specific context in the user prompt based on the player's role and past behavior
        user_prompt = (
            f"Here is what happened in the game so far:\n{game_log}\n\n"
            f"As {self.player_name} (role: {self.role}), please express your thoughts and suspicions about who could be Mafia. "
            "Consider your role and any relevant interactions you've had. Your reason should be logical and persuasive.\n"
            "Use your role’s perspective to guide your response. If you're Mafia, consider how to blend in and mislead others. "
            "If you're a Detective, focus on gathering evidence. If you're a Civilian, be vigilant for inconsistencies.\n"
            "Return only your statement.\n"
        )

        # Get the LLM response
        return self._call_llm(system_prompt, user_prompt)

    def vote_day(self, game_log: str, nominees: list[int]) -> tuple:
        nominee_names = [f"player_{i}" for i in nominees]
        system_prompt = self._build_system_prompt()
        user_prompt = (
            f"Here is what happened in the game so far:\n{game_log}\n\n"
            f"The following players are nominated for elimination: {', '.join(nominee_names)}.\n"
            "Choose who you want to eliminate or vote for no one.\n"
            "First provide the player you want to vote for (or 'no one'). Then provide your reason on the next line.\n"
            "Format: player_# or 'no one'\n\"Reason\"\n"
        )
        response = self._call_llm(system_prompt, user_prompt)

        try:
            # Split the response into vote and reason
            lines = response.split("\n", 1)
            vote_choice = lines[0].strip()  # The first part is the vote
            reason = lines[1].strip() if len(lines) > 1 else "No reason provided"  # The second part is the reason

            # Handle 'no one' vote
            if vote_choice.lower() == "no one":
                return -1, reason  # -1 indicates 'no one' as the vote

            # Check if the vote is in the correct player format
            if vote_choice.lower().startswith("player_"):
                try:
                    voted_player = int(vote_choice.replace("player_", "").strip())  # Extract the player number
                    return voted_player, reason
                except ValueError:
                    # If there's an invalid player format, fallback to a default vote
                    print(f"[vote_day error] Invalid player format: {vote_choice}")
                    return nominees[0], reason
            else:
                # If the vote is not in the correct format, fallback to the first nominee
                print(f"[vote_day error] Invalid vote format: {vote_choice}")
                return nominees[0], reason

        except Exception as e:
            print(f"[vote_day error] {e}")
            return nominees[0], "Fallback vote due to parsing error."

    def investigate(self, game_log: str, alive_players: list[int]) -> int:
        possible_targets = [p for p in alive_players if f"player_{p}" != self.player_name]
        system_prompt = self._build_system_prompt()
        user_prompt = (
            f"Here is what happened in the game so far:\n{game_log}\n\n"
            "You are the Detective. Choose one player to investigate tonight.\n"
            f"The investigation you did so far: \n{self.investigations}"
            f"Alive players: {', '.join(f'player_{i}' for i in possible_targets)}\n"
            "Return only their name in this format: player_#"
        )
        response = self._call_llm(system_prompt, user_prompt)
        try:
            return int(response.replace("player_", "").strip())
        except:
            return random.choice(possible_targets)

    def decide_kill(self, game_log: str, candidates: list[int]) -> int:
        possible_targets = [f"player_{i}" for i in candidates]
        system_prompt = self._build_system_prompt()
        user_prompt = (
            f"Here is what happened in the game so far:\n{game_log}\n\n"
            f"As a Mafia/Don, you must choose who to kill tonight.\n"
            f"Candidates: {', '.join(possible_targets)}\n"
            "Return only one player name in this format: player_#"
        )
        response = self._call_llm(system_prompt, user_prompt)
        try:
            return int(response.replace("player_", "").strip())
        except:
            return candidates[0]
