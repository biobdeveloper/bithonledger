from rncryptor import DecryptionError
from bit import PrivateKey, PrivateKeyTestnet
from bit.network import NetworkAPI, satoshi_to_currency, get_fee
from bit.network.fees import DEFAULT_FEE_FAST
from bit.transaction import address_to_scriptpubkey
from bit.exceptions import InsufficientFunds

from src.utils.bithonledger_msg import BithonledgerMSG as MSG
from src.utils import encrypt, decrypt, SessionController, logger_create
from src.exceptions import *
from config.system import ENCRYPT_ME


class BitcoinController:
    key = PrivateKey
    currency = 'Bitcoin'

    def __init__(self, **kwargs):
        self.debug = kwargs.get('debug')
        self.testnet = kwargs.get('testnet')
        self.interface = kwargs.get('interface')

        self.logger = logger_create(self.__name__, self.debug)
        self.logger.debug(f"Initialized")

        self.conn = SessionController(testnet=self.testnet, debug=self.debug)
        self.settings = self.conn.get_settings()
        if not self.settings:
            while True:
                try:
                    new_password_1 = input(MSG.create_password)
                    new_password_2 = input(MSG.repeat_password)
                    assert new_password_1 == new_password_2
                    self.password = new_password_1
                    _ecn_ex = encrypt(ENCRYPT_ME, self.password)
                    self.conn.add_settings(_ecn_ex)
                    self.logger.debug(MSG.password_created)
                    break
                except AssertionError:
                    self.logger.debug(MSG.passwords_not_match)
        else:
            while True:
                try:
                    self.password = input(MSG.input_msg['password'])
                    assert ENCRYPT_ME == decrypt(self.settings.encrypt_example, self.password)
                    self.logger.debug(MSG.unlocked)
                    break
                except DecryptionError:
                    self.logger.debug(MSG.wrong_password)
        if self.testnet:
            self.key = PrivateKeyTestnet

        self.commands = {'new': self.new,
                         'add': self.add,
                         'remove': self.remove,
                         'refresh': self.refresh,
                         'balance': self.balance,
                         'send': self.send,
                         'stop': self.stop,
                         'unknown_command': self.unknown_command_execute,
                         'test': self.test,
                         'wif': self.wif
                         }

        self._current_total_btc_balance = 0
        self.cached_wallet_info = dict()

    @property
    def __name__(self):
        return 'Bitcoin Controller'

    @property
    def _fee_schedule(self):
        try:
            return get_fee()
        except Exception as ex:
            self.logger.debug(ex)
            return DEFAULT_FEE_FAST

    def connect_interface(self, interface_instance):
        self.interface = interface_instance
        self.logger.debug(MSG.connected.format(self, interface_instance))

    def stop(self):
        self.logger.debug(MSG.exit)
        exit(0)

    def to_amount(self, raw_amount: any):
        try:
            if isinstance(raw_amount, str):
                raw_amount = raw_amount.replace(',', '.')
            return float(raw_amount)
        except:
            raise BadAmountError

    def to_address(self, raw_address):
        try:
            address_to_scriptpubkey(raw_address)
            return raw_address
        except:
            raise BadAddressError

    def to_wif(self, raw_wif):
        try:
            return self.key(raw_wif)
        except:
            raise BadWifError

    def _get_address_balance(self, address=None) -> float:
        if not address:
            address = self.interface.arg_input(param_wait_for='address')
        try:
            if self.testnet:
                balance = NetworkAPI.get_balance_testnet(address)
            else:
                balance = NetworkAPI.get_balance(address)
            p_balance = float(satoshi_to_currency(num=balance, currency='btc'))
        except ConnectionError:
            raise ExternalAPIsUnreachable
        return p_balance

    def _synchronize_user_balance(self):
        addresses = self.conn.get_all_addresses()
        for address in addresses:
            _balance = self._get_address_balance(address)
            self.cached_wallet_info[address] = _balance
            self._current_total_btc_balance += _balance
        self._current_total_btc_balance = sum([i for i in self.cached_wallet_info.values()])

    def _calculate_estimate_fee(self, wif, output, fee):
        estimate_tx = self.key(wif).create_transaction(outputs=output, fee=fee)
        estimate_tx_fee = float(satoshi_to_currency(
            num=len(estimate_tx) // 2,
            currency="btc")) * fee
        return estimate_tx_fee

    def _broadcast_finalized_tx(self, wif, output, fee=None):
        """
        :param wif: ``bit.Key object``
        :param output: ``tuple`` to, amount, "btc"
        :param fee: ``float`` satoshis per byte
        """
        try:
            if not fee:
                fee = self._fee_schedule
            return wif.send([output], fee=fee)
        except Exception as ex:
            return ex

    def _consolidate_tx(self, send_amount: float, to: str):
        outputs = {}
        self.logger.debug("Retrieve current network fee")
        fee_satperbyte = self._fee_schedule
        self.logger.debug("Fee is {}".format(fee_satperbyte))
        self.logger.debug("Retrieve all addresses with balances more than send amount")
        _balances = {k: v for k, v in self.cached_wallet_info.items() if v > send_amount}
        listed = list(_balances.keys())
        if not _balances:
            self.logger.debug("There is no single wallet with enough sum, let's try to build partially transaction")
            listed.sort()
        else:
            self.logger.debug("Iterate all addresses and check comission")
            listed.sort(reverse=True)
            self.logger.debug("calculate tx cost for every non-zero wallet")
            for address in listed:
                balance = _balances[address]
                try:
                    wif = decrypt(self.conn.get_wif(address), self.password)
                    _output = (to, send_amount, "btc")
                    estimate_tx_fee = self._calculate_estimate_fee(wif, [_output], fee_satperbyte)
                    self.logger.debug("estimate fee for {} is {} btc".format(address, estimate_tx_fee))
                    if balance >= send_amount + estimate_tx_fee:
                        outputs[wif] = [_output]
                        break
                except InsufficientFunds:
                    self.logger.debug(InsufficientFunds)
                except Exception as ex:
                    self.logger.debug(ex)

        if outputs:
            return [self._broadcast_finalized_tx(wif, output, fee=fee_satperbyte) for wif, output in outputs.items()]
        else:
            raise InsufficientFundsOnWallets

    def balance(self):
        """
        Process of 'balance' user's request. Return float balance of a single wallet in btc
        :return:
        """
        return self._get_address_balance()

    def refresh(self):
        """
        Process of 'refresh' user's request. Return float sum of all user's addresses balances
        :return: float
        """
        self._synchronize_user_balance()
        return self.cached_wallet_info, self._current_total_btc_balance

    def new(self):
        """
        Process of 'new' user's request
        :return: tuple(str, str)
        """
        _key = self.key()
        self.conn.add_wallet(_key.address, encrypt(_key.to_wif(), self.password))
        return _key.address, _key.to_wif()

    def add(self):
        """
        Process of 'add' user's request. Return True if wif was valid and added to database
        self._current_total_btc_balance automatically grown up to new address balance
        :return: bool
        """
        wif = self.interface.arg_input('wif', hide=True)
        if isinstance(wif, self.key):
            _add = self.conn.add_wallet(wif.address, encrypt(wif.to_wif(), self.password))
            if _add:
                self._current_total_btc_balance += self._get_address_balance(wif.address)
                return True
            else:
                raise WifAlreadyInBaseError

    def remove(self):
        """
        Process of 'remove' user's request. Delete bitcoin wallet from database.
        Return removed address if successfully deleted
        :return: str
        """
        address = self.interface.arg_input(param_wait_for='address')
        balance = self._get_address_balance(address)
        if balance > 0:
            self.logger.debug(MSG.warning_msg.wallet_not_empty.format(address, balance))
            _approve = self.interface.yes_no_input(to_do=MSG.remove_confirm.format(address, balance))
            if not _approve:
                raise UserCancellation
        removing = self.conn.remove_wif(address=address)
        if not removing:
            raise WalletNotInTheBaseError
        self._current_total_btc_balance -= balance
        return address

    def send(self):
        """
        Process of 'send' user's request
        :return:
        """
        to = self.interface.arg_input('address')
        self.logger.debug(MSG.warning_msg.send_to_your) if to in self.cached_wallet_info.keys() else None
        input_wif = self.interface.yes_no_input(to_do=MSG.enter_wallet_to_send)
        if input_wif:
            wif = self.interface.arg_input('wif', hide=True)
            send_amount = self.interface.arg_input('amount',
                                                   max=self._get_address_balance(address=wif.address))
            return self._broadcast_finalized_tx(wif, (to, send_amount, "btc"))
        else:
            send_amount = self.interface.arg_input('amount', max=self._current_total_btc_balance)
            return self._consolidate_tx(send_amount, to)

    def wif(self):
        _address = self.interface.arg_input('address')
        _wif = self.conn.get_wif(_address)
        self.logger.debug(_wif)
        return decrypt(_wif, self.password)

    def unknown_command_execute(self):
        return MSG.error_msg.unknown_command

    def test(self):
        self.logger.debug(self.conn.get_all_addresses())
        raise TestError

    def execute(self, command, *args, **kwargs):
        self.logger.debug(args) if args else None
        self.logger.debug(kwargs) if kwargs else None
        try:
            result = self.commands[command](*args, **kwargs)
            code = 0
        except Exception as ex:
            result = type(ex).__name__
            code = 1
        return {'code': code, 'result': result}
