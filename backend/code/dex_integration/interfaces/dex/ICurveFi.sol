// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface ICurveFi {
    function add_liquidity(
        uint256[2] memory amounts,
        uint256 min_mint_amount,
        uint256 deadline
    ) external payable returns (uint256);
    
    function remove_liquidity(
        uint256 _amount,
        uint256[2] memory min_amounts,
        uint256 deadline
    ) external returns (uint256[2] memory);
    
    function remove_liquidity_one_coin(
        uint256 _burn_amount,
        int128 i,
        uint256 min_received,
        uint256 deadline
    ) external returns (uint256);
    
    function swap(
        int128 i,
        int128 j,
        uint256 dx,
        uint256 min_dy,
        uint256 deadline
    ) external payable returns (uint256 dy);
    
    function coins(uint256 arg0) external view returns (address);
    function coins(int128 arg0) external view returns (address);
    
    function balances(uint256 arg0) external view returns (uint256);
    function balances(int128 arg0) external view returns (uint256);
    
    function get_virtual_price() external view returns (uint256);
    function calc_token_amount(uint256[2] memory amounts, bool deposit) external view returns (uint256);
    function calc_withdraw_one_coin(uint256 _burn_amount, int128 i) external view returns (uint256);
}

interface ICurveFiFactory {
    function pool_count() external view returns (uint256);
    function pool_list(uint256 arg0) external view returns (address);
    function get_n_coins(address arg0) external view returns (uint256);
    function get_coins(address arg0) external view returns (address[8] memory);
    function get_underlying_coins(address arg0) external view returns (address[8] memory);
    function get_balances(address arg0) external view returns (uint256[8] memory);
    function get_underlying_balances(address arg0) external view returns (uint256[8] memory);
    function get_rates(address arg0) external view returns (uint256[8] memory);
    function get_underlying_rates(address arg0) external view returns (uint256[8] memory);
}

interface ICurveFiRegistry {
    function get_pool_from_lp_token(address arg0) external view returns (address);
    function get_lp_token(address arg0) external view returns (address);
    function get_coins(address pool) external view returns (address[8] memory);
    function get_coin_indices(address pool, address from, address to) external view returns (int128, int128);
}

interface ICurveFiPool {
    function add_liquidity(
        uint256[4] memory amounts,
        uint256 min_mint_amount
    ) external payable returns (uint256);
    
    function remove_liquidity(
        uint256 _burn_amount,
        uint256[4] memory min_amounts
    ) external returns (uint256[4] memory);
    
    function remove_liquidity_one_coin(
        uint256 _burn_amount,
        int128 i,
        uint256 min_received
    ) external returns (uint256);
    
    function swap(
        int128 i,
        int128 j,
        uint256 dx,
        uint256 min_dy
    ) external payable returns (uint256 dy);
    
    function calc_token_amount(uint256[4] memory amounts, bool deposit) external view returns (uint256);
    function calc_withdraw_one_coin(uint256 _burn_amount, int128 i) external view returns (uint256);
    function get_virtual_price() external view returns (uint256);
}

interface ICurveFiToken {
    function minter() external view returns (address);
    function lp_token() external view returns (address);
}