from brownie import interface, network, config
from scripts.helpful_scripts import get_account


def get_weth():
    # get abi
    # address
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    # weth = interface.IWeth('0xd0a1e359811322d97991e03f863a0c30c2cf029c')
    tx = weth.deposit({"from": account, "value": 0.1 * 10 ** 18})
    print(f"Received 0.1 WETH")
    tx.wait(1)
    return tx


def main():
    get_weth()
