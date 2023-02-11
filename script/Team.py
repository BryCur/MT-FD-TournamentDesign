from openskill import Rating

class Team:
    _name = ""
    _rating = 0
    _matchVictoryCount = 0
    _cycleVictoryCount = 0
    _roundVictoryCount = 0
    _defenseVictoryCount = 0

    def __init__(self, name:str, rating:Rating) -> None:
        self.name = name
        self.rating = rating
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
        return self.name + " (" + repr(self.rating) + ")"

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
