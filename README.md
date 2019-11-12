# Bithonledger

Light bitcoin wallet implementation. Build on top of [bit](https://github.com/ofek/bit) library.

### Curently support
* Only public APIs (Using Bitcoin-RPC coming soon)
* Sending transactions
* Retrieving balances
* Generating new bitcoin keys
* Encrypted local storage for your private keys
* Working with client console input (bash commands execution with args coming soon)
* Only CLI interface (GUI, WEB and even Telegram interfaces may be implemented in the future)
* Mainnet and testnet is available

## Requirements
* [Python](https://www.python.org/downloads) >= 3.7

## Install and run
```bash
git clone https://github.com/biobdeveloper/bithonledger
python3.7 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
python bithonledger
```


###Arguments
* `-t, --testnet` Work with _testnet_ bitcoin blockchain, all features and commands are the same as _mainnet_
* `-d, --debug` Debug mode

## How it works
* Working only with WIF(Wallet import format)
* All your WIFs stored locally in sqlite3-database file 'bitcoin-base.db' at the root of bithonledger/ directory and can be backuped manually (automatic backups coming soon). Database will be created automatically at first run
* All your WIFs are encrypted with your password by [rncryptor](https://github.com/RNCryptor/RNCryptor-python)
* Bithonledger do not collect any data, and even does not have server-side now. If you lose your funds, check bithonledger source code before you can blame this project
* Currently all bitcoin network requests are processed by public APIs, provided by bit lib (Blockchain.com, Insight, BitPAY, etc.)

### It's experimental software, use it at your own risk!
