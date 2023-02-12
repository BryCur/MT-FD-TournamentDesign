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
from tournaments import *
from AlaraMatch import AlaraMatch
from utils import *

from openskill import Rating, predict_win
import numpy as np
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--n-simulations', type=int, default=10000)
# number of pools, optimal number depends on the number of cores on your machine
parser.add_argument('-p', '--pools', type=int, default=4)
parser.add_argument('-t', '--n-teams', type=int, default=9)
args = parser.parse_args()



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

def single_simulation(rng_generator: np.random.Generator):
    teams = generate_teams(args.n_teams, rng_generator)
    predicted_ranking = predict_result(teams, False)
    playedTournament = TournamentSingleKnockout(teams, rng_generator)
    # brackets = teams_to_brackets(teams)
    if DEBUG_MODE:
        print("predicted winner: " + str(predicted_ranking[0]))
    # Returns winner but currently ignored
    grand_winner = playedTournament.play() #resolve_single_knockout_tournament(brackets, rng_generator) 
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