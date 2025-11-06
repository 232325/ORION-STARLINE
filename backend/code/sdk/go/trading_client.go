/**
 * AI Trading Evolution - Go SDK
 * ==============================
 * Official Go client library for AI Trading Evolution API
 * 
 * Author: MiniMax Agent
 * Version: 1.0.0
 * Date: 2025-11-04
 * 
 * Usage:
 *   client := trading.NewClient("http://localhost:8000", "your-api-key")
 *   
 *   // Get market data
 *   data, err := client.Market.GetData("BTC/USDT", nil)
 *   
 *   // Execute strategy
 *   signal, err := client.Strategy.Execute("grid", "BTC/USDT", nil)
 *   
 *   // Run analytics
 *   sentiment, err := client.Analytics.Sentiment("BTC/USDT")
 */

package trading

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// =============================================================================
// Types
// =============================================================================

// APIError represents an API error
type APIError struct {
	StatusCode int
	Message    string
}

func (e *APIError) Error() string {
	return fmt.Sprintf("API Error %d: %s", e.StatusCode, e.Message)
}

// MarketDataRequest represents market data request
type MarketDataRequest struct {
	Symbol     string                 `json:"symbol"`
	MarketType string                 `json:"market_type"`
	Timeframe  string                 `json:"timeframe"`
	Limit      int                    `json:"limit"`
}

// StrategyRequest represents strategy execution request
type StrategyRequest struct {
	StrategyName string                 `json:"strategy_name"`
	Symbol       string                 `json:"symbol"`
	Timeframe    string                 `json:"timeframe"`
	Parameters   map[string]interface{} `json:"parameters"`
}

// AnalyticsRequest represents analytics request
type AnalyticsRequest struct {
	AnalysisType string                 `json:"analysis_type"`
	Symbol       string                 `json:"symbol,omitempty"`
	Parameters   map[string]interface{} `json:"parameters"`
}

// StrategyResponse represents strategy execution response
type StrategyResponse struct {
	StrategyName string                 `json:"strategy_name"`
	Symbol       string                 `json:"symbol"`
	Signal       string                 `json:"signal"`
	Confidence   float64                `json:"confidence"`
	Price        float64                `json:"price"`
	EntryPrice   *float64               `json:"entry_price,omitempty"`
	StopLoss     *float64               `json:"stop_loss,omitempty"`
	TakeProfit   *float64               `json:"take_profit,omitempty"`
	Timestamp    string                 `json:"timestamp"`
	Metadata     map[string]interface{} `json:"metadata"`
}

// AnalyticsResponse represents analytics response
type AnalyticsResponse struct {
	AnalysisType string                 `json:"analysis_type"`
	Result       map[string]interface{} `json:"result"`
	Timestamp    string                 `json:"timestamp"`
}

// =============================================================================
// Base Client
// =============================================================================

// BaseClient handles HTTP requests
type BaseClient struct {
	baseURL    string
	apiKey     string
	httpClient *http.Client
}

// NewBaseClient creates a new base client
func NewBaseClient(baseURL, apiKey string) *BaseClient {
	return &BaseClient{
		baseURL: baseURL,
		apiKey:  apiKey,
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// request makes HTTP request
func (c *BaseClient) request(method, endpoint string, body interface{}, result interface{}) error {
	url := c.baseURL + endpoint

	var reqBody io.Reader
	if body != nil {
		jsonData, err := json.Marshal(body)
		if err != nil {
			return err
		}
		reqBody = bytes.NewBuffer(jsonData)
	}

	req, err := http.NewRequest(method, url, reqBody)
	if err != nil {
		return err
	}

	req.Header.Set("Content-Type", "application/json")
	if c.apiKey != "" {
		req.Header.Set("Authorization", "Bearer "+c.apiKey)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		var errorResponse map[string]interface{}
		json.NewDecoder(resp.Body).Decode(&errorResponse)
		message := "Unknown error"
		if msg, ok := errorResponse["error"].(string); ok {
			message = msg
		}
		return &APIError{
			StatusCode: resp.StatusCode,
			Message:    message,
		}
	}

	if result != nil {
		return json.NewDecoder(resp.Body).Decode(result)
	}

	return nil
}

// Get makes GET request
func (c *BaseClient) Get(endpoint string, result interface{}) error {
	return c.request("GET", endpoint, nil, result)
}

// Post makes POST request
func (c *BaseClient) Post(endpoint string, body, result interface{}) error {
	return c.request("POST", endpoint, body, result)
}

// =============================================================================
// Market API
// =============================================================================

// MarketAPI handles market data operations
type MarketAPI struct {
	client *BaseClient
}

// GetData retrieves market data
func (m *MarketAPI) GetData(symbol string, options *MarketDataRequest) (map[string]interface{}, error) {
	if options == nil {
		options = &MarketDataRequest{
			Symbol:     symbol,
			MarketType: "crypto",
			Timeframe:  "1h",
			Limit:      100,
		}
	} else {
		options.Symbol = symbol
		if options.MarketType == "" {
			options.MarketType = "crypto"
		}
		if options.Timeframe == "" {
			options.Timeframe = "1h"
		}
		if options.Limit == 0 {
			options.Limit = 100
		}
	}

	var result map[string]interface{}
	err := m.client.Post("/api/v1/market/data", options, &result)
	return result, err
}

// ListSymbols retrieves available symbols
func (m *MarketAPI) ListSymbols(marketType string) (map[string]interface{}, error) {
	var result map[string]interface{}
	err := m.client.Get("/api/v1/market/symbols?market_type="+marketType, &result)
	return result, err
}

// =============================================================================
// Strategy API
// =============================================================================

// StrategyAPI handles strategy operations
type StrategyAPI struct {
	client *BaseClient
}

// Execute executes trading strategy
func (s *StrategyAPI) Execute(strategyName, symbol string, options *StrategyRequest) (*StrategyResponse, error) {
	if options == nil {
		options = &StrategyRequest{
			StrategyName: strategyName,
			Symbol:       symbol,
			Timeframe:    "1h",
			Parameters:   make(map[string]interface{}),
		}
	} else {
		options.StrategyName = strategyName
		options.Symbol = symbol
		if options.Timeframe == "" {
			options.Timeframe = "1h"
		}
		if options.Parameters == nil {
			options.Parameters = make(map[string]interface{})
		}
	}

	var result StrategyResponse
	err := s.client.Post("/api/v1/strategy/execute", options, &result)
	return &result, err
}

// List retrieves available strategies
func (s *StrategyAPI) List() (map[string]interface{}, error) {
	var result map[string]interface{}
	err := s.client.Get("/api/v1/strategy/list", &result)
	return result, err
}

// =============================================================================
// Analytics API
// =============================================================================

// AnalyticsAPI handles analytics operations
type AnalyticsAPI struct {
	client *BaseClient
}

// Analyze runs analytics
func (a *AnalyticsAPI) Analyze(analysisType string, symbol *string, parameters map[string]interface{}) (*AnalyticsResponse, error) {
	req := &AnalyticsRequest{
		AnalysisType: analysisType,
		Parameters:   parameters,
	}
	if symbol != nil {
		req.Symbol = *symbol
	}
	if req.Parameters == nil {
		req.Parameters = make(map[string]interface{})
	}

	var result AnalyticsResponse
	err := a.client.Post("/api/v1/analytics/analyze", req, &result)
	return &result, err
}

// Sentiment retrieves sentiment analysis
func (a *AnalyticsAPI) Sentiment(symbol string) (*AnalyticsResponse, error) {
	return a.Analyze("sentiment", &symbol, nil)
}

// RiskScoring retrieves risk scoring
func (a *AnalyticsAPI) RiskScoring(symbol string) (*AnalyticsResponse, error) {
	return a.Analyze("risk_scoring", &symbol, nil)
}

// ListTypes retrieves available analytics types
func (a *AnalyticsAPI) ListTypes() (map[string]interface{}, error) {
	var result map[string]interface{}
	err := a.client.Get("/api/v1/analytics/types", &result)
	return result, err
}

// =============================================================================
// Main Trading Client
// =============================================================================

// Client is the main AI Trading Evolution client
type Client struct {
	baseClient *BaseClient

	Market    *MarketAPI
	Strategy  *StrategyAPI
	Analytics *AnalyticsAPI
}

// NewClient creates a new trading client
func NewClient(baseURL, apiKey string) *Client {
	baseClient := NewBaseClient(baseURL, apiKey)

	return &Client{
		baseClient: baseClient,
		Market:     &MarketAPI{client: baseClient},
		Strategy:   &StrategyAPI{client: baseClient},
		Analytics:  &AnalyticsAPI{client: baseClient},
	}
}

// Health retrieves API health status
func (c *Client) Health() (map[string]interface{}, error) {
	var result map[string]interface{}
	err := c.baseClient.Get("/health", &result)
	return result, err
}

// Metrics retrieves performance metrics
func (c *Client) Metrics() (map[string]interface{}, error) {
	var result map[string]interface{}
	err := c.baseClient.Get("/metrics", &result)
	return result, err
}
