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
        self._matchupHistory.append(set(matchup))
        return AlaraMatch(matchup, self._rng, self._logger).playMatch()
    
    def getCompleteDuplicateMatchupCount(self)-> int:
        # sorting the tuple so ABC and BAC are found as a duplicate
        sorted_history_matchup = map(lambda matchup: tuple(sorted(matchup, key = lambda t: t.get_score())), self._matchupHistory)

        set_matchup = set(sorted_history_matchup)
        res = len(self._matchupHistory) - len(set_matchup)
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
        #assert is_integer(np.sqrt(len(self._participants))), "can't create brackets for a knockout for non-square number of teams"

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
        if len(participants) % TEAMS_IN_ONE_MATCH == 0:
            super().__init__(participants, rng, logger)
            self._rounds = rounds
        else:
            raise Exception("Swiss System needs for base participants unfulfilled (need multiple of 3)")

    def getFinalRanking(self):
        self._ranking = sorted(self._participants.copy(), key = lambda t: t.get_score(), reverse=True)
        return self._ranking

    def play(self):

        #first round: 
        self._logger.logInfoMessage("--------------------- ROUND 1")
        for i in range(0, len(self._participants), TEAMS_IN_ONE_MATCH):
                self.playTournamentMatch(tuple(self._participants[i:i+TEAMS_IN_ONE_MATCH]))

        for r in range(self._rounds-1):
            self._logger.logInfoMessage(f"--------------------- ROUND {r+2}")
            round_matchup = self.makeRound()
            for matchup in round_matchup: 
                self.playTournamentMatch(matchup)
        return self.getFinalRanking()
    
    def makeRound(self)->tuple[Team, Team, Team]:
        participant_pool_ordered = sorted(self._participants.copy(), key = lambda t: t.get_score(), reverse=True)
        sorted_history_matchup = map(lambda matchup: tuple(sorted(matchup, key = lambda t: t.get_name())), self._matchupHistory)
        set_past_matchups = set(sorted_history_matchup)
        round_matchups = []
        MAX_ATTEMPT = 3

        while len(participant_pool_ordered) >= 3:
            first_participant = participant_pool_ordered.pop()
            second_participant = participant_pool_ordered.pop()
            last_participant = None
            
            attempt = 0

            while attempt < min(MAX_ATTEMPT, len(participant_pool_ordered)):
                ordered_matchup = tuple(sorted((first_participant, second_participant, participant_pool_ordered[attempt]), key = lambda t: t.get_name()))
                if ordered_matchup not in set_past_matchups:
                    last_participant = participant_pool_ordered[attempt]
                    break
                else:
                    attempt += 1

            if last_participant is None:
                last_participant = participant_pool_ordered[0]

            participant_pool_ordered.remove(last_participant)
            round_matchups.append((first_participant, second_participant, last_participant))

        return round_matchups

# ======================================================================================

class tournamentCustom(aTournament):

    def __init__(self, participants: list[Team], rng: np.random.Generator, logger: Logger):
        if len(participants) >= 9 and len(participants) % 3 == 0:
            super().__init__(participants, rng, logger)
        else:
            raise Exception("Not enough participants to run the custom tournament format")

    def getFinalRanking(self):
        self._ranking = sorted(self._participants.copy(), key = lambda t: t.get_score(), reverse=True)
        return self._ranking

    def play(self):
        # step 1 make groups => divide the tournament into 3 groups of equal sizes of 3 participants or more
        groups : list[list[Team]] = [[],[],[]]

        self._rng.shuffle(self._participants) # seeding
        for i in range (0, len(self._participants)):
            groups[i%len(groups)].append(self._participants[i])

        # step 2 => play groups, in swiss system or round robin to have a preliminary ranking
        for group in groups:
            groupPhase: aTournament = None
            if((len(self._participants)/len(groups))% TEAMS_IN_ONE_MATCH == 0): # if enough particpant in a group to play swiss system
                self._logger.logInfoMessage("Using swiss system!")
                groupPhase = tournamentSwissSystem(group, self._rng, self._logger, 8) # TODO change with stable round count
            else:
                self._logger.logInfoMessage("Using round robin!")
                groupPhase = tournamentRoundRobin(group, self._rng, self._logger)

            groupPhase.play()
            self._matchupHistory += groupPhase._matchupHistory

        # step 3 => match the top 3 players of each group against players of other groups to avoid duplicate matches
        finalPhasePlayers = self.seedFinalPhase(groups)

        # step 4 => play single knockout tournament
        finalPhase = TournamentSingleKnockout(finalPhasePlayers, self._rng, self._logger)
        finalPhase.play()
        self._matchupHistory += finalPhase._matchupHistory

        # step 5 => final ranking
        return self.getFinalRanking()


    def seedFinalPhase(self, groups: list[list[Team]]) -> list[Team]:
        n = len(groups)
        result = []

        # consider 3 group orederd by skill ABC, DEF and GHI, thee seeding will put
        # AEI, DHC and GBF together
        for i in range(n):
            for j in range(n):
                result.append(groups[j][(i+j) % n])

        return result
