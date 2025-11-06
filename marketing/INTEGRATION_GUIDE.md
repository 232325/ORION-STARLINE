# Marketing Growth Strategiyasi - Backend Integration Guide

## 📋 Kirish
Ushbu hujjat Orion Starline marketing modullarini mavjud backend tizimi bilan integratsiya qilish bo'yicha to'liq ko'rsatmani beradi.

## 🏗️ Yaratilgan Modullar

### Asosiy Marketing Modullar:
1. **content_engine.py** - Content yaratish va boshqarish tizimi
2. **seo_optimizer.py** - SEO tahlil va optimizatsiya
3. **social_automation.py** - Social media avtomatizatsiya
4. **referral_system.py** - Referral program boshqaruvi
5. **community_manager.py** - Jamoa boshqaruv tizimi
6. **conversion_optimizer.py** - A/B testing va konversiya optimizatsiya
7. **analytics_dashboard.py** - Marketing analytics
8. **email_marketing.py** - Email marketing tizimi
9. **influencer_manager.py** - Influencer hamkorlik boshqaruvi

## 🗄️ Database Schema
Marketing funksiyalari uchun to'liq database schema yaratildi:
- `1762220000_marketing_modules_database_schema.sql`

### Asosiy jadvallar:
- **marketing_content** - Content boshqaruvi
- **content_performance** - Content performance metrics
- **seo_tracking** - SEO kuzatuv
- **social_media_accounts** - Social media akkauntlar
- **social_media_posts** - Social media postlar
- **referral_codes** - Referral kodlar
- **referral_tracking** - Referral kuzatuv
- **community_members** - Jamoa a'zolari
- **community_posts** - Jamoa postlari
- **ab_tests** - A/B testing
- **email_campaigns** - Email kampaniyalari
- **email_subscribers** - Email obunachilar
- **influencer_partnerships** - Influencer hamkorliklar
- **marketing_analytics** - Marketing analytics

## 🔧 Integration Steps

### 1. Environment Variables
Backend `settings.py` fayliga qo'shish kerak:

```python
# Marketing API Keys
GOOGLE_API_KEY: str = Field(default="", env="GOOGLE_API_KEY")
FACEBOOK_ACCESS_TOKEN: str = Field(default="", env="FACEBOOK_ACCESS_TOKEN")
TWITTER_API_KEY: str = Field(default="", env="TWITTER_API_KEY")
LINKEDIN_ACCESS_TOKEN: str = Field(default="", env="LINKEDIN_ACCESS_TOKEN")
INSTAGRAM_ACCESS_TOKEN: str = Field(default="", env="INSTAGRAM_ACCESS_TOKEN")

# Email Service
SMTP_HOST: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
SMTP_USERNAME: str = Field(default="", env="SMTP_USERNAME")
SMTP_PASSWORD: str = Field(default="", env="SMTP_PASSWORD")

# Analytics
GOOGLE_ANALYTICS_ID: str = Field(default="", env="GOOGLE_ANALYTICS_ID")
GOOGLE_ANALYTICS_SECRET: str = Field(default="", env="GOOGLE_ANALYTICS_SECRET")

# SEO Tools
SEMRUSH_API_KEY: str = Field(default="", env="SEMRUSH_API_KEY")
AHREFS_API_TOKEN: str = Field(default="", env="AHREFS_API_TOKEN")
```

### 2. Marketing API Endpoints Yaratish
`/workspace/orion-starline/backend/api/endpoints/marketing/` papkasida quyidagi endpoint fayllarini yarating:

#### a) content_endpoints.py
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...models.schemas import ContentCreate, ContentUpdate, ContentResponse
from ...models.database import get_db

router = APIRouter(prefix="/content", tags=["content"])

@router.post("/", response_model=ContentResponse)
async def create_content(content: ContentCreate, db: Session = Depends(get_db)):
    # ContentEngine dan foydalanib content yaratish
    pass

@router.get("/", response_model=List[ContentResponse])
async def get_contents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Barcha contentlarni olish
    pass

@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(content_id: str, content: ContentUpdate, db: Session = Depends(get_db)):
    # Content yangilash
    pass
```

#### b) social_endpoints.py
```python
from fastapi import APIRouter, Depends
from ...models.database import get_db

router = APIRouter(prefix="/social", tags=["social"])

@router.post("/schedule-post")
async def schedule_social_post(post_data: dict, db: Session = Depends(get_db)):
    # SocialMediaAutomation dan foydalanib post rejalash
    pass

@router.get("/accounts")
async def get_social_accounts(db: Session = Depends(get_db)):
    # Social media akkauntlarni olish
    pass
```

#### c) referral_endpoints.py
```python
from fastapi import APIRouter, Depends, BackgroundTasks
from ...models.database import get_db

router = APIRouter(prefix="/referral", tags=["referral"])

@router.post("/create-code")
async def create_referral_code(user_id: str, db: Session = Depends(get_db)):
    # ReferralSystem dan foydalanib kod yaratish
    pass

@router.get("/tracking/{code}")
async def track_referral(code: str, db: Session = Depends(get_db)):
    # Referral tracking
    pass
```

### 3. Marketing Pydantic Schemas
`/workspace/orion-starline/backend/api/models/schemas/marketing.py` yarating:

```python
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ContentType(str, Enum):
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    VIDEO_SCRIPT = "video_script"

class ContentStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"

class ContentCreate(BaseModel):
    title: str
    content_type: ContentType
    target_keywords: List[str]
    target_audience: str
    content_body: str

class ContentResponse(BaseModel):
    id: str
    title: str
    content_type: ContentType
    status: ContentStatus
    seo_score: float
    created_at: datetime

    class Config:
        from_attributes = True
```

### 4. Main API ga Integration
`main.py` fayliga qo'shish:

```python
from endpoints.marketing.content_endpoints import router as content_router
from endpoints.marketing.social_endpoints import router as social_router
from endpoints.marketing.referral_endpoints import router as referral_router

app.include_router(content_router, prefix="/marketing")
app.include_router(social_router, prefix="/marketing")
app.include_router(referral_router, prefix="/marketing")
```

## 🚀 Frontend Integration

### 1. Marketing Dashboard Component
`/workspace/orion-starline/frontend/src/pages/MarketingDashboard.tsx`:

```typescript
import React, { useState, useEffect } from 'react';
import { Card, Button, Table, Tabs } from 'antd';
import { ContentOutlined, ShareAltOutlined, TeamOutlined } from '@ant-design/icons';

interface MarketingStats {
  totalContent: number;
  socialPosts: number;
  referrals: number;
  emailSubscribers: number;
}

const MarketingDashboard: React.FC = () => {
  const [stats, setStats] = useState<MarketingStats>({
    totalContent: 0,
    socialPosts: 0,
    referrals: 0,
    emailSubscribers: 0
  });

  useEffect(() => {
    // Marketing analytics API dan ma'lumotlarni olish
    fetch('/api/v1/marketing/analytics/dashboard')
      .then(res => res.json())
      .then(data => setStats(data));
  }, []);

  return (
    <div className="marketing-dashboard">
      <h1>Marketing Dashboard</h1>
      
      <div className="stats-grid">
        <Card title="Content" extra={<ContentOutlined />}>
          <div className="stat-number">{stats.totalContent}</div>
        </Card>
        <Card title="Social Media" extra={<ShareAltOutlined />}>
          <div className="stat-number">{stats.socialPosts}</div>
        </Card>
        <Card title="Referrals" extra={<TeamOutlined />}>
          <div className="stat-number">{stats.referrals}</div>
        </Card>
      </div>

      <Tabs
        items={[
          {
            key: 'content',
            label: 'Content Management',
            children: <ContentManager />
          },
          {
            key: 'social',
            label: 'Social Media',
            children: <SocialMediaManager />
          },
          {
            key: 'referrals',
            label: 'Referral System',
            children: <ReferralManager />
          }
        ]}
      />
    </div>
  );
};

export default MarketingDashboard;
```

## 📊 Configuration

### 1. Database Migration
```bash
# Migrationni run qilish
supabase db push
```

### 2. Environment Configuration
`.env` fayliga qo'shing:

```env
# Marketing API Keys
GOOGLE_API_KEY=your_google_api_key
FACEBOOK_ACCESS_TOKEN=your_facebook_token
TWITTER_API_KEY=your_twitter_api_key

# Email Service
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Analytics
GOOGLE_ANALYTICS_ID=GA-XXXXXXXX-X
SEMRUSH_API_KEY=your_semrush_key
```

## 🔍 Testing

### 1. API Testing
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_content():
    response = client.post("/api/v1/marketing/content/", json={
        "title": "Test Content",
        "content_type": "blog_post",
        "target_keywords": ["test", "marketing"],
        "target_audience": "general",
        "content_body": "Test content body"
    })
    assert response.status_code == 201

def test_get_content_list():
    response = client.get("/api/v1/marketing/content/")
    assert response.status_code == 200
```

## 🎯 Key Features

### 1. Content Management
- AI-ga asoslangan content yaratish
- SEO optimizatsiya
- Content performance tracking
- Automated scheduling

### 2. Social Media Automation
- Multi-platform posting
- Engagement tracking
- Automated responses
- Analytics integration

### 3. Referral System
- Multi-level referrals
- Reward management
- Fraud detection
- Commission tracking

### 4. Email Marketing
- Campaign management
- Segmentation
- A/B testing
- Performance analytics

### 5. Influencer Management
- Partnership tracking
- Campaign management
- Performance metrics
- Payment tracking

## 🛡️ Security

### 1. API Security
- JWT authentication
- Rate limiting
- Input validation
- CORS protection

### 2. Data Protection
- Row Level Security (RLS)
- Encrypted tokens
- Secure API keys
- GDPR compliance

## 📈 Performance Optimization

### 1. Database
- Optimized indexes
- Connection pooling
- Query optimization
- Caching

### 2. API
- Async operations
- Background tasks
- Pagination
- Response compression

## 🔧 Maintenance

### 1. Monitoring
- Performance metrics
- Error tracking
- Analytics dashboard
- Health checks

### 2. Updates
- Automated backups
- Version control
- Rollback procedures
- Testing pipeline

## ✅ Next Steps

1. **Database Migration**: `1762220000_marketing_modules_database_schema.sql` ni apply qiling
2. **API Endpoints**: Marketing endpoints ni backend ga qo'shing
3. **Frontend Components**: Marketing dashboard ni yarating
4. **Configuration**: Environment variables ni sozlang
5. **Testing**: Unit va integration testlarni yarating
6. **Monitoring**: Analytics va monitoring ni sozlang

## 📞 Support
Agar qandaydir savol yoki muammo bo'lsa, iltimos backend team ga murojaat qiling.
