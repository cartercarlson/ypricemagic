import pytest
from brownie import ZERO_ADDRESS, chain
from multicall import Call
from tests.constants import STABLECOINS
from tests.fixtures import blocks_for_contract, mutate_tokens
from y.classes.common import ERC20
from y.constants import WRAPPED_GAS_COIN, wbtc
from y.exceptions import call_reverted

TOKENS = STABLECOINS + mutate_tokens([WRAPPED_GAS_COIN, wbtc.address])
TOKENS_BY_BLOCK = [
    (token, block)
    for token in TOKENS
    for block in blocks_for_contract(token)
]

@pytest.mark.parametrize('token',TOKENS)
def test_erc20(token):
    token = ERC20(token)
    if token.address == '0x57ab1e02fee23774580c119740129eac7081e9d3': # old sUSD
        pytest.skip('Not applicable to deprecated sUSD.')
    block = chain.height
    assert token.contract, f'Cannot fetch contract for token {token}'
    assert token.build_name, f'Cannot fetch build name for token {token}'
    assert token.symbol, f'Cannot fetch symbol for token {token}'
    assert token.name, f'Cannot fetch name for token {token}'
    assert token.decimals, f'Cannot fetch decimals for token {token}'
    assert token.scale, f'Cannot fetch scale for token {token}'
    assert 10 ** token.decimals == token.scale, f'Incorrect scale fetched for token {token}'
    assert token.total_supply() is not None, f'Cannot fetch total supply for token {token}'
    assert token.total_supply_readable() is not None, f'Cannot fetch total supply readable for token {token}'
    assert token.total_supply(block) / token.scale == token.total_supply_readable(block), f'Incorrect total supply readable for token {token}'
    assert token.price(), f'Cannot fetch price for token {token}'

@pytest.mark.parametrize('token,block',TOKENS_BY_BLOCK)
def test_erc20_at_block(token, block):
    token = ERC20(token)
    if token.address == '0x57ab1e02fee23774580c119740129eac7081e9d3' and block >= 13222927:
        pytest.skip('Not applicable to the old sUSD after migration block.')

    # NOTE Some proxy tokens would fail tests in early days because no implementation is specified.
    try:
        if Call(token.address, 'implementation()(address)', [['imp',None]], block_id = block)() == ZERO_ADDRESS:
            pytest.skip(f"Not applicable to proxy contracts with implementation not set.")
    except Exception as e:
        if not call_reverted(e):
            raise
    
    # NOTE We've validated token is not problematic proxy, proceed with test.
    assert token._decimals(block), f'Cannot fetch decimals for token {token}'
    assert token._scale(block), f'Cannot fetch scale for token {token}'
    assert token.total_supply(block) is not None, f'Cannot fetch total supply for token {token}'
    assert token.total_supply_readable(block) is not None, f'Cannot fetch total supply readable for token {token}'
    assert token.total_supply(block) / token._scale(block) == token.total_supply_readable(block), f'Incorrect total supply readable for token {token}'
    assert token.price(block), f'Cannot fetch price for token {token}'
