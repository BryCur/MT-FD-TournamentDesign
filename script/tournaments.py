import abc
import math
from Team import Team
from utils import *
import numpy as np
from AlaraMatch import AlaraMatch

class aTournament(abc.ABC):
    _participants: list[Team]
    _ranking: list[Team]
    _matchCount: int
    _rng: np.random.Generator

    @abc.abstractmethod
    def __init__(self, participants: list[Team], rng: np.random.Generator):
        self._participants = participants
        self._rng = rng
        pass

    @abc.abstractmethod
    def play(self):
        pass
 
    @abc.abstractmethod
    def getFinalRanking(self):
        pass

# ======================================================================================

class TournamentSingleKnockout(aTournament):
    def __init__(self, participants: list[Team], rng: np.random.Generator):
        if(is_integer(math.log(len(participants), TEAMS_IN_ONE_MATCH))):
            super().__init__(participants, rng)
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
                    AlaraMatch(brackets[i], self._rng).playMatch(),
                    AlaraMatch(brackets[i+1], self._rng).playMatch(),
                    AlaraMatch(brackets[i+2], self._rng).playMatch(),
                    )
                new_brackets.append(new_bracket)
            brackets = new_brackets
        
        # Resolve the final
        final = brackets[0]
        AlaraMatch(final, self._rng).playMatch()

        return self.getFinalRanking()


