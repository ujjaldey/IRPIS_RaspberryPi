from app.bot.telegrambot import TelegramBot
from app.broker.mqttbroker import MqttBroker
from app.display.oleddisplay import OledDisplay
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

        self.mqtt_broker = MqttBroker(self.config, self.logger)
        self.telegram_bot = TelegramBot(self.config, self.logger, self.db)
        self.telegram_bot.add_handlers()
        self.display = OledDisplay(self.config, self.logger)
        self.irpis = IrpisMain(self.config, self.logger)

    def start(self):
        self.logger.info('Starting IRPIS_RaspberryPi')

        thread_fns = [self.__start_mqtt_telegrambot, self.__start_display_main, self.__start_irpis_main]
        threads = []

        for tfn in thread_fns:
            thread = Thread(target=tfn)
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()

    # TODO split this in separate functions and threads
    def __start_mqtt_telegrambot(self):
        self.logger.info('Creating new thread for MQTT & TelegramBot')

        self.mqtt = self.mqtt_broker.connect()
        self.telegram_bot.set_mqtt(self.mqtt)
        self.telegram_bot.start()

    def __start_display_main(self):
        self.mqtt_broker.set_display(self.display)
        self.display.start()

    def __start_irpis_main(self):
        self.irpis.set_display(self.display)
        self.irpis.start()


if __name__ == '__main__':
    try:
        main = Main()
        main.start()
    except KeyboardInterrupt:
        pass
