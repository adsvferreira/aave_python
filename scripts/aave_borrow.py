from msilib.schema import ListView
from web3 import Web3
from scripts.get_weth import get_weth
from scripts.helpers import get_account
from brownie import interface, network, config

ETH_AMOUNT = 0.1


def main():
    account = get_account()
    weth_addr = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-forked"]:  # For public testnet, run the script manually before.
        get_weth(ETH_AMOUNT)
    lending_pool = get_lending_pool()
    wei_amount = Web3.toWei(ETH_AMOUNT, "ether")
    aprove_erc20(account, weth_addr, lending_pool.address, wei_amount)
    # Last var - referralCode is deprecated = 0
    print("Depositing...")
    tx = lending_pool.deposit(weth_addr, wei_amount, account.address, 0, {"from": account})
    tx.wait(2)
    print("Deposited!")
    print("Getting borrowable data...")
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    # DAI in terms of ETH
    dai_eth_price = get_asset_price(config["networks"][network.show_active()]["dai_eth_price_feed"])
    # safety factor: 0.95
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    dai_address = config["networks"][network.show_active()]["dai_token"]
    # interestRateModel: 1 - Stable / 2 - Variable
    interest_rate_model = 1
    print(f"Borrowing {amount_dai_to_borrow} DAI...")
    borrow_tx = lending_pool.borrow(
        dai_address, Web3.toWei(amount_dai_to_borrow, "ether"), interest_rate_model, 0, account, {"from": account}
    )
    borrow_tx.wait(2)
    print("Borrowed!!")
    get_borrowable_data(lending_pool, account)
    # repay_all(wei_amount, lending_pool, account, dai_address, interest_rate_model)

    # function borrow(
    #     address asset,
    #     uint256 amount,
    #     uint256 interestRateMode,
    #     uint16 referralCode,
    #     address onBehalfOf
    # ) external;


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    return interface.ILendingPool(lending_pool_address)


def aprove_erc20(account, erc20_addr, spender_addr, wei_amount):
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_addr)
    tx = erc20.approve(spender_addr, wei_amount, {"from": account})
    tx.wait(1)
    print("Approved!")
    return tx


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_collateral_eth} worth of ETH deposited.")
    print(f"You have {available_borrow_eth} worth of ETH available to borrow.")
    print(f"You have {total_debt_eth} worth of ETH borrowed.")
    return (float(available_borrow_eth), float(total_debt_eth))

    # function latestRoundData()
    #     external
    #     view
    #     returns (
    #         uint80 roundId,
    #         int256 answer,
    #         uint256 startedAt,
    #         uint256 updatedAt,
    #         uint80 answeredInRound
    #     );


def get_asset_price(price_feed_address):
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    latest_price_in_eth = Web3.fromWei(latest_price, "ether")
    print(f"DAI/ETH price: {latest_price_in_eth}")
    return float(latest_price_in_eth)


def repay_all(wei_amount, lending_pool, account, dai_address, interest_rate_model):
    print("Repaying...")
    aprove_erc20(account, dai_address, lending_pool, wei_amount)
    repay_tx = lending_pool.repay(dai_address, wei_amount, interest_rate_model, account, {"from": account})
    repay_tx.wait(1)
    print("Repayed!!")

    # function repay(
    #     address asset,
    #     uint256 amount,
    #     uint256 rateMode,
    #     address onBehalfOf
    # ) external returns (uint256);
