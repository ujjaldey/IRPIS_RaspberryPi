from app.irpis.irpismainhelper import IrpisMainHelper


class IrpisMain(IrpisMainHelper):
    def __init__(self, config, logger):
        self._set_logger(logger)
        self._set_config(config)

    def start(self):
        self._main()
