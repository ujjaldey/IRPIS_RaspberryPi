from app.telegrambot import TelegramBot
from util.config import Config
from util.logger import Logger


class Main:
  def __init__(self):
    logger = Logger(__file__)
    self.logger = logger.get_logger()

    self.config = Config()
    self.db = None  # Config()  # @ TODO

  def start(self):
    self.logger.info("Starting IRPIS_RaspberryPi")
    telegram_bot = TelegramBot(self.config, self.logger, self.db)


if __name__ == '__main__':
  main = Main()
  main.start()
