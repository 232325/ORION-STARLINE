"""
Content Marketing Engine
AI-ga qo'llab-quvvatlanadigan content yaratish va boshqarish tizimi
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

class ContentType(Enum):
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    VIDEO_SCRIPT = "video_script"
    INFOGRAPHIC = "infographic"
    WHITE_PAPER = "white_paper"
    CASE_STUDY = "case_study"

class ContentStatus(Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"

@dataclass
class ContentMetrics:
    views: int = 0
    shares: int = 0
    comments: int = 0
    engagement_rate: float = 0.0
    conversion_rate: float = 0.0
    seo_score: float = 0.0

@dataclass
class ContentItem:
    id: str
    title: str
    content_type: ContentType
    status: ContentStatus
    target_keywords: List[str]
    target_audience: str
    content_body: str
    created_at: datetime
    published_at: Optional[datetime] = None
    author: str = "AI Engine"
    tags: List[str] = None
    metrics: ContentMetrics = None

class ContentEngine:
    """
    AI-ga qo'llab-quvvatlanadigan Content Marketing Engine
    """
    
    def __init__(self, db_path: str = "marketing_content.db"):
        self.db_path = db_path
        self.content_queue = []
        self.published_content = []
        self.content_templates = self._load_content_templates()
        self.ai_models = {}
        self._init_database()
    
    def _init_database(self):
        """Ma'lumotlar bazasini ishga tushirish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_items (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content_type TEXT NOT NULL,
                status TEXT NOT NULL,
                target_keywords TEXT,
                target_audience TEXT,
                content_body TEXT,
                created_at TEXT,
                published_at TEXT,
                author TEXT,
                tags TEXT,
                metrics TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_performance (
                content_id TEXT,
                date TEXT,
                views INTEGER,
                shares INTEGER,
                comments INTEGER,
                engagement_rate REAL,
                conversion_rate REAL,
                seo_score REAL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_content_templates(self) -> Dict:
        """Content shablonlarini yuklash"""
        return {
            "blog_post": {
                "structure": ["kirish", "asosiy_mazmun", "xulosa"],
                "recommended_length": "1500-2500 so'z",
                "seo_factors": ["title", "meta_description", "headers", "keywords"]
            },
            "social_media": {
                "platforms": ["twitter", "linkedin", "facebook", "instagram"],
                "character_limits": {"twitter": 280, "linkedin": 1300, "facebook": 63206},
                "hashtags": {"recommended": 3, "maximum": 10}
            },
            "email": {
                "subject_lines": {"max_length": 50, "personalization": True},
                "body_structure": ["greeting", "value_prop", "call_to_action"],
                "a_b_testing": True
            }
        }
    
    async def generate_content(
        self,
        topic: str,
        content_type: ContentType,
        target_audience: str,
        keywords: List[str],
        tone: str = "professional",
        length: str = "medium"
    ) -> ContentItem:
        """
        AI yordamida content yaratish
        """
        try:
            content_id = f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # AI content generation logic (simulated)
            content_body = await self._generate_ai_content(
                topic, content_type, target_audience, keywords, tone, length
            )
            
            content_item = ContentItem(
                id=content_id,
                title=await self._generate_title(topic, content_type),
                content_type=content_type,
                status=ContentStatus.DRAFT,
                target_keywords=keywords,
                target_audience=target_audience,
                content_body=content_body,
                created_at=datetime.now(),
                author="AI Content Engine",
                tags=self._extract_tags(content_body),
                metrics=ContentMetrics()
            )
            
            # Database ga saqlash
            await self._save_content(content_item)
            
            logger.info(f"Content generated: {content_id}")
            return content_item
            
        except Exception as e:
            logger.error(f"Content generation error: {e}")
            raise
    
    async def _generate_ai_content(
        self,
        topic: str,
        content_type: ContentType,
        target_audience: str,
        keywords: List[str],
        tone: str,
        length: str
    ) -> str:
        """AI content generation logic"""
        # Bu yerda real AI model integration qilinadi
        # Hozircha simulyatsiya qilingan
        
        templates = {
            ContentType.BLOG_POST: f"""
# {topic} bo'yicha batafsil qo'llanma

## Kirish
{topic} bugungi kunda juda muhim mavzu. Bu maqolada biz {target_audience} uchun 
barcha kerakli ma'lumotlarni taqdim etamiz.

## Asosiy ma'lumotlar
{len(keywords)} ta asosiy kalit so'z: {', '.join(keywords)}

## Batafsil tahlil
[Content generation logic here]

## Xulosa va tavsiyalar
Tavsiyalar va keyingi qadamlar.

## Call to Action
Assalomu alaykum! Batafsil ma'lumot uchun biz bilan bog'laning.
            """,
            
            ContentType.SOCIAL_MEDIA: f"""
🚀 {topic} haqida yangiliklar!

💡 {target_audience} uchun muhim maslahatlar:
• {keywords[0]} bo'yicha expert maslahatlar
• {keywords[1]} strategiyalar
• Tezkor yechimlar

#orionstarline #trading #{keywords[0]}
            """,
            
            ContentType.EMAIL: f"""
Assalomu alaykum!

Sizga {topic} bo'yicha qimmatli ma'lumotlar tayyorladik.

📧 Bo'limlar:
• {keywords[0]} - batafsil ko'rsatma
• {keywords[1]} - amaliy maslahatlar
• Maxsus takliflar

Eng so'ngi yangiliklar uchun obuna bo'ling!
            """
        }
        
        return templates.get(content_type, f"Generated content for {topic}")
    
    async def _generate_title(self, topic: str, content_type: ContentType) -> str:
        """Title generation"""
        templates = {
            ContentType.BLOG_POST: f"{topic} bo'yicha batafsil qo'llanma (2025)",
            ContentType.SOCIAL_MEDIA: f"🚀 {topic} - yangi imkoniyatlar",
            ContentType.EMAIL: f"{topic} - muhim yangiliklar va takliflar"
        }
        return templates.get(content_type, f"{topic} - Generated Title")
    
    def _extract_tags(self, content: str) -> List[str]:
        """Content dan taglarni extraction"""
        # Basit tag extraction logic
        words = content.lower().split()
        tags = []
        for word in words:
            if len(word) > 6 and word not in ['qo\'llanma', 'ma\'lumot', 'maslahat']:
                tags.append(word)
        return list(set(tags))[:10]  # Max 10 tags
    
    async def _save_content(self, content: ContentItem):
        """Content ni database ga saqlash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO content_items 
            (id, title, content_type, status, target_keywords, target_audience, 
             content_body, created_at, published_at, author, tags, metrics)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            content.id, content.title, content.content_type.value,
            content.status.value, json.dumps(content.target_keywords),
            content.target_audience, content.content_body, 
            content.created_at.isoformat(), 
            content.published_at.isoformat() if content.published_at else None,
            content.author, json.dumps(content.tags),
            json.dumps(content.metrics.__dict__)
        ))
        
        conn.commit()
        conn.close()
    
    async def get_content_performance(self, content_id: str) -> Dict:
        """Content performance analizi"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM content_performance WHERE content_id = ?
            ORDER BY date DESC LIMIT 30
        """, (content_id,))
        
        performance_data = cursor.fetchall()
        conn.close()
        
        if not performance_data:
            return {"error": "Performance data not found"}
        
        # Analytics logic
        total_views = sum(row[2] for row in performance_data)
        avg_engagement = sum(row[5] for row in performance_data) / len(performance_data)
        conversion_trend = "increasing" if performance_data[0][6] > performance_data[-1][6] else "decreasing"
        
        return {
            "content_id": content_id,
            "total_views_30_days": total_views,
            "avg_engagement_rate": round(avg_engagement, 2),
            "conversion_trend": conversion_trend,
            "performance_score": min(100, total_views * 0.1 + avg_engagement * 10)
        }
    
    async def optimize_content(
        self,
        content_id: str,
        optimization_type: str = "seo"
    ) -> Dict:
        """Content optimization"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM content_items WHERE id = ?", (content_id,))
            content_data = cursor.fetchone()
            conn.close()
            
            if not content_data:
                return {"error": "Content not found"}
            
            # Optimization logic based on type
            if optimization_type == "seo":
                seo_score = await self._calculate_seo_score(content_data)
                recommendations = await self._get_seo_recommendations(content_data)
                return {
                    "seo_score": seo_score,
                    "recommendations": recommendations,
                    "optimized_title": f"{content_data[1]} - SEO Optimized"
                }
            
            elif optimization_type == "engagement":
                engagement_score = await self._calculate_engagement_score(content_data)
                return {
                    "engagement_score": engagement_score,
                    "improvements": ["Add interactive elements", "Include visuals", "Add call-to-action"]
                }
            
            return {"status": "optimization_complete", "content_id": content_id}
            
        except Exception as e:
            logger.error(f"Content optimization error: {e}")
            return {"error": str(e)}
    
    async def _calculate_seo_score(self, content_data) -> float:
        """SEO score calculation"""
        content_body = content_data[6]  # content_body column
        keywords = json.loads(content_data[4])  # target_keywords column
        
        score = 0
        
        # Keyword density check (5-15%)
        for keyword in keywords:
            keyword_count = content_body.lower().count(keyword.lower())
            density = (keyword_count / len(content_body.split())) * 100
            if 5 <= density <= 15:
                score += 20
        
        # Meta description check
        if len(content_body[:160]) > 50:
            score += 20
        
        # Headers usage
        header_count = content_body.count('#')
        if header_count >= 3:
            score += 20
        
        # Content length
        word_count = len(content_body.split())
        if 1500 <= word_count <= 2500:
            score += 20
        
        # Internal/external links (placeholder)
        score += 20  # Assume good link structure
        
        return min(100, score)
    
    async def _get_seo_recommendations(self, content_data) -> List[str]:
        """SEO improvement recommendations"""
        recommendations = []
        
        # Analyze content for recommendations
        content_body = content_data[6]
        word_count = len(content_body.split())
        
        if word_count < 1500:
            recommendations.append("Content length oshirish tavsiya etiladi (min 1500 so'z)")
        
        if content_body.count('#') < 3:
            recommendations.append("Header strukturani yaxshilash kerak")
        
        if not any(word in content_body.lower() for word in ['maqola', 'qalamp', 'tag']):
            recommendations.append("Internal linking qo'shish zarur")
        
        return recommendations
    
    async def _calculate_engagement_score(self, content_data) -> float:
        """Engagement score calculation"""
        # Simple engagement scoring
        content_body = content_data[6]
        
        score = 0
        
        # Interactive elements
        if '?' in content_body:
            score += 20
        
        # Call to action
        if any(cta in content_body.lower() for cta in ['bog\'laning', 'ro\'yxatdan o\'ting', 'batafsil']):
            score += 30
        
        # Visual elements indicators
        if any(visual in content_body.lower() for visual in ['rasm', 'video', 'infografik']):
            score += 20
        
        # Social sharing prompts
        if 'ulashing' in content_body.lower():
            score += 15
        
        # Readability
        if len(content_body.split()) < 200:
            score += 15
        
        return min(100, score)
    
    async def schedule_content(
        self,
        content_id: str,
        publish_date: datetime,
        channels: List[str]
    ) -> Dict:
        """Content publishing schedule"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update content status to approved and set publish date
            cursor.execute("""
                UPDATE content_items 
                SET status = ?, published_at = ?
                WHERE id = ?
            """, (ContentStatus.APPROVED.value, publish_date.isoformat(), content_id))
            
            conn.commit()
            conn.close()
            
            return {
                "status": "scheduled",
                "content_id": content_id,
                "publish_date": publish_date.isoformat(),
                "channels": channels,
                "estimated_reach": len(channels) * 1000  # Estimated reach calculation
            }
            
        except Exception as e:
            logger.error(f"Content scheduling error: {e}")
            return {"error": str(e)}
    
    async def get_content_calendar(self, days_ahead: int = 30) -> List[Dict]:
        """Content calendar ko'rinishi"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get scheduled content
        cursor.execute("""
            SELECT * FROM content_items 
            WHERE status = ? AND published_at IS NOT NULL
            ORDER BY published_at
        """, (ContentStatus.APPROVED.value,))
        
        scheduled_content = cursor.fetchall()
        conn.close()
        
        calendar = []
        for content in scheduled_content:
            calendar.append({
                "id": content[0],
                "title": content[1],
                "type": content[2],
                "publish_date": content[8],
                "channels": ["website", "social_media"],  # Default channels
                "status": content[3]
            })
        
        return calendar
    
    async def generate_content_report(self) -> Dict:
        """Content marketing hisoboti"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all content
        cursor.execute("SELECT * FROM content_items")
        all_content = cursor.fetchall()
        
        # Calculate metrics
        total_content = len(all_content)
        published_content = len([c for c in all_content if c[3] == ContentStatus.PUBLISHED.value])
        
        conn.close()
        
        return {
            "report_date": datetime.now().isoformat(),
            "total_content_created": total_content,
            "published_content": published_content,
            "content_by_type": {},
            "avg_seo_score": 75.5,  # Placeholder
            "top_performing_content": [],
            "recommendations": [
                "Video contentni ko'paytirish tavsiya etiladi",
                "Social media contentni 20% ga ko'paytirish",
                "Email marketing integratsiyasini kuchaytirish"
            ]
        }
    
    def get_content_templates(self) -> Dict:
        """Available content templates"""
        return self.content_templates
    
    async def bulk_content_generation(
        self,
        topics: List[str],
        content_type: ContentType,
        target_audience: str,
        keywords: List[str]
    ) -> List[ContentItem]:
        """Multiple content generation"""
        generated_content = []
        
        for topic in topics:
            try:
                content = await self.generate_content(
                    topic=topic,
                    content_type=content_type,
                    target_audience=target_audience,
                    keywords=keywords
                )
                generated_content.append(content)
                
                # Small delay to avoid overwhelming
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Bulk content generation error for topic {topic}: {e}")
                continue
        
        return generated_content
    
    async def close(self):
        """Cleanup resources"""
        # Close database connections, cleanup temp files, etc.
        logger.info("Content Engine cleanup completed")