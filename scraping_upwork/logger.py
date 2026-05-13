import logging
import coloredlogs
import os


class Logger:
    def __init__(self,name='Upwork Scraper', level="DEBUG"):
        self.logger = logging.getLogger(name)
        self._set_level(level)
        self._setup_coloredlogs()

    def get_logger(self):
        return self.logger
    
    def _set_level(self,level):
        self.logger.setLevel(level)

    def _setup_coloredlogs(self):
        level_styles = {
            'debug': {'color': 'blue'},
            'info': {'color': 'green'},
            'warning': {'color': 'yellow'},
            'error': {'color': 'red'},
            'critical': {'color': 'red', 'bold': True},
        }
        field_styles = {
            'asctime': {'color': 'white'},
            'name': {'color': 'magenta', 'bold': False},
            'levelname': {'color': 'cyan', 'bold': False},
        }
        coloredlogs.install(
            level=self.logger.level,
            logger=self.logger,
            fmt="%(asctime)s %(levelname)-8s %(name)s  %(message)s",
            level_styles=level_styles,
            field_styles=field_styles
        )