from app.irpis.irpismainhelper import IrpisMainHelper


class IrpisMain(IrpisMainHelper):
    def __init__(self, config, logger):
        self._set_logger(logger)
        self._set_config(config)

    def set_display(self, display):
        self._set_display(display)

    def start(self):
        self._main()
