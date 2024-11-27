# from sqlalchemy import create_engine
#
# from config import config
# from models import BaseCommon
# from services.repository import Repo
#
# def create():
#     db = config.db
#     engine = create_engine(f"postgresql+asyncpg://{db.user}:{db.password}@{db.address}/{db.name}")
#     BaseCommon.metadata.create_all(engine)
