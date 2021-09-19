from threading import Thread
from time import sleep

from app.bot.telegrambot import TelegramBot
from app.display.oleddisplay import OledDisplay
from app.irpis.irpismain import IrpisMain
from app.mq.client.mqttclient import MqttClient
from app.util.config import Config
from app.util.logger import Logger
from app.util.sqlitedb import SqliteDb


class Main:
    def __init__(self):
        logger = Logger(__file__)
        self.logger = logger.get_logger()

        self.config = Config()
        self.db = SqliteDb(self.config)

        self.mqtt_client = MqttClient(self.logger, self.config, self.db)
        self.telegram_bot = TelegramBot(self.logger, self.config)
        self.telegram_bot.add_handlers()
        self.display = OledDisplay(self.logger, self.config)
        self.irpis = IrpisMain(self.logger, self.config, self.db)

        self.thread_fns = [self.__start_mqtt_telegrambot, self.__start_display_main, self.__start_irpis_main]
        self.threads = []

    def start(self):
        self.logger.info('Starting IRPIS_RaspberryPi')

        for thread_fn in self.thread_fns:
            thread = Thread(target=thread_fn)
            thread.start()
            self.threads.append(thread)

        for thread in self.threads:
            thread.join()

    # TODO split this in separate functions and threads
    def __start_mqtt_telegrambot(self):
        self.logger.info('Creating new thread for MQTT & TelegramBot')

        try:
            self.mqtt_client.connect()
            self.telegram_bot.set_mqtt_client(self.mqtt_client)
            self.telegram_bot.start()
        except Exception as ex:
            self.logger.fatal("Exception in __start_mqtt_telegrambot: " + str(ex), exc_info=True)

    def __start_display_main(self):
        self.logger.info('Creating new thread for Display')

        try:
            self.mqtt_client.set_display(self.display)
            self.display.start()
        except Exception as ex:
            self.logger.fatal("Exception in __start_display_main: " + str(ex), exc_info=True)

    def __start_irpis_main(self):
        self.logger.info('Creating new thread for IRPIS Main')

        try:
            # Wait for MQTT to be started
            while not self.mqtt_client.is_connected():
                self.logger.info('Waiting for connecting to the MQTT')
                sleep(0.5)

            self.logger.info('MQTT is not connected')
            self.irpis.set_display(self.display)
            self.irpis.set_mqtt_client(self.mqtt_client)
            self.irpis.start()
        except Exception as ex:
            self.logger.fatal("Exception in __start_irpis_main: " + str(ex), exc_info=True)

    def terminate(self):
        self.logger.info("Terminating")
        self.display.cleanup()


if __name__ == '__main__':
    main = Main()

    try:
        main.start()
    except (KeyboardInterrupt, SystemExit):
        main.terminate()
