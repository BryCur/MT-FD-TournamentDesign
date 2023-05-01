TEAMS_IN_ONE_MATCH = 3
DEBUG_MODE = 0
SAVE_LOGS = 1
DISPLAY_LOGS = 1
PERFORM_SEED = 0 # could be nice to implement

def is_integer(x) -> bool:
    """
    Checks if a number is an integer, mathematically.
    """
    return x % 1 == 0

def getTournamentFormatStr(format) -> str:
    match format:
        case 1: return "Single Knockout"
        case 2: return "Round-Robin"
        case 3: return "Swiss System"
        case 4: return "Custom" 