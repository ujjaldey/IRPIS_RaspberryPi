class TelegramBotHelper:
  def _set_logger(self, logger):
    self.logger = logger

  def _set_config(self, config):
    self.config = config

  def _set_db(self, db):
    self.db = db
    # self.conn = db.connect()
