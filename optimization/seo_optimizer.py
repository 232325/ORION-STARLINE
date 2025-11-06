#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEO Optimizer - Qidiruv tizimi optimizatori
SEO optimizatsiya va mobile performance

Xususiyatlar:
- Meta tag optimizatsiya
- Structured data (Schema.org)
- Open Graph va Twitter Cards
- XML sitemap yaratish
- Robots.txt optimizatsiya
- Mobile-first indexing
- Core Web Vitals optimizatsiya
- Page speed optimization
- Internal linking strategy
- Content optimization
- Image SEO
- Local SEO
- Technical SEO audit
"""

import os
import re
import json
import time
import logging
import asyncio
import hashlib
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta
import aiofiles
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import mimetypes

# Logging sozlamalar
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SEOConfig:
    """SEO konfiguratsiyasi"""
    site_name: str
    site_url: str
    site_description: str
    default_keywords: str
    author: str
    language: str = "uz"
    country: str = "UZ"
    currency: str = "UZS"
    robots_policy: str = "index, follow"  # index, noindex, follow, nofollow
    sitemap_enabled: bool = True
    schema_enabled: bool = True
    social_sharing: bool = True
    mobile_optimized: bool = True
    core_web_vitals: bool = True
    local_seo: bool = False
    organization_name: str = ""
    organization_logo: str = ""
    organization_address: Dict = None
    contact_info: Dict = None

@dataclass
class PageSEOData:
    """Sahifa SEO ma'lumotlari"""
    url: str
    title: str
    description: str
    keywords: List[str]
    h1_tags: List[str]
    images: List[Dict]
    links_internal: List[str]
    links_external: List[str]
    word_count: int
    readability_score: float
    load_time: float
    mobile_score: float
    seo_score: float

@dataclass
class TechnicalSEOIssue:
    """Texnik SEO muammolari"""
    type: str  # error, warning, info
    category: str  # meta, content, performance, technical
    description: str
    impact: str  # high, medium, low
    recommendation: str
    file_path: str = ""

class SchemaGenerator:
    """Structured Data generator"""
    
    def __init__(self, config: SEOConfig):
        self.config = config

    def generate_organization_schema(self) -> Dict:
        """Tashkilot uchun Schema.org"""
        if not self.config.organization_name:
            return {}
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": self.config.organization_name,
            "url": self.config.site_url,
            "description": self.config.site_description
        }
        
        if self.config.organization_logo:
            schema["logo"] = self.config.organization_logo
        
        if self.config.organization_address:
            schema["address"] = {
                "@type": "PostalAddress",
                **self.config.organization_address
            }
        
        if self.config.contact_info:
            schema["contactPoint"] = {
                "@type": "ContactPoint",
                **self.config.contact_info,
                "availableLanguage": self.config.language
            }
        
        return schema

    def generate_website_schema(self) -> Dict:
        """Veb-sayt uchun Schema.org"""
        return {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": self.config.site_name,
            "url": self.config.site_url,
            "description": self.config.site_description,
            "potentialAction": {
                "@type": "SearchAction",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": f"{self.config.site_url}/search?q={{search_term_string}}"
                },
                "query-input": "required name=search_term_string"
            },
            "inLanguage": self.config.language
        }

    def generate_breadcrumb_schema(self, breadcrumbs: List[Dict]) -> Dict:
        """Breadcrumb uchun Schema.org"""
        if len(breadcrumbs) < 2:
            return {}
        
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": index + 1,
                    "name": item["name"],
                    "item": item["url"]
                }
                for index, item in enumerate(breadcrumbs)
            ]
        }

    def generate_article_schema(self, article_data: Dict) -> Dict:
        """Maqola uchun Schema.org"""
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": article_data.get("title", ""),
            "description": article_data.get("description", ""),
            "image": article_data.get("image", ""),
            "author": {
                "@type": "Person",
                "name": article_data.get("author", self.config.author)
            },
            "publisher": {
                "@type": "Organization",
                "name": self.config.organization_name or self.config.site_name,
                "logo": {
                    "@type": "ImageObject",
                    "url": self.config.organization_logo or ""
                }
            },
            "datePublished": article_data.get("published_date", ""),
            "dateModified": article_data.get("modified_date", ""),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": article_data.get("url", "")
            }
        }

    def generate_product_schema(self, product_data: Dict) -> Dict:
        """Mahsulot uchun Schema.org"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": product_data.get("name", ""),
            "description": product_data.get("description", ""),
            "image": product_data.get("image", ""),
            "brand": {
                "@type": "Brand",
                "name": product_data.get("brand", "")
            }
        }
        
        if product_data.get("price"):
            schema["offers"] = {
                "@type": "Offer",
                "price": product_data["price"],
                "priceCurrency": self.config.currency,
                "availability": "https://schema.org/InStock",
                "seller": {
                    "@type": "Organization",
                    "name": self.config.organization_name or self.config.site_name
                }
            }
        
        if product_data.get("rating"):
            schema["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": product_data["rating"]["value"],
                "reviewCount": product_data["rating"]["count"]
            }
        
        return schema

class SitemapGenerator:
    """XML Sitemap generator"""
    
    def __init__(self, config: SEOConfig):
        self.config = config

    def generate_sitemap(self, pages: List[Dict], output_path: str):
        """XML Sitemap yaratish"""
        urlset = ET.Element("urlset")
        urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        
        # Homepage qo'shish
        homepage = ET.SubElement(urlset, "url")
        ET.SubElement(homepage, "loc").text = self.config.site_url
        ET.SubElement(homepage, "lastmod").text = datetime.now().strftime("%Y-%m-%d")
        ET.SubElement(homepage, "changefreq").text = "daily"
        ET.SubElement(homepage, "priority").text = "1.0"
        
        # Sahifalar qo'shish
        for page in pages:
            url_elem = ET.SubElement(urlset, "url")
            ET.SubElement(url_elem, "loc").text = urljoin(self.config.site_url, page.get("url", ""))
            ET.SubElement(url_elem, "lastmod").text = page.get("lastmod", datetime.now().strftime("%Y-%m-%d"))
            ET.SubElement(url_elem, "changefreq").text = page.get("changefreq", "weekly")
            ET.SubElement(url_elem, "priority").text = str(page.get("priority", "0.5"))
        
        # Faylga yozish
        tree = ET.ElementTree(urlset)
        ET.indent(tree, space="  ", level=0)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        
        logger.info(f"Sitemap yaratildi: {output_path}")

    def generate_robots_txt(self, output_path: str):
        """Robots.txt yaratish"""
        robots_content = f"""User-agent: *
Allow: /

# Disallow admin va private papkalar
Disallow: /admin/
Disallow: /private/
Disallow: /temp/
Disallow: /*.json$
Disallow: /api/

# Allow important files
Allow: /sitemap.xml
Allow: /robots.txt
Allow: /*.css$
Allow: /*.js$
Allow: /*.png$
Allow: /*.jpg$
Allow: /*.jpeg$
Allow: /*.gif$
Allow: /*.svg$
Allow: /*.webp$

# Crawl-delay
Crawl-delay: 1

# Sitemap location
Sitemap: {self.config.site_url}/sitemap.xml
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(robots_content)
        
        logger.info(f"Robots.txt yaratildi: {output_path}")

class MetaTagGenerator:
    """Meta tag generator"""
    
    def __init__(self, config: SEOConfig):
        self.config = config

    def generate_base_meta_tags(self) -> Dict:
        """Asosiy meta-teglar"""
        return {
            "charset": "UTF-8",
            "viewport": "width=device-width, initial-scale=1.0",
            "description": self.config.site_description,
            "keywords": self.config.default_keywords,
            "author": self.config.author,
            "robots": self.config.robots_policy,
            "language": self.config.language,
            "geo.region": self.config.country,
            "geo.placename": self.config.country,
            "theme-color": "#000000",
            "msapplication-TileColor": "#000000",
            "msapplication-config": "/browserconfig.xml"
        }

    def generate_open_graph_tags(self, page_data: Dict = None) -> Dict:
        """Open Graph meta-teglar"""
        title = page_data.get("title", self.config.site_name) if page_data else self.config.site_name
        description = page_data.get("description", self.config.site_description) if page_data else self.config.site_description
        image = page_data.get("image", self.config.organization_logo) if page_data else self.config.organization_logo
        url = page_data.get("url", self.config.site_url) if page_data else self.config.site_url
        
        return {
            "og:title": title,
            "og:description": description,
            "og:type": page_data.get("type", "website") if page_data else "website",
            "og:url": url,
            "og:image": image,
            "og:site_name": self.config.site_name,
            "og:locale": self.config.language.replace('-', '_'),
            "article:author": self.config.author,
            "article:published_time": page_data.get("published_date", "") if page_data else "",
            "article:modified_time": page_data.get("modified_date", "") if page_data else ""
        }

    def generate_twitter_card_tags(self, page_data: Dict = None) -> Dict:
        """Twitter Card meta-teglar"""
        title = page_data.get("title", self.config.site_name) if page_data else self.config.site_name
        description = page_data.get("description", self.config.site_description) if page_data else self.config.site_description
        image = page_data.get("image", self.config.organization_logo) if page_data else self.config.organization_logo
        
        return {
            "twitter:card": "summary_large_image",
            "twitter:title": title,
            "twitter:description": description,
            "twitter:image": image,
            "twitter:creator": f"@{self.config.site_name.lower().replace(' ', '')}",
            "twitter:site": f"@{self.config.site_name.lower().replace(' ', '')}"
        }

    def generate_structured_data_tags(self, schema_data: Dict) -> str:
        """Structured Data JSON-LD"""
        if not schema_data:
            return ""
        
        return f'<script type="application/ld+json">{json.dumps(schema_data, ensure_ascii=False, indent=2)}</script>'

class ContentAnalyzer:
    """Content tahlil qiluvchi"""
    
    def __init__(self):
        self.stop_words = {
            'uz': ['va', 'yoki', 'lekin', 'ham', 'emas', 'balki', 'chunki', 'agar', 'bo\'lsa', 'uchun', 'hamda', 'ya\'ni'],
            'en': ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall']
        }

    def analyze_page_content(self, html_content: str, url: str) -> PageSEOData:
        """Sahifa content tahlili"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Title tahlili
        title_tag = soup.find('title')
        title = title_tag.text.strip() if title_tag else ""
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ""
        
        # Keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        keywords = []
        if meta_keywords:
            keywords = [kw.strip() for kw in meta_keywords.get('content', '').split(',') if kw.strip()]
        
        # H1 tags
        h1_tags = [h1.text.strip() for h1 in soup.find_all('h1')]
        
        # Images
        images = []
        for img in soup.find_all('img'):
            images.append({
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'has_alt': bool(img.get('alt'))
            })
        
        # Links
        links_internal = []
        links_external = []
        base_url = urlparse(url)
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if href.startswith('http'):
                if base_url.netloc in href:
                    links_internal.append(href)
                else:
                    links_external.append(href)
            elif href.startswith('/'):
                links_internal.append(urljoin(url, href))
        
        # Text content
        text_content = soup.get_text()
        word_count = len(text_content.split())
        
        # Readability score (simple)
        readability_score = self.calculate_readability_score(text_content)
        
        # Load time (placeholder - real implementation would measure actual load time)
        load_time = 2.5  # seconds
        
        # Mobile score (placeholder)
        mobile_score = 85.0
        
        # SEO score calculation
        seo_score = self.calculate_seo_score({
            'title': title,
            'description': description,
            'keywords': keywords,
            'h1_count': len(h1_tags),
            'images_with_alt': sum(1 for img in images if img['has_alt']),
            'total_images': len(images),
            'internal_links': len(links_internal),
            'word_count': word_count
        })
        
        return PageSEOData(
            url=url,
            title=title,
            description=description,
            keywords=keywords,
            h1_tags=h1_tags,
            images=images,
            links_internal=links_internal,
            links_external=links_external,
            word_count=word_count,
            readability_score=readability_score,
            load_time=load_time,
            mobile_score=mobile_score,
            seo_score=seo_score
        )

    def calculate_readability_score(self, text: str) -> float:
        """Readability score hisoblash"""
        # Simple readability score based on sentence length and word complexity
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # Score from 0-100 (higher is better)
        score = max(0, min(100, 100 - avg_sentence_length))
        return score

    def calculate_seo_score(self, seo_factors: Dict) -> float:
        """SEO score hisoblash"""
        score = 0
        max_score = 100
        
        # Title (15 points)
        if seo_factors.get('title'):
            title_len = len(seo_factors['title'])
            if 30 <= title_len <= 60:
                score += 15
            elif 20 <= title_len <= 70:
                score += 10
        
        # Description (15 points)
        if seo_factors.get('description'):
            desc_len = len(seo_factors['description'])
            if 120 <= desc_len <= 160:
                score += 15
            elif 100 <= desc_len <= 180:
                score += 10
        
        # H1 tags (10 points)
        if seo_factors.get('h1_count', 0) == 1:
            score += 10
        elif seo_factors.get('h1_count', 0) > 0:
            score += 5
        
        # Images with alt (10 points)
        if seo_factors.get('total_images', 0) > 0:
            alt_ratio = seo_factors['images_with_alt'] / seo_factors['total_images']
            score += alt_ratio * 10
        
        # Internal links (15 points)
        if seo_factors.get('internal_links', 0) >= 3:
            score += 15
        elif seo_factors.get('internal_links', 0) > 0:
            score += 10
        
        # Keywords (10 points)
        if seo_factors.get('keywords'):
            score += 10
        
        # Word count (25 points)
        word_count = seo_factors.get('word_count', 0)
        if word_count >= 300:
            score += 25
        elif word_count >= 150:
            score += 20
        elif word_count >= 100:
            score += 15
        
        return score

class TechnicalSEOAuditor:
    """Texnik SEO auditor"""
    
    def __init__(self):
        self.issues = []

    def audit_page(self, html_content: str, url: str) -> List[TechnicalSEOIssue]:
        """Sahifa texnik audit qilish"""
        self.issues = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Meta tag audit
        self._audit_meta_tags(soup, url)
        
        # HTML structure audit
        self._audit_html_structure(soup, url)
        
        # Images audit
        self._audit_images(soup, url)
        
        # Links audit
        self._audit_links(soup, url)
        
        # Performance audit
        self._audit_performance(soup, url)
        
        return self.issues

    def _audit_meta_tags(self, soup: BeautifulSoup, url: str):
        """Meta tag audit"""
        # Title audit
        title_tag = soup.find('title')
        if not title_tag:
            self.issues.append(TechnicalSEOIssue(
                type="error",
                category="meta",
                description="Sahifada title tag topilmadi",
                impact="high",
                recommendation="<title> tag qo'shing va optimallashtiring",
                file_path=url
            ))
        else:
            title_text = title_tag.text.strip()
            title_len = len(title_text)
            if title_len < 30:
                self.issues.append(TechnicalSEOIssue(
                    type="warning",
                    category="meta",
                    description=f"Title juda qisqa ({title_len} belgi)",
                    impact="medium",
                    recommendation="Title ni 30-60 belgi oralig'ida qiling",
                    file_path=url
                ))
            elif title_len > 60:
                self.issues.append(TechnicalSEOIssue(
                    type="warning",
                    category="meta",
                    description=f"Title juda uzun ({title_len} belgi)",
                    impact="medium",
                    recommendation="Title ni 30-60 belgi oralig'ida qiling",
                    file_path=url
                ))
        
        # Description audit
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            self.issues.append(TechnicalSEOIssue(
                type="error",
                category="meta",
                description="Meta description topilmadi",
                impact="high",
                recommendation="Meta description qo'shing",
                file_path=url
            ))
        else:
            desc_content = meta_desc.get('content', '')
            desc_len = len(desc_content)
            if desc_len < 120:
                self.issues.append(TechnicalSEOIssue(
                    type="warning",
                    category="meta",
                    description=f"Description juda qisqa ({desc_len} belgi)",
                    impact="medium",
                    recommendation="Description ni 120-160 belgi oralig'ida qiling",
                    file_path=url
                ))
            elif desc_len > 160:
                self.issues.append(TechnicalSEOIssue(
                    type="warning",
                    category="meta",
                    description=f"Description juda uzun ({desc_len} belgi)",
                    impact="medium",
                    recommendation="Description ni 120-160 belgi oralig'ida qiling",
                    file_path=url
                ))
        
        # Keywords audit (deprecated but still useful)
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and not meta_keywords.get('content', '').strip():
            self.issues.append(TechnicalSEOIssue(
                type="info",
                category="meta",
                description="Keywords meta tag bo'sh",
                impact="low",
                recommendation="Keywords to'g'ri qiymatlar bilan to'ldiring",
                file_path=url
            ))

    def _audit_html_structure(self, soup: BeautifulSoup, url: str):
        """HTML structure audit"""
        # H1 tag audit
        h1_tags = soup.find_all('h1')
        if not h1_tags:
            self.issues.append(TechnicalSEOIssue(
                type="error",
                category="content",
                description="Sahifada H1 tag topilmadi",
                impact="high",
                recommendation="Bitta H1 tag qo'shing",
                file_path=url
            ))
        elif len(h1_tags) > 1:
            self.issues.append(TechnicalSEOIssue(
                type="warning",
                category="content",
                description=f"Bir nechta H1 tag topildi ({len(h1_tags)} ta)",
                impact="medium",
                recommendation="Faqat bitta H1 tag ishlatish tavsiya etiladi",
                file_path=url
            ))
        
        # Heading hierarchy audit
        headings = {}
        for i in range(1, 7):
            headings[f'h{i}'] = len(soup.find_all(f'h{i}'))
        
        # H2 H3 audit
        if headings['h1'] > 0 and headings['h2'] == 0:
            self.issues.append(TechnicalSEOIssue(
                type="info",
                category="content",
                description="H1 dan keyin H2 tag yo'q",
                impact="low",
                recommendation="Sahifa tarkibini H2, H3 bilan tuzing",
                file_path=url
            ))

    def _audit_images(self, soup: BeautifulSoup, url: str):
        """Image audit"""
        images = soup.find_all('img')
        images_without_alt = 0
        
        for img in images:
            alt_text = img.get('alt', '').strip()
            src = img.get('src', '')
            
            if not alt_text:
                images_without_alt += 1
                self.issues.append(TechnicalSEOIssue(
                    type="warning",
                    category="content",
                    description=f"Image uchun alt text yo'q: {src}",
                    impact="medium",
                    recommendation="Har bir image uchun alt text qo'shing",
                    file_path=url
                ))
            
            # Image size audit (placeholder)
            if not img.get('width') or not img.get('height'):
                self.issues.append(TechnicalSEOIssue(
                    type="info",
                    category="content",
                    description=f"Image o'lchamlari ko'rsatilmagan: {src}",
                    impact="low",
                    recommendation="Image o'lchamlarini ko'rsating",
                    file_path=url
                ))
        
        if images_without_alt > len(images) * 0.5:
            self.issues.append(TechnicalSEOIssue(
                type="warning",
                category="content",
                description=f"Sahifadagi ko'plab rasm alt text'siz ({images_without_alt}/{len(images)})",
                impact="high",
                recommendation="Barcha rasmlar uchun alt text qo'shing",
                file_path=url
            ))

    def _audit_links(self, soup: BeautifulSoup, url: str):
        """Link audit"""
        links = soup.find_all('a', href=True)
        
        # External links audit
        external_links = []
        base_domain = urlparse(url).netloc
        
        for link in links:
            href = link.get('href', '')
            if href.startswith('http') and base_domain not in href:
                external_links.append(href)
                if not link.get('rel') or 'nofollow' not in link.get('rel', '').lower():
                    # Suggest rel="nofollow" for some external links
                    if 'advertisement' in link.get('href', '').lower():
                        self.issues.append(TechnicalSEOIssue(
                            type="info",
                            category="content",
                            description=f"Reklama link rel='nofollow' yo'q: {href}",
                            impact="low",
                            recommendation="Reklama link'larda rel='nofollow' qo'shing",
                            file_path=url
                        ))
        
        # Internal links audit
        internal_links = [link for link in links if link.get('href', '').startswith('/')]
        if len(internal_links) < 2:
            self.issues.append(TechnicalSEOIssue(
                type="info",
                category="content",
                description="Kam ichki link",
                impact="low",
                recommendation="Ichki link'lar sonini oshiring",
                file_path=url
            ))

    def _audit_performance(self, soup: BeautifulSoup, url: str):
        """Performance audit"""
        # CSS files
        css_files = soup.find_all('link', rel='stylesheet')
        if len(css_files) > 3:
            self.issues.append(TechnicalSEOIssue(
                type="warning",
                category="performance",
                description=f"Ko'plab CSS fayllar ({len(css_files)} ta)",
                impact="medium",
                recommendation="CSS fayllarni birlashtiring",
                file_path=url
            ))
        
        # JavaScript files
        js_files = soup.find_all('script', src=True)
        blocking_js = len(js_files)  # Simplified - all external JS considered blocking
        if blocking_js > 5:
            self.issues.append(TechnicalSEOIssue(
                type="warning",
                category="performance",
                description=f"Ko'plab blocking JavaScript fayllar ({blocking_js} ta)",
                impact="high",
                recommendation="JavaScript fayllarni asinxron yoki deferred qiling",
                file_path=url
            ))

class SEOOptimizer:
    """Asosiy SEO optimizatori"""
    
    def __init__(self, project_root: str, config: SEOConfig):
        self.project_root = Path(project_root)
        self.config = config
        
        # Components
        self.schema_generator = SchemaGenerator(config)
        self.sitemap_generator = SitemapGenerator(config)
        self.meta_generator = MetaTagGenerator(config)
        self.content_analyzer = ContentAnalyzer()
        self.technical_auditor = TechnicalSEOAuditor()
        
        # SEO papkasi
        self.seo_dir = self.project_root / "seo_assets"
        self.seo_dir.mkdir(exist_ok=True)

    async def optimize_seo(self) -> Dict:
        """SEO optimizatsiya o'tkazish"""
        logger.info("🚀 SEO optimizatsiya boshlanmoqda...")
        
        try:
            # 1. HTML fayllarni qidirish
            html_files = await self._discover_html_files()
            
            # 2. Content tahlili
            page_analysis = await self._analyze_all_pages(html_files)
            
            # 3. Meta tag'larni yangilash
            await self._update_meta_tags(html_files)
            
            # 4. Structured Data qo'shish
            await self._add_structured_data(html_files)
            
            # 5. Open Graph va Twitter Cards
            await self._add_social_meta_tags(html_files)
            
            # 6. Sitemap yaratish
            if self.config.sitemap_enabled:
                await self._generate_sitemap(page_analysis)
            
            # 7. Robots.txt yaratish
            await self._generate_robots_txt()
            
            # 8. Texnik SEO audit
            audit_results = await self._perform_technical_audit(html_files)
            
            # 9. Internal linking strategy
            await self._improve_internal_linking(page_analysis)
            
            # 10. Image SEO optimizatsiya
            await self._optimize_images_seo(html_files)
            
            # 11. Mobile optimization
            await self._optimize_for_mobile(html_files)
            
            # 12. Core Web Vitals
            if self.config.core_web_vitals:
                await self._optimize_core_web_vitals(html_files)
            
            # 13. Local SEO
            if self.config.local_seo:
                await self._optimize_local_seo()
            
            # 14. SEO hisoboti
            await self._generate_seo_report(page_analysis, audit_results)
            
            logger.info("✅ SEO optimizatsiya muvaffaqiyatli tugallandi!")
            return {"status": "success", "pages_analyzed": len(page_analysis)}
            
        except Exception as e:
            logger.error(f"❌ SEO optimizatsiya xatosi: {str(e)}")
            raise

    async def _discover_html_files(self) -> List[Path]:
        """HTML fayllarni topish"""
        html_extensions = ["*.html", "*.htm"]
        html_files = []
        
        for ext in html_extensions:
            html_files.extend(self.project_root.rglob(ext))
        
        # Exclude certain directories
        exclude_dirs = ["node_modules", ".git", "dist", "build", ".next", ".nuxt", "__pycache__"]
        html_files = [f for f in html_files if not any(excl in str(f) for excl in exclude_dirs)]
        
        logger.info(f"Topilgan HTML fayllar: {len(html_files)} ta")
        return html_files

    async def _analyze_all_pages(self, html_files: List[Path]) -> Dict[str, PageSEOData]:
        """Barcha sahifalarni tahlil qilish"""
        logger.info("📊 Sahifalar tahlil qilinmoqda...")
        
        page_analysis = {}
        
        for html_file in html_files:
            try:
                async with aiofiles.open(html_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                
                # Content tahlili
                analysis = self.content_analyzer.analyze_page_content(content, str(html_file))
                page_analysis[str(html_file)] = analysis
                
                logger.info(f"Tahlil qilindi: {html_file.name} (SEO Score: {analysis.seo_score:.1f})")
                
            except Exception as e:
                logger.error(f"Sahifa tahlil xatosi {html_file}: {str(e)}")
        
        return page_analysis

    async def _update_meta_tags(self, html_files: List[Path]):
        """Meta tag'larni yangilash"""
        logger.info("🏷️  Meta tag'lar yangilanmoqda...")
        
        base_meta_tags = self.meta_generator.generate_base_meta_tags()
        
        for html_file in html_files:
            try:
                async with aiofiles.open(html_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                
                soup = BeautifulSoup(content, 'html.parser')
                head = soup.find('head')
                
                if not head:
                    continue
                
                # Mavjud meta tag'lar
                existing_meta = {}
                for meta in soup.find_all('meta'):
                    name = meta.get('name') or meta.get('property')
                    if name:
                        existing_meta[name] = meta.get('content', '')
                
                # Asosiy meta tag'lar qo'shish/yangilash
                for name, content in base_meta_tags.items():
                    if name not in existing_meta:
                        meta_tag = soup.new_tag('meta', attrs={'name': name, 'content': content})
                        head.append(meta_tag)
                    else:
                        existing_meta[name].attrs['content'] = content
                
                # Yangilangan content'ni saqlash
                async with aiofiles.open(html_file, 'w', encoding='utf-8') as f:
                    await f.write(str(soup))
                
                logger.info(f"Meta tag'lar yangilandi: {html_file.name}")
                
            except Exception as e:
                logger.error(f"Meta tag yangilash xatosi {html_file}: {str(e)}")

    async def _add_structured_data(self, html_files: List[Path]):
        """Structured Data qo'shish"""
        if not self.config.schema_enabled:
            return
            
        logger.info("🔍 Structured Data qo'shilmoqda...")
        
        # Organization schema
        org_schema = self.schema_generator.generate_organization_schema()
        website_schema = self.schema_generator.generate_website_schema()
        
        for html_file in html_files:
            try:
                async with aiofiles.open(html_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                
                soup = BeautifulSoup(content, 'html.parser')
                head = soup.find('head')
                
                if not head:
                    continue
                
                # Organization schema qo'shish
                if org_schema:
                    script_tag = soup.new_tag('script', attrs={'type': 'application/ld+json'})
                    script_tag.string = json.dumps(org_schema, ensure_ascii=False, indent=2)
                    head.append(script_tag)
                
                # Website schema qo'shish
                if website_schema:
                    script_tag = soup.new_tag('script', attrs={'type': 'application/ld+json'})
                    script_tag.string = json.dumps(website_schema, ensure_ascii=False, indent=2)
                    head.append(script_tag)
                
                # Breadcrumb schema (agar mavjud bo'lsa)
                # Bu yerda real implementation breadcrumbs detection kerak
                
                # Yangilangan content'ni saqlash
                async with aiofiles.open(html_file, 'w', encoding='utf-8') as f:
                    await f.write(str(soup))
                
                logger.info(f"Structured Data qo'shildi: {html_file.name}")
                
            except Exception as e:
                logger.error(f"Structured Data qo'shish xatosi {html_file}: {str(e)}")

    async def _add_social_meta_tags(self, html_files: List[Path]):
        """Social media meta tag'lar qo'shish"""
        if not self.config.social_sharing:
            return
            
        logger.info("📱 Social media meta tag'lar qo'shilmoqda...")
        
        for html_file in html_files:
            try:
                async with aiofiles.open(html_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                
                soup = BeautifulSoup(content, 'html.parser')
                head = soup.find('head')
                
                if not head:
                    continue
                
                # Page-specific data
                page_data = {}
                title_tag = soup.find('title')
                if title_tag:
                    page_data["title"] = title_tag.text.strip()
                
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    page_data["description"] = meta_desc.get('content', '')
                
                page_data["type"] = "website"
                page_data["url"] = str(html_file)
                
                # Open Graph tags
                og_tags = self.meta_generator.generate_open_graph_tags(page_data)
                for property_name, content in og_tags.items():
                    meta_tag = soup.new_tag('meta', attrs={'property': property_name, 'content': content})
                    head.append(meta_tag)
                
                # Twitter Card tags
                twitter_tags = self.meta_generator.generate_twitter_card_tags(page_data)
                for name, content in twitter_tags.items():
                    meta_tag = soup.new_tag('meta', attrs={'name': name, 'content': content})
                    head.append(meta_tag)
                
                # Yangilangan content'ni saqlash
                async with aiofiles.open(html_file, 'w', encoding='utf-8') as f:
                    await f.write(str(soup))
                
                logger.info(f"Social meta tag'lar qo'shildi: {html_file.name}")
                
            except Exception as e:
                logger.error(f"Social meta tag qo'shish xatosi {html_file}: {str(e)}")

    async def _generate_sitemap(self, page_analysis: Dict[str, PageSEOData]):
        """Sitemap yaratish"""
        logger.info("🗺️  Sitemap yaratilmoqda...")
        
        pages = []
        for file_path, analysis in page_analysis.items():
            # URL path olish
            relative_path = os.path.relpath(file_path, self.project_root)
            url_path = "/" + relative_path.replace("\\", "/")
            
            if url_path.endswith("/index.html"):
                url_path = url_path[:-11] or "/"
            
            pages.append({
                "url": url_path,
                "lastmod": datetime.now().strftime("%Y-%m-%d"),
                "changefreq": "weekly",
                "priority": "0.8" if url_path == "/" else "0.6"
            })
        
        # Sitemap yaratish
        sitemap_path = self.seo_dir / "sitemap.xml"
        self.sitemap_generator.generate_sitemap(pages, str(sitemap_path))
        
        logger.info(f"Sitemap yaratildi: {sitemap_path}")

    async def _generate_robots_txt(self):
        """Robots.txt yaratish"""
        logger.info("🤖 Robots.txt yaratilmoqda...")
        
        robots_path = self.project_root / "robots.txt"
        self.sitemap_generator.generate_robots_txt(str(robots_path))
        
        logger.info(f"Robots.txt yaratildi: {robots_path}")

    async def _perform_technical_audit(self, html_files: List[Path]) -> Dict[str, List[TechnicalSEOIssue]]:
        """Texnik SEO audit o'tkazish"""
        logger.info("🔍 Texnik SEO audit o'tkazilmoqda...")
        
        audit_results = {}
        
        for html_file in html_files:
            try:
                async with aiofiles.open(html_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                
                issues = self.technical_auditor.audit_page(content, str(html_file))
                audit_results[str(html_file)] = issues
                
                # Issues sonini log qilish
                error_count = sum(1 for issue in issues if issue.type == "error")
                warning_count = sum(1 for issue in issues if issue.type == "warning")
                
                if error_count > 0 or warning_count > 0:
                    logger.warning(f"Audit natijasi {html_file.name}: {error_count} xato, {warning_count} ogohlantirish")
                
            except Exception as e:
                logger.error(f"Texnik audit xatosi {html_file}: {str(e)}")
        
        return audit_results

    async def _improve_internal_linking(self, page_analysis: Dict[str, PageSEOData]):
        """Ichki linklarni yaxshilash"""
        logger.info("🔗 Ichki linking yaxshilanmoqda...")
        
        # Internal link'larni tahlil qilish
        link_suggestions = {}
        
        for file_path, analysis in page_analysis.items():
            if analysis.seo_score < 70:  # SEO score past bo'lsa
                # Ko'proq internal link qo'shish tavsiya etiladi
                needed_links = max(0, 5 - len(analysis.links_internal))
                
                if needed_links > 0:
                    link_suggestions[file_path] = {
                        "current_links": len(analysis.links_internal),
                        "suggested_links": needed_links,
                        "recommendation": f"Sahifaga {needed_links} ta ko'proq ichki link qo'shing"
                    }
        
        # Link suggestions'ni saqlash
        suggestions_path = self.seo_dir / "internal_linking_suggestions.json"
        with open(suggestions_path, 'w', encoding='utf-8') as f:
            json.dump(link_suggestions, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Ichki linking tavsiyalari saqlandi: {suggestions_path}")

    async def _optimize_images_seo(self, html_files: List[Path]):
        """Rasmlarni SEO uchun optimallash"""
        logger.info("🖼️  Image SEO optimizatsiya...")
        
        image_improvements = []
        
        for html_file in html_files:
            try:
                async with aiofiles.open(html_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                
                soup = BeautifulSoup(content, 'html.parser')
                images = soup.find_all('img')
                
                for img in images:
                    src = img.get('src', '')
                    alt = img.get('alt', '')
                    
                    # Alt text yo'q bo'lsa qo'shish
                    if not alt and src:
                        # Filename'dan alt text yaratish
                        filename = Path(src).stem
                        alt_text = filename.replace('-', ' ').replace('_', ' ').title()
                        img.attrs['alt'] = alt_text
                        image_improvements.append({
                            "file": str(html_file),
                            "image": src,
                            "improvement": "Alt text qo'shildi",
                            "alt_text": alt_text
                        })
                
                # Yangilangan content'ni saqlash
                async with aiofiles.open(html_file, 'w', encoding='utf-8') as f:
                    await f.write(str(soup))
                
            except Exception as e:
                logger.error(f"Image SEO optimizatsiya xatosi {html_file}: {str(e)}")
        
        # Image improvements'ni saqlash
        improvements_path = self.seo_dir / "image_seo_improvements.json"
        with open(improvements_path, 'w', encoding='utf-8') as f:
            json.dump(image_improvements, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Image SEO yaxshilanishlari: {len(image_improvements)} ta")

    async def _optimize_for_mobile(self, html_files: List[Path]):
        """Mobile optimizatsiya"""
        if not self.config.mobile_optimized:
            return
            
        logger.info("📱 Mobile optimizatsiya...")
        
        mobile_improvements = []
        
        for html_file in html_files:
            try:
                async with aiofiles.open(html_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                
                soup = BeautifulSoup(content, 'html.parser')
                head = soup.find('head')
                
                if not head:
                    continue
                
                # Viewport meta tag tekshirish
                viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
                if not viewport_meta:
                    # Qo'shish
                    viewport_meta = soup.new_tag('meta', attrs={
                        'name': 'viewport',
                        'content': 'width=device-width, initial-scale=1.0'
                    })
                    head.insert(0, viewport_meta)
                    mobile_improvements.append({
                        "file": str(html_file),
                        "improvement": "Viewport meta tag qo'shildi"
                    })
                
                # Touch icon links
                apple_touch_icons = head.find_all('link', attrs={'rel': 'apple-touch-icon'})
                if not apple_touch_icons:
                    # Qo'shish
                    apple_touch = soup.new_tag('link', attrs={
                        'rel': 'apple-touch-icon',
                        'href': '/icon-152x152.png'
                    })
                    head.append(apple_touch)
                    mobile_improvements.append({
                        "file": str(html_file),
                        "improvement": "Apple touch icon link qo'shildi"
                    })
                
                # Yangilangan content'ni saqlash
                async with aiofiles.open(html_file, 'w', encoding='utf-8') as f:
                    await f.write(str(soup))
                
            except Exception as e:
                logger.error(f"Mobile optimizatsiya xatosi {html_file}: {str(e)}")
        
        # Mobile improvements'ni saqlash
        improvements_path = self.seo_dir / "mobile_optimization_improvements.json"
        with open(improvements_path, 'w', encoding='utf-8') as f:
            json.dump(mobile_improvements, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Mobile yaxshilanishlar: {len(mobile_improvements)} ta")

    async def _optimize_core_web_vitals(self, html_files: List[Path]):
        """Core Web Vitals optimizatsiya"""
        logger.info("⚡ Core Web Vitals optimizatsiya...")
        
        cwv_improvements = []
        
        for html_file in html_files:
            try:
                async with aiofiles.open(html_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                
                soup = BeautifulSoup(content, 'html.parser')
                head = soup.find('head')
                
                if not head:
                    continue
                
                # Preload critical resources
                critical_css = head.find_all('link', rel='stylesheet')
                if critical_css:
                    # Birinchi CSS file ni preload qilish
                    first_css = critical_css[0].get('href')
                    if first_css:
                        preload_link = soup.new_tag('link', attrs={
                            'rel': 'preload',
                            'href': first_css,
                            'as': 'style',
                            'onload': "this.onload=null;this.rel='stylesheet'"
                        })
                        head.insert(0, preload_link)
                        cwv_improvements.append({
                            "file": str(html_file),
                            "improvement": "Critical CSS preload qo'shildi",
                            "resource": first_css
                        })
                
                # DNS prefetch for external resources
                external_domains = set()
                for link in head.find_all(['link', 'script', 'img'], src=True):
                    src = link.get('src') or link.get('href', '')
                    if src.startswith('http'):
                        domain = urlparse(src).netloc
                        external_domains.add(domain)
                
                # DNS prefetch qo'shish
                for domain in list(external_domains)[:5]:  # Max 5 ta
                    dns_prefetch = soup.new_tag('link', attrs={
                        'rel': 'dns-prefetch',
                        'href': f'//{domain}'
                    })
                    head.insert(0, dns_prefetch)
                
                if external_domains:
                    cwv_improvements.append({
                        "file": str(html_file),
                        "improvement": f"DNS prefetch qo'shildi {len(external_domains)} ta domain uchun"
                    })
                
                # Yangilangan content'ni saqlash
                async with aiofiles.open(html_file, 'w', encoding='utf-8') as f:
                    await f.write(str(soup))
                
            except Exception as e:
                logger.error(f"Core Web Vitals optimizatsiya xatosi {html_file}: {str(e)}")
        
        # CWV improvements'ni saqlash
        improvements_path = self.seo_dir / "core_web_vitals_improvements.json"
        with open(improvements_path, 'w', encoding='utf-8') as f:
            json.dump(cwv_improvements, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Core Web Vitals yaxshilanishlari: {len(cwv_improvements)} ta")

    async def _optimize_local_seo(self):
        """Local SEO optimizatsiya"""
        if not self.config.local_seo:
            return
            
        logger.info("📍 Local SEO optimizatsiya...")
        
        # Local business schema yaratish
        local_business_schema = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": self.config.organization_name,
            "description": self.config.site_description,
            "url": self.config.site_url,
            "telephone": self.config.contact_info.get("telephone", "") if self.config.contact_info else "",
            "address": self.config.organization_address if self.config.organization_address else {},
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": "41.2995",
                "longitude": "69.2401"
            },
            "openingHours": "Mo-Fr 09:00-18:00",
            "priceRange": "$$"
        }
        
        # Schema faylini saqlash
        schema_path = self.seo_dir / "local_business_schema.json"
        with open(schema_path, 'w', encoding='utf-8') as f:
            json.dump(local_business_schema, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Local business schema yaratildi: {schema_path}")

    async def _generate_seo_report(self, page_analysis: Dict[str, PageSEOData], audit_results: Dict[str, List[TechnicalSEOIssue]]):
        """SEO hisoboti yaratish"""
        logger.info("📊 SEO hisoboti yaratilmoqda...")
        
        # Overall statistics
        total_pages = len(page_analysis)
        avg_seo_score = sum(analysis.seo_score for analysis in page_analysis.values()) / total_pages if total_pages else 0
        avg_load_time = sum(analysis.load_time for analysis in page_analysis.values()) / total_pages if total_pages else 0
        avg_mobile_score = sum(analysis.mobile_score for analysis in page_analysis.values()) / total_pages if total_pages else 0
        
        # Issues summary
        total_issues = sum(len(issues) for issues in audit_results.values())
        errors = sum(1 for issues in audit_results.values() for issue in issues if issue.type == "error")
        warnings = sum(1 for issues in audit_results.values() for issue in issues if issue.type == "warning")
        
        # Pages needing improvement
        low_score_pages = [path for path, analysis in page_analysis.items() if analysis.seo_score < 70]
        
        report = {
            "summary": {
                "total_pages": total_pages,
                "average_seo_score": avg_seo_score,
                "average_load_time": avg_load_time,
                "average_mobile_score": avg_mobile_score,
                "total_issues": total_issues,
                "errors": errors,
                "warnings": warnings,
                "pages_needing_improvement": len(low_score_pages)
            },
            "page_analysis": {path: asdict(analysis) for path, analysis in page_analysis.items()},
            "audit_results": {path: [asdict(issue) for issue in issues] for path, issues in audit_results.items()},
            "recommendations": self._generate_seo_recommendations(page_analysis, audit_results),
            "files_created": {
                "sitemap": "/seo_assets/sitemap.xml",
                "robots_txt": "/robots.txt",
                "improvement_suggestions": {
                    "internal_linking": "/seo_assets/internal_linking_suggestions.json",
                    "image_seo": "/seo_assets/image_seo_improvements.json",
                    "mobile_optimization": "/seo_assets/mobile_optimization_improvements.json",
                    "core_web_vitals": "/seo_assets/core_web_vitals_improvements.json"
                }
            }
        }
        
        # Hisobotni saqlash
        report_path = self.seo_dir / "seo_optimization_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"SEO hisoboti saqlandi: {report_path}")

    def _generate_seo_recommendations(self, page_analysis: Dict[str, PageSEOData], audit_results: Dict[str, List[TechnicalSEOIssue]]) -> List[str]:
        """SEO tavsiyalar yaratish"""
        recommendations = []
        
        # Performance recommendations
        avg_load_time = sum(analysis.load_time for analysis in page_analysis.values()) / len(page_analysis)
        if avg_load_time > 3:
            recommendations.append(f"Sahifalar sekin yuklanadi (o'rtacha {avg_load_time:.1f}s). Code minifikatsiya va image optimizatsiya qiling")
        
        # SEO score recommendations
        low_score_pages = len([analysis for analysis in page_analysis.values() if analysis.seo_score < 70])
        if low_score_pages > 0:
            recommendations.append(f"{low_score_pages} ta sahifa SEO score past. Content optimization va meta tag improvements kerak")
        
        # Image optimization
        images_without_alt = sum(
            len([img for img in analysis.images if not img['has_alt']]) 
            for analysis in page_analysis.values()
        )
        if images_without_alt > 0:
            recommendations.append(f"{images_without_alt} ta rasm alt text'siz. Barcha rasmlar uchun alt text qo'shing")
        
        # Internal linking
        pages_with_few_links = len([analysis for analysis in page_analysis.values() if len(analysis.links_internal) < 3])
        if pages_with_few_links > 0:
            recommendations.append(f"{pages_with_few_links} ta sahifada kam ichki link. Internal linking strategy yaxshilang")
        
        # Technical issues
        if any(issue.type == "error" for issues in audit_results.values() for issue in issues):
            recommendations.append("Texnik SEO xatolari mavjud. Code audit va fixes zarur")
        
        # Mobile optimization
        avg_mobile_score = sum(analysis.mobile_score for analysis in page_analysis.values()) / len(page_analysis)
        if avg_mobile_score < 80:
            recommendations.append(f"Mobile performance past (o'rtacha {avg_mobile_score:.1f}). Mobile-first optimizatsiya zarur")
        
        # Local SEO recommendations
        if self.config.local_seo:
            recommendations.append("Local SEO: Google My Business va local citations yarating")
        
        # General recommendations
        recommendations.extend([
            "Content marketing va blog qo'shish organic traffic oshiradi",
            "Site speed monitoring va Core Web Vitals tracking o'rnatish",
            "Regular content updates va freshness signals",
            "User experience (UX) va engagement metrics yaxshilash",
            "Social media integration va sharing buttons"
        ])
        
        return recommendations

    def get_seo_status(self) -> Dict:
        """SEO holatini olish"""
        seo_files = {
            "sitemap": (self.project_root / "sitemap.xml").exists(),
            "robots_txt": (self.project_root / "robots.txt").exists(),
            "seo_directory": self.seo_dir.exists(),
            "structured_data": self.config.schema_enabled,
            "social_tags": self.config.social_sharing
        }
        
        return {
            "seo_files_configured": sum(seo_files.values()),
            "seo_score": sum(seo_files.values()) / len(seo_files) * 100,
            "features_enabled": {
                "sitemap": seo_files["sitemap"],
                "robots_txt": seo_files["robots_txt"],
                "structured_data": seo_files["structured_data"],
                "social_sharing": seo_files["social_tags"]
            }
        }

# CLI interface
async def main():
    """Asosiy funksiya"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SEO Optimizer - Qidiruv tizimi optimizatori")
    parser.add_argument("--project-root", required=True, help="Loyiha ildiz papka")
    parser.add_argument("--site-name", required=True, help="Sayt nomi")
    parser.add_argument("--site-url", required=True, help="Sayt URL")
    parser.add_argument("--site-description", required=True, help="Sayt tavsifi")
    parser.add_argument("--default-keywords", required=True, help="Standart kalit so'zlar")
    parser.add_argument("--author", required=True, help="Muallif")
    parser.add_argument("--language", default="uz", help="Til")
    parser.add_argument("--enable-sitemap", action="store_true", help="Sitemap yoqish")
    parser.add_argument("--enable-schema", action="store_true", help="Structured Data yoqish")
    parser.add_argument("--social-sharing", action="store_true", help="Social sharing yoqish")
    parser.add_argument("--mobile-optimized", action="store_true", help="Mobile optimizatsiya yoqish")
    parser.add_argument("--local-seo", action="store_true", help="Local SEO yoqish")
    parser.add_argument("--output", help="Hisobot fayl yo'li")
    
    args = parser.parse_args()
    
    # SEO config yaratish
    config = SEOConfig(
        site_name=args.site_name,
        site_url=args.site_url,
        site_description=args.site_description,
        default_keywords=args.default_keywords,
        author=args.author,
        language=args.language,
        sitemap_enabled=args.enable_sitemap,
        schema_enabled=args.enable_schema,
        social_sharing=args.social_sharing,
        mobile_optimized=args.mobile_optimized,
        local_seo=args.local_seo
    )
    
    # SEO Optimizer yaratish
    optimizer = SEOOptimizer(args.project_root, config)
    
    # SEO optimizatsiya o'tkazish
    try:
        results = await optimizer.optimize_seo()
        
        # Natijani ko'rsatish
        print("\n🔍 SEO OPTIMIZATSIYASI NATIJASI:")
        print("=" * 50)
        print(f"Sayt nomi: {config.site_name}")
        print(f"Tahlil qilingan sahifalar: {results['pages_analyzed']}")
        print(f"Sitemap: {'✅' if config.sitemap_enabled else '❌'}")
        print(f"Structured Data: {'✅' if config.schema_enabled else '❌'}")
        print(f"Social sharing: {'✅' if config.social_sharing else '❌'}")
        print(f"Mobile optimizatsiya: {'✅' if config.mobile_optimized else '❌'}")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"Hisobot saqlandi: {args.output}")
        
        print("\n🎉 SEO optimizatsiya muvaffaqiyatli tugallandi!")
        print("Keyingi qadamlar:")
        print("1. Google Search Console ga qo'shing")
        print("2. Google Analytics o'rnating")
        print("3. Regular content yarating va yangilang")
        print("4. Backlink strategy ishlab chiqing")
        print("5. Site speed va Core Web Vitals monitoring")
        
    except Exception as e:
        logger.error(f"SEO optimizatsiya xatosi: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    asyncio.run(main())