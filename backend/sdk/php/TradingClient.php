<?php
/**
 * AI Trading Evolution - PHP SDK
 * ===============================
 * Official PHP client library for AI Trading Evolution API
 * 
 * @author MiniMax Agent
 * @version 1.0.0
 * @date 2025-11-04
 * 
 * Usage:
 * ```php
 * $client = new TradingClient('http://localhost:8000', 'your-api-key');
 * 
 * // Get market data
 * $data = $client->market->getData('BTC/USDT');
 * 
 * // Execute strategy
 * $signal = $client->strategy->execute('grid', 'BTC/USDT');
 * 
 * // Run analytics
 * $sentiment = $client->analytics->sentiment('BTC/USDT');
 * ```
 */

namespace AITrading\SDK;

// =============================================================================
// Exceptions
// =============================================================================

class APIException extends \Exception
{
    protected $statusCode;

    public function __construct($message, $statusCode = 0)
    {
        parent::__construct($message);
        $this->statusCode = $statusCode;
    }

    public function getStatusCode()
    {
        return $this->statusCode;
    }
}

// =============================================================================
// Base Client
// =============================================================================

class BaseClient
{
    private $baseUrl;
    private $apiKey;
    private $timeout;

    public function __construct($baseUrl, $apiKey = null, $timeout = 30)
    {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->apiKey = $apiKey;
        $this->timeout = $timeout;
    }

    private function request($method, $endpoint, $data = null)
    {
        $url = $this->baseUrl . $endpoint;
        
        $ch = curl_init($url);
        
        $headers = [
            'Content-Type: application/json'
        ];
        
        if ($this->apiKey) {
            $headers[] = 'Authorization: Bearer ' . $this->apiKey;
        }
        
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, $this->timeout);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        
        if ($method === 'POST') {
            curl_setopt($ch, CURLOPT_POST, true);
            if ($data) {
                curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
            }
        }
        
        $response = curl_exec($ch);
        $statusCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        curl_close($ch);
        
        if ($error) {
            throw new APIException("Connection error: $error");
        }
        
        $result = json_decode($response, true);
        
        if ($statusCode >= 400) {
            $message = $result['error'] ?? 'Unknown error';
            throw new APIException("API Error $statusCode: $message", $statusCode);
        }
        
        return $result;
    }

    public function get($endpoint)
    {
        return $this->request('GET', $endpoint);
    }

    public function post($endpoint, $data)
    {
        return $this->request('POST', $endpoint, $data);
    }
}

// =============================================================================
// Market API
// =============================================================================

class MarketAPI
{
    private $client;

    public function __construct(BaseClient $client)
    {
        $this->client = $client;
    }

    /**
     * Get market data
     */
    public function getData($symbol, $options = [])
    {
        $request = [
            'symbol' => $symbol,
            'market_type' => $options['market_type'] ?? 'crypto',
            'timeframe' => $options['timeframe'] ?? '1h',
            'limit' => $options['limit'] ?? 100
        ];

        return $this->client->post('/api/v1/market/data', $request);
    }

    /**
     * Get list of symbols
     */
    public function listSymbols($marketType = 'crypto')
    {
        return $this->client->get("/api/v1/market/symbols?market_type=$marketType");
    }
}

// =============================================================================
// Strategy API
// =============================================================================

class StrategyAPI
{
    private $client;

    public function __construct(BaseClient $client)
    {
        $this->client = $client;
    }

    /**
     * Execute trading strategy
     */
    public function execute($strategyName, $symbol, $options = [])
    {
        $request = [
            'strategy_name' => $strategyName,
            'symbol' => $symbol,
            'timeframe' => $options['timeframe'] ?? '1h',
            'parameters' => $options['parameters'] ?? []
        ];

        return $this->client->post('/api/v1/strategy/execute', $request);
    }

    /**
     * Get list of strategies
     */
    public function listStrategies()
    {
        return $this->client->get('/api/v1/strategy/list');
    }
}

// =============================================================================
// Analytics API
// =============================================================================

class AnalyticsAPI
{
    private $client;

    public function __construct(BaseClient $client)
    {
        $this->client = $client;
    }

    /**
     * Run analytics
     */
    public function analyze($analysisType, $symbol = null, $parameters = [])
    {
        $request = [
            'analysis_type' => $analysisType,
            'symbol' => $symbol,
            'parameters' => $parameters
        ];

        return $this->client->post('/api/v1/analytics/analyze', $request);
    }

    /**
     * Get sentiment analysis
     */
    public function sentiment($symbol)
    {
        return $this->analyze('sentiment', $symbol);
    }

    /**
     * Get risk scoring
     */
    public function riskScoring($symbol)
    {
        return $this->analyze('risk_scoring', $symbol);
    }

    /**
     * Get list of analytics types
     */
    public function listTypes()
    {
        return $this->client->get('/api/v1/analytics/types');
    }
}

// =============================================================================
// Main Trading Client
// =============================================================================

/**
 * Main AI Trading Evolution client
 * 
 * Example:
 * ```php
 * $client = new TradingClient('http://localhost:8000', 'your-api-key');
 * $data = $client->market->getData('BTC/USDT');
 * $signal = $client->strategy->execute('grid', 'BTC/USDT');
 * ```
 */
class TradingClient
{
    private $baseClient;

    public $market;
    public $strategy;
    public $analytics;

    /**
     * Create new TradingClient
     * 
     * @param string $baseUrl API base URL (e.g., "http://localhost:8000")
     * @param string|null $apiKey API key (optional)
     * @param int $timeout Request timeout in seconds
     */
    public function __construct($baseUrl, $apiKey = null, $timeout = 30)
    {
        $this->baseClient = new BaseClient($baseUrl, $apiKey, $timeout);

        // Initialize APIs
        $this->market = new MarketAPI($this->baseClient);
        $this->strategy = new StrategyAPI($this->baseClient);
        $this->analytics = new AnalyticsAPI($this->baseClient);
    }

    /**
     * Get API health status
     */
    public function health()
    {
        return $this->baseClient->get('/health');
    }

    /**
     * Get performance metrics
     */
    public function metrics()
    {
        return $this->baseClient->get('/metrics');
    }
}
