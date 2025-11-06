/**
 * AI Trading Evolution - Java SDK
 * ================================
 * Official Java client library for AI Trading Evolution API
 * 
 * @author MiniMax Agent
 * @version 1.0.0
 * @date 2025-11-04
 * 
 * Usage:
 * <pre>
 * {@code
 * TradingClient client = new TradingClient("http://localhost:8000", "your-api-key");
 * 
 * // Get market data
 * MarketDataResponse data = client.market.getData("BTC/USDT");
 * 
 * // Execute strategy
 * StrategyResponse signal = client.strategy.execute("grid", "BTC/USDT");
 * 
 * // Run analytics
 * AnalyticsResponse sentiment = client.analytics.sentiment("BTC/USDT");
 * }
 * </pre>
 */

package com.trading.ai.sdk;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

// =============================================================================
// Exceptions
// =============================================================================

class APIException extends Exception {
    private int statusCode;
    
    public APIException(String message, int statusCode) {
        super(message);
        this.statusCode = statusCode;
    }
    
    public int getStatusCode() {
        return statusCode;
    }
}

// =============================================================================
// Base Client
// =============================================================================

class BaseClient {
    private final String baseUrl;
    private final String apiKey;
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;
    
    public BaseClient(String baseUrl, String apiKey) {
        this.baseUrl = baseUrl.replaceAll("/$", "");
        this.apiKey = apiKey;
        this.httpClient = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(30))
            .build();
        this.objectMapper = new ObjectMapper();
    }
    
    private <T> T request(String method, String endpoint, Object data, Class<T> responseClass) 
            throws APIException, IOException, InterruptedException {
        
        String url = baseUrl + endpoint;
        HttpRequest.Builder builder = HttpRequest.newBuilder()
            .uri(URI.create(url))
            .timeout(Duration.ofSeconds(30));
        
        if (apiKey != null && !apiKey.isEmpty()) {
            builder.header("Authorization", "Bearer " + apiKey);
        }
        builder.header("Content-Type", "application/json");
        
        if ("POST".equals(method) && data != null) {
            String json = objectMapper.writeValueAsString(data);
            builder.POST(HttpRequest.BodyPublishers.ofString(json));
        } else {
            builder.GET();
        }
        
        HttpRequest request = builder.build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        
        if (response.statusCode() >= 400) {
            throw new APIException("API Error " + response.statusCode(), response.statusCode());
        }
        
        return objectMapper.readValue(response.body(), responseClass);
    }
    
    public <T> T get(String endpoint, Class<T> responseClass) 
            throws APIException, IOException, InterruptedException {
        return request("GET", endpoint, null, responseClass);
    }
    
    public <T> T post(String endpoint, Object data, Class<T> responseClass) 
            throws APIException, IOException, InterruptedException {
        return request("POST", endpoint, data, responseClass);
    }
}

// =============================================================================
// Response Models
// =============================================================================

class MarketDataResponse {
    public String symbol;
    public String market_type;
    public String timeframe;
    public Object[] data;
    public Map<String, Object> indicators;
    public String timestamp;
}

class StrategyResponse {
    public String strategy_name;
    public String symbol;
    public String signal;
    public double confidence;
    public double price;
    public Double entry_price;
    public Double stop_loss;
    public Double take_profit;
    public String timestamp;
    public Map<String, Object> metadata;
}

class AnalyticsResponse {
    public String analysis_type;
    public Map<String, Object> result;
    public String timestamp;
}

// =============================================================================
// Market API
// =============================================================================

class MarketAPI {
    private final BaseClient client;
    
    public MarketAPI(BaseClient client) {
        this.client = client;
    }
    
    /**
     * Get market data
     */
    public MarketDataResponse getData(String symbol) 
            throws APIException, IOException, InterruptedException {
        return getData(symbol, "crypto", "1h", 100);
    }
    
    public MarketDataResponse getData(String symbol, String marketType, String timeframe, int limit) 
            throws APIException, IOException, InterruptedException {
        
        Map<String, Object> request = new HashMap<>();
        request.put("symbol", symbol);
        request.put("market_type", marketType);
        request.put("timeframe", timeframe);
        request.put("limit", limit);
        
        return client.post("/api/v1/market/data", request, MarketDataResponse.class);
    }
    
    /**
     * Get list of symbols
     */
    public Object listSymbols(String marketType) 
            throws APIException, IOException, InterruptedException {
        return client.get("/api/v1/market/symbols?market_type=" + marketType, Object.class);
    }
}

// =============================================================================
// Strategy API
// =============================================================================

class StrategyAPI {
    private final BaseClient client;
    
    public StrategyAPI(BaseClient client) {
        this.client = client;
    }
    
    /**
     * Execute trading strategy
     */
    public StrategyResponse execute(String strategyName, String symbol) 
            throws APIException, IOException, InterruptedException {
        return execute(strategyName, symbol, "1h", null);
    }
    
    public StrategyResponse execute(String strategyName, String symbol, String timeframe, Map<String, Object> parameters) 
            throws APIException, IOException, InterruptedException {
        
        Map<String, Object> request = new HashMap<>();
        request.put("strategy_name", strategyName);
        request.put("symbol", symbol);
        request.put("timeframe", timeframe);
        request.put("parameters", parameters != null ? parameters : new HashMap<>());
        
        return client.post("/api/v1/strategy/execute", request, StrategyResponse.class);
    }
    
    /**
     * Get list of strategies
     */
    public Object list() throws APIException, IOException, InterruptedException {
        return client.get("/api/v1/strategy/list", Object.class);
    }
}

// =============================================================================
// Analytics API
// =============================================================================

class AnalyticsAPI {
    private final BaseClient client;
    
    public AnalyticsAPI(BaseClient client) {
        this.client = client;
    }
    
    /**
     * Run analytics
     */
    public AnalyticsResponse analyze(String analysisType, String symbol, Map<String, Object> parameters) 
            throws APIException, IOException, InterruptedException {
        
        Map<String, Object> request = new HashMap<>();
        request.put("analysis_type", analysisType);
        request.put("symbol", symbol);
        request.put("parameters", parameters != null ? parameters : new HashMap<>());
        
        return client.post("/api/v1/analytics/analyze", request, AnalyticsResponse.class);
    }
    
    /**
     * Get sentiment analysis
     */
    public AnalyticsResponse sentiment(String symbol) 
            throws APIException, IOException, InterruptedException {
        return analyze("sentiment", symbol, null);
    }
    
    /**
     * Get risk scoring
     */
    public AnalyticsResponse riskScoring(String symbol) 
            throws APIException, IOException, InterruptedException {
        return analyze("risk_scoring", symbol, null);
    }
}

// =============================================================================
// Main Trading Client
// =============================================================================

/**
 * Main AI Trading Evolution client
 * 
 * Example:
 * <pre>
 * {@code
 * TradingClient client = new TradingClient("http://localhost:8000", "your-api-key");
 * MarketDataResponse data = client.market.getData("BTC/USDT");
 * StrategyResponse signal = client.strategy.execute("grid", "BTC/USDT");
 * }
 * </pre>
 */
public class TradingClient {
    private final BaseClient baseClient;
    
    public final MarketAPI market;
    public final StrategyAPI strategy;
    public final AnalyticsAPI analytics;
    
    /**
     * Create new TradingClient
     * 
     * @param baseUrl API base URL (e.g., "http://localhost:8000")
     * @param apiKey API key (optional)
     */
    public TradingClient(String baseUrl, String apiKey) {
        this.baseClient = new BaseClient(baseUrl, apiKey);
        
        // Initialize APIs
        this.market = new MarketAPI(baseClient);
        this.strategy = new StrategyAPI(baseClient);
        this.analytics = new AnalyticsAPI(baseClient);
    }
    
    /**
     * Create new TradingClient without API key
     */
    public TradingClient(String baseUrl) {
        this(baseUrl, null);
    }
    
    /**
     * Get API health status
     */
    public Object health() throws APIException, IOException, InterruptedException {
        return baseClient.get("/health", Object.class);
    }
    
    /**
     * Get performance metrics
     */
    public Object metrics() throws APIException, IOException, InterruptedException {
        return baseClient.get("/metrics", Object.class);
    }
}
