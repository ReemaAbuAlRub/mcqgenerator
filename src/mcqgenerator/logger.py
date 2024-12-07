import logging 
import os 
from  datetime import datetime 

logging.basicConfig(
    level=logging.INFO,
    filename='logs/logger.log',
    format="[%(asctime)s] %(filename)s:%(lineno)d %(name)s - %(levelname)s - %(message)s"
)
