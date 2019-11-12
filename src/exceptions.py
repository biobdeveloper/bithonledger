class ParamWrongSpecifiedError(Exception):
    pass


class BadWifError(Exception):
    pass


class WifAlreadyInBaseError(Exception):
    pass


class BadAddressError(Exception):
    pass


class BadAmountError(Exception):
    pass


class UserCancellation(Exception):
    pass


class TestError(Exception):
    pass


class InsufficientFundsOnWallets(Exception):
    pass

class WalletNotInTheBaseError(Exception):
    pass

class ExternalAPIsUnreachable(Exception):
    pass