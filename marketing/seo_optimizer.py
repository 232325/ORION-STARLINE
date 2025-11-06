"""
SEO Optimizer
AI-ga qo'llab-quvvatlanadigan SEO optimization tizimi
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import sqlite3
import re
import logging

logger = logging.getLogger(__name__)

class SEOAuditType(Enum):
    TECHNICAL = "technical"
    CONTENT = "content"
    KEYWORDS = "keywords"
    BACKLINKS = "backlinks"
    PERFORMANCE = "performance"

@dataclass
class SEOIssue:
    id: str
    type: SEOAuditType
    severity: str  # "high", "medium", "low"
    title: str
    description: str
    recommendation: str
    impact_score: float

@dataclass
class KeywordData:
    keyword: str
    search_volume: int
    competition: str
    difficulty: float
    trend: str
    related_keywords: List[str]

@dataclass
class SEOScore:
    overall_score: float
    technical_score: float
    content_score: float
    keyword_score: float
    performance_score: float
    last_updated: datetime

class SEOOptimizer:
    """
    Comprehensive SEO Optimization Engine
    """
    
    def __init__(self, db_path: str = "marketing_seo.db"):
        self.db_path = db_path
        self.keyword_research_data = {}
        self.audit_cache = {}
        self._init_database()
        self.seo_tools = {
            "meta_analyzer": self._analyze_meta_tags,
            "content_analyzer": self._analyze_content_seo,
            "keyword_analyzer": self._analyze_keywords,
            "technical_analyzer": self._analyze_technical_seo
        }
    
    def _init_database(self):
        """SEO ma'lumotlar bazasini ishga tushirish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Keywords table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS keywords (
                id TEXT PRIMARY KEY,
                keyword TEXT NOT NULL,
                search_volume INTEGER,
                competition TEXT,
                difficulty REAL,
                trend TEXT,
                related_keywords TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # SEO audits table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS seo_audits (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                audit_type TEXT,
                score REAL,
                issues TEXT,
                recommendations TEXT,
                created_at TEXT,
                status TEXT
            )
        """)
        
        # Backlinks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backlinks (
                id TEXT PRIMARY KEY,
                source_url TEXT,
                target_url TEXT,
                anchor_text TEXT,
                domain_authority REAL,
                status TEXT,
                discovered_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def analyze_website(self, url: str) -> Dict:
        """Complete website SEO audit"""
        try:
            audit_id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Run all audit types
            technical_audit = await self._run_technical_audit(url)
            content_audit = await self._run_content_audit(url)
            keyword_audit = await self._run_keyword_audit(url)
            performance_audit = await self._run_performance_audit(url)
            
            # Calculate overall score
            scores = [
                technical_audit.get('score', 0),
                content_audit.get('score', 0),
                keyword_audit.get('score', 0),
                performance_audit.get('score', 0)
            ]
            overall_score = sum(scores) / len(scores)
            
            # Compile recommendations
            all_issues = []
            all_recommendations = []
            
            for audit_type, audit_data in [
                ('technical', technical_audit),
                ('content', content_audit),
                ('keywords', keyword_audit),
                ('performance', performance_audit)
            ]:
                if 'issues' in audit_data:
                    all_issues.extend(audit_data['issues'])
                if 'recommendations' in audit_data:
                    all_recommendations.extend(audit_data['recommendations'])
            
            # Save audit results
            await self._save_audit_results(
                audit_id, url, overall_score, all_issues, all_recommendations
            )
            
            return {
                "audit_id": audit_id,
                "url": url,
                "overall_score": round(overall_score, 2),
                "technical_score": technical_audit.get('score', 0),
                "content_score": content_audit.get('score', 0),
                "keyword_score": keyword_audit.get('score', 0),
                "performance_score": performance_audit.get('score', 0),
                "total_issues": len(all_issues),
                "critical_issues": len([i for i in all_issues if i.get('severity') == 'high']),
                "recommendations": all_recommendations,
                "priority_fixes": self._prioritize_issues(all_issues),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Website SEO analysis error: {e}")
            return {"error": str(e)}
    
    async def _run_technical_audit(self, url: str) -> Dict:
        """Technical SEO audit"""
        issues = []
        score = 100  # Start with perfect score
        
        # Page speed analysis
        speed_score = await self._analyze_page_speed(url)
        if speed_score < 80:
            issues.append(SEOIssue(
                id="speed_001",
                type=SEOAuditType.TECHNICAL,
                severity="high",
                title="Sahifa tezligi sekin",
                description="Sahifa yuklanish vaqti 3 soniyadan ko'p",
                recommendation="Image optimizatsiya, caching yoqish, CDN ishlatish",
                impact_score=90
            ))
            score -= 20
        
        # Mobile responsiveness
        mobile_score = await self._analyze_mobile_responsiveness(url)
        if mobile_score < 90:
            issues.append(SEOIssue(
                id="mobile_001",
                type=SEOAuditType.TECHNICAL,
                severity="high",
                title="Mobile qurilmalarga mos emas",
                description="Sahifa mobile qurilmalarda yaxshi ko'rinmaydi",
                recommendation="Responsive design qo'llash, mobile-first approach",
                impact_score=85
            ))
            score -= 15
        
        # SSL certificate
        ssl_score = await self._check_ssl_certificate(url)
        if not ssl_score:
            issues.append(SEOIssue(
                id="ssl_001",
                type=SEOAuditType.TECHNICAL,
                severity="high",
                title="SSL sertifikati yo'q",
                description="Sahifa HTTPS da emas, bu SEO ga salbiy ta'sir qiladi",
                recommendation="SSL sertifikati o'rnatish",
                impact_score=95
            ))
            score -= 25
        
        # XML Sitemap
        sitemap_score = await self._check_xml_sitemap(url)
        if not sitemap_score:
            issues.append(SEOIssue(
                id="sitemap_001",
                type=SEOAuditType.TECHNICAL,
                severity="medium",
                title="XML Sitemap yo'q",
                description="Search enginelar uchun XML sitemap yaratilmagan",
                recommendation="XML sitemap yaratish va Search Console ga qo'shish",
                impact_score=70
            ))
            score -= 10
        
        # Robots.txt
        robots_score = await self._check_robots_txt(url)
        if not robots_score:
            issues.append(SEOIssue(
                id="robots_001",
                type=SEOAuditType.TECHNICAL,
                severity="low",
                title="Robots.txt fayli yo'q",
                description="Robots.txt fayli search engine crawling ni boshqarish uchun kerak",
                recommendation="Robots.txt fayli yaratish",
                impact_score=50
            ))
            score -= 5
        
        return {
            "score": max(0, score),
            "issues": issues,
            "recommendations": [issue.recommendation for issue in issues],
            "technical_details": {
                "page_speed_score": speed_score,
                "mobile_score": mobile_score,
                "ssl_enabled": ssl_score,
                "sitemap_exists": sitemap_score,
                "robots_txt_exists": robots_score
            }
        }
    
    async def _run_content_audit(self, url: str) -> Dict:
        """Content SEO audit"""
        issues = []
        score = 100
        
        # Get page content
        content = await self._fetch_page_content(url)
        if not content:
            return {"score": 0, "error": "Could not fetch page content"}
        
        # Title tag analysis
        title_score = await self._analyze_title_tag(content)
        if title_score < 80:
            issues.append(SEOIssue(
                id="title_001",
                type=SEOAuditType.CONTENT,
                severity="high",
                title="Title tag optimal emas",
                description="Title tag juda qisqa yoki uzun, yoki keyword yo'q",
                recommendation="Title tagni keyword bilan 50-60 belgida yozish",
                impact_score=80
            ))
            score -= 20
        
        # Meta description analysis
        meta_score = await self._analyze_meta_description(content)
        if meta_score < 70:
            issues.append(SEOIssue(
                id="meta_001",
                type=SEOAuditType.CONTENT,
                severity="medium",
                title="Meta description yo'q yoki optimal emas",
                description="Meta description 150-160 belgi bo'lishi kerak",
                recommendation="Captivating meta description yaratish",
                impact_score=75
            ))
            score -= 15
        
        # Header structure analysis
        header_score = await self._analyze_header_structure(content)
        if header_score < 60:
            issues.append(SEOIssue(
                id="header_001",
                type=SEOAuditType.CONTENT,
                severity="medium",
                title="Header strukturasi yo'q",
                description="H1, H2, H3 taglari to'g'ri ishlatilmagan",
                recommendation="Header strukturani to'g'ri qurish",
                impact_score=70
            ))
            score -= 15
        
        # Content length and quality
        content_score = await self._analyze_content_quality(content)
        if content_score < 70:
            issues.append(SEOIssue(
                id="content_001",
                type=SEOAuditType.CONTENT,
                severity="medium",
                title="Content sifati yoki uzunligi yetarli emas",
                description="Content juda qisqa yoki sifati past",
                recommendation="Content ni 1500+ so'zga yetkazish va sifati oshirish",
                impact_score=65
            ))
            score -= 15
        
        # Internal linking
        internal_score = await self._analyze_internal_linking(content, url)
        if internal_score < 50:
            issues.append(SEOIssue(
                id="internal_001",
                type=SEOAuditType.CONTENT,
                severity="low",
                title="Internal linking yetarli emas",
                description="Sahifada internal linklar kam",
                recommendation="Related sahifalar bilan internal linking qilish",
                impact_score=60
            ))
            score -= 10
        
        return {
            "score": max(0, score),
            "issues": issues,
            "recommendations": [issue.recommendation for issue in issues],
            "content_metrics": {
                "title_score": title_score,
                "meta_score": meta_score,
                "header_score": header_score,
                "content_score": content_score,
                "internal_linking_score": internal_score
            }
        }
    
    async def _run_keyword_audit(self, url: str) -> Dict:
        """Keyword research and optimization audit"""
        issues = []
        score = 100
        
        # Extract current keywords
        keywords = await self._extract_keywords_from_content(url)
        
        # Analyze keyword density
        for keyword, density in keywords.items():
            if density < 1:  # Very low density
                issues.append(SEOIssue(
                    id=f"kw_low_{keyword}",
                    type=SEOAuditType.KEYWORDS,
                    severity="medium",
                    title=f"Keyword density juda past: {keyword}",
                    description=f"{keyword} keyword density juda past (1% dan kam)",
                    recommendation=f"{keyword} keyword ni content da ko'proq ishlatish",
                    impact_score=60
                ))
                score -= 10
            elif density > 3:  # Very high density (keyword stuffing)
                issues.append(SEOIssue(
                    id=f"kw_high_{keyword}",
                    type=SEOAuditType.KEYWORDS,
                    severity="high",
                    title=f"Keyword density juda yuqori: {keyword}",
                    description=f"{keyword} keyword density juda yuqori (3% dan ko'p)",
                    recommendation=f"{keyword} keyword ni kamroq ishlatish",
                    impact_score=85
                ))
                score -= 15
        
        # Check for long-tail keywords
        long_tail_score = await self._analyze_long_tail_keywords(keywords)
        if long_tail_score < 50:
            issues.append(SEOIssue(
                id="longtail_001",
                type=SEOAuditType.KEYWORDS,
                severity="medium",
                title="Long-tail keywordlar yo'q",
                description="Specific va targeted keywordlar yetarli emas",
                recommendation="Long-tail keyword research qilish va content ga qo'shish",
                impact_score=70
            ))
            score -= 15
        
        # Keyword competition analysis
        competition_score = await self._analyze_keyword_competition(keywords)
        if competition_score < 60:
            issues.append(SEOIssue(
                id="competition_001",
                type=SEOAuditType.KEYWORDS,
                severity="medium",
                title="Yuqori raqobatdagi keywordlar",
                description="Target qilingan keywordlar juda competitive",
                recommendation="Lower competition keywordlarga focus qilish",
                impact_score=75
            ))
            score -= 10
        
        return {
            "score": max(0, score),
            "issues": issues,
            "recommendations": [issue.recommendation for issue in issues],
            "keyword_metrics": {
                "total_keywords": len(keywords),
                "avg_density": sum(keywords.values()) / len(keywords) if keywords else 0,
                "long_tail_ratio": long_tail_score / 100,
                "competition_level": "medium"
            }
        }
    
    async def _run_performance_audit(self, url: str) -> Dict:
        """Performance SEO audit"""
        issues = []
        score = 100
        
        # Core Web Vitals simulation
        core_web_vitals = await self._analyze_core_web_vitals(url)
        
        if core_web_vitals.get('lcp', 0) > 2.5:  # Largest Contentful Paint
            issues.append(SEOIssue(
                id="lcp_001",
                type=SEOAuditType.PERFORMANCE,
                severity="high",
                title="LCP ko'rsatkichi yuqori",
                description="Largest Contentful Paint 2.5 soniyadan ko'p",
                recommendation="Image optimizatsiya, lazy loading yoqish",
                impact_score=90
            ))
            score -= 20
        
        if core_web_vitals.get('fid', 0) > 100:  # First Input Delay
            issues.append(SEOIssue(
                id="fid_001",
                type=SEOAuditType.PERFORMANCE,
                severity="high",
                title="FID ko'rsatkichi yuqori",
                description="First Input Delay 100ms dan ko'p",
                recommendation="JavaScript optimizatsiya, code splitting",
                impact_score=85
            ))
            score -= 15
        
        if core_web_vitals.get('cls', 0) > 0.1:  # Cumulative Layout Shift
            issues.append(SEOIssue(
                id="cls_001",
                type=SEOAuditType.PERFORMANCE,
                severity="medium",
                title="CLS ko'rsatkichi yuqori",
                description="Cumulative Layout Shift 0.1 dan ko'p",
                recommendation="Image va ads uchun reserved space",
                impact_score=75
            ))
            score -= 10
        
        return {
            "score": max(0, score),
            "issues": issues,
            "recommendations": [issue.recommendation for issue in issues],
            "core_web_vitals": core_web_vitals
        }
    
    async def keyword_research(
        self,
        seed_keyword: str,
        language: str = "uz",
        location: str = "Uzbekistan"
    ) -> List[KeywordData]:
        """Keyword research va analysis"""
        try:
            # Simulate keyword research
            related_keywords = await self._generate_related_keywords(seed_keyword)
            
            keyword_results = []
            for keyword in related_keywords:
                keyword_data = KeywordData(
                    keyword=keyword,
                    search_volume=await self._get_search_volume(keyword, language),
                    competition=await self._get_competition_level(keyword),
                    difficulty=await self._calculate_keyword_difficulty(keyword),
                    trend=await self._analyze_keyword_trend(keyword),
                    related_keywords=await self._get_related_keywords(keyword)
                )
                keyword_results.append(keyword_data)
                
                # Save to database
                await self._save_keyword_data(keyword_data)
            
            return keyword_results
            
        except Exception as e:
            logger.error(f"Keyword research error: {e}")
            return []
    
    async def optimize_content_for_keywords(
        self,
        content: str,
        target_keywords: List[str]
    ) -> Dict:
        """Content optimization for target keywords"""
        try:
            optimization_score = 0
            recommendations = []
            
            # Title optimization
            title_optimized = await self._optimize_title(content, target_keywords)
            title_score = title_optimized.get('score', 0)
            optimization_score += title_score * 0.3
            if title_score < 80:
                recommendations.append("Title tagni target keywordlar bilan optimizatsiya qilish")
            
            # Meta description optimization
            meta_optimized = await self._optimize_meta_description(content, target_keywords)
            meta_score = meta_optimized.get('score', 0)
            optimization_score += meta_score * 0.2
            if meta_score < 70:
                recommendations.append("Meta description ni target keywordlar bilan qayta yozish")
            
            # Content optimization
            content_optimized = await self._optimize_content_keyword_density(content, target_keywords)
            content_score = content_optimized.get('score', 0)
            optimization_score += content_score * 0.4
            if content_score < 70:
                recommendations.append("Content dagi keyword density ni optimizatsiya qilish")
            
            # Header optimization
            header_optimized = await self._optimize_headers(content, target_keywords)
            header_score = header_optimized.get('score', 0)
            optimization_score += header_score * 0.1
            if header_score < 60:
                recommendations.append("Header taglariga target keywordlarni qo'shish")
            
            # Generate optimized content
            optimized_content = await self._generate_optimized_content(content, target_keywords)
            
            return {
                "optimization_score": round(optimization_score, 2),
                "before_optimization": {
                    "title_score": title_score,
                    "meta_score": meta_score,
                    "content_score": content_score,
                    "header_score": header_score
                },
                "recommendations": recommendations,
                "optimized_content": optimized_content,
                "keyword_density_analysis": content_optimized.get('density_analysis', {}),
                "optimization_details": {
                    "target_keywords": target_keywords,
                    "recommended_keyword_density": "1-3%",
                    "title_length": len(title_optimized.get('optimized_title', '')),
                    "meta_length": len(meta_optimized.get('optimized_meta', ''))
                }
            }
            
        except Exception as e:
            logger.error(f"Content optimization error: {e}")
            return {"error": str(e)}
    
    async def create_sitemap(self, urls: List[str], output_path: str = "sitemap.xml") -> Dict:
        """XML sitemap yaratish"""
        try:
            sitemap_xml = await self._generate_xml_sitemap(urls)
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(sitemap_xml)
            
            # Analyze sitemap
            sitemap_analysis = await self._analyze_sitemap(sitemap_xml)
            
            return {
                "status": "created",
                "sitemap_path": output_path,
                "urls_count": len(urls),
                "analysis": sitemap_analysis,
                "recommendations": [
                    "Sitemap ni Google Search Console ga qo'shing",
                    "Robots.txt ga sitemap reference qo'shing",
                    "URL structure ni consistent qilib saqlang"
                ]
            }
            
        except Exception as e:
            logger.error(f"Sitemap creation error: {e}")
            return {"error": str(e)}
    
    async def get_seo_recommendations(self, audit_results: Dict) -> List[Dict]:
        """Personalized SEO recommendations"""
        recommendations = []
        
        overall_score = audit_results.get('overall_score', 0)
        
        if overall_score < 30:
            recommendations.append({
                "priority": "critical",
                "category": "technical",
                "title": "Asosiy technical SEO muammolari",
                "description": "Website technical SEO da critical issues bor",
                "actions": [
                    "SSL sertifikati o'rnatish",
                    "Page speed optimizatsiya",
                    "Mobile responsiveness ta'minlash"
                ],
                "timeline": "1-2 hafta",
                "impact": "high"
            })
        elif overall_score < 70:
            recommendations.append({
                "priority": "high",
                "category": "content",
                "title": "Content optimizatsiyasi kerak",
                "description": "Content SEO optimizatsiya kerak",
                "actions": [
                    "Keyword research qilish",
                    "Content sifati oshirish",
                    "Meta description yaratish"
                ],
                "timeline": "2-4 hafta",
                "impact": "medium"
            })
        
        # Performance-based recommendations
        if audit_results.get('technical_score', 0) < 80:
            recommendations.append({
                "priority": "high",
                "category": "technical",
                "title": "Technical SEO improvement",
                "description": "Technical aspects needs improvement",
                "actions": [
                    "Core Web Vitals optimization",
                    "Image compression va lazy loading",
                    "Code minification"
                ],
                "timeline": "1-3 hafta",
                "impact": "high"
            })
        
        if audit_results.get('content_score', 0) < 75:
            recommendations.append({
                "priority": "medium",
                "category": "content",
                "title": "Content strategy optimization",
                "description": "Content marketing strategy needs enhancement",
                "actions": [
                    "Long-tail keyword targeting",
                    "Content gap analysis",
                    "Internal linking strategy"
                ],
                "timeline": "3-6 hafta",
                "impact": "medium"
            })
        
        return recommendations
    
    async def track_keyword_rankings(
        self,
        keywords: List[str],
        domains: List[str],
        location: str = "Uzbekistan"
    ) -> Dict:
        """Keyword ranking tracking"""
        try:
            ranking_data = {}
            
            for domain in domains:
                domain_rankings = {}
                
                for keyword in keywords:
                    # Simulate ranking data
                    position = await self._get_keyword_position(keyword, domain, location)
                    
                    domain_rankings[keyword] = {
                        "position": position,
                        "url": f"https://{domain}/page-for-{keyword.replace(' ', '-')}",
                        "search_volume": await self._get_search_volume(keyword),
                        "difficulty": await self._calculate_keyword_difficulty(keyword),
                        "previous_position": position + 2 if position <= 10 else position,  # Previous ranking
                        "change": 2 if position <= 10 else 0,  # Position change
                        "tracked_date": datetime.now().isoformat()
                    }
                
                ranking_data[domain] = domain_rankings
            
            # Calculate average rankings
            all_positions = []
            for domain_data in ranking_data.values():
                for keyword_data in domain_data.values():
                    if keyword_data["position"] <= 100:
                        all_positions.append(keyword_data["position"])
            
            avg_position = sum(all_positions) / len(all_positions) if all_positions else 0
            top_10_count = len([p for p in all_positions if p <= 10])
            
            return {
                "tracking_date": datetime.now().isoformat(),
                "domains_analyzed": len(domains),
                "keywords_tracked": len(keywords),
                "rankings": ranking_data,
                "summary": {
                    "avg_position": round(avg_position, 2),
                    "top_10_keywords": top_10_count,
                    "improving_keywords": len([d for domain_data in ranking_data.values() for d in domain_data.values() if d["change"] > 0]),
                    "declining_keywords": len([d for domain_data in ranking_data.values() for d in domain_data.values() if d["change"] < 0])
                },
                "recommendations": [
                    "Top 10 keywordlar uchun position qo'llab turish strategiyasi",
                    "Long-tail keywordlar bilan niche targeting",
                    "Content refresh va update qilish"
                ]
            }
            
        except Exception as e:
            logger.error(f"Keyword ranking tracking error: {e}")
            return {"error": str(e)}
    
    # Helper methods
    async def _analyze_page_speed(self, url: str) -> float:
        """Page speed analysis"""
        # Simulate page speed score
        return 75.5
    
    async def _analyze_mobile_responsiveness(self, url: str) -> float:
        """Mobile responsiveness analysis"""
        return 82.3
    
    async def _check_ssl_certificate(self, url: str) -> bool:
        """SSL certificate check"""
        return url.startswith('https')
    
    async def _check_xml_sitemap(self, url: str) -> bool:
        """XML sitemap check"""
        # Simulate sitemap check
        return True
    
    async def _check_robots_txt(self, url: str) -> bool:
        """Robots.txt check"""
        # Simulate robots.txt check
        return True
    
    async def _fetch_page_content(self, url: str) -> str:
        """Fetch page content"""
        # Simulate content fetching
        return f"Sample content from {url}"
    
    async def _analyze_title_tag(self, content: str) -> float:
        """Title tag analysis"""
        return 78.5
    
    async def _analyze_meta_description(self, content: str) -> float:
        """Meta description analysis"""
        return 65.2
    
    async def _analyze_header_structure(self, content: str) -> float:
        """Header structure analysis"""
        return 58.9
    
    async def _analyze_content_quality(self, content: str) -> float:
        """Content quality analysis"""
        return 72.1
    
    async def _analyze_internal_linking(self, content: str, url: str) -> float:
        """Internal linking analysis"""
        return 45.3
    
    async def _extract_keywords_from_content(self, url: str) -> Dict[str, float]:
        """Extract keywords from content"""
        return {"orion starline": 2.5, "trading": 1.8, "ai": 1.2}
    
    async def _analyze_long_tail_keywords(self, keywords: Dict) -> float:
        """Long-tail keyword analysis"""
        return 35.7
    
    async def _analyze_keyword_competition(self, keywords: Dict) -> float:
        """Keyword competition analysis"""
        return 68.4
    
    async def _analyze_core_web_vitals(self, url: str) -> Dict:
        """Core Web Vitals analysis"""
        return {
            "lcp": 2.1,
            "fid": 85,
            "cls": 0.08
        }
    
    async def _generate_related_keywords(self, seed_keyword: str) -> List[str]:
        """Generate related keywords"""
        base = seed_keyword.lower()
        return [
            f"{base} qo'llanma",
            f"{base} strategiya",
            f"{base} texnologiya",
            f"{base} bo'yicha maslahat",
            f"{base} xususiyatlari"
        ]
    
    async def _get_search_volume(self, keyword: str, language: str = "uz") -> int:
        """Get search volume"""
        # Simulate search volume
        volume_map = {
            "orion starline": 1200,
            "trading": 5800,
            "ai": 8900,
            "forex": 3200,
            "savdo": 2100
        }
        return volume_map.get(keyword.lower(), 500)
    
    async def _get_competition_level(self, keyword: str) -> str:
        """Get competition level"""
        # Simulate competition analysis
        if keyword.lower() in ["ai", "trading"]:
            return "yuqori"
        elif keyword.lower() in ["forex", "savdo"]:
            return "o'rta"
        else:
            return "past"
    
    async def _calculate_keyword_difficulty(self, keyword: str) -> float:
        """Calculate keyword difficulty"""
        # Simulate keyword difficulty calculation
        return 45.7
    
    async def _analyze_keyword_trend(self, keyword: str) -> str:
        """Analyze keyword trend"""
        # Simulate trend analysis
        trends = {
            "ai": "yuqori",
            "trading": "o'zgarmas",
            "forex": "past"
        }
        return trends.get(keyword.lower(), "o'rta")
    
    async def _get_related_keywords(self, keyword: str) -> List[str]:
        """Get related keywords"""
        return [
            f"{keyword} haqida",
            f"{keyword} texnologiyasi",
            f"{keyword} qo'llanma"
        ]
    
    async def _save_keyword_data(self, keyword_data: KeywordData):
        """Save keyword data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO keywords 
            (id, keyword, search_volume, competition, difficulty, trend, related_keywords, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"kw_{keyword_data.keyword.replace(' ', '_')}",
            keyword_data.keyword,
            keyword_data.search_volume,
            keyword_data.competition,
            keyword_data.difficulty,
            keyword_data.trend,
            json.dumps(keyword_data.related_keywords),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    async def _optimize_title(self, content: str, keywords: List[str]) -> Dict:
        """Optimize title for keywords"""
        return {
            "score": 75.0,
            "optimized_title": f"{keywords[0]} - Qadamma Qadamma Academy",
            "recommendations": ["Title ni 60 belgidan kam saqlash"]
        }
    
    async def _optimize_meta_description(self, content: str, keywords: List[str]) -> Dict:
        """Optimize meta description"""
        return {
            "score": 70.0,
            "optimized_meta": f"{keywords[0]} bo'yicha expert maslahatlar va qo'llanmalar",
            "recommendations": ["Meta description 160 belgidan kam bo'lishi kerak"]
        }
    
    async def _optimize_content_keyword_density(self, content: str, keywords: List[str]) -> Dict:
        """Optimize content keyword density"""
        density_analysis = {}
        for keyword in keywords:
            density = (content.lower().count(keyword.lower()) / len(content.split())) * 100
            density_analysis[keyword] = {
                "current_density": density,
                "recommended": "1-3%",
                "status": "optimal" if 1 <= density <= 3 else "needs_adjustment"
            }
        
        return {
            "score": 72.5,
            "density_analysis": density_analysis
        }
    
    async def _optimize_headers(self, content: str, keywords: List[str]) -> Dict:
        """Optimize headers"""
        return {
            "score": 68.0,
            "recommendations": ["H1 tagiga target keyword qo'shish"]
        }
    
    async def _generate_optimized_content(self, content: str, keywords: List[str]) -> str:
        """Generate optimized version"""
        # Simple optimization logic
        optimized = content
        for keyword in keywords:
            if keyword not in optimized:
                optimized = f"{keyword.upper()}: {optimized}"
        
        return optimized
    
    async def _generate_xml_sitemap(self, urls: List[str]) -> str:
        """Generate XML sitemap"""
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        urlset_open = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        urlset_close = '</urlset>'
        
        urls_xml = ""
        for url in urls:
            urls_xml += f"""
    <url>
        <loc>{url}</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>"""
        
        return xml_declaration + urlset_open + urls_xml + "\n" + urlset_close
    
    async def _analyze_sitemap(self, sitemap_xml: str) -> Dict:
        """Analyze sitemap"""
        urls_count = sitemap_xml.count('<url>')
        return {
            "total_urls": urls_count,
            "valid_xml": sitemap_xml.startswith('<?xml'),
            "has_namespace": 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"' in sitemap_xml
        }
    
    async def _get_keyword_position(self, keyword: str, domain: str, location: str) -> int:
        """Get keyword position"""
        # Simulate position tracking
        import random
        return random.randint(1, 50)
    
    async def _save_audit_results(self, audit_id: str, url: str, score: float, issues: List, recommendations: List):
        """Save audit results to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO seo_audits 
            (id, url, audit_type, score, issues, recommendations, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            audit_id, url, "comprehensive", score,
            json.dumps([issue.__dict__ for issue in issues]) if hasattr(issues[0], '__dict__') else json.dumps(issues),
            json.dumps(recommendations),
            datetime.now().isoformat(),
            "completed"
        ))
        
        conn.commit()
        conn.close()
    
    def _prioritize_issues(self, issues: List) -> List[Dict]:
        """Prioritize SEO issues"""
        prioritized = []
        for issue in issues:
            prioritized.append({
                "title": issue.title,
                "severity": issue.severity,
                "impact_score": issue.impact_score,
                "category": issue.type.value
            })
        
        # Sort by impact score descending
        prioritized.sort(key=lambda x: x['impact_score'], reverse=True)
        return prioritized[:10]  # Top 10 issues