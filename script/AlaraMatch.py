from Team import Team
import numpy as np
from openskill import predict_win
from utils import *

class AlaraMatch:
    _teams: list[Team]
    _rng: np.random.Generator

    matchNumber: int = 0
    roundCount: int = 0

    def __init__(self, teams: list[Team], rng_generator: np.random.Generator) -> None:
        self._teams = teams
        self._rng = rng_generator
        AlaraMatch.matchNumber += 1
        self.roundCount = 0

    def playMatch(self):
        MAX_CYCLE_SCORE= 2
        MAX_MATCH_SCORE= 2
        cycleScore = [0,0,0]
        matchScore = [0,0,0]

        defenderTeam = 0

        if DEBUG_MODE:
            print("PLAYING MATCH N°" + AlaraMatch.matchNumber + " --------------------------------------------------")

        while MAX_MATCH_SCORE not in matchScore:
            while MAX_CYCLE_SCORE not in cycleScore:
                winner_index = self._playRound(defenderTeam)
                cycleScore[winner_index] += 1
                self._teams[winner_index].addRoundVictory()
                defenderTeam = (defenderTeam + 1) % TEAMS_IN_ONE_MATCH
                self.roundCount+=1
            
            cycleWinnerIndex = cycleScore.index(MAX_CYCLE_SCORE)
            matchScore[cycleWinnerIndex] += 1
            self._teams[cycleWinnerIndex].addCycleVictory()
            cycleScore = [0,0,0]
        
        matchWinnerIndex = matchScore.index(MAX_MATCH_SCORE)
        self._teams[matchWinnerIndex].addMatchVictory()

        return self._teams[matchWinnerIndex]


    def _playRound(self, defender_index: int):
        """
        Takes the teams that are to play a match, and returns the winner
        """
        # win_p_t1 is the win probability of team_1
        if DEBUG_MODE:
            print("ROUND: " + str(self._teams[0]) + " VS " + str(self._teams[1]) + " VS " + str(self._teams[2]) + "|| Defending team: " + str(self._teams[defender_index]))

        # TODO mess around to represent the defending advantage and collaboration focus
        win_p_t1, win_p_t2, win_p_t3 = predict_win(teams=[[self._teams[0].get_rating()], [self._teams[1].get_rating()], [self._teams[2].get_rating()]])

        if DEBUG_MODE:
            print("WR T1:" + str(win_p_t1) + " -- WR T2: " + str(win_p_t2) + " -- WR T3: " + str(win_p_t3))

        # Random number in (0, 1)
        u = self._rng.random()
        if DEBUG_MODE:
            print("result:" + str(u))
        # we define threshold that will determine the team winning. 
        # If the random number is between 0 and win_p_t1 then team 1 wins
        # If the random number is between win_p_t1 and win_p_t2 then team 2 wins
        # If the random number is above win_p_t2 then team 3 wins
        bucket = np.where(u < win_p_t1, 0, np.where(u < win_p_t1 + win_p_t2, 1, 2)).astype(int)

        if DEBUG_MODE:
            print("winner: " + str(self._teams[bucket]))

        if(defender_index == bucket):
            self._teams[bucket].addDefenseVictory()  
        
        return bucket
