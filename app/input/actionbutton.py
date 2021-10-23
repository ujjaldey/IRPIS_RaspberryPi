from signal import pause

from gpiozero import Button

from app.enum.actionbuttonenum import ActionButtonEnum
from app.enum.mqttclientenum import MqttClientEnum
from app.util.common import Common


class ActionButton:
    def __init__(self, logger, config, db, mqtt_client, display):
        self.logger = logger
        self.config = config
        self.db = db
        self.mqtt_client = mqtt_client
        self.display = display

        self.conn = db.connect().execution_options(autocommit=True)
        self.common = Common()

    def register_buttons(self):
        debounce_time = ActionButtonEnum.BUTTON_DEBOUNCE_TIME_SEC.value
        wakeup_button_pin = ActionButtonEnum.BUTTON_WAKEUP_GPIO_PIN.value
        adhoc_button_pin = ActionButtonEnum.BUTTON_ADHOC_GPIO_PIN.value
        skip_button_pin = ActionButtonEnum.BUTTON_SKIP_GPIO_PIN.value

        btn_wakeup = Button(wakeup_button_pin, bounce_time=debounce_time)
        btn_adhoc = Button(adhoc_button_pin, bounce_time=debounce_time)
        btn_skip = Button(skip_button_pin, bounce_time=debounce_time)

        btn_wakeup.when_pressed = self.__on_wakeup_button_clicked
        btn_adhoc.when_pressed = self.__on_adhoc_button_clicked
        btn_skip.when_pressed = self.__on_skip_button_clicked

        pause()

    def __on_wakeup_button_clicked(self):
        self.logger.info("__on_wakeup_button_clicked is called")

        self.display.display_on_off(True)

    def __on_adhoc_button_clicked(self):
        self.logger.info("__on_adhoc_button_clicked is called")

        self.mqtt_client.turn_on_payload(self.config.get_default_payload_duration_sec(),
                                         MqttClientEnum.TRIGGER_MANUAL.value)

    def __on_skip_button_clicked(self):
        self.logger.info("__on_skip_button_clicked is called")

        curr_schedule, next_schedule, next_duration, success = self.common.skip_next_execution(self.conn, self.config)
