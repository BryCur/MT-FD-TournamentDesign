"""
The setup for this example is:
- four teams a, b, c, d
- play in a single knockout
- a vs. b, c vs. d
- team skills are drawn from a normal distribution
- the skill-model we use is openskill


How to modelize players incentive depending on te tournament state
"""
import argparse
import multiprocessing
from Team import Team # we represent a team with a name and a rating

from openskill import Rating, predict_win
import numpy as np
from tqdm import tqdm

success_prediction = 0


parser = argparse.ArgumentParser()
parser.add_argument('-n', '--n-simulations', type=int, default=10000)
# number of pools, optimal number depends on the number of cores on your machine
parser.add_argument('-p', '--pools', type=int, default=4)
parser.add_argument('-t', '--n-teams', type=int, default=4)
args = parser.parse_args()


def is_integer(x) -> bool:
    """
    Checks if a number is an integer, mathematically.
    """
    return x % 1 == 0


def generate_teams(n: int, rng_generator: np.random.Generator) -> list[Team]:
    """
    In this case, a team is represented by a openskill Rating

    25, 25/3 and 0.1 are magic numbers here, but
    - 25 is average skill for all players
    - 25/3 is the standard deviation of the skills of players
    - 0.1 is the standard deviation of an individual players skill
    """
    mus = rng_generator.normal(25, 25 / 3, n)
    return [Team("Team %3d" % (i), Rating(mus[i], 0.1)) for i in range(n)]

def predict_result(teams: list[Team], display = True):
    ordered = teams.copy()
    ordered.sort(reverse=True)

    if display:
        for x in range(len(ordered)):
            print(str(x+1) + " - " + str(ordered[x]))

    return ordered


def teams_to_brackets(teams: list[Team]) -> list[tuple[Team, Team]]:
    assert is_integer(np.sqrt(len(teams))), "can't create brackets for a knockout for non-square number of teams"

    return [(teams[i], teams[i+1]) for i in range(0, len(teams), 2)]


def resolve_match(team_1: Team, team_2: Team, rng_generator: np.random.Generator) -> Team:
    """
    Takes two teams that are to play a match, and returns the winner
    """
    # win_p_t1 is the win probability of team_1
    print("team 1 " + str(team_1) + " VS " + str(team_2))
    
    win_p_t1, _ = predict_win(teams=[[team_1.get_rating()], [team_2.get_rating()]])

    # Random number in (0, 1)
    u = rng_generator.random()

    # If we assume that the openskill model is true, and that the win probabilities do
    # not depend on the current state of the tournament, then:
    # The probability of (win_p_t1 < u) is precicely win_p_t1!
    # (this is generally not going to be the case, especially in a 3 team tournament)
    if win_p_t1 < u:
        return team_1
    else:
        # if team_1 did not win, team_2 did (assuming no draws)
        return team_2


def resolve_single_knockout_tournament(brackets: list[tuple[Team, Team]], rng_generator: np.random.Generator) -> Team:
    # while we're not in the final, resolve matches into new brackets
    while len(brackets) > 1:
        new_brackets = []
        for i in range(0, len(brackets), 2):
            new_bracket = (
                resolve_match(*brackets[i], rng_generator=rng_generator),
                resolve_match(*brackets[i+1], rng_generator=rng_generator),
                )
            new_brackets.append(new_bracket)
        brackets = new_brackets
    
    # Resolve the final
    final = brackets[0]
    return resolve_match(*final, rng_generator=rng_generator)


def single_simulation(rng_generator: np.random.Generator):
    teams = generate_teams(args.n_teams, rng_generator)
    predicted_ranking = predict_result(teams, False)   
    brackets = teams_to_brackets(teams)
    # Returns winner but currently ignored
    grand_winner = resolve_single_knockout_tournament(brackets, rng_generator)
    # print("grand winner: " + str(grand_winner))

    if predicted_ranking[0].get_name == grand_winner.get_name: 
        global success_prediction
        success_prediction += 1

    # Do some calculation on the result of the tournament

def run_simulations(n, pools):
    global success_prediction
    success_prediction = 0
    ss = np.random.SeedSequence(42)
    seeds = ss.spawn(n)
    streams = [np.random.default_rng(seed) for seed in seeds]
    single_simulation(streams[5])
    # with multiprocessing.Pool(pools) as p:
    #     res = list(tqdm(p.imap(single_simulation, streams), total=len(streams)))


if __name__ == "__main__":
    print("Running %5d simulations for %2d team" % (args.n_simulations, args.n_teams))
    run_simulations(args.n_simulations, args.pools)
    accuracy = success_prediction / args.n_simulations * 100;
    print("Simulation finshed, accuracy: %5f percent" % (accuracy))