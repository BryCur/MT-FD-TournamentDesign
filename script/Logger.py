import logging
import os
from Team import Team

class Logger:
    def __init__(self, name, level=logging.DEBUG, filepath=None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        
        if filepath:
            log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), filepath)
            log_file = os.path.normpath(log_file) # normalize path separators
            log_folder = os.path.dirname(log_file)
            
            if not os.path.exists(log_folder):
                os.makedirs(log_folder)

            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        else:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
    def logRanking(self, name:str, ranking: list[Team]):
        self.logger.info(f"{name} ranking : -----------------")
        for i in range(len(ranking)):
            self.logger.info(f"{i+1} - {ranking[i].get_name()} ({ranking[i].get_rating_str()} | {ranking[i].get_score_str()})")

    def logWinningOdds(self, teams: tuple[Team, Team, Team], odds: list[float]): 
        self.logger.info("winning odds for teams ---------------------------------")
        for i in range(3):
            self.logger.info(f"{teams[i].get_name()}: {odds[i]}")

    def logInfoMessage(self, message: str):
        self.logger.info(message)

    def logWarningMessage(self, message: str):
        self.logger.warning(message)

    def logErrorMessage(self, message: str):
        self.logger.error(message)
    

    