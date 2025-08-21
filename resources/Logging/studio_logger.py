import os
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Log_levels = {'CRITICAL': 50, 'ERROR': 40, 'WARNING': 30, 'INFO': 20, 'DEBUG': 10}


class Logger:
    def __init__(self, use_case_id: str):
        self.log = self.get_logger(logger_id=use_case_id)

    def debug(self, logging_string):
        """
        Provide Logger for debug states, ensure debug level is set.
        """
        self.log.debug(logging_string, exc_info=True)

    def info(self, logging_string):
        """
        Provide Logger for Info states, ensure debug level is set.
        """
        self.log.info(logging_string)

    def warning(self, logging_string):
        """
         Provide Logger for warning states, ensure debug level is set.
        """
        self.log.warning(logging_string, exc_info=True)

    def error(self, logging_string,throw:bool=True):
        """
            Provide Logger for Error states, ensure debug level is set.
        """
        self.log.error(logging_string, exc_info=True)
        if throw:
            raise Exception(logging_string)

    def critical(self, logging_string):
        """
            Provide Logger for critical states, ensure debug level is set.
        """
        self.log.critical(logging_string, exc_info=True)

    def __log_file(self, logger_id):
        """
        logger_id: flow_id to create dedicated log file
        """
        log_file = BASE_DIR + os.getenv("logFile") + str(logger_id) + ".log"
        return log_file

    def get_logger(self, logger_id):
        """
        provide logger which will be used for logging
        """
        # logfile_path = self.__log_file(logger_id)
        """creates a logger for the processes"""
        try:
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)
            if os.getenv("LOG_LEVEL") and os.getenv("LOG_LEVEL") in Log_levels:
                LEVEL = Log_levels[os.getenv("LOG_LEVEL")]
            else:
                LEVEL = Log_levels['INFO']

            if os.getenv("IS_TERMINAL") == "True":
                logging.basicConfig(level=LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                    handlers=[logging.StreamHandler()]
                                    )

            else:
                logging.basicConfig(level=LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                    handlers=[]
                                    )

        except OSError as err:
            raise Exception(f"Error in creating logger due to {err}")
        log = logging.getLogger(logger_id)
        return log


def log(use_case: str):
    """
    this will initialize logger for global usage with respect to specific use case and will register
    the logs based on selected usecase
    @param use_case: selected usecase to run and setting up logger
    @return: will return the log instance
    """
    return Logger(use_case_id=use_case)
