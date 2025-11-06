// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface ISushiSwapRouter {
    struct ExactInputSingleParams {
        address tokenIn;
        address tokenOut;
        address recipient;
        uint256 deadline;
        uint256 amountIn;
        uint256 amountOutMinimum;
        uint160 sqrtPriceLimitX96;
    }
    
    struct ExactInputParams {
        bytes path;
        address recipient;
        uint256 deadline;
        uint256 amountIn;
        uint256 amountOutMinimum;
    }
    
    struct ExactOutputSingleParams {
        address tokenIn;
        address tokenOut;
        address recipient;
        uint256 deadline;
        uint256 amountOut;
        uint256 amountInMaximum;
        uint160 sqrtPriceLimitX96;
    }
    
    function exactInputSingle(ExactInputSingleParams calldata params)
        external
        payable
        returns (uint256 amountOut);
        
    function exactInput(ExactInputParams calldata params)
        external
        payable
        returns (uint256 amountOut);
        
    function exactOutputSingle(ExactOutputSingleParams calldata params)
        external
        payable
        returns (uint256 amountIn);
        
    function multicall(bytes[] calldata data) external payable returns (bytes[] memory results);
}

interface ISushiSwapFactory {
    function getPair(address tokenA, address tokenB) external view returns (address pair);
    function createPair(address tokenA, address tokenB) external returns (address pair);
}

interface ISushiSwapPair {
    function token0() external view returns (address);
    function token1() external view returns (address);
    function getReserves() external view returns (
        uint112 reserve0,
        uint112 reserve1,
        uint32 blockTimestampLast
    );
    
    function swap(uint256 amount0Out, uint256 amount1Out, address to, bytes calldata data) external;
    function mint(address to) external returns (uint256 liquidity);
    function burn(address to) external returns (uint256 amount0, uint256 amount1);
    
    function flashLoan(
        address receiver,
        address token,
        uint256 amount,
        bytes calldata data
    ) external;
}

interface ISushiSwapMasterChefV2 {
    struct UserInfo {
        uint256 amount;
        int256 rewardDebt;
        uint256 rewardLockedUp;
        uint256 nextHarvestUntil;
    }
    
    struct PoolInfo {
        address lpToken;
        uint256 allocPoint;
        uint256 lastRewardBlock;
        uint256 accSushiPerShare;
        uint16 depositFeeBP;
        uint256 harvestInterval;
    }
    
    function poolInfo(uint256 pid) external view returns (PoolInfo memory);
    function userInfo(uint256 pid, address user) external view returns (UserInfo memory);
    function deposit(uint256 pid, uint256 amount) external;
    function withdraw(uint256 pid, uint256 amount) external;
    function harvest(uint256 pid) external;
    function pendingSushi(uint256 pid, address user) external view returns (uint256);
}