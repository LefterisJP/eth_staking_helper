import json
from typing import Optional

from web3 import HTTPProvider, Web3

from .constants import (DEPOSIT_CONTRACT_ABI, DEPOSIT_CONTRACT_ADDRESS,
                        EXTRA_GAS, STAKEFISH_BATCH_ABI_STR,
                        STAKEFISH_BATCH_ADDRESS)
from .utils import error


def stakefish_deposit(
        web3,
        only_estimate_gas: bool,
        value: int,
        from_address: str,
        pubkeys: str,
        withdrawal_credentials: str,
        signatures: str,
        deposit_data_roots: list[str],
        max_fee: Optional[str],
        max_priority_fee: Optional[str],
):
    batch_deposit = web3.eth.contract(
        address=STAKEFISH_BATCH_ADDRESS,
        abi=STAKEFISH_BATCH_ABI_STR,
    )
    if batch_deposit.functions.fee().call() != 0:
        error('Stakefish has activated their fee. You can find better batching solutions')
        return
    if batch_deposit.functions.paused().call() is True:
        error('Stakefish admin has paused the contract')
        return
    
    arguments = {
        'pubkeys': bytes.fromhex(pubkeys.removeprefix('0x')),
        'withdrawal_credentials': bytes.fromhex(withdrawal_credentials.removeprefix('0x')),
        'signatures': bytes.fromhex(signatures.removeprefix('0x')),
        'deposit_data_roots': [bytes.fromhex(x.removeprefix('0x')) for x in deposit_data_roots],
    }
    estimated_gas = batch_deposit.functions.batchDeposit(**arguments).estimate_gas({
        'from': from_address,
        'value': value,
    })
    print(f'Gas estimate: {estimated_gas}')
    if only_estimate_gas:
        return

    if max_fee is None:
        error('Need to provide a max fee')
        return
    if max_priority_fee is None:
        error('Need to provide a max priority fee')
        return

    batch_deposit.functions.batchDeposit(**arguments).transact({
        'from': from_address,
        'value': value,
        'gas': estimated_gas + EXTRA_GAS,
        'maxFeePerGas': web3.toWei(max_fee, 'gwei'),
        'maxPriorityFeePerGas': web3.toWei(max_priority_fee, 'gwei'),
    })


def direct_deposit(
        web3,
        only_estimate_gas: bool,
        value: int,
        from_address: str,
        pubkey: str,
        withdrawal_credentials: str,
        signature: str,
        deposit_data_root: str,
        max_fee: Optional[str],
        max_priority_fee: Optional[str],
):
    deposit_contract = web3.eth.contract(
        address=DEPOSIT_CONTRACT_ADDRESS,
        abi=DEPOSIT_CONTRACT_ABI,
    )
    arguments = {
        'pubkey': bytes.fromhex(pubkey.removeprefix('0x')),
        'withdrawal_credentials': bytes.fromhex(withdrawal_credentials.removeprefix('0x')),
        'signature': bytes.fromhex(signature.removeprefix('0x')),
        'deposit_data_root': bytes.fromhex(deposit_data_root.removeprefix('0x')),
    }
    estimated_gas = deposit_contract.functions.deposit(**arguments).estimate_gas({
        'from': from_address,
        'value': value,
    })
    print(f'Gas estimate: {estimated_gas}')
    if only_estimate_gas:
        return

    if max_fee is None:
        error('Need to provide a max fee')
        return
    if max_priority_fee is None:
        error('Need to provide a max priority fee')
        return

    deposit_contract.functions.deposit(**arguments).transact({
        'from': from_address,
        'value': value,
        'gas': estimated_gas + EXTRA_GAS,
        'maxFeePerGas': web3.toWei(max_fee, 'gwei'),
        'maxPriorityFeePerGas': web3.toWei(max_priority_fee, 'gwei'),
    })


def perform_deposit(
        only_estimate_gas: bool,
        rpc_endpoint: str,
        from_address: str,
        pubkeys: str,
        withdrawal_credentials: str,
        signatures: str,
        deposit_data_roots: list[str],
        max_fee: Optional[str],
        max_priority_fee: Optional[str],
):
    provider = HTTPProvider(
        endpoint_uri=rpc_endpoint,
        request_kwargs={'timeout': 480},  # give time to sign the transaction
    )
    web3 = Web3(provider)
    deposit_length = len(deposit_data_roots)
    value = web3.toWei(deposit_length * 32, 'ether')
    if deposit_length == 1:
        direct_deposit(
            web3=web3,
            only_estimate_gas=only_estimate_gas,
            value=value,
            from_address=from_address,
            pubkey=pubkeys,
            withdrawal_credentials=withdrawal_credentials,
            signature=signatures,
            deposit_data_root=deposit_data_roots[0],
            max_fee=max_fee,
            max_priority_fee=max_priority_fee,
        )
    else:
        stakefish_deposit(
            web3=web3,
            only_estimate_gas=only_estimate_gas,
            value=value,
            from_address=from_address,
            pubkeys=pubkeys,
            withdrawal_credentials=withdrawal_credentials,
            signatures=signatures,
            deposit_data_roots=deposit_data_roots,
            max_fee=max_fee,
            max_priority_fee=max_priority_fee,
        )
