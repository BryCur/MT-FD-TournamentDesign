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
    tau_distance = 1 - 4 * disagreements / (n * (n - 1))
    
    
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






