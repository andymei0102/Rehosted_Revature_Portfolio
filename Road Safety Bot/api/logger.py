import logging

def setup_app_logger(name, logfile="./logger/app.log"):
    """Configure a custom logger."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )

        # Console handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        # File handler
        file_handler = logging.FileHandler(logfile)
        file_handler.setFormatter(formatter)

        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

    return logger

def setup_email_logger(name, logfile="./logger/emails.log"):
    """Configure a custom logger."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )

        # Console handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        # File handler
        file_handler = logging.FileHandler(logfile)
        file_handler.setFormatter(formatter)

        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

    return logger
