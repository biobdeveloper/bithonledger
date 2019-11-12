class BithonledgerMSG:
    commands = ("Available commands:\n\n\n"
                "new\n "
                "   to generate new key\n\n"
                "add\n "
                "   to add new WIF to database\n\n"
                "balance\n"
                "   to check single address balance\n\n"
                "wif\n"
                "   to retrieve key's wif from database by address\n\n"
                "refresh\n "
                "   to get all wallets with balances and total value of btc\n\n"
                "send\n "
                "   to send transaction\n\n"
                "stop\n "
                "   to quit\n\n")
    exit = "Goodbye"
    start = "Welcome to {}"
    connected = "{} connected to {}"
    cancel_instruction = "(Ctrl+C to cancel)\n"
    create_password = "It's your first run, let's create password!\n"
    repeat_password = "Ok, repeat the password\n"
    passwords_not_match = "Passwords do not match. Try again\n"
    wrong_password = "Password is wrong! Try again\n"
    unlocked = "Database is unlocked! Welcome!"
    password_created = "Password was created!"
    enter_wallet_to_send = "enter or choose wif to send transaction from"
    remove_confirm = "remove {} with {} btc from database"
    do_this = 'do this'

    input_msg = dict(
        password="Please, unlock your database\n",
        yes_no="Do you want to {}? y/n\n",
        command="Enter command: ",
        amount="Enter BTC amount Max is : ",
        address="Enter BTC address:\n",
        wif="Enter WIF:\n"
    )

    result_msg = dict(
        unknown_command={0: "Unknown command"},
        new={0: "Address: {}\nWIF: {}",
             1: "Unable to create address: {}"},
        add={0: "New wallet was recorded to database",
             1: "Unable to record to database: {}"},
        send={0: "Transaction successfully broadcasted, hashes is {}",
              1: "Unable to send transaction"},
        remove={0: "Successfully remove wallet {}",
                1: "Wallet wasn't remove: {}"},
        balance={0: "{} BTC",
                 1: "Unable to retrieve balance"},
        refresh={0: "{}\nCurrent balance is {} BTC",
                 1: "Unable to refresh: {}"},
        wif={0: "Keep it in secret!\n{}",
             1: "Unable to retrieve fee: {}"},
        test={0: "Good scenario",
              1: "Bad scenario: {}"},
    )

    class warning_msg:
        wallet_not_empty = "Warning! {} wallet is not empty: {} btc"
        send_to_your = "Warning! You want to send money on your own address!"

    class error_msg:
        no_consolidation = "Unable to consolidate transaction"
        not_enough_balance = "Not enough balance, try again",
        unknown_command = "Unknown command\n",
        command_failed = "Failed to execute command: "
        bad_input = f"Bad value, try again"

    class system_msg:
        pass