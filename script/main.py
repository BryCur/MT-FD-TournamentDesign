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
import uuid
from Team import Team # we represent a team with a name and a rating
from tournaments import *
from utils import *
from RankingComparator import kendall_tau_distance
from Logger import Logger
from csvManager import *

from openskill import Rating
import numpy as np
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--n-simulations', type=int, default=10000)
# number of pools, optimal number depends on the number of cores on your machine
parser.add_argument('-p', '--pools', type=int, default=4)
parser.add_argument('-t', '--n-teams', type=int, default=27)
parser.add_argument('-f', '--format', type=int, default=3) # 1-single knockout, 2-round robin, 3-Swiss system, 4-custom
args = parser.parse_args()

g_folder_name = "./simulations/"


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

def single_simulation(input: tuple[np.random.Generator, str]):
    simulation_uid = uuid.uuid4().hex

    simulation_log_file = f"{input[1]}logs/{simulation_uid}.log"

    #print(simulation_log_file)
    logger = Logger(simulation_uid, filepath=simulation_log_file)
    teams = generate_teams(args.n_teams, input[0])
    predicted_ranking = predict_result(teams, False)
    logger.logRanking("Predicted", predicted_ranking)

    # playedTournament = TournamentSingleKnockout(teams, input[0], logger)
    playedTournament = None

    match args.format:
        case 1: playedTournament = TournamentSingleKnockout(teams, input[0], logger)
        case 2: playedTournament = tournamentRoundRobin(teams, input[0], logger)
        case 3: playedTournament = tournamentSwissSystem(teams, input[0], logger, 8)
        case 4: playedTournament = tournamentCustom(teams, input[0], logger)
    
    # Returns winner but currently ignored
    resulting_ranking = playedTournament.play() #resolve_single_knockout_tournament(brackets, rng_generator) 
    match_count = playedTournament.getMatchCount()
    tie_count = playedTournament.getTieCount()
    complete_duplicate_match_count = playedTournament.getCompleteDuplicateMatchupCount()
    kt_ranking_distance = kendall_tau_distance(predicted_ranking, resulting_ranking)

    logger.logRanking("Resulting", resulting_ranking)
    logger.logInfoMessage(f"Kendall Tau Distance: {kt_ranking_distance}")

    return simulation_uid, *kt_ranking_distance, match_count, tie_count, complete_duplicate_match_count


def run_simulations(n, pools):
    global g_folder_name
    now = datetime.datetime.now()
    ss = np.random.SeedSequence(int(round(now.timestamp())))
    seeds = ss.spawn(n)
    streams = [(np.random.default_rng(seed), g_folder_name) for seed in seeds]
    

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

    g_folder_name = g_folder_name if DEBUG_MODE  else f"./simulations/{datetime.datetime.now().strftime('%Y%m%d_%H-%M-%S')}-{args.n_simulations}s-{args.n_teams}t-{getTournamentFormatStr(args.format).replace(' ', '')}/"

    res = run_simulations(args.n_simulations, args.pools)

    if DEBUG_MODE: 
        success_prediction = res 
    else: 
        headers = ["simId", "kendalTauDistance", "disagreement", "matchCount", "tieCount", "completeDuplicateMatches"]
        results_to_csv(res, headers, g_folder_name)
        