from openskill import Rating

class Team:
    name = ""
    rating = 0

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
        return self.name
    
    def get_rating(self) -> Rating:
        return self.rating
