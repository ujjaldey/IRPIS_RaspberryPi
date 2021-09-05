from app.bot.telegrambot import TelegramBot
from app.broker.mqttbroker import MqttBroker
from util.config import Config
from util.logger import Logger


class Main:
    def __init__(self):
        logger = Logger(__file__)
        self.logger = logger.get_logger()

        self.config = Config()
        self.db = None  # Config()  # @ TODO

    def start(self):
        self.logger.info('Starting IRPIS_RaspberryPi')

        mqtt_borker = MqttBroker(self.config, self.logger)
        mqtt = mqtt_borker.connect()

        telegram_bot = TelegramBot(self.config, self.logger, self.db, mqtt)
        telegram_bot.add_handlers()
        telegram_bot.start()


if __name__ == '__main__':
    main = Main()
    main.start()
