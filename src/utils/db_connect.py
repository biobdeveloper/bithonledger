"""
Database ORM and SQL-session control
"""
import datetime

from sqlalchemy import create_engine
from sqlalchemy import Column, DateTime, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError

from src.utils import logger_create
from config.system import DATABASE_NAME, project_root_dir


engine = create_engine("sqlite:///" + str(project_root_dir) + '/' + DATABASE_NAME, echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True)
    address = Column(String, unique=True)
    wif = Column(String, unique=True)
    added = Column(DateTime, default=datetime.datetime.now())


class TestnetWallet(Base):
    __tablename__ = "testnetwallets"

    id = Column(Integer, primary_key=True)
    address = Column(String, unique=True)
    wif = Column(String, unique=True)
    added = Column(DateTime, default=datetime.datetime.now())


class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    auto_refresh = Column(Boolean, default=False)
    encrypt_example = Column(String, unique=True)


Base.metadata.create_all(engine)


class SessionController:
    wallet = Wallet

    @property
    def __name__(self):
        return 'SessionController'

    def __init__(self,  **kwargs):
        self.debug = kwargs.get('debug')
        self.logger = logger_create(self.__name__, self.debug)
        self.logger.debug("Initialized")
        self.session = Session()
        self.testnet = kwargs.get('testnet')
        if self.testnet:
            self.wallet = TestnetWallet

    def get_settings(self):
        return self.session.query(Setting).first()

    def add_settings(self, enc_ex):
        new_settings = Setting()
        new_settings.encrypt_example = enc_ex
        self.session.add(new_settings)
        self.session.commit()
        return True

    def add_wallet(self, address, wif):
        try:
            wallet = self.wallet(address=address, wif=wif)
            self.session.add(wallet)
            self.session.commit()
            return True
        except IntegrityError:
            self.logger.debug("WIF of wallet {} already in base, skipped".format(address))
            return False

    def get_wif(self, address):
        _wallet = self.session.query(self.wallet.wif).filter(self.wallet.address == address).first()[0]
        return _wallet

    def get_all_addresses(self):
        _addresses = self.session.query(self.wallet.address).all()
        return [i[0] for i in _addresses]

    def remove_wif(self, address):
        wallet_to_delete = self.session.query(self.wallet).filter(self.wallet.address == address).first()
        if wallet_to_delete:
            self.session.delete(wallet_to_delete)
            self.session.commit()
            return True
