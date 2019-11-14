"""Bithonledger command line interface

"""
import getpass
import string

from src.utils.bithonledger_msg import BithonledgerMSG as MSG
from src.exceptions import UserCancellation
from config.system import YES_ANSWERS


def filtered_string(text):
    return ''.join(filter(lambda x: x in string.printable, text))


class Cli:
    name = 'cli'

    def __init__(self, controller):
        print(MSG.start.format(self.__name__))
        print(filtered_string(MSG.commands))
        self.controller = controller

    @property
    def __name__(self):
        return Cli.name

    def arg_input(self, param_wait_for, **kwargs):
        _msg = MSG.input_msg[param_wait_for]

        # Only when param_wait_for is amount
        if kwargs.get('max'):
            _msg += str(kwargs.get('max')) + "\n"

        if not kwargs.get('hide'):
            _input = input
        else:
            _input = getpass.getpass

        _msg += MSG.cancel_instruction

        while True:
            try:
                raw = _input(_msg)
                if not raw:
                    continue
                if param_wait_for == 'amount':
                    max = self.controller.to_amount(kwargs.get('max'))
                    arg = self.controller.to_amount(raw)
                    if arg > max:
                        continue
                elif param_wait_for == 'wif':
                    arg = self.controller.to_wif(raw)
                elif param_wait_for == 'address':
                    arg = self.controller.to_address(raw)
                elif param_wait_for == 'password':
                    arg = raw
                else:
                    raise

                return arg
            except KeyboardInterrupt:
                raise UserCancellation
            except Exception as ex:
                print(MSG.error_msg.bad_input)

    def _parse_command(self, raw):
        command = raw.split()[0]
        # TODO parse arguments from user input
        if self.controller.commands.get(command):
            return command
        return "unknown_command"

    @classmethod
    def _format_response(cls, command: str,
                         result: any,
                         code: int = 0):
        result = [result] if not isinstance(result, tuple) else result
        pretty_result = MSG.result_msg[command][code]
        if not code:
            if command == 'refresh':
                pretty_dict = str()
                for k, v in result[0].items():
                    pretty_dict += "{} :  {} btc\n".format(k, v)
                result = [pretty_dict, result[1]]
        if '{}' in pretty_result:
            pretty_result = pretty_result.format(*result)
        return pretty_result

    def yes_no_input(self, to_do=MSG.do_this):
        answer = input(MSG.input_msg['yes_no'].format(to_do))
        if answer in YES_ANSWERS:
            return True
        return False

    def input_loop(self):
        while True:
            try:
                command = input(MSG.input_msg['command'])
                if not command:
                    continue
                parsed_command = self._parse_command(command)
                result = self.controller.execute(parsed_command)
                print(self._format_response(parsed_command, **result))
            except KeyboardInterrupt or EOFError:
                self.controller.execute('stop')
