from threading import Thread
from time import sleep

from app.bot.telegrambot import TelegramBot
from app.display.oleddisplay import OledDisplay
from app.irpis.irpismain import IrpisMain
from app.mq.client.mqttclient import MqttClient
from util.config import Config
from util.logger import Logger


class Main:
    def __init__(self):
        logger = Logger(__file__)
        self.logger = logger.get_logger()

        self.config = Config()
        self.db = None  # @TODO

        self.mqtt_client = MqttClient(self.config, self.logger)
        self.telegram_bot = TelegramBot(self.config, self.logger)
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

        try:
            self.mqtt = self.mqtt_client.connect()
            self.telegram_bot.set_mqtt(self.mqtt)
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
            self.irpis.set_mqtt(self.mqtt)
            self.irpis.start()
        except Exception as ex:
            self.logger.fatal("Exception in __start_irpis_main: " + str(ex), exc_info=True)

    def terminate(self):
        self.logger.info("Terminating")
        self.display.cleanup()


if __name__ == '__main__':
    try:
        main = Main()
        main.start()
    except KeyboardInterrupt:
        main.terminate()
