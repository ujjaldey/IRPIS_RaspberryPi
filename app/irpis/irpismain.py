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
        self._main()
