from brownie import accounts, network, config, interface


LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-forked"]


def get_account(index: int = None, id: str = None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)  # Ex: af_test_account
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS + FORKED_LOCAL_ENVIRONMENTS:
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])
