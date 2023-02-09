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
import datetime
from Team import Team # we represent a team with a name and a rating

from openskill import Rating, predict_win
import numpy as np
from tqdm import tqdm

TEAMS_IN_ONE_MATCH = 3
DEBUG_MODE = 1

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--n-simulations', type=int, default=10000)
# number of pools, optimal number depends on the number of cores on your machine
parser.add_argument('-p', '--pools', type=int, default=4)
parser.add_argument('-t', '--n-teams', type=int, default=9)
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


def teams_to_brackets(teams: list[Team]) -> list[tuple[Team, Team, Team]]:
    assert is_integer(np.sqrt(len(teams))), "can't create brackets for a knockout for non-square number of teams"

    return [(teams[i], teams[i+1], teams[i+2]) for i in range(0, len(teams), TEAMS_IN_ONE_MATCH)]


def resolve_match(team_1: Team, team_2: Team, team_3: Team, rng_generator: np.random.Generator) -> Team:
    """
    Takes two teams that are to play a match, and returns the winner
    """
    # win_p_t1 is the win probability of team_1
    if DEBUG_MODE:
        print("MATCH: " + str(team_1) + " VS " + str(team_2) + " VS " + str(team_3))

    win_p_t1, win_p_t2, win_p_t3 = predict_win(teams=[[team_1.get_rating()], [team_2.get_rating()], [team_3.get_rating()]])

    if DEBUG_MODE:
        print("WR T1:" + str(win_p_t1) + " -- WR T2: " + str(win_p_t2) + " -- WR T3: " + str(win_p_t3))

    # Random number in (0, 1)
    u = rng_generator.random()
    if DEBUG_MODE:
        print("result:" + str(u))
    bucket = np.where(u < win_p_t1, 0, np.where(u < win_p_t1 + win_p_t2, 1, 2)).astype(int)

    # If we assume that the openskill model is true, and that the win probabilities do
    # not depend on the current state of the tournament, then:
    # The probability of (win_p_t1 < u) is precicely win_p_t1!
    # (this is generally not going to be the case, especially in a 3 team tournament)
    if bucket == 0:
        if DEBUG_MODE:
            print("winner: " + str(team_1))
        return team_1
    elif bucket == 1:
        # if team_1 did not win, team_2 did (assuming no draws)
        if DEBUG_MODE:
            print("winner: " + str(team_2))
        return team_2
    else: 
                # if team_1 did not win, team_2 did (assuming no draws)
        if DEBUG_MODE:
            print("winner: " + str(team_3))
        return team_3

def resolve_single_knockout_tournament(brackets: list[tuple[Team, Team, Team]], rng_generator: np.random.Generator) -> Team:
    # while we're not in the final, resolve matches into new brackets
    while len(brackets) > 1:
        new_brackets = []
        for i in range(0, len(brackets), 3):
            new_bracket = (
                resolve_match(*brackets[i], rng_generator=rng_generator),
                resolve_match(*brackets[i+1], rng_generator=rng_generator),
                resolve_match(*brackets[i+2], rng_generator=rng_generator),
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
    if DEBUG_MODE:
        print("predicted winner: " + str(predicted_ranking[0]))
    # Returns winner but currently ignored
    grand_winner = resolve_single_knockout_tournament(brackets, rng_generator) 
    if DEBUG_MODE:
        print("grand winner: " + str(grand_winner))

    return predicted_ranking[0].get_name == grand_winner.get_name


def run_simulations(n, pools):
    now = datetime.datetime.now()
    ss = np.random.SeedSequence(int(round(now.timestamp())))
    seeds = ss.spawn(n)
    streams = [np.random.default_rng(seed) for seed in seeds]
    if DEBUG_MODE:
        return single_simulation(streams[0])
    else:
        with multiprocessing.Pool(pools) as p:
            return list(tqdm(p.imap(single_simulation, streams), total=len(streams)))



if __name__ == "__main__":
    if DEBUG_MODE:
        print("Running one simulation, at " + datetime.datetime.now().isoformat())
    else:
        print("Running %5d simulations for %2d team" % (args.n_simulations, args.n_teams))

    res = run_simulations(args.n_simulations, args.pools)

    success_prediction = sum(res)

    accuracy = success_prediction / len(res) * 100
    print("succesful predictions: " + str(success_prediction))
    print("Simulation finshed, accuracy: %5f percent" % (accuracy))