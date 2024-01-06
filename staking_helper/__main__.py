"""Reads a deposit data directory along with the deposit data file and the keystore files in order to validate they are correct, no validator is active and we are double depositing. And finally submits the transaction by sending a transaction.

contract addy: https://etherscan.io/address/0x0194512e77d798e4871973d9cb9d7ddfc0ffd801
"""
import json
import re
import sys
from pathlib import Path

import requests

from .args import parse_args
from .onchain import perform_deposit
from .utils import error, ts_now


def parse_deposit_data(path, withdrawal_address, return_data):
    with open(path, 'r') as json_file:
        data = json.load(json_file)

    if return_data == {}:
        return_data = {
            'validators': {},
            'pubkeys': '',
            'withdrawals': '',
            'signatures': '',
            'deposit_data_roots': [],
        }
    pubkeys_field = ''
    signatures_field = ''
    deposit_data_roots = []
    if withdrawal_address.startswith('0x'):
        withdrawal_address = withdrawal_address[2:]
    expected_credentials = '010000000000000000000000' + withdrawal_address.lower()
    for validator in data:
        pubkey = validator['pubkey']
        withdrawal_credentials = validator['withdrawal_credentials']
        if withdrawal_credentials != expected_credentials:
            error(f'Expected {expected_credentials}, but found {withdrawal_credentials=}')

        signature = validator['signature']
        deposit_data_root = validator['deposit_data_root']
        if pubkey in return_data['validators']:
            error(f'{pubkey} seen multiple times')

        pubkeys_field += pubkey
        signatures_field += signature
        deposit_data_roots.append('0x' + deposit_data_root)

        return_data['validators'][pubkey] = {
            'withdrawal_credentials': withdrawal_credentials,
            'signature': signature,
            'deposit_data_root': deposit_data_root,
        }

    return_data['pubkeys'] += pubkeys_field
    return_data['withdrawals'] = expected_credentials
    return_data['signatures'] += signatures_field
    return_data['deposit_data_roots'].extend(deposit_data_roots)
    return return_data


def check_beaconchain(return_data):
    """Check with beaconchain that none of the public keys of the validators have had a deposit.

    Protect the user from making a double deposit.
    """
    if len(return_data['validators']) > 100:
        error('Batch contract can not work with more than 100 validators')

    args = ','.join(return_data['validators'])
    response = requests.get(f'https://beaconcha.in/api/v1/validator/{args}/deposits')
    if response.status_code != 200:
        error(f'Requested beaconchain validation and call failed with: {response.text}')

    result = response.json()
    deposits_length = len(result['data'])
    if deposits_length != 0:
        error(f'Found {deposits_length} already existing deposits for the given public keys. Aborting!')

    print('\n-- Checked beaconchain for validator existence!\n')


def check_keystore(path, return_data):
    with open(path, 'r') as json_file:
        data = json.load(json_file)
        if data['pubkey'] not in return_data['validators']:
            error(f'{data["pubkey"]} from keystore file {path} was not found in deposit data')


FILENAME_PARSE_REGEX = re.compile(r'(.*)-(.*?).json')


def iterate_files(
        data_dir,
        withdrawal_address,
        should_check_keystores,
        should_check_beaconchain,
        should_combine_deposit_data,
        should_update_filenames_timestamp,
):
    return_data = {}
    now = ts_now()
    for path in data_dir.iterdir():
        if path.name.startswith('deposit_data') or path.name.startswith('deposit-data'):
            if return_data != {} and not should_combine_deposit_data:
                error('Found second deposit data json without request to combine')

            return_data = parse_deposit_data(path, withdrawal_address, return_data)

        elif should_update_filenames_timestamp:
            match = FILENAME_PARSE_REGEX.match(path.name)
            new_path = Path(path.parent, f'{match.group(1)}-{now}.json')
            if new_path.exists():
                error(f'Can not rename {path} to {new_path} as it already exists')
            path.rename(new_path)
            print(f'Renamed {path} to {new_path}')

    if not return_data:
        error('Did not find deposit data in the directory')

    if should_check_keystores:
        for path in data_dir.iterdir():
            if path.name.startswith('keystore-'):
                check_keystore(path, return_data)

        print('\n-- Checked keystore files!\n')

    if should_check_beaconchain:
        check_beaconchain(return_data)

    return return_data


def main():
    args = parse_args()
    data_dir = Path(args.data_dir)
    if not data_dir.is_dir():
        error(f'Path {data_dir} is not a directory')

    data = iterate_files(
        data_dir=data_dir,
        withdrawal_address=args.withdrawal_address,
        should_check_keystores=args.check_keystores,
        should_check_beaconchain=args.check_beaconchain,
        should_combine_deposit_data=args.combine_deposit_data,
        should_update_filenames_timestamp=args.update_filenames_timestamp,
    )
    print(f'pubkeys: {data["pubkeys"]}')
    print(f'withdrawal_credentials: {data["withdrawals"]}')
    print(f'signatures: {data["signatures"]}')
    print(f'deposit_data_roots: {data["deposit_data_roots"]}')

    print(f'\nCalculated {len(data["deposit_data_roots"])} deposits\n')

    if args.execute_transaction or args.only_estimate_gas:
        perform_deposit(
            only_estimate_gas=args.only_estimate_gas,
            rpc_endpoint=args.rpc_endpoint,
            from_address=args.from_address,
            pubkeys=data['pubkeys'],
            withdrawal_credentials=data['withdrawals'],
            signatures=data['signatures'],
            deposit_data_roots=data['deposit_data_roots'],
            max_fee=args.max_fee,
            max_priority_fee=args.max_priority_fee,
        )

if __name__ == '__main__':
    main()
