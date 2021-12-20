from brownie import interface, network, config
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from web3 import Web3

amount = Web3.toWei(0.5, "ether")


def aave_borrow():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    dai_eth_price_address = config["networks"][network.show_active()][
        "dai_eth_price_feed"
    ]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    lending_pool = get_lending_pool()
    # approve sending erc20 token
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    print("depositing")
    tx = lending_pool.deposit(
        erc20_address, amount, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("deposited")
    (borrowable_eth, total_debt) = get_borrowable_data(lending_pool, account)
    print("let's borrow")
    # price feed dai in terms of eth
    dai_eth_price = get_asset_price(dai_eth_price_address)
    amount_dai_to_borrow = (1 / dai_eth_price) * (
        borrowable_eth * 0.95
    )  # 95% to be safe
    print(f"we are going to borrow {amount_dai_to_borrow}")
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    print("borrowed some dai")
    get_borrowable_data(lending_pool, account)
    # repay_all(amount, lending_pool, account)


def repay_all(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amout,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("repayed")


def get_asset_price(price_feed_address):
    # ABI
    # Address
    dai_eth_price_feed = interface.IAggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_price = Web3.fromWei(latest_price, "ether")
    print(f"dai eth price is {converted_price}")
    return float(converted_price)


def approve_erc20(amount, spender, erc20_address, account):
    # abi
    # address
    print("approving erc20 token")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved ERC20")
    return tx


def get_lending_pool():
    # abi
    # address
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def get_borrowable_data(lending_pool, account):
    (
        toal_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_treshold,
        loan_to_value,
        health,
    ) = lending_pool.getUserAccountData(account.address)
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    toal_collateral_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    current_liquidation_treshold = Web3.fromWei(current_liquidation_treshold, "ether")
    loan_to_value = Web3.fromWei(loan_to_value, "ether")
    health = Web3.fromWei(health, "ether")
    print(f"You have {toal_collateral_eth} worth of ETH deposited")
    print(f"You can borrow {available_borrow_eth} worth of ETH")
    return (float(available_borrow_eth), float(total_debt_eth))


def main():
    aave_borrow()
