"""
Model util module
"""
import os
from sqlalchemy.ext.declarative import declarative_base

DB_SCHEMA = os.getenv('DB_SCHEMA', 'tpt')
BASE = declarative_base()
