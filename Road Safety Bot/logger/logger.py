import logging
import psycopg2
import datetime
from logging.handlers import QueueHandler, QueueListener
class PostgreSQLHandler(logging.Handler):
    def __init__(self, db_config, table_name):
        super().__init__()
        self.db_config = db_config
        self.table_name = table_name

    def emit(self, record):
        try:
            dt_timestamp = datetime.datetime.fromtimestamp(record.created)
            formatted_time = dt_timestamp.strftime('%Y-%m-%d %H:%M:%S')

            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            query = f"""
                INSERT INTO {self.table_name} (asc_time, name, level_name, messages) 
                VALUES (%s, %s, %s, %s);
            """
            cursor.execute(query, (formatted_time, record.name, record.levelname, record.message))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception:
            self.handleError(record)

import queue

def setup_logger(name, table_name, use_queue, db_config = {"dbname": "logs", "user": "postgres", "password": "password", "host": "localhost", "port": "5432"}):
    """
    Configures a logger with a PostgreSQL handler.
    
    Args:
        name: Name of the logger.
        table_name: Database table to write to.
        db_config: Dictionary of DB credentials.
        use_queue: If True, uses a background thread (non-blocking).
    """
    logger = logging.getLogger(name)
    
    # Avoid re-adding handlers if the logger is already configured
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    
    # 1. Initialize the PostgreSQL handler
    db_handler = PostgreSQLHandler(db_config, table_name)
    
    # Formatter is only needed if you are also printing to console or file,
    # but I've kept it here per your original code.
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(messages)s', datefmt='%H:%M:%S')
    db_handler.setFormatter(formatter)

    # 2. Add handler either directly or via queue
    if use_queue:
        log_queue = queue.Queue()
        # The listener runs in a background thread to handle DB writes
        listener = QueueListener(log_queue, db_handler)
        listener.start()
        
        # Attach the queue handler to the logger
        queue_handler = logging.handlers.QueueHandler(log_queue)
        logger.addHandler(queue_handler)
    else:
        # Standard synchronous logging (blocks the main thread)
        logger.addHandler(db_handler)

    return logger
