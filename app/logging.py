import logging


def setup_loggers(app):
    #main logger
    main_logger = app.logger
    handler = logging.FileHandler('app.log')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    main_logger.addHandler(handler)

    #hp log
    honeypot_logger = logging.getLogger('honeypot')
    honeypot_handler = logging.FileHandler('honeypot.log')
    honeypot_handler.setLevel(logging.WARNING)
    honeypot_handler.setFormatter(formatter)
    honeypot_logger.addHandler(honeypot_handler)
