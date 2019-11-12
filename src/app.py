from src.bitcoin_contoller import BitcoinController
from src.interfaces import interfaces
from argparse import ArgumentParser


def main():
    parser = ArgumentParser()
    parser.add_argument('-t', '--testnet', default=None, type=bool, help='If not, run the mainnet')
    parser.add_argument('-i', '--interface', default='cli', type=str, help='Interface (cli, gui, telegram, etc.')
    parser.add_argument('-e', '--execute', default='', type=str, help='Execute some bitcoin stuff')
    parser.add_argument('-d', '--debug', default=False, type=bool, help="Debug mode")
    args = parser.parse_args()

    testnet = args.testnet
    interface = args.interface
    debug = args.debug

    controller = BitcoinController(testnet=testnet, debug=debug)

    client = interfaces.get(interface)(controller=controller)
    controller.connect_interface(client)

    client.input_loop()
