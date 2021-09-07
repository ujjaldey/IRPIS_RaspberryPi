from app.bot.telegrambot import TelegramBot
from app.broker.mqttbroker import MqttBroker
from app.irpis.irpismain import IrpisMain
from util.config import Config
from util.logger import Logger
from threading import Thread


class Main:
    def __init__(self):
        logger = Logger(__file__)
        self.logger = logger.get_logger()

        self.config = Config()
        self.db = None  # Config()  # @ TODO

    def start(self):
        self.logger.info('Starting IRPIS_RaspberryPi')

        telegram_thread = Thread(target=self.__start_mqtt_telegrambot)
        irpis_thread = Thread(target=self.__start_irpis_main)
        telegram_thread.start()
        irpis_thread.start()

        telegram_thread.join()
        irpis_thread.join()

    def __start_mqtt_telegrambot(self):
        self.logger.info('Creating new thread for MQTT & TelegramBot')
        mqtt_broker = MqttBroker(self.config, self.logger)
        mqtt = mqtt_broker.connect()

        telegram_bot = TelegramBot(self.config, self.logger, self.db, mqtt)
        telegram_bot.add_handlers()
        telegram_bot.start()

    def __start_irpis_main(self):
        irpis = IrpisMain(self.config, self.logger)
        irpis.start()


if __name__ == '__main__':
    main = Main()
    main.start()
