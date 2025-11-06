"""
Influencer Manager
AI-ga qo'llab-quvvatlanadigan influencer partnership va management tizimi
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import sqlite3
import logging

logger = logging.getLogger(__name__)

class InfluencerTier(Enum):
    NANO = "nano"        # 1K-10K followers
    MICRO = "micro"      # 10K-100K followers  
    MACRO = "macro"      # 100K-1M followers
    MEGA = "mega"        # 1M+ followers

class Platform(Enum):
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TELEGRAM = "telegram"

class ContentType(Enum):
    POST = "post"
    STORY = "story"
    VIDEO = "video"
    LIVE = "live"
    REEL = "reel"
    SHORTS = "shorts"

class CampaignStatus(Enum):
    PLANNING = "planning"
    NEGOTIATION = "negotiation"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class InfluencerProfile:
    id: str
    name: str
    username: str
    email: str
    platforms: List[Platform]
    follower_count: int
    tier: InfluencerTier
    niche: str
    engagement_rate: float
    average_view_rate: float
    demographics: Dict
    content_quality_score: float
    brand_safety_score: float
    last_activity: datetime
    contact_info: Dict
    portfolio: List[str]

@dataclass
class CampaignBrief:
    id: str
    name: str
    brand: str
    objectives: List[str]
    target_audience: Dict
    budget: float
    timeline: Dict
    deliverables: List[Dict]
    content_guidelines: Dict
    success_metrics: List[str]

class InfluencerManager:
    """
    Comprehensive Influencer Marketing Management System
    """
    
    def __init__(self, db_path: str = "marketing_influencer.db"):
        self.db_path = db_path
        self.tier_configs = self._load_tier_configs()
        self.platform_configs = self._load_platform_configs()
        self._init_database()
    
    def _init_database(self):
        """Influencer ma'lumotlar bazasini ishga tushirish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Influencer profiles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS influencers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                username TEXT NOT NULL,
                email TEXT,
                platforms TEXT,
                follower_count INTEGER,
                tier TEXT,
                niche TEXT,
                engagement_rate REAL,
                average_view_rate REAL,
                demographics TEXT,
                content_quality_score REAL,
                brand_safety_score REAL,
                last_activity TEXT,
                contact_info TEXT,
                portfolio TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # Campaign briefs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaign_briefs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                brand TEXT NOT NULL,
                objectives TEXT,
                target_audience TEXT,
                budget REAL,
                timeline TEXT,
                deliverables TEXT,
                content_guidelines TEXT,
                success_metrics TEXT,
                status TEXT DEFAULT 'planning',
                created_at TEXT
            )
        """)
        
        # Partnerships
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS partnerships (
                id TEXT PRIMARY KEY,
                campaign_brief_id TEXT,
                influencer_id TEXT,
                status TEXT,
                compensation_type TEXT,
                compensation_amount REAL,
                deliverables TEXT,
                timeline TEXT,
                performance_data TEXT,
                created_at TEXT,
                FOREIGN KEY (campaign_brief_id) REFERENCES campaign_briefs(id),
                FOREIGN KEY (influencer_id) REFERENCES influencers(id)
            )
        """)
        
        # Performance tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_tracking (
                id TEXT PRIMARY KEY,
                partnership_id TEXT,
                content_type TEXT,
                platform TEXT,
                published_date TEXT,
                metrics TEXT,
                engagement_data TEXT,
                roi_data TEXT,
                FOREIGN KEY (partnership_id) REFERENCES partnerships(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_tier_configs(self) -> Dict:
        """Influencer tier konfiguratsiyalari"""
        return {
            InfluencerTier.NANO: {
                "follower_range": [1000, 10000],
                "avg_engagement_rate": 5.0,
                "cost_per_post": "50-200 USD",
                "targeting": "niche_communities",
                "benefits": ["High engagement", "Authentic content", "Cost-effective"],
                "best_for": ["Product launches", "Community building", "Authentic reviews"]
            },
            InfluencerTier.MICRO: {
                "follower_range": [10000, 100000],
                "avg_engagement_rate": 3.5,
                "cost_per_post": "200-1000 USD",
                "targeting": "specific_interests",
                "benefits": ["Good reach", "Quality engagement", "Professional"],
                "best_for": ["Brand awareness", "Product campaigns", "Thought leadership"]
            },
            InfluencerTier.MACRO: {
                "follower_range": [100000, 1000000],
                "avg_engagement_rate": 2.0,
                "cost_per_post": "1000-10000 USD",
                "targeting": "broad_audience",
                "benefits": ["High reach", "Brand recognition", "Professional quality"],
                "best_for": ["Major campaigns", "Brand partnerships", "Event promotion"]
            },
            InfluencerTier.MEGA: {
                "follower_range": [1000000, 999999999],
                "avg_engagement_rate": 1.5,
                "cost_per_post": "10000+ USD",
                "targeting": "mass_market",
                "benefits": ["Maximum reach", "Media attention", "Premium placement"],
                "best_for": ["Major launches", "Brand repositioning", "Crisis management"]
            }
        }
    
    def _load_platform_configs(self) -> Dict:
        """Platform-specific konfiguratsiyalar"""
        return {
            Platform.INSTAGRAM: {
                "content_types": ["post", "story", "reel", "igtv"],
                "algorithm_factors": ["engagement", "relevance", "relationship"],
                "best_practices": ["High-quality visuals", "Consistent posting", "Story engagement"],
                "analytics_metrics": ["reach", "impressions", "engagement", "saves"],
                "optimal_posting": "6-9 PM weekdays, 10 AM weekends",
                "audience_demographics": "18-34, 60% female"
            },
            Platform.YOUTUBE: {
                "content_types": ["video", "shorts", "live"],
                "algorithm_factors": ["watch_time", "engagement", "relevance"],
                "best_practices": ["SEO optimization", "Consistent uploads", "Audience interaction"],
                "analytics_metrics": ["views", "watch_time", "subscribers", "engagement"],
                "optimal_posting": "2-4 PM weekdays",
                "audience_demographics": "25-54, 60% male"
            },
            Platform.TIKTOK: {
                "content_types": ["video"],
                "algorithm_factors": ["completion_rate", "engagement", "trend_alignment"],
                "best_practices": ["Trend participation", "Short-form content", "Music usage"],
                "analytics_metrics": ["views", "likes", "shares", "comments"],
                "optimal_posting": "6-10 AM, 7-9 PM",
                "audience_demographics": "16-24, 55% female"
            },
            Platform.TWITTER: {
                "content_types": ["tweet", "thread", "spaces"],
                "algorithm_factors": ["relevance", "engagement", "freshness"],
                "best_practices": ["Real-time engagement", "Threads", "Visual content"],
                "analytics_metrics": ["impressions", "engagement", "retweets", "link_clicks"],
                "optimal_posting": "8-10 AM, 7-9 PM",
                "audience_demographics": "25-44, 55% male"
            }
        }
    
    async def discover_influencers(
        self,
        criteria: Dict,
        platform: Platform = None,
        tier: InfluencerTier = None,
        niche: str = None,
        location: str = None
    ) -> Dict:
        """Influencer discovery va search"""
        try:
            # Generate search query based on criteria
            search_query = await self._build_search_query(criteria, platform, tier, niche, location)
            
            # Search influencers
            discovered_influencers = await self._search_influencers(search_query, criteria)
            
            # Score and filter influencers
            scored_influencers = await this._score_influencers(discovered_influencers, criteria)
            
            # Analyze engagement quality
            engagement_analysis = await self._analyze_engagement_quality(scored_influencers)
            
            # Calculate reach potential
            reach_analysis = await self._calculate_reach_potential(scored_influencers, platform)
            
            # Generate discovery insights
            discovery_insights = await self._generate_discovery_insights(scored_influencers, criteria)
            
            return {
                "search_criteria": criteria,
                "total_discovered": len(scored_influencers),
                "top_influencers": scored_influencers[:20],  # Top 20
                "tier_distribution": self._analyze_tier_distribution(scored_influencers),
                "engagement_analysis": engagement_analysis,
                "reach_analysis": reach_analysis,
                "discovery_insights": discovery_insights,
                "recommended_next_steps": [
                    "Review top candidates manually",
                    "Conduct brand safety check",
                    "Check past collaboration history",
                    "Prepare outreach strategy"
                ],
                "search_metadata": {
                    "search_timestamp": datetime.now().isoformat(),
                    "search_scope": "global",
                    "data_freshness": "real-time"
                }
            }
            
        except Exception as e:
            logger.error(f"Influencer discovery error: {e}")
            return {"error": str(e)}
    
    async def create_influencer_profile(
        self,
        name: str,
        username: str,
        email: str,
        platforms: List[Platform],
        follower_count: int,
        niche: str,
        contact_info: Dict = None
    ) -> Dict:
        """Influencer profile yaratish"""
        try:
            # Determine tier based on follower count
            tier = self._determine_influencer_tier(follower_count)
            
            # Generate profile ID
            profile_id = f"influencer_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Analyze content quality
            content_quality_score = await self._analyze_content_quality(username, platforms)
            
            # Assess brand safety
            brand_safety_score = await self._assess_brand_safety(username, content_quality_score)
            
            # Get demographics data
            demographics = await self._get_demographics_data(username, platforms)
            
            # Calculate engagement metrics
            engagement_data = await self._calculate_engagement_metrics(username, platforms)
            
            # Create influencer profile
            profile = InfluencerProfile(
                id=profile_id,
                name=name,
                username=username,
                email=email,
                platforms=platforms,
                follower_count=follower_count,
                tier=tier,
                niche=niche,
                engagement_rate=engagement_data["engagement_rate"],
                average_view_rate=engagement_data["average_view_rate"],
                demographics=demographics,
                content_quality_score=content_quality_score,
                brand_safety_score=brand_safety_score,
                last_activity=datetime.now(),
                contact_info=contact_info or {},
                portfolio=[]
            )
            
            # Save profile
            await self._save_influencer_profile(profile)
            
            # Generate profile insights
            profile_insights = await self._generate_profile_insights(profile)
            
            # Calculate market value
            market_value = await self._calculate_market_value(profile)
            
            # Generate collaboration recommendations
            collaboration_recs = await self._generate_collaboration_recommendations(profile)
            
            logger.info(f"Influencer profile created: {profile_id}")
            
            return {
                "status": "created",
                "profile_id": profile_id,
                "profile_summary": {
                    "name": name,
                    "username": username,
                    "tier": tier.value,
                    "niche": niche,
                    "total_followers": follower_count,
                    "engagement_rate": engagement_data["engagement_rate"]
                },
                "tier_analysis": self.tier_configs[tier],
                "profile_insights": profile_insights,
                "market_value": market_value,
                "collaboration_recommendations": collaboration_recs,
                "platform_breakdown": await self._analyze_platform_performance(profile),
                "content_analysis": await this._analyze_content_strategy(profile),
                "brand_fit_score": await self._calculate_brand_fit_score(profile)
            }
            
        except Exception as e:
            logger.error(f"Influencer profile creation error: {e}")
            return {"error": str(e)}
    
    async def create_campaign_brief(
        self,
        name: str,
        brand: str,
        objectives: List[str],
        target_audience: Dict,
        budget: float,
        timeline: Dict,
        deliverables: List[Dict]
    ) -> Dict:
        """Campaign brief yaratish"""
        try:
            # Generate campaign ID
            campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Validate objectives
            objective_validation = await self._validate_campaign_objectives(objectives)
            
            # Analyze budget allocation
            budget_analysis = await self._analyze_budget_allocation(budget, deliverables)
            
            # Create content guidelines
            content_guidelines = await self._create_content_guidelines(target_audience, objectives)
            
            # Define success metrics
            success_metrics = await self._define_success_metrics(objectives, deliverables)
            
            # Create campaign brief
            brief = CampaignBrief(
                id=campaign_id,
                name=name,
                brand=brand,
                objectives=objectives,
                target_audience=target_audience,
                budget=budget,
                timeline=timeline,
                deliverables=deliverables,
                content_guidelines=content_guidelines,
                success_metrics=success_metrics
            )
            
            # Save campaign brief
            await self._save_campaign_brief(brief)
            
            # Generate influencer recommendations
            influencer_recommendations = await this._recommend_influencers(brief)
            
            # Create campaign strategy
            strategy = await self._create_campaign_strategy(brief, influencer_recommendations)
            
            # Estimate campaign performance
            performance_estimate = await self._estimate_campaign_performance(brief, influencer_recommendations)
            
            logger.info(f"Campaign brief created: {campaign_id}")
            
            return {
                "status": "created",
                "campaign_id": campaign_id,
                "campaign_name": name,
                "brand": brand,
                "budget_analysis": budget_analysis,
                "objective_validation": objective_validation,
                "content_guidelines": content_guidelines,
                "success_metrics": success_metrics,
                "influencer_recommendations": influencer_recommendations,
                "campaign_strategy": strategy,
                "performance_estimate": performance_estimate,
                "timeline_breakdown": await self._create_timeline_breakdown(timeline),
                "risk_assessment": await this._assess_campaign_risks(brief),
                "compliance_checklist": await self._create_compliance_checklist(brief)
            }
            
        except Exception as e:
            logger.error(f"Campaign brief creation error: {e}")
            return {"error": str(e)}
    
    async def negotiate_partnership(
        self,
        campaign_id: str,
        influencer_id: str,
        offer_details: Dict
    ) -> Dict:
        """Partnership negotiation"""
        try:
            # Get influencer profile
            influencer = await self._get_influencer_profile(influencer_id)
            if not influencer:
                return {"error": "Influencer not found"}
            
            # Get campaign brief
            brief = await self._get_campaign_brief(campaign_id)
            if not brief:
                return {"error": "Campaign not found"}
            
            # Analyze offer competitiveness
            offer_analysis = await self._analyze_offer_competitiveness(influencer, offer_details)
            
            # Calculate negotiation parameters
            negotiation_params = await this._calculate_negotiation_parameters(influencer, brief, offer_details)
            
            # Generate counter-offer suggestions
            counter_offers = await self._generate_counter_offer_suggestions(influencer, offer_analysis)
            
            # Create negotiation timeline
            negotiation_timeline = await self._create_negotiation_timeline(offer_details)
            
            # Set up tracking
            negotiation_tracking = await self._setup_negotiation_tracking(campaign_id, influencer_id)
            
            return {
                "campaign_id": campaign_id,
                "influencer_id": influencer_id,
                "offer_analysis": offer_analysis,
                "negotiation_parameters": negotiation_params,
                "counter_offer_suggestions": counter_offers,
                "negotiation_timeline": negotiation_timeline,
                "tracking_setup": negotiation_tracking,
                "success_probability": negotiation_params["success_probability"],
                "recommended_strategy": negotiation_params["recommended_strategy"],
                "risk_factors": await this._identify_negotiation_risks(influencer, offer_details),
                "expected_outcome": await self._predict_negotiation_outcome(influencer, offer_details)
            }
            
        except Exception as e:
            logger.error(f"Partnership negotiation error: {e}")
            return {"error": str(e)}
    
    async def track_partnership_performance(
        self,
        partnership_id: str,
        content_data: Dict
    ) -> Dict:
        """Partnership performance tracking"""
        try:
            # Validate content data
            validation_result = await self._validate_content_data(content_data)
            if not validation_result["valid"]:
                return {"error": "Invalid content data", "issues": validation_result["issues"]}
            
            # Get current performance metrics
            current_performance = await self._get_current_partnership_metrics(partnership_id)
            
            # Calculate new metrics
            new_metrics = await self._calculate_content_metrics(content_data)
            
            # Analyze performance trends
            performance_trends = await self._analyze_performance_trends(current_performance, new_metrics)
            
            # Calculate ROI
            roi_analysis = await self._calculate_partnership_roi(partnership_id, new_metrics)
            
            # Generate performance insights
            insights = await self._generate_performance_insights(performance_trends, roi_analysis)
            
            # Create optimization recommendations
            optimization_recs = await self._create_optimization_recommendations(performance_trends)
            
            # Update tracking data
            await self._update_partnership_tracking(partnership_id, new_metrics)
            
            return {
                "partnership_id": partnership_id,
                "content_type": content_data.get("type"),
                "platform": content_data.get("platform"),
                "published_date": content_data.get("published_date"),
                "performance_metrics": new_metrics,
                "performance_trends": performance_trends,
                "roi_analysis": roi_analysis,
                "insights": insights,
                "optimization_recommendations": optimization_recs,
                "benchmarks": await self._get_platform_benchmarks(content_data.get("platform")),
                "next_steps": await self._suggest_next_steps(performance_trends),
                "alerts": await self._check_performance_alerts(new_metrics)
            }
            
        except Exception as e:
            logger.error(f"Performance tracking error: {e}")
            return {"error": str(e)}
    
    async def manage_content_approval(
        self,
        content_id: str,
        status: str,
        feedback: str = None,
        revision_request: Dict = None
    ) -> Dict:
        """Content approval management"""
        try:
            # Get content details
            content_details = await self._get_content_details(content_id)
            if not content_details:
                return {"error": "Content not found"}
            
            # Process approval decision
            approval_result = await self._process_approval_decision(content_id, status, feedback, revision_request)
            
            # Check compliance
            compliance_check = await self._check_content_compliance(content_details)
            
            # Generate feedback if needed
            feedback_report = await self._generate_feedback_report(content_details, status, feedback)
            
            # Update content status
            await self._update_content_status(content_id, status, approval_result)
            
            # Notify relevant parties
            notifications = await this._send_approval_notifications(content_id, status, feedback)
            
            return {
                "content_id": content_id,
                "status": status,
                "approval_result": approval_result,
                "compliance_check": compliance_check,
                "feedback_report": feedback_report,
                "notifications_sent": notifications,
                "next_actions": await self._suggest_next_actions(status, content_details),
                "approval_timeline": await this._create_approval_timeline(content_details),
                "quality_score": await self._calculate_content_quality_score(content_details),
                "brand_guidelines_compliance": await this._check_brand_guidelines(content_details)
            }
            
        except Exception as e:
            logger.error(f"Content approval error: {e}")
            return {"error": str(e)}
    
    async def generate_campaign_report(
        self,
        campaign_id: str,
        report_type: str = "comprehensive",
        date_range: Tuple[datetime, datetime] = None
    ) -> Dict:
        """Campaign performance report generation"""
        try:
            if not date_range:
                date_range = (datetime.now() - timedelta(days=30), datetime.now())
            
            # Get campaign data
            campaign_data = await self._get_campaign_data(campaign_id, date_range)
            
            # Get partnerships data
            partnerships_data = await self._get_partnerships_data(campaign_id, date_range)
            
            # Calculate overall metrics
            overall_metrics = await self._calculate_overall_metrics(campaign_data, partnerships_data)
            
            # Analyze influencer performance
            influencer_analysis = await self._analyze_influencer_performance(partnerships_data)
            
            # Generate ROI analysis
            roi_analysis = await this._generate_roi_analysis(partnerships_data, campaign_data)
            
            # Create audience insights
            audience_insights = await self._create_audience_insights(partnerships_data)
            
            # Generate recommendations
            recommendations = await self._generate_campaign_recommendations(overall_metrics, influencer_analysis)
            
            # Create executive summary
            executive_summary = await self._create_executive_summary(overall_metrics, roi_analysis)
            
            return {
                "report_type": report_type,
                "campaign_id": campaign_id,
                "report_period": {
                    "start": date_range[0].isoformat(),
                    "end": date_range[1].isoformat()
                },
                "executive_summary": executive_summary,
                "overall_metrics": overall_metrics,
                "influencer_performance": influencer_analysis,
                "roi_analysis": roi_analysis,
                "audience_insights": audience_insights,
                "recommendations": recommendations,
                "key_achievements": await self._identify_key_achievements(campaign_data, partnerships_data),
                "challenges": await self._identify_challenges(campaign_data, partnerships_data),
                "best_performing_content": await this._identify_best_performing_content(partnerships_data),
                "benchmark_comparison": await this._compare_with_industry_benchmarks(overall_metrics),
                "next_steps": await self._suggest_campaign_next_steps(campaign_data, partnerships_data)
            }
            
        except Exception as e:
            logger.error(f"Campaign report generation error: {e}")
            return {"error": str(e)}
    
    async def create_relationship_management_system(
        self,
        influencer_id: str,
        relationship_type: str = "partnership"
    ) -> Dict:
        """Influencer relationship management"""
        try:
            # Get influencer profile
            profile = await self._get_influencer_profile(influencer_id)
            if not profile:
                return {"error": "Influencer not found"}
            
            # Analyze relationship history
            history_analysis = await self._analyze_relationship_history(influencer_id)
            
            # Create engagement strategy
            engagement_strategy = await self._create_engagement_strategy(profile, history_analysis)
            
            # Set up communication schedule
            communication_schedule = await self._create_communication_schedule(profile, relationship_type)
            
            # Generate value propositions
            value_props = await self._generate_value_propositions(profile)
            
            # Create retention plan
            retention_plan = await this._create_retention_plan(profile, history_analysis)
            
            return {
                "influencer_id": influencer_id,
                "relationship_type": relationship_type,
                "relationship_score": await self._calculate_relationship_score(profile, history_analysis),
                "history_analysis": history_analysis,
                "engagement_strategy": engagement_strategy,
                "communication_schedule": communication_schedule,
                "value_propositions": value_props,
                "retention_plan": retention_plan,
                "loyalty_metrics": await this._calculate_loyalty_metrics(history_analysis),
                "growth_opportunities": await self._identify_growth_opportunities(profile, history_analysis),
                "collaboration_history": await this._get_collaboration_history(influencer_id),
                "preferred_communication": await this._get_preferred_communication_methods(profile),
                "next_engagement": await this._suggest_next_engagement(profile, history_analysis)
            }
            
        except Exception as e:
            logger.error(f"Relationship management error: {e}")
            return {"error": str(e)}
    
    # Helper methods
    def _determine_influencer_tier(self, follower_count: int) -> InfluencerTier:
        """Determine influencer tier based on follower count"""
        if follower_count >= 1000000:
            return InfluencerTier.MEGA
        elif follower_count >= 100000:
            return InfluencerTier.MACRO
        elif follower_count >= 10000:
            return InfluencerTier.MICRO
        else:
            return InfluencerTier.NANO
    
    async def _build_search_query(self, criteria: Dict, platform: Platform = None, tier: InfluencerTier = None, niche: str = None, location: str = None) -> str:
        """Build search query based on criteria"""
        query_parts = []
        
        if niche:
            query_parts.append(f"niche:{niche}")
        
        if platform:
            query_parts.append(f"platform:{platform.value}")
        
        if tier:
            query_parts.append(f"tier:{tier.value}")
        
        if location:
            query_parts.append(f"location:{location}")
        
        # Add engagement criteria
        if "min_engagement" in criteria:
            query_parts.append(f"engagement_rate:>{criteria['min_engagement']}")
        
        return " AND ".join(query_parts)
    
    async def _search_influencers(self, query: str, criteria: Dict) -> List[Dict]:
        """Search influencers based on query"""
        # Simplified search - in reality would use real APIs
        return [
            {
                "name": "Sample Influencer 1",
                "username": "sample1",
                "platforms": ["instagram"],
                "follower_count": 50000,
                "engagement_rate": 4.2,
                "niche": "tech"
            },
            {
                "name": "Sample Influencer 2", 
                "username": "sample2",
                "platforms": ["youtube"],
                "follower_count": 150000,
                "engagement_rate": 3.1,
                "niche": "education"
            }
        ]
    
    async def _score_influencers(self, influencers: List[Dict], criteria: Dict) -> List[Dict]:
        """Score and rank influencers"""
        scored = []
        
        for influencer in influencers:
            score = 0
            
            # Engagement score
            if "min_engagement" in criteria:
                if influencer["engagement_rate"] >= criteria["min_engagement"]:
                    score += 40
            
            # Follower score
            if "follower_range" in criteria:
                followers = influencer["follower_count"]
                if criteria["follower_range"][0] <= followers <= criteria["follower_range"][1]:
                    score += 30
            
            # Niche match score
            if "niche_match" in criteria and influencer.get("niche") == criteria["niche_match"]:
                score += 20
            
            # Brand safety score
            score += 10  # Assume good brand safety
            
            influencer["score"] = score
            scored.append(influencer)
        
        # Sort by score
        return sorted(scored, key=lambda x: x["score"], reverse=True)
    
    async def _analyze_engagement_quality(self, influencers: List[Dict]) -> Dict:
        """Analyze engagement quality across influencers"""
        avg_engagement = sum(inf["engagement_rate"] for inf in influencers) / len(influencers)
        
        return {
            "average_engagement_rate": avg_engagement,
            "high_engagement_count": len([inf for inf in influencers if inf["engagement_rate"] > avg_engagement]),
            "engagement_distribution": {
                "excellent": len([inf for inf in influencers if inf["engagement_rate"] > 5.0]),
                "good": len([inf for inf in influencers if 3.0 <= inf["engagement_rate"] <= 5.0]),
                "average": len([inf for inf in influencers if inf["engagement_rate"] < 3.0])
            }
        }
    
    async def _calculate_reach_potential(self, influencers: List[Dict], platform: Platform = None) -> Dict:
        """Calculate total reach potential"""
        total_followers = sum(inf["follower_count"] for inf in influencers)
        
        platform_multipliers = {
            Platform.INSTAGRAM: 0.15,
            Platform.YOUTUBE: 0.10,
            Platform.TIKTOK: 0.20,
            Platform.TWITTER: 0.05
        }
        
        multiplier = platform_multipliers.get(platform, 0.15)
        estimated_reach = int(total_followers * multiplier)
        
        return {
            "total_followers": total_followers,
            "estimated_reach": estimated_reach,
            "platform_multiplier": multiplier,
            "reach_confidence": "medium"
        }
    
    async def _generate_discovery_insights(self, influencers: List[Dict], criteria: Dict) -> List[str]:
        """Generate insights about influencer discovery"""
        insights = [
            f"{len(influencers)} ta influencer topildi",
            f"O'rtacha engagement rate: {sum(inf['engagement_rate'] for inf in influencers) / len(influencers):.1f}%",
            "High-quality nano va micro influencerlar ko'p topildi"
        ]
        
        return insights
    
    def _analyze_tier_distribution(self, influencers: List[Dict]) -> Dict:
        """Analyze distribution across influencer tiers"""
        tier_counts = {
            InfluencerTier.NANO.value: 0,
            InfluencerTier.MICRO.value: 0,
            InfluencerTier.MACRO.value: 0,
            InfluencerTier.MEGA.value: 0
        }
        
        for influencer in influencers:
            tier = self._determine_influencer_tier(influencer["follower_count"])
            tier_counts[tier.value] += 1
        
        return tier_counts
    
    async def _save_influencer_profile(self, profile: InfluencerProfile):
        """Save influencer profile to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO influencers 
            (id, name, username, email, platforms, follower_count, tier, niche,
             engagement_rate, average_view_rate, demographics, content_quality_score,
             brand_safety_score, last_activity, contact_info, portfolio, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile.id, profile.name, profile.username, profile.email,
            json.dumps([p.value for p in profile.platforms]), profile.follower_count,
            profile.tier.value, profile.niche, profile.engagement_rate,
            profile.average_view_rate, json.dumps(profile.demographics),
            profile.content_quality_score, profile.brand_safety_score,
            profile.last_activity.isoformat(), json.dumps(profile.contact_info),
            json.dumps(profile.portfolio), datetime.now().isoformat(), datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    async def _analyze_content_quality(self, username: str, platforms: List[Platform]) -> float:
        """Analyze content quality score"""
        # Simplified quality analysis
        base_score = 75.0
        
        # Platform-specific adjustments
        platform_adjustments = {
            Platform.INSTAGRAM: 5.0,
            Platform.YOUTUBE: 10.0,
            Platform.TIKTOK: 8.0,
            Platform.TWITTER: 3.0
        }
        
        adjustment = sum(platform_adjustments.get(p, 0) for p in platforms)
        final_score = min(100, base_score + adjustment)
        
        return final_score
    
    async def _assess_brand_safety(self, username: str, content_quality: float) -> float:
        """Assess brand safety score"""
        # Simplified brand safety assessment
        base_score = 80.0
        
        # Higher quality content generally safer
        quality_bonus = (content_quality - 75.0) * 0.5
        final_score = min(100, base_score + quality_bonus)
        
        return final_score
    
    async def _get_demographics_data(self, username: str, platforms: List[Platform]) -> Dict:
        """Get demographics data"""
        return {
            "age_groups": {
                "18-24": 30,
                "25-34": 40,
                "35-44": 20,
                "45+": 10
            },
            "gender": {
                "male": 45,
                "female": 55
            },
            "top_locations": ["Uzbekistan", "Russia", "Kazakhstan"],
            "interests": ["technology", "business", "education"]
        }
    
    async def _calculate_engagement_metrics(self, username: str, platforms: List[Platform]) -> Dict:
        """Calculate engagement metrics"""
        # Simplified calculation
        platform_rates = {
            Platform.INSTAGRAM: 4.2,
            Platform.YOUTUBE: 2.8,
            Platform.TIKTOK: 8.5,
            Platform.TWITTER: 1.5
        }
        
        avg_engagement = sum(platform_rates.get(p, 3.0) for p in platforms) / len(platforms)
        avg_view_rate = avg_engagement * 0.6  # Views typically higher than engagement
        
        return {
            "engagement_rate": round(avg_engagement, 2),
            "average_view_rate": round(avg_view_rate, 2)
        }
    
    async def _generate_profile_insights(self, profile: InfluencerProfile) -> List[str]:
        """Generate profile insights"""
        insights = [
            f"Engagement rate {profile.tier.value} influencer uchun {profile.engagement_rate}% - yaxshi ko'rsatkich",
            f"Content quality score {profile.content_quality_score}/100 - professional darajada",
            f"Brand safety score {profile.brand_safety_score}/100 - yuqori darajada xavfsiz"
        ]
        
        return insights
    
    async def _calculate_market_value(self, profile: InfluencerProfile) -> Dict:
        """Calculate market value"""
        tier_config = self.tier_configs[profile.tier]
        
        # Extract cost range
        cost_range = tier_config["cost_per_post"]
        min_cost, max_cost = map(int, cost_range.replace("USD", "").replace("$", "").replace("-", " ").split())
        
        # Adjust based on engagement rate
        engagement_multiplier = profile.engagement_rate / tier_config["avg_engagement_rate"]
        adjusted_min_cost = int(min_cost * engagement_multiplier)
        adjusted_max_cost = int(max_cost * engagement_multiplier)
        
        return {
            "estimated_cost_per_post": f"{adjusted_min_cost}-{adjusted_max_cost} USD",
            "engagement_multiplier": round(engagement_multiplier, 2),
            "value_factors": [
                f"{profile.engagement_rate}% engagement rate",
                f"{profile.content_quality_score}/100 content quality",
                f"{profile.brand_safety_score}/100 brand safety"
            ]
        }
    
    async def _generate_collaboration_recommendations(self, profile: InfluencerProfile) -> List[str]:
        """Generate collaboration recommendations"""
        tier_config = self.tier_configs[profile.tier]
        
        recommendations = [
            f"Best for: {', '.join(tier_config['best_for'])}",
            "Product review content",
            "Tutorial va how-to content",
            "Behind-the-scenes content"
        ]
        
        if profile.engagement_rate > tier_config["avg_engagement_rate"]:
            recommendations.append("High engagement - ideal for brand partnerships")
        
        return recommendations
    
    async def _analyze_platform_performance(self, profile: InfluencerProfile) -> Dict:
        """Analyze platform-specific performance"""
        breakdown = {}
        
        for platform in profile.platforms:
            platform_config = self.platform_configs.get(platform, {})
            breakdown[platform.value] = {
                "content_types": platform_config.get("content_types", []),
                "optimal_posting": platform_config.get("optimal_posting", ""),
                "audience_demographics": platform_config.get("audience_demographics", "")
            }
        
        return breakdown
    
    async def _analyze_content_strategy(self, profile: InfluencerProfile) -> Dict:
        """Analyze content strategy"""
        return {
            "content_frequency": "daily",
            "best_performing_content": "educational",
            "visual_style": "professional",
            "tone_of_voice": "informative",
            "hashtag_strategy": "niche_specific",
            "collaboration_style": "authentic"
        }
    
    async def _calculate_brand_fit_score(self, profile: InfluencerProfile) -> float:
        """Calculate brand fit score"""
        # Combine multiple factors
        quality_score = profile.content_quality_score * 0.3
        safety_score = profile.brand_safety_score * 0.3
        engagement_score = min(100, profile.engagement_rate * 20) * 0.2
        niche_score = 80  # Assume good niche match * 0.2
        
        total_score = quality_score + safety_score + engagement_score + niche_score
        return round(total_score, 1)
    
    # Additional placeholder methods for comprehensive functionality
    async def _save_campaign_brief(self, brief: CampaignBrief):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO campaign_briefs 
            (id, name, brand, objectives, target_audience, budget, timeline, 
             deliverables, content_guidelines, success_metrics, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            brief.id, brief.name, brief.brand, json.dumps(brief.objectives),
            json.dumps(brief.target_audience), brief.budget, json.dumps(brief.timeline),
            json.dumps(brief.deliverables), json.dumps(brief.content_guidelines),
            json.dumps(brief.success_metrics), "planning", datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    async def _get_influencer_profile(self, influencer_id: str) -> Optional[Dict]:
        """Get influencer profile by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM influencers WHERE id = ?", (influencer_id,))
        profile = cursor.fetchone()
        conn.close()
        
        if profile:
            return {
                "id": profile[0], "name": profile[1], "username": profile[2],
                "email": profile[3], "platforms": json.loads(profile[4]),
                "follower_count": profile[5], "tier": profile[6], "niche": profile[7],
                "engagement_rate": profile[8], "average_view_rate": profile[9]
            }
        return None
    
    async def _get_campaign_brief(self, campaign_id: str) -> Optional[Dict]:
        """Get campaign brief by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM campaign_briefs WHERE id = ?", (campaign_id,))
        brief = cursor.fetchone()
        conn.close()
        
        if brief:
            return {
                "id": brief[0], "name": brief[1], "brand": brief[2],
                "objectives": json.loads(brief[3]), "budget": brief[5]
            }
        return None
    
    # Additional helper methods would continue here for comprehensive functionality...
    # For brevity, including key methods that would be implemented:
    
    async def _validate_campaign_objectives(self, objectives: List[str]) -> Dict:
        return {"valid": True, "issues": []}
    
    async def _analyze_budget_allocation(self, budget: float, deliverables: List[Dict]) -> Dict:
        return {"total_budget": budget, "recommended_allocation": {"influencers": 70, "content": 20, "management": 10}}
    
    async def _create_content_guidelines(self, audience: Dict, objectives: List[str]) -> Dict:
        return {"tone": "professional", "visual_style": "clean", "key_messages": objectives}
    
    async def _define_success_metrics(self, objectives: List[str], deliverables: List[Dict]) -> List[str]:
        return ["reach", "engagement", "conversions", "brand_awareness"]
    
    async def _recommend_influencers(self, brief: CampaignBrief) -> List[Dict]:
        return [{"influencer_id": "sample", "fit_score": 85, "estimated_cost": 500}]
    
    async def _create_campaign_strategy(self, brief: CampaignBrief, recommendations: List[Dict]) -> Dict:
        return {"strategy": "influencer_amplification", "timeline": "4 weeks", "key_phases": ["discovery", "negotiation", "execution"]}
    
    async def _estimate_campaign_performance(self, brief: CampaignBrief, recommendations: List[Dict]) -> Dict:
        return {"estimated_reach": 500000, "estimated_engagement": 25000, "confidence": 75}
    
    async def _create_timeline_breakdown(self, timeline: Dict) -> Dict:
        return {"total_duration": "4 weeks", "phases": {"planning": "1 week", "execution": "3 weeks"}}
    
    async def _assess_campaign_risks(self, brief: CampaignBrief) -> Dict:
        return {"risk_level": "medium", "key_risks": ["content_delays", "performance_variance"]}
    
    async def _create_compliance_checklist(self, brief: CampaignBrief) -> List[str]:
        return ["FTC disclosure", "Brand guidelines", "Content approval process"]