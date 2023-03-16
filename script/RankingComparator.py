from itertools import combinations
from Team import Team


def kendall_tau_distance(predicted: list[Team], actual: list[Team]):

    n = len(predicted)
    assert n == len(actual)

    # Create dictionary mapping team names to their indices in the predicted list
    index_dict = {(team.get_name()): i for i, team in enumerate(predicted)}
    
    # Compute number of pairwise disagreements between predicted and actual rankings
    disagreements = 0
    for team1, team2 in combinations(actual, 2):
        pred1, pred2 = index_dict[team1.get_name()], index_dict[team2.get_name()]
        actual1, actual2 = actual.index(team1), actual.index(team2)
        if (pred1 - pred2) * (actual1 - actual2) < 0:
            disagreements += 1
    
    # Compute Kendall tau distance
    tau_distance = (2 * disagreements) / (n * (n - 1))
    
    
    return tau_distance, disagreements


def weighted_kendall_tau_distance(expected_ranking, predicted_ranking, weights):

    assert len(expected_ranking) == len(predicted_ranking) == len(weights), "All lists must have the same length."

    n = len(expected_ranking)
    discordant_pairs = 0
    for i in range(n):
        for j in range(i+1, n):
            # Check if the order of the two teams in the expected ranking is the same as the order in the predicted ranking
            if (expected_ranking.index(expected_ranking[i]) < expected_ranking.index(expected_ranking[j]) and
                    predicted_ranking.index(expected_ranking[i]) > predicted_ranking.index(expected_ranking[j])):
                discordant_pairs += weights[j]
            elif (expected_ranking.index(expected_ranking[i]) > expected_ranking.index(expected_ranking[j]) and
                    predicted_ranking.index(expected_ranking[i]) < predicted_ranking.index(expected_ranking[j])):
                discordant_pairs += weights[i]

    # Calculate the weighted Kendall Tau distance
    weighted_tau = 1 - 4 * discordant_pairs / (n * (n - 1))
    return weighted_tau, discordant_pairs




""" # Create Team objects
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
print("------------------ classic kendall tau -----------------------")
complete_agreement = kendall_tau_distance(expected_ranking, agreed_ranking)
print(f"result complete agreement: {complete_agreement}") # (0.0, 0)
complete_disagreement = kendall_tau_distance(expected_ranking, disagreed_ranking)
print(f"result complete disagreement: {complete_disagreement}") # (1.0, 28)
random_result = kendall_tau_distance(expected_ranking, random_ranking)
print(f"result random: {random_result}") # (0.07142857142857142, 2)
random_result = kendall_tau_distance(expected_ranking, random_ranking_2)
print(f"result random: {random_result}") # (0.10714285714285714, 3)

## test of weighted kendall tau

neutral_weights = [1]*len(expected_ranking)
top_3_weights = [2]*3 + [1]*5
top_half_weights = [2]*4 + [1]*4
top_3_and_half_weights = [3]*3 + [2] + [1]*4
normalized_weights = [1/8]*8
print("------------------ weighted kendall tau -----------------------")
weights = [2, 4, 6, 5, 4, 3, 2, 1]
print(weights)

complete_agreement = weighted_kendall_tau_distance(expected_ranking, agreed_ranking, weights)
print(f"result complete agreement: {complete_agreement}") # (0.0, 0)
complete_disagreement = weighted_kendall_tau_distance(expected_ranking, disagreed_ranking, weights)
print(f"result complete disagreement: {complete_disagreement}") # (1.0, 28)
random_result = weighted_kendall_tau_distance(expected_ranking, random_ranking, weights)
print(f"result random: {random_result}") # (0.07142857142857142, 2)
random_result = weighted_kendall_tau_distance(expected_ranking, random_ranking_2, weights)
print(f"result random: {random_result}") # (0.07142857142857142, 2) """



