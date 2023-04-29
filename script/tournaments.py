import abc
import math
from Team import Team
from utils import *
import numpy as np
from AlaraMatch import AlaraMatch
from Logger import Logger
from itertools import combinations

class aTournament(abc.ABC):
    _participants: list[Team]
    _ranking: list[Team]
    _rng: np.random.Generator
    _logger: Logger
    _matchupHistory: list[tuple[Team, Team, Team]]

    @abc.abstractmethod
    def __init__(self, participants: list[Team], rng: np.random.Generator, logger: Logger):
        self._participants = participants
        self._rng = rng
        self._logger = logger
        self._matchupHistory = []
        pass

    @abc.abstractmethod
    def play(self):
        pass
 
    @abc.abstractmethod
    def getFinalRanking(self):
        pass

    def getMatchCount(self):
        self._logger.logInfoMessage(f"Match played in tournament: {len(self._matchupHistory)}")
        return len(self._matchupHistory)
    
    def getTieCount(self):
        ties = 0
        tiedScores: list[tuple[int, int, int, int]] = []
        for i in range(len(self._participants)):
            reference_score = self._participants[i].get_score()

            if reference_score in tiedScores :
                continue

            for j in range(i+1, len(self._participants)):
                compared_score = self._participants[j].get_score()
                if reference_score == compared_score:
                    ties += 1

            tiedScores.append(reference_score)

        self._logger.logInfoMessage(f"Ties in tournament: {ties}")
        return ties

    def playTournamentMatch(self, matchup: tuple[Team, Team, Team]) -> Team:
        self._matchupHistory.append(matchup)
        return AlaraMatch(matchup, self._rng, self._logger).playMatch()
    
    def getCompleteDuplicateMatchupCount(self)-> int:
        res = len(self._matchupHistory) - len(set(self._matchupHistory))
        self._logger.logInfoMessage(f"Duplicate matches in tournament: {res}")
        return res

# ======================================================================================

class TournamentSingleKnockout(aTournament):
    def __init__(self, participants: list[Team], rng: np.random.Generator, logger: Logger):
        if(is_integer(math.log(len(participants), TEAMS_IN_ONE_MATCH))):
            super().__init__(participants, rng, logger)
        else:
            raise Exception("Single knockout needs for base participants unfulfilled (need power of 3)")

    def _teams_to_brackets(self) -> list[tuple[Team, Team, Team]]:
        assert is_integer(np.sqrt(len(self._participants))), "can't create brackets for a knockout for non-square number of teams"

        return [(self._participants[i], self._participants[i+1], self._participants[i+2]) for i in range(0, len(self._participants), TEAMS_IN_ONE_MATCH)]
    
    def getFinalRanking(self):
        self._ranking = sorted(self._participants.copy(), key = lambda t: t.get_score(), reverse=True)
        return self._ranking

    def play(self):
        brackets = self._teams_to_brackets()

        # while we're not in the final, resolve matches into new brackets
        while len(brackets) > 1:
            new_brackets = []
            for i in range(0, len(brackets), 3):
                new_bracket = (
                    self.playTournamentMatch(brackets[i]),
                    self.playTournamentMatch(brackets[i+1]),
                    self.playTournamentMatch(brackets[i+2])
                    )
                new_brackets.append(new_bracket)
            brackets = new_brackets
        
        # Resolve the final
        self.playTournamentMatch(brackets[0])
        
        return self.getFinalRanking()

# ======================================================================================

class tournamentRoundRobin(aTournament):
    def __init__(self, participants: list[Team], rng: np.random.Generator, logger: Logger):
        super().__init__(participants, rng, logger)

    def getFinalRanking(self):
        self._ranking = sorted(self._participants.copy(), key = lambda t: t.get_score(), reverse=True)
        return self._ranking

    def play(self):
        all_matches= combinations(self._participants, TEAMS_IN_ONE_MATCH)
        
        for matchup in all_matches:
            self.playTournamentMatch(matchup)
        
        return self.getFinalRanking()

# ======================================================================================

class tournamentSwissSystem(aTournament):
    _rounds = 5

    def __init__(self, participants: list[Team], rng: np.random.Generator, logger: Logger, rounds: int):
        super().__init__(participants, rng, logger)
        self._rounds = rounds

    def getFinalRanking(self):
        self._ranking = sorted(self._participants.copy(), key = lambda t: t.get_score(), reverse=True)
        return self._ranking

    def play(self):
        # finish this
        all_matches= combinations(self._participants, TEAMS_IN_ONE_MATCH)
        
        for r in range(self._rounds):
            for i in range(len(self._participants),step=TEAMS_IN_ONE_MATCH):
                self.playTournamentMatch(self._participants[i:i+3])
        
        return self.getFinalRanking()
