# Eth staking helper

This is a simple python script to help with staking, especially for multiple deposits.

It's taking the deposit data json file as input and performs various checks to make sure data is valid. More checks are available via arguments.

Heavily recommend to use the ``--check-beaconchain`` argument to make sure none of the pubkeys have pending or completed deposits.

The biggest usecase is utilizing the stakefish deposit batching [contract](https://etherscan.io/address/0x0194512e77d798e4871973d9cb9d7ddfc0ffd801) in order to do multiple eth staking deposits in a single transaction if there is multiple deposits.

It's made to work out of the box with frame's local proxy rpc endpoint. So if you run frame in your computer it just works!

Otherwise you can provide your own via CLI args.

## Disclaimer

THIS SCRIPT IS PROVIDED AS-IS AND WITHOUT ANY GUARANTEES. BY USING IT AND NOT KNOWING WHAT YOU ARE DOING YOU WILL LOSE FUNDS. DO NOT USE UNLESS YOU KNOW WHAT YOU ARE DOING AND EVEN THEN QUADRUPLE CHECK EVERYTHING.

THE AUTHOR IS NOT LIABLE FOR ANY DAMAGES THAT MAY RESULT BY EITHER BUGS IN THE CODE OR BY MISTAKEN USAGE OF THE SCRIPT.

## Installation

You will need python 3 to run this.

Create a virtualenv, for example with mkvirtualenv:
```
mkvirtualenv staking_helper
```

and then install the requirements:

```
pip install -r requirements.txt
```

Run with:
```
python -m staking_helper --help
```

## CLI args

```
usage: Eth staking helper [-h] --data-dir DATA_DIR --from-address FROM_ADDRESS --withdrawal-address WITHDRAWAL_ADDRESS [--check-keystores] [--check-beaconchain] [--execute-transaction] [--only-estimate-gas] [--max-fee MAX_FEE]
                          [--max-priority-fee MAX_PRIORITY_FEE] [--rpc-endpoint RPC_ENDPOINT]

Reads the eth staking deposit data,validates it, checks against already deposited validators, and finally sends a (potentially batched) deposit transaction.

options:
  -h, --help            show this help message and exit
  --data-dir DATA_DIR   The directory where the deposit data is
  --from-address FROM_ADDRESS
                        The address to send from
  --withdrawal-address WITHDRAWAL_ADDRESS
                        The withdrawal address. Since the batching contract allows only single withdrawal credentials we use this to check if withdrawals credentials match the eth1 address. Script does not work with 0x00 credentials for
                        now. But should be trivial to adjust
  --check-keystores     False by default. If true will also check keystore files in directory for existence of pubkey
  --check-beaconchain   False by default. If true will also check if pubkeys are known to have made any deposit via the beaconcha.in API
  --execute-transaction
                        False by default. If true will try to execute the batch deposit transaction
  --only-estimate-gas   False by default. If true will not execute but just estimate gas
  --max-fee MAX_FEE     The max fee in gwei for the transaction. Only needed for execution
  --max-priority-fee MAX_PRIORITY_FEE
                        The max priority fee in gwei for the transaction. Only needed for execution
  --rpc-endpoint RPC_ENDPOINT
                        The rpc endpoint to use when estimating gas or sending the transaction. Defaults to frame's local proxy
```

## Examples

**Addresses are examples here. DO NOT use them in production.**

### Simple execution

```
python -m staking_helper --data-dir ~/w/lattice-cli/deposit-data --withdrawal-address 0x690B9A9E9aa1C9dB991C7721a92d351Db4FaC990 --from-address 0x4e7C9d9240E1946DdaF765230E58E55a2b35fA2a --max-fee 36.1 --max-priority-fee 0.19 --execute-transaction
```

This would read from your deposit data directory, take all deposit data and validate it that they are for the given withdrawal address.

Then it would proceed to send the transaction with 36.1 gwei max fee and priority fee 0.19.

### Estimate gas

```
python -m staking_helper --data-dir ~/w/lattice-cli/deposit-data --withdrawal-address 0x690B9A9E9aa1C9dB991C7721a92d351Db4FaC990 --from-address 0x4e7C9d9240E1946DdaF765230E58E55a2b35fA2a --only-estimate-gas
```

Same as before but this time no transaction will be execute. Only the gas estimate for the deposit will be printed.

### Extra validations

```
python -m staking_helper --data-dir ~/w/lattice-cli/deposit-data --withdrawal-address 0x690B9A9E9aa1C9dB991C7721a92d351Db4FaC990 --from-address 0x4e7C9d9240E1946DdaF765230E58E55a2b35fA2a --check-beaconchain --check-keystores --max-fee 36.1 --max-priority-fee 0.19 --execute-transaction
```

This is adding two extra recommended validations.

- `--check-keystores` goes through all keystore validator files in the deposit directory and mnakes sure their public key is in the deposit data.
- `--check-beaconchain` takes all deposit public keys and checks the beaconchain via beaconcha.in API to see if there is any pending or finished deposits. If yes then script stops as that means you are about to do at least one double deposit.


## Future additions

PRs are welcome.

1. Could be made to work with more batching contracts such as [staked.us](https://etherscan.io/address/0x39dc6a99209b5e6b81dc8540c86ff10981ebda29#code) contract.
2. Could accept `0x00` withdrawal credentials (easy)
3. Could accept different withdrawal credentials per validator. Stakefish batcher does not allow for this, so first (1) should be implemented.
