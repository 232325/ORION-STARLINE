// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title FutarchyMarkets
 * @dev Futarchy prediction market governance
 * @author Advanced Voting Systems
 */
contract FutarchyMarkets is Ownable, ReentrancyGuard, Pausable {
    using Counters for Counters.Counter;

    enum MarketResolution {
        UNRESOLVED,
        RESOLVED_YES,
        RESOLVED_NO,
        RESOLVED_INCONCLUSIVE
    }

    enum Outcome {
        PENDING,
        SUCCESS,
        FAILURE,
        INCONCLUSIVE
    }

    struct FutarchyMarket {
        uint256 id;
        string title;
        string description;
        string resolutionCriteria;
        address marketCreator;
        uint256 creationTime;
        uint256 tradingEndTime;
        uint256 resolutionTime;
        uint256 outcomeTime;
        uint256 yesShares;
        uint256 noShares;
        uint256 totalShares;
        MarketResolution resolution;
        Outcome outcome;
        uint256 tradingVolume;
        bool isActive;
    }

    struct TradingPosition {
        address trader;
        uint256 yesShares;
        uint256 noShares;
        uint256 averageYesPrice;
        uint256 averageNoPrice;
        uint256 lastTradeTime;
    }

    struct FutarchyProposal {
        uint256 id;
        uint256 marketId;
        string title;
        string description;
        uint256 submissionTime;
        uint256 votingStartTime;
        uint256 votingEndTime;
        uint256 executionTime;
        int256 votingResult;
        Outcome marketOutcome;
        bool executed;
        mapping(address => int256) votes;
        uint256 totalYesVotingPower;
        uint256 totalNoVotingPower;
    }

    mapping(uint256 => FutarchyMarket) public markets;
    mapping(uint256 => FutarchyProposal) public proposals;
    mapping(uint256 => mapping(address => TradingPosition)) public tradingPositions;
    mapping(address => uint256[]) public userMarkets;
    mapping(address => FutarchyMarket[]) public userCreatedMarkets;
    
    Counters.Counter private marketCounter;
    Counters.Counter private proposalCounter;
    IERC20 public tradingToken;
    IERC20 public governanceToken;
    
    uint256 public constant TRADING_FEE = 50; // 0.5%
    uint256 public constant MIN_TRADE_SIZE = 100;
    uint256 public constant MAX_TRADING_PERIOD = 30 days;
    uint256 public constant MIN_RESOLUTION_TIME = 7 days;
    
    event MarketCreated(uint256 indexed marketId, string title, address indexed creator);
    event TradeExecuted(uint256 indexed marketId, address indexed trader, bool isYes, uint256 amount);
    event MarketResolved(uint256 indexed marketId, MarketResolution resolution, Outcome outcome);
    event FutarchyProposalCreated(uint256 indexed proposalId, uint256 indexed marketId, string title);
    event FutarchyVoted(address indexed voter, uint256 indexed proposalId, int256 choice);
    event FutarchyProposalExecuted(uint256 indexed proposalId, Outcome outcome);

    constructor(address _tradingToken, address _governanceToken) {
        tradingToken = IERC20(_tradingToken);
        governanceToken = IERC20(_governanceToken);
    }

    /**
     * @dev Create a new futarchy market
     */
    function createMarket(
        string memory _title,
        string memory _description,
        string memory _resolutionCriteria,
        uint256 _tradingDuration,
        uint256 _resolutionDuration
    ) external nonReentrant returns (uint256) {
        require(_tradingDuration >= 1 days && _tradingDuration <= MAX_TRADING_PERIOD, "Invalid trading duration");
        require(_resolutionDuration >= MIN_RESOLUTION_TIME, "Invalid resolution duration");
        
        marketCounter.increment();
        uint256 marketId = marketCounter.current();
        
        markets[marketId] = FutarchyMarket({
            id: marketId,
            title: _title,
            description: _description,
            resolutionCriteria: _resolutionCriteria,
            marketCreator: msg.sender,
            creationTime: block.timestamp,
            tradingEndTime: block.timestamp + _tradingDuration,
            resolutionTime: block.timestamp + _tradingDuration + _resolutionDuration,
            outcomeTime: 0,
            yesShares: 0,
            noShares: 0,
            totalShares: 0,
            resolution: MarketResolution.UNRESOLVED,
            outcome: Outcome.PENDING,
            tradingVolume: 0,
            isActive: true
        });
        
        userCreatedMarkets[msg.sender].push(markets[marketId]);
        emit MarketCreated(marketId, _title, msg.sender);
        return marketId;
    }

    /**
     * @dev Trade in prediction market (buy yes/no shares)
     */
    function trade(
        uint256 _marketId,
        bool _buyYes,
        uint256 _amount
    ) external nonReentrant {
        FutarchyMarket storage market = markets[_marketId];
        require(market.isActive, "Market not active");
        require(block.timestamp <= market.tradingEndTime, "Trading ended");
        require(_amount >= MIN_TRADE_SIZE, "Trade too small");
        
        // Calculate trading fee
        uint256 fee = _amount * TRADING_FEE / 10000;
        uint256 netAmount = _amount - fee;
        
        // Transfer tokens
        require(
            tradingToken.transferFrom(msg.sender, address(this), _amount),
            "Token transfer failed"
        );
        
        // Update market state
        if (_buyYes) {
            market.yesShares += netAmount;
        } else {
            market.noShares += netAmount;
        }
        market.totalShares += netAmount;
        market.tradingVolume += _amount;
        
        // Update trading position
        TradingPosition storage position = tradingPositions[_marketId][msg.sender];
        
        if (_buyYes) {
            if (position.yesShares > 0) {
                position.averageYesPrice = (position.averageYesPrice * position.yesShares + _amount) / 
                                          (position.yesShares + _amount);
            } else {
                position.averageYesPrice = _amount;
            }
            position.yesShares += netAmount;
        } else {
            if (position.noShares > 0) {
                position.averageNoPrice = (position.averageNoPrice * position.noShares + _amount) / 
                                         (position.noShares + _amount);
            } else {
                position.averageNoPrice = _amount;
            }
            position.noShares += netAmount;
        }
        
        position.lastTradeTime = block.timestamp;
        
        // Add to user's markets list
        bool exists = false;
        for (uint256 i = 0; i < userMarkets[msg.sender].length; i++) {
            if (userMarkets[msg.sender][i] == _marketId) {
                exists = true;
                break;
            }
        }
        if (!exists) {
            userMarkets[msg.sender].push(_marketId);
        }
        
        emit TradeExecuted(_marketId, msg.sender, _buyYes, _amount);
    }

    /**
     * @dev Resolve market outcome
     */
    function resolveMarket(uint256 _marketId, MarketResolution _resolution) external {
        FutarchyMarket storage market = markets[_marketId];
        require(market.isActive, "Market not active");
        require(block.timestamp >= market.resolutionTime, "Resolution time not reached");
        require(market.resolution == MarketResolution.UNRESOLVED, "Already resolved");
        require(_resolution != MarketResolution.UNRESOLVED, "Invalid resolution");
        
        // Verify resolver authorization (could be oracle, creator, or governance)
        require(
            msg.sender == market.marketCreator || msg.sender == owner(),
            "Not authorized to resolve"
        );
        
        market.resolution = _resolution;
        
        // Determine outcome based on resolution
        if (_resolution == MarketResolution.RESOLVED_YES) {
            market.outcome = Outcome.SUCCESS;
        } else if (_resolution == MarketResolution.RESOLVED_NO) {
            market.outcome = Outcome.FAILURE;
        } else if (_resolution == MarketResolution.RESOLVED_INCONCLUSIVE) {
            market.outcome = Outcome.INCONCLUSIVE;
        }
        
        market.outcomeTime = block.timestamp;
        
        emit MarketResolved(_marketId, _resolution, market.outcome);
        
        // If outcome is conclusive, resolve related proposals
        if (market.outcome != Outcome.INCONCLUSIVE) {
            _resolveFutarchyProposals(_marketId);
        }
    }

    /**
     * @dev Create futarchy proposal
     */
    function createFutarchyProposal(
        uint256 _marketId,
        string memory _title,
        string memory _description,
        uint256 _votingDuration
    ) external onlyOwner returns (uint256) {
        FutarchyMarket storage market = markets[_marketId];
        require(market.resolution == MarketResolution.RESOLVED_YES || market.resolution == MarketResolution.RESOLVED_NO, 
                "Market must be resolved");
        
        proposalCounter.increment();
        uint256 proposalId = proposalCounter.current();
        
        proposals[proposalId] = FutarchyProposal({
            id: proposalId,
            marketId: _marketId,
            title: _title,
            description: _description,
            submissionTime: block.timestamp,
            votingStartTime: block.timestamp,
            votingEndTime: block.timestamp + _votingDuration,
            executionTime: block.timestamp + _votingDuration + 1 days,
            votingResult: 0,
            marketOutcome: market.outcome,
            executed: false,
            totalYesVotingPower: 0,
            totalNoVotingPower: 0
        });
        
        emit FutarchyProposalCreated(proposalId, _marketId, _title);
        return proposalId;
    }

    /**
     * @dev Vote in futarchy (voting power based on market prediction accuracy)
     */
    function futarchyVote(
        uint256 _proposalId,
        int256 _choice,
        uint256 _votingPower
    ) external {
        require(_choice >= -1 && _choice <= 1, "Invalid choice");
        require(_votingPower > 0, "Voting power must be positive");
        
        FutarchyProposal storage proposal = proposals[_proposalId];
        require(block.timestamp >= proposal.votingStartTime, "Voting not started");
        require(block.timestamp <= proposal.votingEndTime, "Voting ended");
        
        // Calculate voting multiplier based on market prediction accuracy
        uint256 votingMultiplier = _calculateVotingMultiplier(msg.sender, proposal.marketId);
        uint256 effectivePower = _votingPower * votingMultiplier / 1000;
        
        proposal.votes[msg.sender] = _choice;
        
        if (_choice > 0) {
            proposal.totalYesVotingPower += effectivePower;
        } else if (_choice < 0) {
            proposal.totalNoVotingPower += effectivePower;
        }
        
        emit FutarchyVoted(msg.sender, _proposalId, _choice);
    }

    /**
     * @dev Execute futarchy proposal
     */
    function executeFutarchyProposal(uint256 _proposalId) external {
        FutarchyProposal storage proposal = proposals[_proposalId];
        require(!proposal.executed, "Already executed");
        require(block.timestamp > proposal.executionTime, "Execution time not reached");
        require(proposal.marketOutcome != Outcome.PENDING, "Market not resolved");
        
        proposal.executed = true;
        
        // Determine result based on market outcome and voting
        if (proposal.marketOutcome == Outcome.SUCCESS) {
            proposal.votingResult = proposal.totalYesVotingPower > proposal.totalNoVotingPower ? 1 : -1;
        } else if (proposal.marketOutcome == Outcome.FAILURE) {
            proposal.votingResult = proposal.totalNoVotingPower > proposal.totalYesVotingPower ? 1 : -1;
        }
        
        emit FutarchyProposalExecuted(_proposalId, proposal.marketOutcome);
        
        if (proposal.votingResult > 0) {
            _executeProposalActions(_proposalId);
        }
    }

    /**
     * @dev Calculate voting multiplier based on market prediction accuracy
     */
    function _calculateVotingMultiplier(address _user, uint256 _marketId) internal view returns (uint256) {
        FutarchyMarket storage market = markets[_marketId];
        TradingPosition storage position = tradingPositions[_marketId][_user];
        
        if (market.resolution == MarketResolution.UNRESOLVED) {
            return 1000; // Base multiplier
        }
        
        uint256 totalAccuracy = 0;
        uint256 predictionQuality = 0;
        
        if (market.resolution == MarketResolution.RESOLVED_YES) {
            // For YES resolution, holders of YES shares get bonus, NO holders get penalty
            if (position.yesShares > 0) {
                predictionQuality = Math.min(position.yesShares * 1000 / position.averageYesPrice, 2000);
            }
            if (position.noShares > 0) {
                predictionQuality = Math.max(predictionQuality - 100, 100);
            }
        } else if (market.resolution == MarketResolution.RESOLVED_NO) {
            // For NO resolution, holders of NO shares get bonus, YES holders get penalty
            if (position.noShares > 0) {
                predictionQuality = Math.min(position.noShares * 1000 / position.averageNoPrice, 2000);
            }
            if (position.yesShares > 0) {
                predictionQuality = Math.max(predictionQuality - 100, 100);
            }
        }
        
        return Math.max(predictionQuality, 500); // Minimum 50% multiplier
    }

    /**
     * @dev Resolve all futarchy proposals related to market
     */
    function _resolveFutarchyProposals(uint256 _marketId) internal {
        for (uint256 i = 1; i <= proposalCounter.current(); i++) {
            FutarchyProposal storage proposal = proposals[i];
            if (proposal.marketId == _marketId && !proposal.executed) {
                // Automatically resolve based on market outcome
                if (proposal.marketOutcome == Outcome.SUCCESS) {
                    proposal.votingResult = 1; // Assume success unless voting shows otherwise
                } else {
                    proposal.votingResult = -1; // Assume failure
                }
            }
        }
    }

    /**
     * @dev Internal execution function
     */
    function _executeProposalActions(uint256 _proposalId) internal {
        // Implementation for executing successful futarchy proposals
    }

    /**
     * @dev Get market price (probability)
     */
    function getMarketPrice(uint256 _marketId) external view returns (uint256 yesPrice, uint256 noPrice) {
        FutarchyMarket storage market = markets[_marketId];
        if (market.totalShares == 0) {
            return (500, 500); // 50/50 split for new markets
        }
        
        yesPrice = market.yesShares * 10000 / market.totalShares;
        noPrice = market.noShares * 10000 / market.totalShares;
    }

    /**
     * @dev Get trading position for user
     */
    function getTradingPosition(uint256 _marketId, address _user) external view returns (
        TradingPosition memory position
    ) {
        return tradingPositions[_marketId][_user];
    }

    /**
     * @dev Emergency pause
     */
    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }
}

// Math library
library Math {
    function min(uint256 a, uint256 b) internal pure returns (uint256) {
        return a < b ? a : b;
    }
    
    function max(uint256 a, uint256 b) internal pure returns (uint256) {
        return a > b ? a : b;
    }
}