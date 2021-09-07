from time import sleep


class IrpisMainHelper:
    def _set_logger(self, logger):
        self.logger = logger

    def _set_config(self, config):
        self.config = config

    def _main(self):
        while True:
            self.logger.info("Calling IRPIS main")
            sleep(10)
