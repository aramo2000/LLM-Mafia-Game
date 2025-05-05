import re
import time
from typing import List
import config
import prompts_constants
from utils import retry


class Agent:
    def __init__(self, llm_name: str, player_name: str, player_role: str, mafia_player_indices: List[int], don_index: int = None):
        self.llm_name = llm_name  # Store LLM name
        self.player_name = player_name
        self.role = player_role
        self.status = "alive"  # Default status is alive
        self.input_tokens_used = 0
        self.output_tokens_used = 0
        self.thinking_tokens_used = 0
        self.votes = []
        self.statements = []
        self.investigations = []
        self.mafia_thinking = []  # To store the internal reasons for the mafia kill decisions
        self.detective_thinking = []  # To store detective reasoning
        self.mafia_kill_targets = []
        self.don_guesses = []
        self.opinion_speech_generation_durations = []

        if self.role in ["mafia", "don"]:
            self.mafia_players = [f"player_{i}" for i in mafia_player_indices]
            self.don = f"player_{don_index}" if don_index is not None else "Unknown"
        else:
            self.mafia_players = []
            self.don = None


    def get_player_info(self):
        # Return a dictionary with the player's information
        return {
            "player_id": self.player_name,
            "role": self.role,
            "status": self.status,
            "llm_name": self.llm_name  # This ensures the LLM name is tracked
        }

    @retry(retries=4, delay=10)
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        if self.llm_name == "openai":
            llm_response = config.OPENAI_CLIENT.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
            )
            output_text = llm_response.choices[0].message.content.strip()
            self.input_tokens_used += llm_response.usage.prompt_tokens
            self.output_tokens_used += (
                        llm_response.usage.completion_tokens - llm_response.usage.completion_tokens_details.reasoning_tokens)
            self.thinking_tokens_used += llm_response.usage.completion_tokens_details.reasoning_tokens

        elif self.llm_name == "gemini":
            prompt = system_prompt + "\n\n" + user_prompt
            llm_response = config.GEMINI_CLIENT.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt,
            )
            output_text = llm_response.text.strip() if hasattr(llm_response, "text") else ""
            self.input_tokens_used += llm_response.usage_metadata.prompt_token_count
            self.output_tokens_used += llm_response.usage_metadata.candidates_token_count
            self.thinking_tokens_used += llm_response.usage_metadata.thoughts_token_count

        elif self.llm_name == "deepseek":
            llm_response = config.DEEPSEEK_CLIENT.chat.completions.create(
                model=config.DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
            )
            output_text = llm_response.choices[0].message.content.strip()
            self.input_tokens_used += llm_response.usage.prompt_tokens
            self.output_tokens_used += (
                        llm_response.usage.completion_tokens - llm_response.usage.completion_tokens_details.reasoning_tokens)
            self.thinking_tokens_used += llm_response.usage.completion_tokens_details.reasoning_tokens

        elif self.llm_name == "claude":
            llm_response = config.CLAUDE_CLIENT.messages.create(
                model=config.CLAUDE_MODEL,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=6000,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 5000
                }
            )
            output_text = llm_response.content[1].text.strip() if hasattr(llm_response, "content") else ""
            self.input_tokens_used += llm_response.usage.input_tokens
            self.output_tokens_used += llm_response.usage.output_tokens

        elif self.llm_name == "grok":
            llm_response = config.GROK_CLIENT.chat.completions.create(
                model=config.GROK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            output_text = llm_response.choices[0].message.content.strip()
            self.input_tokens_used += llm_response.usage.prompt_tokens
            self.output_tokens_used += llm_response.usage.completion_tokens
            self.thinking_tokens_used += llm_response.usage.completion_tokens_details.reasoning_tokens

        return output_text


    def _build_system_prompt(self):
        rules = prompts_constants.SYSTEM_PROMPTS["rules"]
        role_prompt = prompts_constants.SYSTEM_PROMPTS.get(self.role, "")

        mafia_prompt = ""
        if self.role in ["mafia", "don"]:
            mafia_list = ", ".join(self.mafia_players)
            mafia_prompt += f"\nYou are part of the Mafia. The Don is {self.don}. The other mafia players are: {mafia_list}."

        return f"{rules}\n\n{role_prompt}\n\nYou are {self.player_name}. Your role is {self.role}.{mafia_prompt}"

    def speak_opinion(self, game_log: str) -> str:
        system_prompt = self._build_system_prompt()
        investigation_history = ""
        if self.role == "detective" and self.investigations:
            investigation_history = "Here is your investigation history:\n" + "\n".join(self.investigations) + "\n"
        if self.role in ["mafia","don"] and self.don_guesses:
            investigation_history = "Here the insight from don's investigation until now:\n " + "\n".join(self.don_guesses) + "\n"

        user_prompt = (
            f"Here is what happened in the game so far:\n{game_log}\n\n"
            f"As {self.player_name} (role: {self.role}), please express your thoughts and suspicions about who could be Mafia. "
            f"{investigation_history}"
            "Use the information from the game of how a player died to assess how many Mafia could still be alive.\n"
            "Note: Mafia are only eliminated through DAY voting, not during the night.\n"
            "You must reason about whether it's safe to vote or not. If Mafia reach parity (equal number as civilians), they win immediately.\n"
            "Consider your role and any relevant interactions you've had. Your reason should be logical and persuasive.\n"
            "Return only your statement. The statement should be brief and not exceed 3-4 sentences in length to keep it concise.\n"
        )
        start_time = time.time()
        statement = self._call_llm(system_prompt, user_prompt)
        end_time = time.time()
        self.opinion_speech_generation_durations.append(end_time - start_time)
        self.statements.append({
            "player_id": self.player_name,
            "statement": statement
        })
        return statement

    def vote_day(self, game_log: str, nominees: list[int], past_votes: str = "") -> tuple:
        nominee_names = [f"player_{i}" for i in nominees]
        system_prompt = self._build_system_prompt()
        investigation_history = ""
        if self.role == "detective" and self.investigations:
            investigation_history = "Here is your investigation history:\n" + "\n".join(self.investigations) + "\n"
        if self.role in ["mafia","don"] and self.don_guesses:
            investigation_history = "Here the insight from don's investigation until now:\n " + "\n".join(self.don_guesses) + "\n"
        user_prompt = (
            f"Here is what happened in the game so far:\n{game_log}\n\n"
            f"The following players are nominated for elimination: {', '.join(nominee_names)}.\n"
            f"Past votes and reasons:\n{past_votes}\n\n"
            "Choose who you want to eliminate or vote for no one.\n"
            f"{investigation_history}"
            "Use the information from the game of how a player died to assess how many Mafia could still be alive.\n"
            "Note: Mafia are only eliminated through DAY voting, not during the night.\n"
            "You must reason about whether it's safe to vote or not. If Mafia reach parity (equal number as civilians), they win immediately.\n"
        )

        user_prompt += """
        \n\nNote: Return your vote for the player you want to eliminate or 'no one' in case you don't want to vote out anyone, and then provide your internal reason.
        Format your response as follows:
        - First, provide the player ID you want to vote for in the format: 'player_#', or 'no one' in case you don't want to vote for anyone.
        - After that, provide a brief internal reason for why you are choosing this player, in 2-3 sentences.
        
        Example response:
        player_#
        short vote reasoning...
        
        YOU MUST RESPOND WITH THE EXAMPLE FORMAT, IF YOUR RESPONSE IS NOT ACCORDING TO THE EXAMPLE THEN YOU WILL FAIL YOUR TASK"""

        response = self._call_llm(system_prompt, user_prompt)

        lines = response.split("\n", 1)
        vote_choice = int(re.search(r'\d+', response).group()) if re.search(r'\d+', response) else None
        if vote_choice:
            vote_choice = f"player_{vote_choice}"
        else:
            vote_choice = "no one"
        reason = lines[1].strip() if len(lines) > 1 else "No reason provided"

        self.votes.append({
            "player_id": self.player_name,
            "vote": vote_choice,
            "reason": reason
        })

        if vote_choice.lower() == "no one":
            return -1, reason

        voted_player = int(vote_choice.replace("player_", "").strip())
        return voted_player, reason


    def investigate(self, game_log: str, alive_players: list[int], current_night: int = 1) -> int:
        possible_targets = [p for p in alive_players if f"player_{p}" != self.player_name]
        system_prompt = self._build_system_prompt()
        user_prompt = (
            f"Here is what happened in the game so far:\n{game_log}\n\n"
            "You are the Detective. Choose one player to investigate tonight.\n"
            f"The investigation you did so far: \n{self.investigations}"
            f"Alive players: {', '.join(f'player_{i}' for i in possible_targets)}\n"
            f"You are {self.player_name}, do not investigate yourself as you know you are the detective."
        )

        # Add reasoning for investigation decision
        if current_night > 1:
            user_prompt += """\n\nNote: Return your guess and provide your internal reason.
            Format your response as follows:
            - First, provide the player ID you suspect is the Detective in the format: 'player_#'
            - Then, on the next line, provide your internal reason for suspecting them in 2–3 sentences.
            
            Example response:
            player_#
            short vote reasoning...
            
            YOU MUST RESPOND WITH THE EXAMPLE FORMAT, IF YOUR RESPONSE IS NOT ACCORDING TO THE EXAMPLE THEN YOU WILL FAIL YOUR TASK"""
        else:
            user_prompt += """Example response:
            player_#
            
            YOU MUST RESPOND WITH THE EXAMPLE FORMAT, IF YOUR RESPONSE IS NOT ACCORDING TO THE EXAMPLE THEN YOU WILL FAIL YOUR TASK"""

        response = self._call_llm(system_prompt, user_prompt)

        # Split the response into the investigated player and the internal reason
        lines = response.split("\n", 1)
        investigated_player = int(re.search(r'\d+', response).group()) if re.search(r'\d+', response) else None
        internal_reason = lines[1].strip() if len(lines) > 1 else "No reason provided"

        # Store the internal reason for analysis (not visible to others)
        if current_night > 1:  # Only store reasoning starting from Day 2
            self.detective_thinking.append({
                "player_id": self.player_name,
                "investigated_player": investigated_player,
                "internal_reason": internal_reason
            })

        return investigated_player


    def don_guess_detective(self, game_log: str, alive_players: list[int], current_night: int = 1) -> tuple:
        possible_targets = [p for p in alive_players if
                            f"player_{p}" != self.player_name and f"player_{p}" not in self.mafia_players]
        system_prompt = self._build_system_prompt()
        user_prompt = (
            f"Here is what happened in the game so far:\n{game_log}\n\n"
            "You are the **Mafia Don**. Tonight, you may try to identify who the Detective is.\n"
            f"The following players are alive and not part of the Mafia: {', '.join(f'player_{i}' for i in possible_targets)}\n"
            "Your task is to guess which one might be the Detective, if you haven't guessed already."
        )
        if current_night > 1 and self.don_guesses:
            history ="\n".join(self.don_guesses) + "\n"
            user_prompt += f"\n\nHere is your past guessing history:{history}"

        if current_night > 1:
            user_prompt += """\n\nNote: Return your guess and provide your internal reason.
            Format your response as follows:
            - First, provide the player ID you suspect is the Detective in the format: 'player_#'
            - Then, on the next line, provide your internal reason for suspecting them in 2–3 sentences.
            
            Example response:
            player_#
            choice reasoning...
            
            YOU MUST RESPOND WITH THE EXAMPLE FORMAT."""
        else:
            user_prompt +="""\n\nNote: This is the first night. Just return your guess.
            
            Example response:
            player_#
            
            YOU MUST RESPOND WITH THE EXAMPLE FORMAT."""

        response = self._call_llm(system_prompt, user_prompt)
        lines = response.strip().split("\n", 1)
        guessed_player = int(re.search(r'\d+', response).group()) if re.search(r'\d+', response) else None
        reason = lines[1].strip() if len(lines) > 1 else "No reason provided"
        return guessed_player, reason


    def decide_kill(self, game_log: str, candidates: list[int], mafia_votes: list[tuple] = None) -> int:
        possible_targets = [f"player_{i}" for i in candidates]
        system_prompt = self._build_system_prompt()
        user_prompt = f"""Here is what happened in the game so far:\n{game_log}
        
        
        As part of the mafia, you must choose who to kill tonight.
        Candidates: {', '.join(possible_targets)}
        """

        if self.don_guesses:
            history = "\n".join(self.don_guesses) + "\n"
            user_prompt += f"""[Don's Suspicion Info]
            Here is the don's past investigations for the detective:
            {history}
            Use this information to help you decide whom to eliminate tonight."""

        if mafia_votes:
            vote_summary = "Mafia votes:\n" + "\n".join([f"player_{voter} voted for player_{target}" for voter, target in mafia_votes])
            user_prompt += f"\n\n{vote_summary}\n\nDon, based on these votes, please decide the final target. You are free to choose a player not in the other Mafia votes"

        user_prompt += """
        \n\nNote: Return your vote for the player you want to eliminate and provide your internal reason.\n
        Format your response as follows:\n
        - First, provide the player ID you want to vote for in the format: 'player_#'\n"
        - After that, provide a brief internal reason for why you are choosing this player, in 2-3 sentences. This reason will not be visible to anyone else.\n"
        
        Example response:
        player_#
        vote reasoning...
        
        YOU MUST RESPOND WITH THE EXAMPLE FORMAT."""

        response = self._call_llm(system_prompt, user_prompt)
        print("\n" + response + "\n")
        lines = response.split("\n", 1)
        voted_player = int(re.search(r'\d+', response).group()) if re.search(r'\d+', response) else None
        internal_reason = lines[1].strip() if len(lines) > 1 else "No reason provided"

        self.mafia_thinking.append({
            "player_id": self.player_name,
            "vote": voted_player,
            "internal_reason": internal_reason
        })

        self.mafia_kill_targets.append(f"player_{voted_player}")
        return voted_player


    def final_words(self, game_log: str, cause_of_death: str) -> str:
        system_prompt = self._build_system_prompt()

        user_prompt = (
            f"Here is what happened in the game so far:\n{game_log}\n\n"
            f"You are {self.player_name}. You have just been eliminated from the game.\n"
            f"You were a **{self.role}** and you were {'voted out by the town during the day' if cause_of_death == 'vote' else 'killed by the mafia during the night'}.\n"
            f"You don't have to say anything if you're a civilian who died during the first night."
        )

        if self.role == "detective":
            if self.investigations:
                user_prompt += "\nHere are the investigation results you gathered during the game:\n"
                user_prompt += "\n".join(self.investigations) + "\n"
            else:
                user_prompt += "\nYou had not completed any investigations yet.\n"
            user_prompt += "Now, give your final words. Share your discoveries and suspicions to help the civilians win.\n"

        elif self.role in ["mafia", "don"]:
            if self.mafia_kill_targets:
                user_prompt += "\nHere are the players you voted to kill during the night:\n"
                user_prompt += "\n".join(
                    [f"Night {i + 1}: Targeted {target}" for i, target in enumerate(self.mafia_kill_targets)]) + "\n"
            else:
                user_prompt += "\nYou did not kill any player yet.\n"
            user_prompt += (
                "Now that you're out, you must lie to protect the Mafia and confuse the civilians.\n"
                "Try to cast suspicion on innocent players or mislead them about your role.\n"
            )

        else:  # Civilian
            user_prompt += (
                "You were an innocent civilian.\n"
                "Now that you're gone, give your final thoughts to help your team.\n"
                "Mention who you suspected or anything strange you noticed.\n"
            )

        user_prompt += (
            "\nReturn your final words in 2–4 sentences. Be sincere, persuasive, emotional, or cryptic as you wish.\n"
            "Do not restate your role or how you died. Just speak your mind.\n"
        )

        final_statement = self._call_llm(system_prompt, user_prompt)
        return final_statement.strip()