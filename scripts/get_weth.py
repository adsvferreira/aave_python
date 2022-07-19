from web3 import Web3
from scripts.helpers import get_account
from brownie import interface, network, config


def main():
    get_weth()


def get_weth(eth_amount=0.1):
    """
    Mints WETH by depositing ETH
    """
    # ABI
    # Contract Address
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": Web3.toWei(eth_amount, "ether")})
    tx.wait(1)
    print(f"Received {eth_amount} WETH")
    return tx
