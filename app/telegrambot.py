from app.telegrambothelper import TelegramBotHelper


class TelegramBot(TelegramBotHelper):
  def __init__(self, config, logger, db):
    self._set_logger(logger)
    self._set_config(config)
    self._set_db(db)
