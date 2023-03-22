import abc
import math
from Team import Team
from utils import *
import numpy as np
from AlaraMatch import AlaraMatch
from Logger import Logger

class aTournament(abc.ABC):
    _participants: list[Team]
    _ranking: list[Team]
    _matchCount: int
    _rng: np.random.Generator
    _logger: Logger

    @abc.abstractmethod
    def __init__(self, participants: list[Team], rng: np.random.Generator, logger: Logger):
        self._participants = participants
        self._rng = rng
        self._logger = logger
        self._matchCount = 0
        pass

    @abc.abstractmethod
    def play(self):
        pass
 
    @abc.abstractmethod
    def getFinalRanking(self):
        pass

    def getMatchCount(self):
        return self._matchCount

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
        self._ranking = sorted(self._participants.copy(), key = lambda t: (t.getMatchVictoryCount(), t.getCycleVictoryCount(), t.getRoundVictoryCount(), t.getDefenseVictoryCount()), reverse=True)
        return self._ranking

    def play(self):
        brackets = self._teams_to_brackets()

        # while we're not in the final, resolve matches into new brackets
        while len(brackets) > 1:
            new_brackets = []
            for i in range(0, len(brackets), 3):
                new_bracket = (
                    AlaraMatch(brackets[i], self._rng, self._logger).playMatch(),
                    AlaraMatch(brackets[i+1], self._rng, self._logger).playMatch(),
                    AlaraMatch(brackets[i+2], self._rng, self._logger).playMatch(),
                    )
                new_brackets.append(new_bracket)
                self._matchCount +=3
            brackets = new_brackets
        
        # Resolve the final
        AlaraMatch(brackets[0], self._rng, self._logger).playMatch()
        self._matchCount += 1
        return self.getFinalRanking()
    
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


        return ties
    
    def getMatchCount(self):
        return super().getMatchCount()


