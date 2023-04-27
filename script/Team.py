from openskill import Rating

class Team:
    _name: str
    _matchVictoryCount = 0
    _cycleVictoryCount = 0
    _roundVictoryCount = 0
    _defenseVictoryCount = 0
    _matchCount = 0
    _cycleCount = 0
    _roundCount = 0
    _defenseCount = 0

    def __init__(self, name:str, rating:Rating) -> None:
        self._name = name
        self._rating = rating
        pass

    def __lt__(self, other):
         return self.get_rating() < other.get_rating()
    
    def __gt__(self, other):
         return self.get_rating() > other.get_rating()
    
    def __le__(self, other):
         return self.get_rating() <= other.get_rating()

    def __ge__(self, other):
         return self.get_rating() >= other.get_rating()

    def __str__(self):
        return self.get_name()

    def get_name(self) -> str:
        return self._name
    
    def get_rating_str(self) -> str:
        return repr(self._rating)
    
    def get_score_str(self) -> str:
        return f"{self.getMatchVictoryCount()}/{self.getCycleVictoryCount()}/{self.getRoundVictoryCount()}/{self.getDefenseVictoryCount()} (match/cycle/round/defense)"
    
    def get_rating(self) -> Rating:
        return self._rating

    def addMatchVictory(self): 
        self._matchVictoryCount += 1

    def addCycleVictory(self): 
        self._cycleVictoryCount += 1

    def addRoundVictory(self): 
        self._roundVictoryCount += 1

    def addDefenseVictory(self): 
        self._defenseVictoryCount += 1

    def addMatch(self): 
        self._matchCount += 1

    def addCycle(self): 
        self._cycleCount += 1

    def addRound(self): 
        self._roundCount += 1

    def addDefense(self): 
        self._defenseCount += 1

    def getMatchVictoryCount(self) -> int:
        return self._matchVictoryCount
        
    def getCycleVictoryCount(self) -> int:
        return self._cycleVictoryCount
        
    def getRoundVictoryCount(self) -> int:
        return self._roundVictoryCount
        
    def getDefenseVictoryCount(self) -> int:
        return self._defenseVictoryCount
        
    def get_score(self) -> tuple[int, int, int, int]:
        return (self._matchVictoryCount, self._cycleVictoryCount / self._cycleCount if self._cycleCount > 0 else 1, self._roundVictoryCount / self._roundCount if self._roundCount > 0 else 1, self._defenseVictoryCount / self._defenseCount if self._defenseCount > 0 else 1)
