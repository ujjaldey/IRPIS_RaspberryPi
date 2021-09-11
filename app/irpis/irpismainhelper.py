from time import sleep


class IrpisMainHelper:
    def _set_logger(self, logger):
        self.logger = logger

    def _set_config(self, config):
        self.config = config

    def _set_display(self, display):
        self.display = display

    def _main(self):
        on = True
        while True:
            self.logger.info("Calling IRPIS main")

            # self.display.toggle_display_on_off(on)
            # sleep(5 if on else 30)
            # on = not on

            sleep(10)
