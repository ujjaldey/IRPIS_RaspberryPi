import subprocess
from threading import Thread
from time import sleep, time

from RPi import GPIO

from app.bot.telegrambot import TelegramBot
from app.display.oleddisplay import OledDisplay
from app.input.actionbutton import ActionButton
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

        app_start_time = time()

        self.mqtt_client = MqttClient(self.logger, self.config, self.db)
        self.telegram_bot = TelegramBot(self.logger, self.config, self.db, app_start_time)
        self.telegram_bot.add_handlers()
        self.display = OledDisplay(self.logger, self.config)
        self.irpis = IrpisMain(self.logger, self.config, self.db)
        self.action_button = ActionButton(self.logger, self.config, self.db, self.mqtt_client, self.display)

        self.thread_fns = [self.__start_mqtt_client,
                           self.__start_telegrambot,
                           self.__start_display_main,
                           self.__start_irpis_main,
                           self.__start_action_button]
        self.threads = []

    def is_process_already_running(self):
        command = 'ps -ef | grep main.py'
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        processes = result.stdout.decode("utf-8").split("\n")
        process_count = 0

        for process in processes:
            if 'python' in process:
                process_count += 1
        if process_count > 1:
            self.logger.error('Another instance is already running')
            return True
        else:
            return False

    def start(self):
        self.logger.info('Starting IRPIS_RaspberryPi')

        for thread_fn in self.thread_fns:
            thread = Thread(target=thread_fn)
            thread.start()
            self.threads.append(thread)

        for thread in self.threads:
            thread.join()

    def __start_mqtt_client(self):
        self.logger.info('Creating new thread for MQTT Client')

        try:
            self.mqtt_client.connect()
        except Exception as ex:
            self.logger.fatal('Exception in __start_mqtt_client: ' + str(ex), exc_info=True)

    def __start_telegrambot(self):
        self.logger.info('Creating new thread for TelegramBot')

        try:
            self.telegram_bot.set_mqtt_client(self.mqtt_client)
            self.telegram_bot.start()
        except Exception as ex:
            self.logger.fatal('Exception in __start_telegrambot: ' + str(ex), exc_info=True)

    def __start_display_main(self):
        self.logger.info('Creating new thread for Display')

        try:
            self.telegram_bot.set_display(self.display)
            self.mqtt_client.set_display(self.display)
            self.display.start()
        except Exception as ex:
            self.logger.fatal('Exception in __start_display_main: ' + str(ex), exc_info=True)

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
            self.logger.fatal('Exception in __start_irpis_main: ' + str(ex), exc_info=True)

    def __start_action_button(self):
        self.logger.info('Creating new thread for buttons')

        try:
            self.action_button.register_buttons()
        except Exception as ex:
            self.logger.fatal('Exception in __start_action_button: ' + str(ex), exc_info=True)

    def terminate(self):
        self.logger.info('Terminating')
        self.display.cleanup()


if __name__ == '__main__':
    GPIO.setwarnings(False)
    main = Main()

    try:
        if not main.is_process_already_running():
            main.start()
    except (KeyboardInterrupt, SystemExit):
        main.terminate()
    finally:
        pass
