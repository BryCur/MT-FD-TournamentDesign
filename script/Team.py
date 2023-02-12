from openskill import Rating

class Team:
    _matchVictoryCount = 0
    _cycleVictoryCount = 0
    _roundVictoryCount = 0
    _defenseVictoryCount = 0

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
        return self._name + " (" + repr(self._rating) + ")"

    def get_name(self) -> str:
        return self._name
    
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
