// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "../interfaces/IERC20.sol";
import "../utils/SafeMath.sol";
import "../interfaces/tokens/IMetalTokens.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @dev Custom AMM implementation for metal-backed tokens
 */
contract CustomMetalAMM is AccessControl, ReentrancyGuard {
    using SafeMath for uint256;
    
    bytes32 public constant LIQUIDITY_PROVIDER_ROLE = keccak256("LIQUIDITY_PROVIDER_ROLE");
    bytes32 public constant ORACLE_ROLE = keccak256("ORACLE_ROLE");
    
    struct LiquidityPool {
        address tokenA;
        address tokenB;
        uint256 reserveA;
        uint256 reserveB;
        uint256 totalSupply;
        mapping(address => uint256) liquidity;
        uint256 swapFee;
        uint256 protocolFee;
        uint256 lastPriceA;
        uint256 lastPriceB;
        uint256 priceUpdateTime;
        bool isActive;
        MetalType metalType;
    }
    
    struct PoolInfo {
        address tokenA;
        address tokenB;
        uint256 reserveA;
        uint256 reserveB;
        uint256 totalSupply;
        uint256 swapFee;
        uint256 protocolFee;
        uint256 kLast;
        bool isActive;
        MetalType metalType;
    }
    
    // Pools mapping
    mapping(bytes32 => LiquidityPool) public pools;
    PoolInfo[] public poolList;
    
    // Fee management
    uint256 public protocolFeeRate = 300; // 0.3% (300 basis points)
    address public feeRecipient;
    
    // MEV Protection
    mapping(address => uint256) public lastTransactionBlock;
    mapping(address => uint256) public transactionCount;
    uint256 public mevBlockDelay = 3; // Minimum blocks between transactions
    
    // Price protection
    uint256 public maxPriceImpact = 1000; // 10% (1000 basis points)
    uint256 public maxSlippage = 300; // 3% (300 basis points)
    
    // Events
    event PoolCreated(address indexed tokenA, address indexed tokenB, uint256 initialLiquidity, bytes32 poolId);
    event LiquidityAdded(bytes32 indexed poolId, address indexed provider, uint256 amountA, uint256 amountB);
    event LiquidityRemoved(bytes32 indexed poolId, address indexed provider, uint256 amountA, uint256 amountB);
    event SwapExecuted(bytes32 indexed poolId, address indexed trader, address tokenIn, address tokenOut, uint256 amountIn, uint256 amountOut);
    event PriceUpdated(address indexed token, uint256 newPrice, address indexed oracle);
    event ProtocolFeeCollected(address indexed feeRecipient, uint256 amount);
    event MEVProtectionActivated(address indexed user, uint256 blockNumber);
    
    constructor(address _feeRecipient) {
        require(_feeRecipient != address(0), "Invalid fee recipient");
        feeRecipient = _feeRecipient;
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(ORACLE_ROLE, msg.sender);
    }
    
    /**
     * @dev Create a new liquidity pool for metal-backed tokens
     */
    function createPool(
        address tokenA,
        address tokenB,
        uint256 initialLiquidityA,
        uint256 initialLiquidityB,
        MetalType metalType
    ) external onlyRole(DEFAULT_ADMIN_ROLE) returns (bytes32 poolId) {
        require(tokenA != tokenB, "Tokens must be different");
        require(tokenA != address(0) && tokenB != address(0), "Invalid token addresses");
        require(initialLiquidityA > 0 && initialLiquidityB > 0, "Initial liquidity must be positive");
        
        poolId = keccak256(abi.encodePacked(tokenA, tokenB, metalType));
        require(!pools[poolId].isActive, "Pool already exists");
        
        // Transfer tokens from creator
        IERC20(tokenA).transferFrom(msg.sender, address(this), initialLiquidityA);
        IERC20(tokenB).transferFrom(msg.sender, address(this), initialLiquidityB);
        
        // Initialize pool
        pools[poolId].tokenA = tokenA;
        pools[poolId].tokenB = tokenB;
        pools[poolId].reserveA = initialLiquidityA;
        pools[poolId].reserveB = initialLiquidityB;
        pools[poolId].swapFee = 30; // 0.3% default
        pools[poolId].protocolFee = protocolFeeRate;
        pools[poolId].isActive = true;
        pools[poolId].metalType = metalType;
        pools[poolId].totalSupply = _calculateInitialLiquidity(initialLiquidityA, initialLiquidityB);
        
        // Add pool to list
        poolList.push(PoolInfo({
            tokenA: tokenA,
            tokenB: tokenB,
            reserveA: initialLiquidityA,
            reserveB: initialLiquidityB,
            totalSupply: pools[poolId].totalSupply,
            swapFee: pools[poolId].swapFee,
            protocolFee: pools[poolId].protocolFee,
            kLast: _calculateK(initialLiquidityA, initialLiquidityB),
            isActive: true,
            metalType: metalType
        }));
        
        emit PoolCreated(tokenA, tokenB, initialLiquidityA, poolId);
    }
    
    /**
     * @dev Add liquidity to an existing pool
     */
    function addLiquidity(
        bytes32 poolId,
        uint256 amountA,
        uint256 amountB,
        uint256 minAmountA,
        uint256 minAmountB,
        uint256 deadline
    ) external nonReentrant returns (uint256 liquidityMinted) {
        require(block.timestamp <= deadline, "Deadline exceeded");
        require(pools[poolId].isActive, "Pool not active");
        
        LiquidityPool storage pool = pools[poolId];
        
        // Check current reserves
        uint256 currentReserveA = IERC20(pool.tokenA).balanceOf(address(this));
        uint256 currentReserveB = IERC20(pool.tokenB).balanceOf(address(this));
        
        // Verify minimum amounts
        require(amountA >= minAmountA, "Amount A below minimum");
        require(amountB >= minAmountB, "Amount B below minimum");
        
        // Transfer tokens from provider
        IERC20(pool.tokenA).transferFrom(msg.sender, address(this), amountA);
        IERC20(pool.tokenB).transferFrom(msg.sender, address(this), amountB);
        
        // Update reserves
        currentReserveA = currentReserveA.add(amountA);
        currentReserveB = currentReserveB.add(amountB);
        
        // Calculate liquidity to mint
        if (pool.totalSupply == 0) {
            liquidityMinted = _calculateInitialLiquidity(amountA, amountB);
        } else {
            uint256 liquidityA = amountA.mul(pool.totalSupply).div(pool.reserveA);
            uint256 liquidityB = amountB.mul(pool.totalSupply).div(pool.reserveB);
            liquidityMinted = liquidityA < liquidityB ? liquidityA : liquidityB;
        }
        
        require(liquidityMinted > 0, "Insufficient liquidity minted");
        
        // Update pool state
        pool.reserveA = currentReserveA;
        pool.reserveB = currentReserveB;
        pool.totalSupply = pool.totalSupply.add(liquidityMinted);
        pool.liquidity[msg.sender] = pool.liquidity[msg.sender].add(liquidityMinted);
        
        // Update pool list
        _updatePoolInList(poolId, currentReserveA, currentReserveB, pool.totalSupply);
        
        emit LiquidityAdded(poolId, msg.sender, amountA, amountB);
    }
    
    /**
     * @dev Remove liquidity from a pool
     */
    function removeLiquidity(
        bytes32 poolId,
        uint256 liquidityAmount,
        uint256 minAmountA,
        uint256 minAmountB,
        uint256 deadline
    ) external nonReentrant returns (uint256 amountA, uint256 amountB) {
        require(block.timestamp <= deadline, "Deadline exceeded");
        require(pools[poolId].isActive, "Pool not active");
        
        LiquidityPool storage pool = pools[poolId];
        require(pool.liquidity[msg.sender] >= liquidityAmount, "Insufficient liquidity");
        
        // Calculate amounts to receive
        uint256 currentSupply = pool.totalSupply;
        amountA = liquidityAmount.mul(pool.reserveA).div(currentSupply);
        amountB = liquidityAmount.mul(pool.reserveB).div(currentSupply);
        
        require(amountA >= minAmountA, "Amount A below minimum");
        require(amountB >= minAmountB, "Amount B below minimum");
        
        // Update pool state
        pool.liquidity[msg.sender] = pool.liquidity[msg.sender].sub(liquidityAmount);
        pool.totalSupply = pool.totalSupply.sub(liquidityAmount);
        pool.reserveA = pool.reserveA.sub(amountA);
        pool.reserveB = pool.reserveB.sub(amountB);
        
        // Transfer tokens to provider
        IERC20(pool.tokenA).transfer(msg.sender, amountA);
        IERC20(pool.tokenB).transfer(msg.sender, amountB);
        
        // Update pool list
        _updatePoolInList(poolId, pool.reserveA, pool.reserveB, pool.totalSupply);
        
        emit LiquidityRemoved(poolId, msg.sender, amountA, amountB);
    }
    
    /**
     * @dev Execute a swap with MEV and slippage protection
     */
    function swapExactTokensForTokens(
        bytes32 poolId,
        uint256 amountIn,
        uint256 amountOutMin,
        address tokenIn,
        address tokenOut,
        uint256 deadline
    ) external nonReentrant returns (uint256 amountOut) {
        require(block.timestamp <= deadline, "Deadline exceeded");
        require(pools[poolId].isActive, "Pool not active");
        
        LiquidityPool storage pool = pools[poolId];
        
        // MEV protection check
        _checkMEVProtection(msg.sender);
        
        // Identify token positions
        bool isTokenA = tokenIn == pool.tokenA;
        require(isTokenA || tokenIn == pool.tokenB, "Invalid input token");
        require(tokenOut != tokenIn, "Cannot swap same token");
        require(tokenOut == (isTokenA ? pool.tokenB : pool.tokenA), "Invalid output token");
        
        // Calculate amount out with price impact protection
        (uint256 reserveIn, uint256 reserveOut, uint256 priceIn, uint256 priceOut) = _getReservesAndPrices(poolId, isTokenA);
        
        // Check price impact
        uint256 priceImpact = _calculatePriceImpact(reserveIn, reserveOut, amountIn);
        require(priceImpact <= maxPriceImpact, "Price impact too high");
        
        // Calculate output amount
        amountOut = _getAmountOut(amountIn, reserveIn, reserveOut, pool.swapFee);
        require(amountOut >= amountOutMin, "Slippage protection");
        
        // Update reserves
        if (isTokenA) {
            pool.reserveA = pool.reserveA.add(amountIn);
            pool.reserveB = pool.reserveB.sub(amountOut);
        } else {
            pool.reserveB = pool.reserveB.add(amountIn);
            pool.reserveA = pool.reserveA.sub(amountOut);
        }
        
        // Collect protocol fee
        uint256 protocolFeeAmount = amountOut.mul(pool.protocolFee).div(10000);
        if (protocolFeeAmount > 0) {
            IERC20(tokenOut).transfer(feeRecipient, protocolFeeAmount);
            emit ProtocolFeeCollected(feeRecipient, protocolFeeAmount);
            amountOut = amountOut.sub(protocolFeeAmount);
        }
        
        // Transfer tokens
        IERC20(tokenIn).transferFrom(msg.sender, address(this), amountIn);
        IERC20(tokenOut).transfer(msg.sender, amountOut);
        
        // Update pool list
        _updatePoolInList(poolId, pool.reserveA, pool.reserveB, pool.totalSupply);
        
        emit SwapExecuted(poolId, msg.sender, tokenIn, tokenOut, amountIn, amountOut);
    }
    
    /**
     * @dev Get current price of a token in a pool
     */
    function getPrice(bytes32 poolId, address token) external view returns (uint256) {
        require(pools[poolId].isActive, "Pool not active");
        LiquidityPool storage pool = pools[poolId];
        
        if (token == pool.tokenA) {
            return pool.reserveB.mul(1e18).div(pool.reserveA);
        } else if (token == pool.tokenB) {
            return pool.reserveA.mul(1e18).div(pool.reserveB);
        } else {
            revert("Token not in pool");
        }
    }
    
    /**
     * @dev Get pool information
     */
    function getPoolInfo(bytes32 poolId) external view returns (PoolInfo memory) {
        require(pools[poolId].isActive, "Pool not active");
        LiquidityPool storage pool = pools[poolId];
        
        return PoolInfo({
            tokenA: pool.tokenA,
            tokenB: pool.tokenB,
            reserveA: pool.reserveA,
            reserveB: pool.reserveB,
            totalSupply: pool.totalSupply,
            swapFee: pool.swapFee,
            protocolFee: pool.protocolFee,
            kLast: _calculateK(pool.reserveA, pool.reserveB),
            isActive: pool.isActive,
            metalType: pool.metalType
        });
    }
    
    /**
     * @dev Get all pools
     */
    function getAllPools() external view returns (PoolInfo[] memory) {
        return poolList;
    }
    
    /**
     * @dev Set price oracle for a token
     */
    function updatePrice(address token, uint256 newPrice) external onlyRole(ORACLE_ROLE) {
        require(newPrice > 0, "Invalid price");
        emit PriceUpdated(token, newPrice, msg.sender);
    }
    
    /**
     * @dev Set maximum price impact
     */
    function setMaxPriceImpact(uint256 newMaxImpact) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(newMaxImpact <= 5000, "Price impact too high (max 50%)");
        maxPriceImpact = newMaxImpact;
    }
    
    /**
     * @dev Set maximum slippage
     */
    function setMaxSlippage(uint256 newMaxSlippage) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(newMaxSlippage <= 1000, "Slippage too high (max 10%)");
        maxSlippage = newMaxSlippage;
    }
    
    /**
     * @dev Get liquidation amount for a user
     */
    function getLiquidity(bytes32 poolId, address user) external view returns (uint256) {
        return pools[poolId].liquidity[user];
    }
    
    /**
     * @dev Internal functions
     */
    function _calculateInitialLiquidity(uint256 amountA, uint256 amountB) internal pure returns (uint256) {
        return Math.sqrt(amountA.mul(amountB));
    }
    
    function _calculateK(uint256 reserveA, uint256 reserveB) internal pure returns (uint256) {
        return reserveA.mul(reserveB);
    }
    
    function _getAmountOut(
        uint256 amountIn,
        uint256 reserveIn,
        uint256 reserveOut,
        uint256 swapFee
    ) internal pure returns (uint256) {
        uint256 amountInWithFee = amountIn.mul(10000 - swapFee);
        uint256 numerator = amountInWithFee.mul(reserveOut);
        uint256 denominator = reserveIn.mul(10000).add(amountInWithFee);
        return numerator.div(denominator);
    }
    
    function _calculatePriceImpact(uint256 reserveIn, uint256 reserveOut, uint256 amountIn) 
        internal view returns (uint256) {
        uint256 newReserveIn = reserveIn.add(amountIn);
        uint256 expectedOut = reserveOut.mul(newReserveIn).div(reserveIn);
        uint256 actualOut = _getAmountOut(amountIn, reserveIn, reserveOut, 30);
        
        return actualOut < expectedOut ? expectedOut.sub(actualOut).mul(10000).div(expectedOut) : 0;
    }
    
    function _getReservesAndPrices(bytes32 poolId, bool isTokenA) 
        internal view returns (uint256 reserveIn, uint256 reserveOut, uint256 priceIn, uint256 priceOut) {
        LiquidityPool storage pool = pools[poolId];
        
        if (isTokenA) {
            reserveIn = pool.reserveA;
            reserveOut = pool.reserveB;
            priceIn = pool.reserveA > 0 ? pool.reserveB.mul(1e18).div(pool.reserveA) : 0;
            priceOut = pool.reserveB > 0 ? pool.reserveA.mul(1e18).div(pool.reserveB) : 0;
        } else {
            reserveIn = pool.reserveB;
            reserveOut = pool.reserveA;
            priceIn = pool.reserveB > 0 ? pool.reserveA.mul(1e18).div(pool.reserveB) : 0;
            priceOut = pool.reserveA > 0 ? pool.reserveB.mul(1e18).div(pool.reserveA) : 0;
        }
    }
    
    function _updatePoolInList(bytes32 poolId, uint256 reserveA, uint256 reserveB, uint256 totalSupply) 
        internal {
        for (uint256 i = 0; i < poolList.length; i++) {
            if (keccak256(abi.encodePacked(poolList[i].tokenA, poolList[i].tokenB, poolList[i].metalType)) == poolId) {
                poolList[i].reserveA = reserveA;
                poolList[i].reserveB = reserveB;
                poolList[i].totalSupply = totalSupply;
                poolList[i].kLast = _calculateK(reserveA, reserveB);
                break;
            }
        }
    }
    
    function _checkMEVProtection(address user) internal {
        uint256 currentBlock = block.number;
        uint256 lastBlock = lastTransactionBlock[user];
        
        if (lastBlock > 0 && currentBlock <= lastBlock.add(mevBlockDelay)) {
            emit MEVProtectionActivated(user, lastBlock.add(mevBlockDelay));
            revert("MEV protection: insufficient block delay");
        }
        
        if (transactionCount[user] > 10) {
            if (currentBlock > lastBlock.add(mevBlockDelay * 2)) {
                transactionCount[user] = 0;
            } else {
                revert("MEV protection: too many transactions");
            }
        }
        
        lastTransactionBlock[user] = currentBlock;
        transactionCount[user] = transactionCount[user].add(1);
    }
}

// Math library for square root calculation
library Math {
    function sqrt(uint256 y) internal pure returns (uint256 z) {
        if (y > 3) {
            z = y;
            uint256 x = y / 2 + 1;
            while (x < z) {
                z = x;
                x = (y / x + x) / 2;
            }
        } else if (y != 0) {
            z = 1;
        }
    }
}