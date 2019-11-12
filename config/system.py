"""This is system config, there is no data that need to be changed.
All user's data saved in bitcoin_base.db
"""
from pathlib import Path

project_root_dir = Path(__file__).parent.parent
DATABASE_NAME = 'bitcoin_base.db'
ENCRYPT_ME = "ENCRYPT_ME"
