import argparse


def parse_args():
    p = argparse.ArgumentParser(
        prog='Eth staking helper',
        description='Reads the eth staking deposit data,validates it, checks against already deposited validators, and finally sends a (potentially batched) deposit transaction.',
    )
    p.add_argument(
        '--combine-deposit-data',
        help='Look inside a given directory of deposit data and if it has multiple deposit data read all of them',
        action='store_true',
    )
    p.add_argument(
        '--update-filenames-timestamp',
        help='If true all filenames under the directory which end in a timestamp will get updated to latest',
        action='store_true',
    )
    p.add_argument(
        '--data-dir',
        help='The directory where the deposit data is',
        type=str,
        required=True,
    )
    p.add_argument(
        '--from-address',
        help='The address to send from',
        type=str,
        required=True,
    )
    p.add_argument(
        '--withdrawal-address',
        help='The withdrawal address. Since the batching contract allows only single withdrawal credentials we use this to check if withdrawals credentials match the eth1 address. Script does not work with 0x00 credentials for now. But should be trivial to adjust',
        type=str,
        required=True,
    )
    p.add_argument(
        '--check-keystores',
        help='False by default. If true will also check keystore files in directory for existence of pubkey',
        action='store_true',
    )
    p.add_argument(
        '--check-beaconchain',
        help='False by default. If true will also check if pubkeys are known to have made any deposit via the beaconcha.in API',
        action='store_true',
    )
    p.add_argument(
        '--execute-transaction',
        help='False by default. If true will try to execute the batch deposit transaction',
        action='store_true',
    )
    p.add_argument(
        '--only-estimate-gas',
        help='False by default. If true will not execute but just estimate gas',
        action='store_true',
    )
    p.add_argument(
        '--max-fee',
        help='The max fee in gwei for the transaction. Only needed for execution',
        type=str,
    )
    p.add_argument(
        '--max-priority-fee',
        help='The max priority fee in gwei for the transaction. Only needed for execution',
        type=str,
    )
    p.add_argument(
        '--rpc-endpoint',
        help="The rpc endpoint to use when estimating gas or sending the transaction. Defaults to frame's local proxy",
        type=str,
        default='http://127.0.0.1:1248',  # frame's local proxy
    )
    args = p.parse_args()
    return args
