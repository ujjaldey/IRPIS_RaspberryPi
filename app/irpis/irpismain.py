from time import sleep

from app.irpis.irpismainhelper import IrpisMainHelper


class IrpisMain(IrpisMainHelper):
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config
        self.display = None
        self.mqtt_client = None

    def set_display(self, display):
        self.display = display

    def set_mqtt_client(self, mqtt_client):
        self.mqtt_client = mqtt_client

    def start(self):
        counter = 0
        while True:
            self.logger.info("Calling IRPIS main")
            # TODO should be checked at certain interval only
            self.display.set_wifi_online(self._is_internet_connected())

            if counter >= 20:
                duration = 5
                self.mqtt_client.turn_on_payload(duration)
                counter = 0

            counter += 1
            sleep(1)
