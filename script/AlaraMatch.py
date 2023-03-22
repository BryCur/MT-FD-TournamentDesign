from Team import Team
import numpy as np
from openskill import predict_win
from utils import *
from Logger import Logger

class AlaraMatch:
    _teams: tuple[Team, Team, Team]
    _rng: np.random.Generator

    matchNumber: int = 0
    roundCount: int = 0

    def __init__(self, teams: tuple[Team, Team, Team], rng_generator: np.random.Generator, logger: Logger) -> None:
        self._teams = teams
        self._rng = rng_generator
        AlaraMatch.matchNumber += 1
        self.matchNumber = AlaraMatch.matchNumber
        self.roundCount = 0
        self.cycleScore = [0,0,0]
        self.matchScore = [0,0,0]
        self.logger = logger

    def playMatch(self):
        MAX_CYCLE_SCORE= 2
        MAX_MATCH_SCORE= 2

        defenderTeam = 0

        self.logger.logInfoMessage(f"PLAYING MATCH N°{self.matchNumber} --------------------------------------------------")
        odds = predict_win(teams=[[self._teams[0].get_rating()], [self._teams[1].get_rating()], [self._teams[2].get_rating()]])
        self.logger.logWinningOdds(self._teams, odds)

        while MAX_MATCH_SCORE not in self.matchScore:
            while MAX_CYCLE_SCORE not in self.cycleScore:
                self.roundCount+=1
                winner_index = self._playRound(defenderTeam)
                self.cycleScore[winner_index] += 1
                self._teams[winner_index].addRoundVictory()
                defenderTeam = (defenderTeam + 1) % TEAMS_IN_ONE_MATCH

                self.logger.logInfoMessage(f"State of current cycle")
                self.logger.logInfoMessage(f"{self._teams[0].get_name()}/{self._teams[1].get_name()}/{self._teams[2].get_name()} -- {self.cycleScore[0]}/{self.cycleScore[1]}/{self.cycleScore[2]}")
            
            cycleWinnerIndex = self.cycleScore.index(MAX_CYCLE_SCORE)
            self.matchScore[cycleWinnerIndex] += 1
            self._teams[cycleWinnerIndex].addCycleVictory()
            self.cycleScore = [0,0,0]

            self.logger.logInfoMessage(f"State of current match")
            self.logger.logInfoMessage(f"{self._teams[0].get_name()}/{self._teams[1].get_name()}/{self._teams[2].get_name()} -- {self.matchScore[0]}/{self.matchScore[1]}/{self.matchScore[2]}")

        matchWinnerIndex = self.matchScore.index(MAX_MATCH_SCORE)
        self._teams[matchWinnerIndex].addMatchVictory()

        self.logger.logInfoMessage("\r\n" *3)

        return self._teams[matchWinnerIndex]


    def _playRound(self, defender_index: int):
        """
        Takes the teams that are to play a match, and returns the winner
        """
        # win_p_t1 is the win probability of team_1
        self.logger.logInfoMessage(f"ROUND:  {self._teams[0].get_name()} VS {self._teams[0].get_name()}  VS  {self._teams[0].get_name()} || Defending team: {self._teams[defender_index].get_name()}")

        # TODO mess around to represent the defending advantage and collaboration focus
        win_p_t1, win_p_t2, win_p_t3 = predict_win(teams=[[self._teams[0].get_rating()], [self._teams[1].get_rating()], [self._teams[2].get_rating()]])

        self.logger.logWinningOdds(self._teams, [win_p_t1, win_p_t2, win_p_t3])

        # Random number in (0, 1)
        u = self._rng.random()
        # we define threshold that will determine the team winning. 
        # If the random number is between 0 and win_p_t1 then team 1 wins
        # If the random number is between win_p_t1 and win_p_t2 then team 2 wins
        # If the random number is above win_p_t2 then team 3 wins
        bucket = np.where(u < win_p_t1, 0, np.where(u < win_p_t1 + win_p_t2, 1, 2)).astype(int)

        self.logger.logInfoMessage("winner: " + str(self._teams[bucket]))

        if(defender_index == bucket):
            self._teams[bucket].addDefenseVictory()  
        
        return bucket
    
    def getRoundState(self) -> list[int]:
        return self.cycleScore
    
    def getCycleState(self) -> list[int]:
        return self.matchScore
    
    def getParticipants(self) -> tuple[Team, Team, Team]:
        return self._teams
