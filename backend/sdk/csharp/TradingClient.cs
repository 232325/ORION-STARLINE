/**
 * AI Trading Evolution - C# SDK
 * ==============================
 * Official C# client library for AI Trading Evolution API
 * 
 * Author: MiniMax Agent
 * Version: 1.0.0
 * Date: 2025-11-04
 * 
 * Usage:
 *   var client = new TradingClient("http://localhost:8000", "your-api-key");
 *   
 *   // Get market data
 *   var data = await client.Market.GetDataAsync("BTC/USDT");
 *   
 *   // Execute strategy
 *   var signal = await client.Strategy.ExecuteAsync("grid", "BTC/USDT");
 *   
 *   // Run analytics
 *   var sentiment = await client.Analytics.SentimentAsync("BTC/USDT");
 */

using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace AITrading.SDK
{
    // =========================================================================
    // Exceptions
    // =========================================================================

    public class APIException : Exception
    {
        public int StatusCode { get; }

        public APIException(string message, int statusCode) : base(message)
        {
            StatusCode = statusCode;
        }
    }

    // =========================================================================
    // Models
    // =========================================================================

    public class StrategyResponse
    {
        public string StrategyName { get; set; }
        public string Symbol { get; set; }
        public string Signal { get; set; }
        public double Confidence { get; set; }
        public double Price { get; set; }
        public double? EntryPrice { get; set; }
        public double? StopLoss { get; set; }
        public double? TakeProfit { get; set; }
        public string Timestamp { get; set; }
        public Dictionary<string, object> Metadata { get; set; }
    }

    public class AnalyticsResponse
    {
        public string AnalysisType { get; set; }
        public Dictionary<string, object> Result { get; set; }
        public string Timestamp { get; set; }
    }

    // =========================================================================
    // Base Client
    // =========================================================================

    internal class BaseClient
    {
        private readonly string _baseUrl;
        private readonly string _apiKey;
        private readonly HttpClient _httpClient;
        private readonly JsonSerializerOptions _jsonOptions;

        public BaseClient(string baseUrl, string apiKey)
        {
            _baseUrl = baseUrl.TrimEnd('/');
            _apiKey = apiKey;
            _httpClient = new HttpClient
            {
                Timeout = TimeSpan.FromSeconds(30)
            };

            if (!string.IsNullOrEmpty(apiKey))
            {
                _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {apiKey}");
            }

            _jsonOptions = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            };
        }

        public async Task<T> GetAsync<T>(string endpoint)
        {
            var url = $"{_baseUrl}{endpoint}";
            var response = await _httpClient.GetAsync(url);

            if (!response.IsSuccessStatusCode)
            {
                var error = await response.Content.ReadAsStringAsync();
                throw new APIException($"API Error {response.StatusCode}", (int)response.StatusCode);
            }

            var content = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<T>(content, _jsonOptions);
        }

        public async Task<T> PostAsync<T>(string endpoint, object data)
        {
            var url = $"{_baseUrl}{endpoint}";
            var json = JsonSerializer.Serialize(data, _jsonOptions);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync(url, content);

            if (!response.IsSuccessStatusCode)
            {
                var error = await response.Content.ReadAsStringAsync();
                throw new APIException($"API Error {response.StatusCode}", (int)response.StatusCode);
            }

            var responseContent = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<T>(responseContent, _jsonOptions);
        }
    }

    // =========================================================================
    // Market API
    // =========================================================================

    public class MarketAPI
    {
        private readonly BaseClient _client;

        internal MarketAPI(BaseClient client)
        {
            _client = client;
        }

        /// <summary>
        /// Get market data
        /// </summary>
        public async Task<object> GetDataAsync(
            string symbol,
            string marketType = "crypto",
            string timeframe = "1h",
            int limit = 100)
        {
            var request = new
            {
                symbol,
                market_type = marketType,
                timeframe,
                limit
            };

            return await _client.PostAsync<object>("/api/v1/market/data", request);
        }

        /// <summary>
        /// Get list of symbols
        /// </summary>
        public async Task<object> ListSymbolsAsync(string marketType = "crypto")
        {
            return await _client.GetAsync<object>($"/api/v1/market/symbols?market_type={marketType}");
        }
    }

    // =========================================================================
    // Strategy API
    // =========================================================================

    public class StrategyAPI
    {
        private readonly BaseClient _client;

        internal StrategyAPI(BaseClient client)
        {
            _client = client;
        }

        /// <summary>
        /// Execute trading strategy
        /// </summary>
        public async Task<StrategyResponse> ExecuteAsync(
            string strategyName,
            string symbol,
            string timeframe = "1h",
            Dictionary<string, object> parameters = null)
        {
            var request = new
            {
                strategy_name = strategyName,
                symbol,
                timeframe,
                parameters = parameters ?? new Dictionary<string, object>()
            };

            return await _client.PostAsync<StrategyResponse>("/api/v1/strategy/execute", request);
        }

        /// <summary>
        /// Get list of strategies
        /// </summary>
        public async Task<object> ListAsync()
        {
            return await _client.GetAsync<object>("/api/v1/strategy/list");
        }
    }

    // =========================================================================
    // Analytics API
    // =========================================================================

    public class AnalyticsAPI
    {
        private readonly BaseClient _client;

        internal AnalyticsAPI(BaseClient client)
        {
            _client = client;
        }

        /// <summary>
        /// Run analytics
        /// </summary>
        public async Task<AnalyticsResponse> AnalyzeAsync(
            string analysisType,
            string symbol = null,
            Dictionary<string, object> parameters = null)
        {
            var request = new
            {
                analysis_type = analysisType,
                symbol,
                parameters = parameters ?? new Dictionary<string, object>()
            };

            return await _client.PostAsync<AnalyticsResponse>("/api/v1/analytics/analyze", request);
        }

        /// <summary>
        /// Get sentiment analysis
        /// </summary>
        public async Task<AnalyticsResponse> SentimentAsync(string symbol)
        {
            return await AnalyzeAsync("sentiment", symbol);
        }

        /// <summary>
        /// Get risk scoring
        /// </summary>
        public async Task<AnalyticsResponse> RiskScoringAsync(string symbol)
        {
            return await AnalyzeAsync("risk_scoring", symbol);
        }

        /// <summary>
        /// Get list of analytics types
        /// </summary>
        public async Task<object> ListTypesAsync()
        {
            return await _client.GetAsync<object>("/api/v1/analytics/types");
        }
    }

    // =========================================================================
    // Main Trading Client
    // =========================================================================

    /// <summary>
    /// Main AI Trading Evolution client
    /// </summary>
    public class TradingClient
    {
        private readonly BaseClient _baseClient;

        public MarketAPI Market { get; }
        public StrategyAPI Strategy { get; }
        public AnalyticsAPI Analytics { get; }

        /// <summary>
        /// Create new TradingClient
        /// </summary>
        /// <param name="baseUrl">API base URL (e.g., "http://localhost:8000")</param>
        /// <param name="apiKey">API key (optional)</param>
        public TradingClient(string baseUrl, string apiKey = null)
        {
            _baseClient = new BaseClient(baseUrl, apiKey);

            Market = new MarketAPI(_baseClient);
            Strategy = new StrategyAPI(_baseClient);
            Analytics = new AnalyticsAPI(_baseClient);
        }

        /// <summary>
        /// Get API health status
        /// </summary>
        public async Task<object> HealthAsync()
        {
            return await _baseClient.GetAsync<object>("/health");
        }

        /// <summary>
        /// Get performance metrics
        /// </summary>
        public async Task<object> MetricsAsync()
        {
            return await _baseClient.GetAsync<object>("/metrics");
        }
    }
}
