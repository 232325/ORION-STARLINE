// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "../interfaces/dex/IUniswapV3.sol";
import "../interfaces/dex/ISushiSwap.sol";
import "../interfaces/dex/IPancakeSwap.sol";
import "../interfaces/dex/ICurveFi.sol";
import "../interfaces/IERC20.sol";
import "../utils/SafeMath.sol";

contract DEXAggregator {
    using SafeMath for uint256;
    
    address public owner;
    address public weth = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2; // WETH on Ethereum
    
    struct SwapParams {
        address tokenIn;
        address tokenOut;
        uint256 amountIn;
        uint256 minAmountOut;
        uint256 deadline;
        address[] path;
        uint24[] fees;
        uint8 dexId; // 0: UniswapV3, 1: SushiSwap, 2: PancakeSwapV2, 3: PancakeSwapV3, 4: Curve
        bool isMultiHop;
    }
    
    struct RouteInfo {
        uint8 dexId;
        address router;
        uint256 expectedAmountOut;
        uint256 gasEstimate;
        uint256 priceImpact;
        uint256 slippage;
    }
    
    struct BestRoute {
        RouteInfo[] routes;
        uint256 totalAmountOut;
        uint256 totalGasUsed;
        uint256 totalPriceImpact;
        uint256 totalSlippage;
        bool isValid;
    }
    
    // Uniswap V3 addresses
    IUniswapV3Router public immutable uniswapV3Router;
    IUniswapV3Factory public immutable uniswapV3Factory;
    
    // SushiSwap addresses
    ISushiSwapRouter public immutable sushiSwapRouter;
    ISushiSwapFactory public immutable sushiSwapFactory;
    
    // PancakeSwap addresses
    IPancakeSwapV3Router public immutable pancakeSwapV3Router;
    IPancakeSwapV3Pool public immutable pancakeSwapV3Pool;
    IPancakeSwapV2Router public immutable pancakeSwapV2Router;
    
    // Curve addresses
    mapping(address => ICurveFi) public curvePools;
    
    // Price oracle for comparison
    mapping(address => uint256) public lastPrices;
    mapping(address => uint256) public priceUpdateTime;
    
    // Gas optimization
    mapping(address => uint256) public gasPriceOfToken;
    mapping(address => uint256) public lastGasUpdate;
    
    // Events
    event SwapExecuted(address indexed tokenIn, address indexed tokenOut, uint256 amountIn, uint256 amountOut, uint8 dexId);
    event BestRouteFound(uint256 totalAmountOut, uint256 totalGasUsed);
    event PriceOracleUpdated(address token, uint256 price);
    event GasEstimateUpdated(address token, uint256 gasPrice);
    
    modifier onlyValidToken(address token) {
        require(token != address(0), "Invalid token address");
        require(gasPriceOfToken[token] > 0 || token == weth, "Token not supported");
        _;
    }
    
    modifier onlyAdmin() {
        require(msg.sender == owner, "Only admin");
        _;
    }
    
    constructor(
        address _uniswapV3Router,
        address _uniswapV3Factory,
        address _sushiSwapRouter,
        address _sushiSwapFactory,
        address _pancakeSwapV3Router,
        address _pancakeSwapV2Router
    ) {
        owner = msg.sender;
        uniswapV3Router = IUniswapV3Router(_uniswapV3Router);
        uniswapV3Factory = IUniswapV3Factory(_uniswapV3Factory);
        sushiSwapRouter = ISushiSwapRouter(_sushiSwapRouter);
        sushiSwapFactory = ISushiSwapFactory(_sushiSwapFactory);
        pancakeSwapV3Router = IPancakeSwapV3Router(_pancakeSwapV3Router);
        pancakeSwapV2Router = IPancakeSwapV2Router(_pancakeSwapV2Router);
    }
    
    /**
     * @dev Swap tokens using the best available route
     */
    function swapTokens(SwapParams calldata params) external payable returns (uint256 amountOut) {
        require(block.timestamp <= params.deadline, "Swap expired");
        require(params.amountIn > 0, "Invalid amount");
        
        BestRoute memory bestRoute = findBestRoute(params);
        require(bestRoute.isValid, "No valid route found");
        require(bestRoute.totalAmountOut >= params.minAmountOut, "Insufficient output");
        
        // Transfer tokens from user
        IERC20(params.tokenIn).transferFrom(msg.sender, address(this), params.amountIn);
        
        // Approve routers
        if (params.tokenIn != weth) {
            _approveToken(params.tokenIn);
        }
        
        // Execute swap based on best route
        if (params.dexId == 0) {
            amountOut = _swapUniswapV3(params.tokenIn, params.tokenOut, params.amountIn, params.fees, params.path);
        } else if (params.dexId == 1) {
            amountOut = _swapSushiSwap(params.tokenIn, params.tokenOut, params.amountIn, params.path);
        } else if (params.dexId == 2) {
            amountOut = _swapPancakeSwapV2(params.tokenIn, params.tokenOut, params.amountIn);
        } else if (params.dexId == 3) {
            amountOut = _swapPancakeSwapV3(params.tokenIn, params.tokenOut, params.amountIn, params.fees, params.path);
        }
        
        require(amountOut >= params.minAmountOut, "Slippage exceeded");
        
        // Transfer output tokens to user
        if (params.tokenOut == weth) {
            payable(msg.sender).transfer(amountOut);
        } else {
            IERC20(params.tokenOut).transfer(msg.sender, amountOut);
        }
        
        emit SwapExecuted(params.tokenIn, params.tokenOut, params.amountIn, amountOut, params.dexId);
    }
    
    /**
     * @dev Find the best route for swapping tokens
     */
    function findBestRoute(SwapParams calldata params) public view returns (BestRoute memory) {
        BestRoute memory bestRoute;
        RouteInfo[] memory routes = new RouteInfo[](5);
        uint256 routeCount = 0;
        
        // Check Uniswap V3
        if (_checkUniswapV3Availability(params.tokenIn, params.tokenOut)) {
            uint256 amountOut = _estimateUniswapV3Swap(params.tokenIn, params.tokenOut, params.amountIn);
            if (amountOut > 0) {
                routes[routeCount] = RouteInfo({
                    dexId: 0,
                    router: address(uniswapV3Router),
                    expectedAmountOut: amountOut,
                    gasEstimate: _estimateGas(0, params.amountIn),
                    priceImpact: _calculatePriceImpact(params.tokenIn, params.tokenOut, params.amountIn, amountOut),
                    slippage: _calculateSlippage(amountOut, params.minAmountOut)
                });
                routeCount++;
            }
        }
        
        // Check SushiSwap
        if (_checkSushiSwapAvailability(params.tokenIn, params.tokenOut)) {
            uint256 amountOut = _estimateSushiSwapSwap(params.tokenIn, params.tokenOut, params.amountIn);
            if (amountOut > 0) {
                routes[routeCount] = RouteInfo({
                    dexId: 1,
                    router: address(sushiSwapRouter),
                    expectedAmountOut: amountOut,
                    gasEstimate: _estimateGas(1, params.amountIn),
                    priceImpact: _calculatePriceImpact(params.tokenIn, params.tokenOut, params.amountIn, amountOut),
                    slippage: _calculateSlippage(amountOut, params.minAmountOut)
                });
                routeCount++;
            }
        }
        
        // Add other DEX checks...
        
        if (routeCount > 0) {
            RouteInfo[] memory validRoutes = new RouteInfo[](routeCount);
            for (uint256 i = 0; i < routeCount; i++) {
                validRoutes[i] = routes[i];
            }
            
            // Sort routes by best value (amountOut - gas cost)
            _sortRoutes(validRoutes);
            
            bestRoute = BestRoute({
                routes: validRoutes,
                totalAmountOut: validRoutes[0].expectedAmountOut,
                totalGasUsed: validRoutes[0].gasEstimate,
                totalPriceImpact: validRoutes[0].priceImpact,
                totalSlippage: validRoutes[0].slippage,
                isValid: true
            });
        }
        
        return bestRoute;
    }
    
    /**
     * @dev Update price oracle for a token
     */
    function updatePriceOracle(address token, uint256 price) external onlyAdmin {
        lastPrices[token] = price;
        priceUpdateTime[token] = block.timestamp;
        emit PriceOracleUpdated(token, price);
    }
    
    /**
     * @dev Update gas estimate for a token
     */
    function updateGasEstimate(address token, uint256 gasPrice) external onlyAdmin {
        gasPriceOfToken[token] = gasPrice;
        lastGasUpdate[token] = block.timestamp;
        emit GasEstimateUpdated(token, gasPrice);
    }
    
    /**
     * @dev Internal function to swap on Uniswap V3
     */
    function _swapUniswapV3(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint24[] memory fees,
        address[] memory path
    ) internal returns (uint256 amountOut) {
        if (fees.length == 1) {
            IUniswapV3Router.ExactInputSingleParams memory params = IUniswapV3Router.ExactInputSingleParams({
                tokenIn: tokenIn,
                tokenOut: tokenOut,
                fee: fees[0],
                recipient: address(this),
                deadline: block.timestamp + 300,
                amountIn: amountIn,
                amountOutMinimum: 0,
                sqrtPriceLimitX96: 0
            });
            amountOut = uniswapV3Router.exactInputSingle(params);
        } else {
            bytes memory pathBytes = _encodePath(path, fees);
            IUniswapV3Router.ExactInputParams memory params = IUniswapV3Router.ExactInputParams({
                path: pathBytes,
                recipient: address(this),
                deadline: block.timestamp + 300,
                amountIn: amountIn,
                amountOutMinimum: 0
            });
            amountOut = uniswapV3Router.exactInput(params);
        }
    }
    
    /**
     * @dev Internal function to swap on SushiSwap
     */
    function _swapSushiSwap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        address[] memory path
    ) internal returns (uint256 amountOut) {
        ISushiSwapRouter.ExactInputSingleParams memory params = ISushiSwapRouter.ExactInputSingleParams({
            tokenIn: tokenIn,
            tokenOut: tokenOut,
            recipient: address(this),
            deadline: block.timestamp + 300,
            amountIn: amountIn,
            amountOutMinimum: 0,
            sqrtPriceLimitX96: 0
        });
        amountOut = sushiSwapRouter.exactInputSingle(params);
    }
    
    /**
     * @dev Internal function to swap on PancakeSwap V2
     */
    function _swapPancakeSwapV2(
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) internal returns (uint256 amountOut) {
        IPancakeSwapV2Router.ExactInputSingleParams memory params = IPancakeSwapV2Router.ExactInputSingleParams({
            tokenIn: tokenIn,
            tokenOut: tokenOut,
            recipient: address(this),
            deadline: block.timestamp + 300,
            amountIn: amountIn,
            amountOutMinimum: 0
        });
        amountOut = pancakeSwapV2Router.exactInputSingle(params);
    }
    
    /**
     * @dev Internal function to swap on PancakeSwap V3
     */
    function _swapPancakeSwapV3(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint24[] memory fees,
        address[] memory path
    ) internal returns (uint256 amountOut) {
        if (fees.length == 1) {
            IPancakeSwapV3Router.ExactInputSingleParams memory params = IPancakeSwapV3Router.ExactInputSingleParams({
                tokenIn: tokenIn,
                tokenOut: tokenOut,
                fee: fees[0],
                recipient: address(this),
                deadline: block.timestamp + 300,
                amountIn: amountIn,
                amountOutMinimum: 0,
                sqrtPriceLimitX96: 0
            });
            amountOut = pancakeSwapV3Router.exactInputSingle(params);
        } else {
            bytes memory pathBytes = _encodePath(path, fees);
            IPancakeSwapV3Router.ExactInputParams memory params = IPancakeSwapV3Router.ExactInputParams({
                path: pathBytes,
                recipient: address(this),
                deadline: block.timestamp + 300,
                amountIn: amountIn,
                amountOutMinimum: 0
            });
            amountOut = pancakeSwapV3Router.exactInput(params);
        }
    }
    
    /**
     * @dev Helper functions for DEX checks and estimations
     */
    function _checkUniswapV3Availability(address tokenIn, address tokenOut) internal view returns (bool) {
        address pool = uniswapV3Factory.getPool(tokenIn, tokenOut, 500); // 0.05% fee
        return pool != address(0);
    }
    
    function _checkSushiSwapAvailability(address tokenIn, address tokenOut) internal view returns (bool) {
        address pair = sushiSwapFactory.getPair(tokenIn, tokenOut);
        return pair != address(0);
    }
    
    function _estimateUniswapV3Swap(address tokenIn, address tokenOut, uint256 amountIn) 
        internal view returns (uint256) {
        // Simplified estimation - in practice, this would call getQuoteAtTick
        address pool = uniswapV3Factory.getPool(tokenIn, tokenOut, 500);
        if (pool == address(0)) return 0;
        
        // Mock calculation - should use actual pool state
        return amountIn.mul(95).div(100); // 5% slippage estimate
    }
    
    function _estimateSushiSwapSwap(address tokenIn, address tokenOut, uint256 amountIn) 
        internal view returns (uint256) {
        address pair = sushiSwapFactory.getPair(tokenIn, tokenOut);
        if (pair == address(0)) return 0;
        
        // Mock calculation
        return amountIn.mul(94).div(100); // 6% slippage estimate
    }
    
    function _calculatePriceImpact(address tokenIn, address tokenOut, uint256 amountIn, uint256 amountOut) 
        internal view returns (uint256) {
        uint256 currentPrice = lastPrices[tokenIn].div(lastPrices[tokenOut]);
        uint256 actualPrice = amountIn.mul(1e18).div(amountOut);
        return actualPrice > currentPrice ? actualPrice.sub(currentPrice) : currentPrice.sub(actualPrice);
    }
    
    function _calculateSlippage(uint256 expectedAmount, uint256 minimumAmount) 
        internal pure returns (uint256) {
        if (expectedAmount == 0) return 0;
        return expectedAmount.sub(minimumAmount).mul(10000).div(expectedAmount);
    }
    
    function _sortRoutes(RouteInfo[] memory routes) internal pure {
        // Simple bubble sort - in practice, use more efficient sorting
        for (uint256 i = 0; i < routes.length - 1; i++) {
            for (uint256 j = i + 1; j < routes.length; j++) {
                if (_routeValue(routes[j]) > _routeValue(routes[i])) {
                    RouteInfo memory temp = routes[i];
                    routes[i] = routes[j];
                    routes[j] = temp;
                }
            }
        }
    }
    
    function _routeValue(RouteInfo memory route) internal pure returns (uint256) {
        // Value = expected output - gas cost
        return route.expectedAmountOut.sub(route.gasEstimate);
    }
    
    function _estimateGas(uint8 dexId, uint256 amountIn) internal view returns (uint256) {
        // Simplified gas estimation
        if (dexId == 0) return 150000; // Uniswap V3
        if (dexId == 1) return 120000; // SushiSwap
        if (dexId == 2) return 100000; // PancakeSwap V2
        if (dexId == 3) return 140000; // PancakeSwap V3
        return 200000; // Curve and others
    }
    
    function _encodePath(address[] memory path, uint24[] memory fees) internal pure returns (bytes memory) {
        bytes memory encoded = abi.encodePacked(path[0]);
        for (uint256 i = 0; i < fees.length; i++) {
            encoded = abi.encodePacked(encoded, fees[i], path[i + 1]);
        }
        return encoded;
    }
    
    function _approveToken(address token) internal {
        IERC20(token).approve(address(uniswapV3Router), type(uint256).max);
        IERC20(token).approve(address(sushiSwapRouter), type(uint256).max);
        IERC20(token).approve(address(pancakeSwapV2Router), type(uint256).max);
        IERC20(token).approve(address(pancakeSwapV3Router), type(uint256).max);
    }
}