import logging
import os


class Logger:
    def __init__(self, file_name):
        formatter = logging.Formatter("%(asctime)s|%(levelname)s|%(message)s", "%Y-%m-%d %H:%M:%S")

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        log_file = self.__get_log_file_name(file_name)
        log_handler = logging.FileHandler(log_file)
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        self.logger = logger

    def get_logger(self):
        return self.logger

    @staticmethod
    def __get_log_file_name(file_name):
        path = os.path.dirname(os.path.abspath(file_name))
        log_path = os.path.join(path, "log")
        if not os.path.exists(log_path):
            os.mkdir(log_path)

        return os.path.join(log_path, os.path.basename(file_name).replace(".py", ".log"))
