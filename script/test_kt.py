# from Team import Team
from RankingComparator import *
from scipy.stats import kendalltau, weightedtau

class Team:
    def __init__(self, name):
        self.name = name
    
    def get_name(self):
        return self.name

# Create Team objects
team1 = Team("A")
team2 = Team("B")
team3 = Team("C")
team4 = Team("D")
team5 = Team("E")
team6 = Team("F")
team7 = Team("G")
team8 = Team("H")

expected_ranking = agreed_ranking = [team1, team2, team3, team4, team5, team6, team7, team8]
disagreed_ranking = [team8, team7, team6, team5, team4, team3, team2, team1]
random_ranking = [team3, team1, team2, team4, team5, team6, team7, team8]
random_ranking_2 = [team1, team2, team3, team6, team5, team4, team7, team8]

## test of classic kendall tau
print("------------------ custom kendall tau -----------------------")
complete_agreement = kendall_tau_distance(expected_ranking, agreed_ranking)
print(f"result complete agreement: {complete_agreement}") # (0.0, 0)
complete_disagreement = kendall_tau_distance(expected_ranking, disagreed_ranking)
print(f"result complete disagreement: {complete_disagreement}") # (1.0, 28)
random_result = kendall_tau_distance(expected_ranking, random_ranking)
print(f"result random: {random_result}") # (0.07142857142857142, 2)
random_result = kendall_tau_distance(expected_ranking, random_ranking_2)
print(f"result random: {random_result}") # (0.10714285714285714, 3)

## test of weighted kendall tau

neutral_weights = [1]*len(expected_ranking) # sum the weight to the length of the list ? 
top_3_weights = [2]*3 + [1]*5
top_half_weights = [2]*4 + [1]*4
top_3_and_half_weights = [3]*3 + [2] + [1]*4
normalized_weights = [1/8]*8
normalized_top3_weights = [len(expected_ranking)*x/sum(top_3_weights) for x in top_3_weights]
print("------------------ weighted kendall tau -----------------------")
weights = [2, 4, 6, 5, 4, 3, 2, 1]
print(weights)

complete_agreement = weighted_kendall_tau_distance(expected_ranking, agreed_ranking, normalized_top3_weights)
print(f"result complete agreement: {complete_agreement}") # (0.0, 0)
complete_disagreement = weighted_kendall_tau_distance(expected_ranking, disagreed_ranking, normalized_top3_weights)
print(f"result complete disagreement: {complete_disagreement}") # (1.0, 28)
random_result = weighted_kendall_tau_distance(expected_ranking, random_ranking, normalized_top3_weights)
print(f"result random: {random_result}") # (0.07142857142857142, 2)
random_result = weighted_kendall_tau_distance(expected_ranking, random_ranking_2, normalized_top3_weights)
print(f"result random: {random_result}") # (0.07142857142857142, 2) 


expected = agreement = range(len(expected_ranking))
print("------------------ scipy weighted kendall tau -----------------------")
r1 = weightedtau(expected, agreement, True, lambda x: len(expected) - x / len(expected))
print(r1)

r2 = weightedtau(expected, disgreement, True, lambda x: len(expected) - x / len(expected))
print(r2)
