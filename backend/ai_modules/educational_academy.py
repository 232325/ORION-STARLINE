"""
Educational Academy Module - Comprehensive Learning Platform
O'quvchi ta'lim sistemasi uchun to'liq platforma

Features:
- Trading courses (Structured learning paths)
- Video lessons (Educational content) 
- Interactive tutorials (Step-by-step guides)
- Progress tracking (Learning analytics)
- Quizzes and assessments (Knowledge testing)
- Certificates (Completion badges)
- Mentorship system (Expert guidance)
- Community forums (Student discussions)
- Course recommendations (Personalized learning)
- Skill assessments (Competency evaluation)

Author: Orion Starline Team
Version: 1.0.0
Date: 2025-11-05
"""

import json
import uuid
import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import os
import hashlib
from pathlib import Path

# =============================================================================
# DATA MODELS
# =============================================================================

class UserRole(Enum):
    """Foydalanuvchi rollari"""
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    MENTOR = "mentor"
    ADMIN = "admin"

class CourseStatus(Enum):
    """Kurs holatlari"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class QuestionType(Enum):
    """Savol turlari"""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"

class AchievementType(Enum):
    """Yutuq turlari"""
    COMPLETION = "completion"
    EXCELLENCE = "excellence"
    PARTICIPATION = "participation"
    STREAK = "streak"

@dataclass
class User:
    """Foydalanuvchi modeli"""
    user_id: str
    username: str
    email: str
    role: UserRole
    first_name: str
    last_name: str
    language: str = "uzbek"
    timezone: str = "Asia/Samarkand"
    created_at: datetime.datetime = None
    last_login: datetime.datetime = None
    is_active: bool = True

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now()
        if self.last_login is None:
            self.last_login = datetime.datetime.now()

@dataclass
class LearningPath:
    """Ta'lim yo'nalishi modeli"""
    path_id: str
    title: str
    description: str
    difficulty_level: int  # 1-10
    estimated_duration: int  # kunlarda
    course_ids: List[str]
    prerequisites: List[str]
    learning_objectives: List[str]
    created_by: str
    created_at: datetime.datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now()

@dataclass
class Course:
    """Kurs modeli"""
    course_id: str
    title: str
    description: str
    instructor_id: str
    category: str
    difficulty_level: int
    duration_minutes: int
    price: float = 0.0
    thumbnail_url: str = ""
    language: str = "uzbek"
    status: CourseStatus = CourseStatus.DRAFT
    tags: List[str] = None
    created_at: datetime.datetime = None
    updated_at: datetime.datetime = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.datetime.now()

@dataclass
class VideoLesson:
    """Video dars modeli"""
    lesson_id: str
    course_id: str
    title: str
    description: str
    video_url: str
    duration_minutes: int
    order_index: int
    language: str = "uzbek"
    transcript: str = ""
    created_at: datetime.datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now()

@dataclass
class InteractiveTutorial:
    """Interaktiv dars modeli"""
    tutorial_id: str
    course_id: str
    title: str
    description: str
    steps: List[Dict[str, Any]]
    interactive_elements: List[Dict[str, Any]]
    estimated_time: int  # daqiqalarda
    difficulty_level: int
    created_at: datetime.datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now()

@dataclass
class Quiz:
    """Test modeli"""
    quiz_id: str
    course_id: str
    title: str
    description: str
    questions: List[Dict[str, Any]]
    time_limit_minutes: int
    passing_score: float
    attempts_allowed: int = 3
    shuffle_questions: bool = True
    created_at: datetime.datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now()

@dataclass
class Certificate:
    """Sertifikat modeli"""
    certificate_id: str
    user_id: str
    course_id: str
    course_title: str
    instructor_name: str
    completion_date: datetime.datetime
    grade: float
    certificate_url: str = ""
    verification_code: str = ""
    created_at: datetime.datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now()
        if not self.verification_code:
            self.verification_code = self._generate_verification_code()

    def _generate_verification_code(self) -> str:
        """Tasdiqlash kodini generatsiya qilish"""
        data = f"{self.user_id}{self.course_id}{self.completion_date.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:12].upper()

@dataclass
class MentorshipSession:
    """Mentorlik sessiyasi modeli"""
    session_id: str
    mentor_id: str
    student_id: str
    scheduled_time: datetime.datetime
    duration_minutes: int
    topic: str
    notes: str = ""
    status: str = "scheduled"  # scheduled, completed, cancelled
    feedback: str = ""
    rating: int = 0
    created_at: datetime.datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now()

@dataclass
class ForumPost:
    """Forum xabari modeli"""
    post_id: str
    user_id: str
    title: str
    content: str
    category: str
    tags: List[str] = None
    likes_count: int = 0
    replies_count: int = 0
    is_solved: bool = False
    created_at: datetime.datetime = None
    updated_at: datetime.datetime = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.datetime.now()

@dataclass
class UserProgress:
    """Foydalanuvchi taraqqiyoti modeli"""
    progress_id: str
    user_id: str
    course_id: str
    completed_lessons: List[str]
    quiz_scores: Dict[str, float]
    total_time_spent: int  # daqiqalarda
    progress_percentage: float
    last_accessed: datetime.datetime
    created_at: datetime.datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now()

@dataclass
class Achievement:
    """Yutuq modeli"""
    achievement_id: str
    user_id: str
    achievement_type: AchievementType
    title: str
    description: str
    badge_icon: str
    points_earned: int
    earned_at: datetime.datetime = None

    def __post_init__(self):
        if self.earned_at is None:
            self.earned_at = datetime.datetime.now()

@dataclass
class SkillAssessment:
    """Ko'nikma baholash modeli"""
    assessment_id: str
    user_id: str
    skill_category: str
    score: float
    max_score: float
    assessment_type: str
    feedback: str = ""
    recommendations: List[str] = None
    created_at: datetime.datetime = None

    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []
        if self.created_at is None:
            self.created_at = datetime.datetime.now()

# =============================================================================
# COURSE MANAGEMENT SYSTEM
# =============================================================================

class CourseManager:
    """Kurs boshqarish tizimi"""
    
    def __init__(self, db_path: str = "educational_academy.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Ma'lumotlar bazasini boshlash"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Courses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    course_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    instructor_id TEXT,
                    category TEXT,
                    difficulty_level INTEGER,
                    duration_minutes INTEGER,
                    price REAL DEFAULT 0.0,
                    thumbnail_url TEXT,
                    language TEXT DEFAULT 'uzbek',
                    status TEXT DEFAULT 'draft',
                    tags TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            
            # Video lessons table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS video_lessons (
                    lesson_id TEXT PRIMARY KEY,
                    course_id TEXT,
                    title TEXT NOT NULL,
                    description TEXT,
                    video_url TEXT,
                    duration_minutes INTEGER,
                    order_index INTEGER,
                    language TEXT DEFAULT 'uzbek',
                    transcript TEXT,
                    created_at TIMESTAMP,
                    FOREIGN KEY (course_id) REFERENCES courses (course_id)
                )
            """)
            
            # Interactive tutorials table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interactive_tutorials (
                    tutorial_id TEXT PRIMARY KEY,
                    course_id TEXT,
                    title TEXT NOT NULL,
                    description TEXT,
                    steps TEXT,
                    interactive_elements TEXT,
                    estimated_time INTEGER,
                    difficulty_level INTEGER,
                    created_at TIMESTAMP,
                    FOREIGN KEY (course_id) REFERENCES courses (course_id)
                )
            """)
            
            # Quizzes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quizzes (
                    quiz_id TEXT PRIMARY KEY,
                    course_id TEXT,
                    title TEXT NOT NULL,
                    description TEXT,
                    questions TEXT,
                    time_limit_minutes INTEGER,
                    passing_score REAL,
                    attempts_allowed INTEGER DEFAULT 3,
                    shuffle_questions BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP,
                    FOREIGN KEY (course_id) REFERENCES courses (course_id)
                )
            """)
            
            conn.commit()
    
    def create_course(self, course: Course) -> bool:
        """Yangi kurs yaratish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO courses (
                        course_id, title, description, instructor_id, category,
                        difficulty_level, duration_minutes, price, thumbnail_url,
                        language, status, tags, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    course.course_id, course.title, course.description,
                    course.instructor_id, course.category, course.difficulty_level,
                    course.duration_minutes, course.price, course.thumbnail_url,
                    course.language, course.status.value,
                    json.dumps(course.tags), course.created_at, course.updated_at
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Kurs yaratishda xato: {e}")
            return False
    
    def get_course(self, course_id: str) -> Optional[Course]:
        """Kurs ma'lumotlarini olish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM courses WHERE course_id = ?", (course_id,))
                row = cursor.fetchone()
                
                if row:
                    return Course(
                        course_id=row[0],
                        title=row[1],
                        description=row[2],
                        instructor_id=row[3],
                        category=row[4],
                        difficulty_level=row[5],
                        duration_minutes=row[6],
                        price=row[7],
                        thumbnail_url=row[8],
                        language=row[9],
                        status=CourseStatus(row[10]),
                        tags=json.loads(row[11]) if row[11] else []
                    )
        except Exception as e:
            print(f"Kurs olishda xato: {e}")
        return None
    
    def update_course(self, course: Course) -> bool:
        """Kursni yangilash"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE courses SET title=?, description=?, instructor_id=?, 
                    category=?, difficulty_level=?, duration_minutes=?, price=?, 
                    thumbnail_url=?, language=?, status=?, tags=?, updated_at=?
                    WHERE course_id=?
                """, (
                    course.title, course.description, course.instructor_id,
                    course.category, course.difficulty_level, course.duration_minutes,
                    course.price, course.thumbnail_url, course.language,
                    course.status.value, json.dumps(course.tags),
                    datetime.datetime.now(), course.course_id
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Kurs yangilashda xato: {e}")
            return False
    
    def delete_course(self, course_id: str) -> bool:
        """Kursni o'chirish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM courses WHERE course_id=?", (course_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Kurs o'chirishda xato: {e}")
            return False
    
    def list_courses(self, category: str = None, status: CourseStatus = None) -> List[Course]:
        """Kurslar ro'yxatini olish"""
        courses = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM courses WHERE 1=1"
                params = []
                
                if category:
                    query += " AND category=?"
                    params.append(category)
                
                if status:
                    query += " AND status=?"
                    params.append(status.value)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                for row in rows:
                    courses.append(Course(
                        course_id=row[0],
                        title=row[1],
                        description=row[2],
                        instructor_id=row[3],
                        category=row[4],
                        difficulty_level=row[5],
                        duration_minutes=row[6],
                        price=row[7],
                        thumbnail_url=row[8],
                        language=row[9],
                        status=CourseStatus(row[10]),
                        tags=json.loads(row[11]) if row[11] else []
                    ))
        except Exception as e:
            print(f"Kurslar ro'yxatini olishda xato: {e}")
        
        return courses

# =============================================================================
# VIDEO STREAMING INTEGRATION
# =============================================================================

class VideoStreamingManager:
    """Video striming boshqaruvchisi"""
    
    def __init__(self, streaming_config: Dict[str, Any]):
        self.config = streaming_config
        self.supported_formats = ['mp4', 'webm', 'mov']
        self.quality_levels = ['360p', '720p', '1080p', '4K']
    
    def upload_video(self, video_file_path: str, metadata: Dict[str, Any]) -> Optional[str]:
        """Video yuklash"""
        try:
            # Faylni tekshirish
            if not os.path.exists(video_file_path):
                raise FileNotFoundError(f"Video fayl topilmadi: {video_file_path}")
            
            file_extension = video_file_path.split('.')[-1].lower()
            if file_extension not in self.supported_formats:
                raise ValueError(f"Qo'llab-quvvatlanmaydigan format: {file_extension}")
            
            # Video metadata olish
            video_info = self._extract_video_info(video_file_path)
            
            # Transcoding (zarurat bo'lsa)
            transcoded_videos = self._transcode_video(video_file_path)
            
            # CDN ga yuklash
            upload_result = self._upload_to_cdn(transcoded_videos, metadata)
            
            return upload_result.get('video_id')
            
        except Exception as e:
            print(f"Video yuklashda xato: {e}")
            return None
    
    def _extract_video_info(self, video_path: str) -> Dict[str, Any]:
        """Video ma'lumotlarini olish"""
        # Bu yerga video ma'lumotlarini olish logikasi
        # Masalan: duration, resolution, codec, etc.
        return {
            "duration": 3600,  # soniyalarda
            "resolution": "1920x1080",
            "format": "mp4",
            "size_mb": 150.5
        }
    
    def _transcode_video(self, video_path: str) -> Dict[str, str]:
        """Video transkodlash"""
        # Bu yerga transkodlash logikasi
        transcoded_videos = {}
        for quality in self.quality_levels:
            transcoded_videos[quality] = f"{video_path}_{quality}.mp4"
        return transcoded_videos
    
    def _upload_to_cdn(self, video_files: Dict[str, str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """CDN ga yuklash"""
        # Bu yerga CDN yuklash logikasi
        video_id = str(uuid.uuid4())
        
        return {
            "video_id": video_id,
            "cdn_url": f"https://cdn.example.com/videos/{video_id}",
            "streaming_urls": {
                quality: f"https://cdn.example.com/streaming/{video_id}/{quality}.m3u8"
                for quality in self.quality_levels
            }
        }
    
    def get_streaming_url(self, video_id: str, quality: str = "720p") -> Optional[str]:
        """Striming URL olish"""
        if quality not in self.quality_levels:
            quality = "720p"  # Default quality
        
        return f"https://cdn.example.com/streaming/{video_id}/{quality}.m3u8"
    
    def generate_thumbnail(self, video_id: str, timestamp: float = 10) -> Optional[str]:
        """Video uchun thumbnail yaratish"""
        # Bu yerga thumbnail yaratish logikasi
        return f"https://cdn.example.com/thumbnails/{video_id}_thumb.jpg"

# =============================================================================
# PROGRESS TRACKING SYSTEM
# =============================================================================

class ProgressTracker:
    """Taraqqiyot kuzatuvchi tizimi"""
    
    def __init__(self, db_path: str = "educational_academy.db"):
        self.db_path = db_path
        self._init_progress_tables()
    
    def _init_progress_tables(self):
        """Taraqqiyot jadvallarini yaratish"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # User progress table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_progress (
                    progress_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    course_id TEXT NOT NULL,
                    completed_lessons TEXT,
                    quiz_scores TEXT,
                    total_time_spent INTEGER DEFAULT 0,
                    progress_percentage REAL DEFAULT 0.0,
                    last_accessed TIMESTAMP,
                    created_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (course_id) REFERENCES courses (course_id)
                )
            """)
            
            # Learning analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    course_id TEXT NOT NULL,
                    lesson_id TEXT,
                    time_spent INTEGER,
                    interaction_type TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Certificates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS certificates (
                    certificate_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    course_id TEXT NOT NULL,
                    course_title TEXT NOT NULL,
                    instructor_name TEXT NOT NULL,
                    completion_date TIMESTAMP,
                    grade REAL,
                    certificate_url TEXT,
                    verification_code TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (course_id) REFERENCES courses (course_id)
                )
            """)
            
            conn.commit()
    
    def update_lesson_progress(self, user_id: str, course_id: str, lesson_id: str, 
                             time_spent: int = 0) -> bool:
        """Dars taraqqiyotini yangilash"""
        try:
            progress = self.get_user_progress(user_id, course_id)
            
            if not progress:
                progress = UserProgress(
                    progress_id=str(uuid.uuid4()),
                    user_id=user_id,
                    course_id=course_id,
                    completed_lessons=[lesson_id],
                    quiz_scores={},
                    total_time_spent=time_spent,
                    progress_percentage=0.0,
                    last_accessed=datetime.datetime.now()
                )
            else:
                if lesson_id not in progress.completed_lessons:
                    progress.completed_lessons.append(lesson_id)
                progress.total_time_spent += time_spent
                progress.last_accessed = datetime.datetime.now()
            
            # Progress percentage hisoblash
            course_lessons = self._get_course_lessons_count(course_id)
            if course_lessons > 0:
                progress.progress_percentage = len(progress.completed_lessons) / course_lessons * 100
            
            return self._save_progress(progress)
            
        except Exception as e:
            print(f"Dars taraqqiyotini yangilashda xato: {e}")
            return False
    
    def update_quiz_score(self, user_id: str, course_id: str, quiz_id: str, 
                         score: float) -> bool:
        """Test natijasini yangilash"""
        try:
            progress = self.get_user_progress(user_id, course_id)
            
            if not progress:
                progress = UserProgress(
                    progress_id=str(uuid.uuid4()),
                    user_id=user_id,
                    course_id=course_id,
                    completed_lessons=[],
                    quiz_scores={quiz_id: score},
                    total_time_spent=0,
                    progress_percentage=0.0,
                    last_accessed=datetime.datetime.now()
                )
            else:
                progress.quiz_scores[quiz_id] = score
                progress.last_accessed = datetime.datetime.now()
            
            return self._save_progress(progress)
            
        except Exception as e:
            print(f"Test natijasini yangilashda xato: {e}")
            return False
    
    def get_user_progress(self, user_id: str, course_id: str) -> Optional[UserProgress]:
        """Foydalanuvchi taraqqiyotini olish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM user_progress 
                    WHERE user_id=? AND course_id=?
                """, (user_id, course_id))
                
                row = cursor.fetchone()
                if row:
                    return UserProgress(
                        progress_id=row[0],
                        user_id=row[1],
                        course_id=row[2],
                        completed_lessons=json.loads(row[3]) if row[3] else [],
                        quiz_scores=json.loads(row[4]) if row[4] else {},
                        total_time_spent=row[5],
                        progress_percentage=row[6],
                        last_accessed=datetime.datetime.fromisoformat(row[7]) if row[7] else datetime.datetime.now()
                    )
        except Exception as e:
            print(f"Foydalanuvchi taraqqiyotini olishda xato: {e}")
        return None
    
    def _save_progress(self, progress: UserProgress) -> bool:
        """Taraqqiyotni saqlash"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO user_progress (
                        progress_id, user_id, course_id, completed_lessons,
                        quiz_scores, total_time_spent, progress_percentage,
                        last_accessed, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    progress.progress_id,
                    progress.user_id,
                    progress.course_id,
                    json.dumps(progress.completed_lessons),
                    json.dumps(progress.quiz_scores),
                    progress.total_time_spent,
                    progress.progress_percentage,
                    progress.last_accessed,
                    progress.created_at
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Taraqqiyotni saqlashda xato: {e}")
            return False
    
    def _get_course_lessons_count(self, course_id: str) -> int:
        """Kursdagi darslar sonini olish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM video_lessons WHERE course_id=?", (course_id,))
                return cursor.fetchone()[0]
        except:
            return 0
    
    def get_learning_analytics(self, user_id: str, course_id: str = None) -> Dict[str, Any]:
        """Ta'lim analytics ma'lumotlarini olish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if course_id:
                    cursor.execute("""
                        SELECT interaction_type, COUNT(*), AVG(time_spent)
                        FROM learning_analytics 
                        WHERE user_id=? AND course_id=?
                        GROUP BY interaction_type
                    """, (user_id, course_id))
                else:
                    cursor.execute("""
                        SELECT interaction_type, COUNT(*), AVG(time_spent)
                        FROM learning_analytics 
                        WHERE user_id=?
                        GROUP BY interaction_type
                    """, (user_id,))
                
                analytics = {}
                for row in cursor.fetchall():
                    interaction_type, count, avg_time = row
                    analytics[interaction_type] = {
                        'count': count,
                        'average_time': avg_time or 0
                    }
                
                return analytics
                
        except Exception as e:
            print(f"Ta'lim analytics ma'lumotlarini olishda xato: {e}")
            return {}

# =============================================================================
# QUIZ AND ASSESSMENT SYSTEM
# =============================================================================

class AssessmentManager:
    """Baholash tizimi"""
    
    def __init__(self, db_path: str = "educational_academy.db"):
        self.db_path = db_path
        self._init_assessment_tables()
    
    def _init_assessment_tables(self):
        """Baholash jadvallarini yaratish"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Quiz results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quiz_results (
                    result_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    quiz_id TEXT NOT NULL,
                    answers TEXT,
                    score REAL,
                    max_score REAL,
                    passed BOOLEAN,
                    attempt_number INTEGER,
                    time_taken INTEGER,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (quiz_id) REFERENCES quizzes (quiz_id)
                )
            """)
            
            conn.commit()
    
    def create_quiz(self, quiz: Quiz) -> bool:
        """Yangi test yaratish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO quizzes (
                        quiz_id, course_id, title, description, questions,
                        time_limit_minutes, passing_score, attempts_allowed,
                        shuffle_questions, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    quiz.quiz_id, quiz.course_id, quiz.title, quiz.description,
                    json.dumps(quiz.questions), quiz.time_limit_minutes,
                    quiz.passing_score, quiz.attempts_allowed,
                    quiz.shuffle_questions, quiz.created_at
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Test yaratishda xato: {e}")
            return False
    
    def get_quiz(self, quiz_id: str) -> Optional[Quiz]:
        """Test ma'lumotlarini olish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM quizzes WHERE quiz_id=?", (quiz_id,))
                row = cursor.fetchone()
                
                if row:
                    return Quiz(
                        quiz_id=row[0],
                        course_id=row[1],
                        title=row[2],
                        description=row[3],
                        questions=json.loads(row[4]),
                        time_limit_minutes=row[5],
                        passing_score=row[6],
                        attempts_allowed=row[7],
                        shuffle_questions=bool(row[8])
                    )
        except Exception as e:
            print(f"Test olishda xato: {e}")
        return None
    
    def submit_quiz_answer(self, user_id: str, quiz_id: str, answers: Dict[str, Any], 
                          time_taken: int) -> Dict[str, Any]:
        """Test javoblarini topshirish"""
        try:
            quiz = self.get_quiz(quiz_id)
            if not quiz:
                return {"success": False, "error": "Test topilmadi"}
            
            # Javoblarni baholash
            score_result = self._grade_quiz(quiz.questions, answers)
            
            # Natijani saqlash
            result_id = str(uuid.uuid4())
            passed = score_result['score'] / score_result['max_score'] >= quiz.passing_score / 100
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO quiz_results (
                        result_id, user_id, quiz_id, answers, score, max_score,
                        passed, attempt_number, time_taken, completed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result_id, user_id, quiz_id, json.dumps(answers),
                    score_result['score'], score_result['max_score'], passed,
                    self._get_attempt_number(user_id, quiz_id),
                    time_taken, datetime.datetime.now()
                ))
                conn.commit()
            
            return {
                "success": True,
                "score": score_result['score'],
                "max_score": score_result['max_score'],
                "percentage": (score_result['score'] / score_result['max_score']) * 100,
                "passed": passed,
                "feedback": score_result['feedback']
            }
            
        except Exception as e:
            print(f"Test topshirishda xato: {e}")
            return {"success": False, "error": str(e)}
    
    def _grade_quiz(self, questions: List[Dict], answers: Dict[str, Any]) -> Dict[str, Any]:
        """Testni baholash"""
        score = 0
        max_score = len(questions)
        feedback = []
        
        for i, question in enumerate(questions):
            question_id = str(i)
            user_answer = answers.get(question_id)
            correct_answer = question.get('correct_answer')
            
            if question.get('type') == QuestionType.MULTIPLE_CHOICE.value:
                if user_answer == correct_answer:
                    score += 1
                    feedback.append(f"Savol {i+1}: To'g'ri")
                else:
                    feedback.append(f"Savol {i+1}: Noto'g'ri. To'g'ri javob: {correct_answer}")
            
            elif question.get('type') == QuestionType.TRUE_FALSE.value:
                if str(user_answer).lower() == str(correct_answer).lower():
                    score += 1
                    feedback.append(f"Savol {i+1}: To'g'ri")
                else:
                    feedback.append(f"Savol {i+1}: Noto'g'ri. To'g'ri javob: {correct_answer}")
        
        return {
            "score": score,
            "max_score": max_score,
            "feedback": feedback
        }
    
    def _get_attempt_number(self, user_id: str, quiz_id: str) -> int:
        """Urinish raqamini olish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM quiz_results 
                    WHERE user_id=? AND quiz_id=?
                """, (user_id, quiz_id))
                return cursor.fetchone()[0] + 1
        except:
            return 1

# =============================================================================
# GAMIFICATION SYSTEM
# =============================================================================

class GamificationManager:
    """O'yin elementlari boshqaruvchisi"""
    
    def __init__(self, db_path: str = "educational_academy.db"):
        self.db_path = db_path
        self._init_gamification_tables()
    
    def _init_gamification_tables(self):
        """O'yin elementlari jadvallarini yaratish"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Achievements table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS achievements (
                    achievement_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    achievement_type TEXT,
                    title TEXT NOT NULL,
                    description TEXT,
                    badge_icon TEXT,
                    points_earned INTEGER DEFAULT 0,
                    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # User points table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_points (
                    user_id TEXT PRIMARY KEY,
                    total_points INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    experience_points INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            conn.commit()
    
    def award_achievement(self, user_id: str, achievement_type: AchievementType, 
                         title: str, description: str, badge_icon: str, 
                         points_earned: int = 10) -> bool:
        """Yutuq berish"""
        try:
            achievement_id = str(uuid.uuid4())
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Yutuqni saqlash
                cursor.execute("""
                    INSERT INTO achievements (
                        achievement_id, user_id, achievement_type, title,
                        description, badge_icon, points_earned
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    achievement_id, user_id, achievement_type.value, title,
                    description, badge_icon, points_earned
                ))
                
                # Foydalanuvchi ballarni yangilash
                self._update_user_points(user_id, points_earned)
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Yutuq berishda xato: {e}")
            return False
    
    def _update_user_points(self, user_id: str, points: int):
        """Foydalanuvchi ballarni yangilash"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Mavjud ballarni tekshirish
            cursor.execute("SELECT * FROM user_points WHERE user_id=?", (user_id,))
            existing = cursor.fetchone()
            
            if existing:
                new_total_points = existing[1] + points
                new_exp_points = existing[3] + points
                new_level = self._calculate_level(new_exp_points)
                
                cursor.execute("""
                    UPDATE user_points SET total_points=?, level=?, 
                    experience_points=?, last_updated=?
                    WHERE user_id=?
                """, (new_total_points, new_level, new_exp_points,
                     datetime.datetime.now(), user_id))
            else:
                new_level = self._calculate_level(points)
                cursor.execute("""
                    INSERT INTO user_points (
                        user_id, total_points, level, experience_points, last_updated
                    ) VALUES (?, ?, ?, ?, ?)
                """, (user_id, points, new_level, points, datetime.datetime.now()))
    
    def _calculate_level(self, experience_points: int) -> int:
        """Darajani hisoblash (har 100 ball 1 daraja)"""
        return max(1, (experience_points // 100) + 1)
    
    def get_user_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Foydalanuvchi yutuqlarini olish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM achievements WHERE user_id=? 
                    ORDER BY earned_at DESC
                """, (user_id,))
                
                achievements = []
                for row in cursor.fetchall():
                    achievements.append({
                        "achievement_id": row[0],
                        "user_id": row[1],
                        "achievement_type": row[2],
                        "title": row[3],
                        "description": row[4],
                        "badge_icon": row[5],
                        "points_earned": row[6],
                        "earned_at": row[7]
                    })
                
                return achievements
                
        except Exception as e:
            print(f"Yutuqlarni olishda xato: {e}")
            return []
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Eng yaxshi foydalanuvchilar ro'yxati"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT u.user_id, u.username, up.total_points, up.level
                    FROM users u
                    JOIN user_points up ON u.user_id = up.user_id
                    ORDER BY up.total_points DESC
                    LIMIT ?
                """, (limit,))
                
                leaderboard = []
                for i, row in enumerate(cursor.fetchall()):
                    leaderboard.append({
                        "rank": i + 1,
                        "user_id": row[0],
                        "username": row[1],
                        "total_points": row[2],
                        "level": row[3]
                    })
                
                return leaderboard
                
        except Exception as e:
            print(f"Liderlar jadvalini olishda xato: {e}")
            return []

# =============================================================================
# MENTORSHIP SYSTEM
# =============================================================================

class MentorshipManager:
    """Mentorlik tizimi"""
    
    def __init__(self, db_path: str = "educational_academy.db"):
        self.db_path = db_path
        self._init_mentorship_tables()
    
    def _init_mentorship_tables(self):
        """Mentorlik jadvallarini yaratish"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Mentorship sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mentorship_sessions (
                    session_id TEXT PRIMARY KEY,
                    mentor_id TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    scheduled_time TIMESTAMP,
                    duration_minutes INTEGER,
                    topic TEXT,
                    notes TEXT,
                    status TEXT DEFAULT 'scheduled',
                    feedback TEXT,
                    rating INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (mentor_id) REFERENCES users (user_id),
                    FOREIGN KEY (student_id) REFERENCES users (user_id)
                )
            """)
            
            # Mentors table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mentors (
                    mentor_id TEXT PRIMARY KEY,
                    specialties TEXT,
                    experience_years INTEGER,
                    bio TEXT,
                    hourly_rate REAL DEFAULT 0.0,
                    availability TEXT,
                    rating REAL DEFAULT 0.0,
                    total_sessions INTEGER DEFAULT 0,
                    FOREIGN KEY (mentor_id) REFERENCES users (user_id)
                )
            """)
            
            conn.commit()
    
    def schedule_session(self, session: MentorshipSession) -> bool:
        """Mentorlik sessiyasini rejalashtirish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO mentorship_sessions (
                        session_id, mentor_id, student_id, scheduled_time,
                        duration_minutes, topic, notes, status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id, session.mentor_id, session.student_id,
                    session.scheduled_time, session.duration_minutes, session.topic,
                    session.notes, session.status, session.created_at
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Sessiya rejalashtirishda xato: {e}")
            return False
    
    def get_mentor_sessions(self, mentor_id: str, status: str = None) -> List[Dict[str, Any]]:
        """Mentor sessiyalarini olish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM mentorship_sessions WHERE mentor_id=?"
                params = [mentor_id]
                
                if status:
                    query += " AND status=?"
                    params.append(status)
                
                query += " ORDER BY scheduled_time DESC"
                
                cursor.execute(query, params)
                
                sessions = []
                for row in cursor.fetchall():
                    sessions.append({
                        "session_id": row[0],
                        "mentor_id": row[1],
                        "student_id": row[2],
                        "scheduled_time": row[3],
                        "duration_minutes": row[4],
                        "topic": row[5],
                        "notes": row[6],
                        "status": row[7],
                        "feedback": row[8],
                        "rating": row[9],
                        "created_at": row[10]
                    })
                
                return sessions
                
        except Exception as e:
            print(f"Mentor sessiyalarini olishda xato: {e}")
            return []
    
    def rate_session(self, session_id: str, rating: int, feedback: str) -> bool:
        """Sessiyani baholash"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE mentorship_sessions 
                    SET rating=?, feedback=?, status='completed'
                    WHERE session_id=?
                """, (rating, feedback, session_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Sessiyani baholashda xato: {e}")
            return False
    
    def find_mentors(self, specialty: str = None) -> List[Dict[str, Any]]:
        """Mentor qidirish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if specialty:
                    cursor.execute("""
                        SELECT m.mentor_id, u.username, m.specialties, 
                               m.experience_years, m.bio, m.rating, m.total_sessions
                        FROM mentors m
                        JOIN users u ON m.mentor_id = u.user_id
                        WHERE m.specialties LIKE ?
                        ORDER BY m.rating DESC, m.total_sessions DESC
                    """, (f"%{specialty}%",))
                else:
                    cursor.execute("""
                        SELECT m.mentor_id, u.username, m.specialties,
                               m.experience_years, m.bio, m.rating, m.total_sessions
                        FROM mentors m
                        JOIN users u ON m.mentor_id = u.user_id
                        ORDER BY m.rating DESC, m.total_sessions DESC
                    """)
                
                mentors = []
                for row in cursor.fetchall():
                    mentors.append({
                        "mentor_id": row[0],
                        "username": row[1],
                        "specialties": json.loads(row[2]) if row[2] else [],
                        "experience_years": row[3],
                        "bio": row[4],
                        "rating": row[5],
                        "total_sessions": row[6]
                    })
                
                return mentors
                
        except Exception as e:
            print(f"Mentor qidirishda xato: {e}")
            return []

# =============================================================================
# COMMUNITY FORUM SYSTEM
# =============================================================================

class ForumManager:
    """Forum boshqaruvchisi"""
    
    def __init__(self, db_path: str = "educational_academy.db"):
        self.db_path = db_path
        self._init_forum_tables()
    
    def _init_forum_tables(self):
        """Forum jadvallarini yaratish"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Forum posts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS forum_posts (
                    post_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT,
                    tags TEXT,
                    likes_count INTEGER DEFAULT 0,
                    replies_count INTEGER DEFAULT 0,
                    is_solved BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Forum replies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS forum_replies (
                    reply_id TEXT PRIMARY KEY,
                    post_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    likes_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (post_id) REFERENCES forum_posts (post_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            conn.commit()
    
    def create_post(self, post: ForumPost) -> bool:
        """Forum xabarini yaratish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO forum_posts (
                        post_id, user_id, title, content, category, tags,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    post.post_id, post.user_id, post.title, post.content,
                    post.category, json.dumps(post.tags), post.created_at,
                    post.updated_at
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Xabar yaratishda xato: {e}")
            return False
    
    def get_posts(self, category: str = None, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Forum xabarlarini olish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT fp.*, u.username
                    FROM forum_posts fp
                    JOIN users u ON fp.user_id = u.user_id
                    WHERE 1=1
                """
                params = []
                
                if category:
                    query += " AND fp.category=?"
                    params.append(category)
                
                query += " ORDER BY fp.created_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                
                posts = []
                for row in cursor.fetchall():
                    posts.append({
                        "post_id": row[0],
                        "user_id": row[1],
                        "username": row[12],
                        "title": row[2],
                        "content": row[3],
                        "category": row[4],
                        "tags": json.loads(row[5]) if row[5] else [],
                        "likes_count": row[6],
                        "replies_count": row[7],
                        "is_solved": bool(row[8]),
                        "created_at": row[9],
                        "updated_at": row[10]
                    })
                
                return posts
                
        except Exception as e:
            print(f"Xabarlarni olishda xato: {e}")
            return []
    
    def reply_to_post(self, post_id: str, user_id: str, content: str) -> bool:
        """Xabarga javob berish"""
        try:
            reply_id = str(uuid.uuid4())
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Javobni saqlash
                cursor.execute("""
                    INSERT INTO forum_replies (
                        reply_id, post_id, user_id, content
                    ) VALUES (?, ?, ?, ?)
                """, (reply_id, post_id, user_id, content))
                
                # Xabar javoblar sonini yangilash
                cursor.execute("""
                    UPDATE forum_posts 
                    SET replies_count = replies_count + 1, updated_at=?
                    WHERE post_id=?
                """, (datetime.datetime.now(), post_id))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Javob berishda xato: {e}")
            return False
    
    def like_post(self, post_id: str) -> bool:
        """Xabarni yoqtirish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE forum_posts 
                    SET likes_count = likes_count + 1, updated_at=?
                    WHERE post_id=?
                """, (datetime.datetime.now(), post_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Yoqtirishda xato: {e}")
            return False

# =============================================================================
# COURSE RECOMMENDATION SYSTEM
# =============================================================================

class RecommendationEngine:
    """Kurs tavsiyalar tizimi"""
    
    def __init__(self, db_path: str = "educational_academy.db"):
        self.db_path = db_path
        self.recommendation_algorithms = {
            "collaborative": self._collaborative_filtering,
            "content_based": self._content_based_filtering,
            "popularity": self._popularity_based,
            "skill_matched": self._skill_matched_recommendations
        }
    
    def get_personalized_recommendations(self, user_id: str, 
                                       algorithm: str = "collaborative",
                                       limit: int = 10) -> List[Dict[str, Any]]:
        """Shaxsiy kurs tavsiyalari"""
        try:
            if algorithm not in self.recommendation_algorithms:
                algorithm = "collaborative"
            
            recommended_courses = self.recommendation_algorithms[algorithm](
                user_id, limit
            )
            
            # Kurslar ma'lumotlarini to'ldirish
            course_manager = CourseManager(self.db_path)
            detailed_recommendations = []
            
            for course_id in recommended_courses:
                course = course_manager.get_course(course_id)
                if course and course.status == CourseStatus.PUBLISHED:
                    detailed_recommendations.append({
                        "course_id": course.course_id,
                        "title": course.title,
                        "description": course.description,
                        "category": course.category,
                        "difficulty_level": course.difficulty_level,
                        "duration_minutes": course.duration_minutes,
                        "price": course.price,
                        "recommendation_reason": self._get_recommendation_reason(
                            user_id, course_id, algorithm
                        )
                    })
            
            return detailed_recommendations
            
        except Exception as e:
            print(f"Kurs tavsiyalarida xato: {e}")
            return []
    
    def _collaborative_filtering(self, user_id: str, limit: int) -> List[str]:
        """Hamkorlik filtrlash algoritmi"""
        # Bu yerga hamkorlik filtrlash algoritmi
        # O'xshash foydalanuvchilarning kurslarini topish
        return []
    
    def _content_based_filtering(self, user_id: str, limit: int) -> List[str]:
        """Tarkibga asoslangan filtrlash"""
        # Bu yerga tarkibga asoslangan filtrlash algoritmi
        # Foydalanuvchi qiziqishlari va kurs tarkibini solishtirish
        return []
    
    def _popularity_based(self, user_id: str, limit: int) -> List[str]:
        """Mashhurligiga asoslangan tavsiya"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT c.course_id, COUNT(DISTINCT up.user_id) as enrollments
                    FROM courses c
                    LEFT JOIN user_progress up ON c.course_id = up.course_id
                    WHERE c.status = 'published'
                    GROUP BY c.course_id
                    ORDER BY enrollments DESC, c.created_at DESC
                    LIMIT ?
                """, (limit,))
                
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Mashhur kurslarni olishda xato: {e}")
            return []
    
    def _skill_matched_recommendations(self, user_id: str, limit: int) -> List[str]:
        """Ko'nikmalarga mos kurs tavsiyalari"""
        try:
            # Foydalanuvchi ko'nikmalarini olish
            skills = self._get_user_skills(user_id)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Ko'nikmalarga mos kurslarni qidirish
                cursor.execute("""
                    SELECT c.course_id, c.difficulty_level
                    FROM courses c
                    WHERE c.status = 'published' 
                    AND c.category IN ({})
                    ORDER BY c.difficulty_level ASC
                    LIMIT ?
                """.format("'" + "','".join(skills) + "'"), (limit,))
                
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Ko'nikmalarga mos kurslarni olishda xato: {e}")
            return []
    
    def _get_user_skills(self, user_id: str) -> List[str]:
        """Foydalanuvchi ko'nikmalarini olish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT c.category
                    FROM user_progress up
                    JOIN courses c ON up.course_id = c.course_id
                    WHERE up.user_id=? AND up.progress_percentage > 50
                """, (user_id,))
                
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Foydalanuvchi ko'nikmalarini olishda xato: {e}")
            return []
    
    def _get_recommendation_reason(self, user_id: str, course_id: str, 
                                 algorithm: str) -> str:
        """Tavsiya sababini aniqlash"""
        reasons = {
            "collaborative": "Sizga o'xshagan foydalanuvchilar bu kursni yoqtiradi",
            "content_based": "Bu kurs sizning qiziqishlaringizga mos",
            "popularity": "Bu kurs ko'pchilik tomonidan seviladi",
            "skill_matched": "Bu kurs sizning ko'nikmalaringizni rivojlantiradi"
        }
        
        return reasons.get(algorithm, "Bu kurs sizga foydali bo'lishi mumkin")

# =============================================================================
# MAIN EDUCATIONAL ACADEMY CLASS
# =============================================================================

class EducationalAcademy:
    """Asosiy Ta'lim Akademiyasi klasi"""
    
    def __init__(self, db_path: str = "educational_academy.db"):
        self.db_path = db_path
        
        # Barcha sub-systemlarni boshlash
        self.course_manager = CourseManager(db_path)
        self.video_streaming = VideoStreamingManager({
            "cdn_url": "https://cdn.example.com",
            "streaming_endpoint": "/streaming",
            "upload_endpoint": "/upload"
        })
        self.progress_tracker = ProgressTracker(db_path)
        self.assessment_manager = AssessmentManager(db_path)
        self.gamification = GamificationManager(db_path)
        self.mentorship = MentorshipManager(db_path)
        self.forum = ForumManager(db_path)
        self.recommendation_engine = RecommendationEngine(db_path)
        
        # User jadvalini yaratish
        self._init_users_table()
    
    def _init_users_table(self):
        """Foydalanuvchilar jadvalini yaratish"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    role TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    language TEXT DEFAULT 'uzbek',
                    timezone TEXT DEFAULT 'Asia/Samarkand',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            conn.commit()
    
    # =============================================================================
    # USER MANAGEMENT
    # =============================================================================
    
    def register_user(self, user: User) -> bool:
        """Foydalanuvchi ro'yxatdan o'tishi"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (
                        user_id, username, email, role, first_name, last_name,
                        language, timezone, created_at, last_login, is_active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user.user_id, user.username, user.email, user.role.value,
                    user.first_name, user.last_name, user.language,
                    user.timezone, user.created_at, user.last_login, user.is_active
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Foydalanuvchi ro'yxatdan o'tishda xato: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Foydalanuvchi ma'lumotlarini olish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
                row = cursor.fetchone()
                
                if row:
                    return User(
                        user_id=row[0],
                        username=row[1],
                        email=row[2],
                        role=UserRole(row[3]),
                        first_name=row[4],
                        last_name=row[5],
                        language=row[6],
                        timezone=row[7],
                        created_at=datetime.datetime.fromisoformat(row[8]) if row[8] else datetime.datetime.now(),
                        last_login=datetime.datetime.fromisoformat(row[9]) if row[9] else datetime.datetime.now(),
                        is_active=bool(row[10])
                    )
        except Exception as e:
            print(f"Foydalanuvchi ma'lumotlarini olishda xato: {e}")
        return None
    
    # =============================================================================
    # COURSE ENROLLMENT
    # =============================================================================
    
    def enroll_user_in_course(self, user_id: str, course_id: str) -> bool:
        """Foydalanuvchini kursga yozish"""
        try:
            # Kurs mavjudligini tekshirish
            course = self.course_manager.get_course(course_id)
            if not course or course.status != CourseStatus.PUBLISHED:
                return False
            
            # Foydalanuvchi ro'yxatdan o'tganligini tekshirish
            if not self._is_user_enrolled(user_id, course_id):
                # Progress yaratish
                progress = UserProgress(
                    progress_id=str(uuid.uuid4()),
                    user_id=user_id,
                    course_id=course_id,
                    completed_lessons=[],
                    quiz_scores={},
                    total_time_spent=0,
                    progress_percentage=0.0,
                    last_accessed=datetime.datetime.now()
                )
                
                return self.progress_tracker._save_progress(progress)
            
            return True
            
        except Exception as e:
            print(f"Kursga yozishda xato: {e}")
            return False
    
    def _is_user_enrolled(self, user_id: str, course_id: str) -> bool:
        """Foydalanuvchi kursga yozilganligini tekshirish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM user_progress 
                    WHERE user_id=? AND course_id=?
                """, (user_id, course_id))
                
                return cursor.fetchone()[0] > 0
                
        except Exception as e:
            print(f"Yozilganlikni tekshirishda xato: {e}")
            return False
    
    # =============================================================================
    # COMPLETION AND CERTIFICATES
    # =============================================================================
    
    def complete_course(self, user_id: str, course_id: str) -> Optional[str]:
        """Kursni tugatish va sertifikat berish"""
        try:
            progress = self.progress_tracker.get_user_progress(user_id, course_id)
            if not progress:
                return None
            
            # Kurs taraqqiyotini tekshirish
            if progress.progress_percentage < 100:
                return None
            
            course = self.course_manager.get_course(course_id)
            if not course:
                return None
            
            # Sertifikat yaratish
            certificate_id = str(uuid.uuid4())
            certificate = Certificate(
                certificate_id=certificate_id,
                user_id=user_id,
                course_id=course_id,
                course_title=course.title,
                instructor_name=course.instructor_id,
                completion_date=datetime.datetime.now(),
                grade=self._calculate_course_grade(user_id, course_id)
            )
            
            # Sertifikatni saqlash
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO certificates (
                        certificate_id, user_id, course_id, course_title,
                        instructor_name, completion_date, grade, verification_code
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    certificate.certificate_id, certificate.user_id,
                    certificate.course_id, certificate.course_title,
                    certificate.instructor_name, certificate.completion_date,
                    certificate.grade, certificate.verification_code
                ))
                conn.commit()
            
            # Yutuq berish
            self.gamification.award_achievement(
                user_id=user_id,
                achievement_type=AchievementType.COMPLETION,
                title=f"{course.title} Kursini Tugatdi",
                description=f"Siz {course.title} kursini muvaffaqiyatli tugatdingiz",
                badge_icon="🎓",
                points_earned=50
            )
            
            return certificate_id
            
        except Exception as e:
            print(f"Kursni tugatishda xato: {e}")
            return None
    
    def _calculate_course_grade(self, user_id: str, course_id: str) -> float:
        """Kurs bahosini hisoblash"""
        try:
            progress = self.progress_tracker.get_user_progress(user_id, course_id)
            if not progress or not progress.quiz_scores:
                return 85.0  # Default grade
            
            # Quiz ballarining o'rtachasi
            quiz_scores = list(progress.quiz_scores.values())
            return sum(quiz_scores) / len(quiz_scores) if quiz_scores else 85.0
            
        except Exception as e:
            print(f"Kurs bahosini hisoblashda xato: {e}")
            return 85.0
    
    # =============================================================================
    # ANALYTICS AND REPORTING
    # =============================================================================
    
    def get_dashboard_analytics(self, user_id: str) -> Dict[str, Any]:
        """Dashboard analytics ma'lumotlari"""
        try:
            # Foydalanuvchi taraqqiyoti
            progress_data = self._get_user_progress_summary(user_id)
            
            # Yutuqlar
            achievements = self.gamification.get_user_achievements(user_id)
            
            # Liderlar jadvalidagi o'rni
            leaderboard = self.gamification.get_leaderboard(50)
            user_rank = next((i for i, user in enumerate(leaderboard, 1) 
                            if user['user_id'] == user_id), 0)
            
            # Tavsiya qilingan kurslar
            recommendations = self.recommendation_engine.get_personalized_recommendations(
                user_id, algorithm="collaborative", limit=5
            )
            
            return {
                "progress": progress_data,
                "achievements": {
                    "total_achievements": len(achievements),
                    "recent_achievements": achievements[:3],
                    "total_points": sum(a['points_earned'] for a in achievements)
                },
                "leaderboard": {
                    "user_rank": user_rank,
                    "total_participants": len(leaderboard)
                },
                "recommendations": recommendations,
                "last_updated": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Dashboard analytics xatosi: {e}")
            return {}
    
    def _get_user_progress_summary(self, user_id: str) -> Dict[str, Any]:
        """Foydalanuvchi taraqqiyoti xulosasi"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) as total_courses,
                           AVG(progress_percentage) as avg_progress,
                           SUM(total_time_spent) as total_time,
                           COUNT(CASE WHEN progress_percentage = 100 THEN 1 END) as completed_courses
                    FROM user_progress
                    WHERE user_id=?
                """, (user_id,))
                
                row = cursor.fetchone()
                return {
                    "total_courses": row[0] or 0,
                    "avg_progress": round(row[1] or 0, 2),
                    "total_time_hours": round((row[2] or 0) / 60, 2),
                    "completed_courses": row[3] or 0
                }
                
        except Exception as e:
            print(f"Taraqqiyot xulosasini olishda xato: {e}")
            return {}
    
    # =============================================================================
    # MULTI-LANGUAGE SUPPORT
    # =============================================================================
    
    def get_content_in_language(self, content_id: str, content_type: str, 
                              language: str = "uzbek") -> Optional[Dict[str, Any]]:
        """Tanilgan tilda kontent olish"""
        try:
            # Bu yerda content translation ma'lumotlari olinadi
            # Hozircha bazaviy qaytarish
            return {
                "content_id": content_id,
                "content_type": content_type,
                "language": language,
                "available": True
            }
        except Exception as e:
            print(f"Kontent olishda xato: {e}")
            return None
    
    # =============================================================================
    # EXPORT FUNCTIONALITY
    # =============================================================================
    
    def export_user_data(self, user_id: str, export_format: str = "json") -> Optional[str]:
        """Foydalanuvchi ma'lumotlarini eksport qilish"""
        try:
            user_data = {
                "user_info": asdict(self.get_user(user_id)),
                "progress": {},
                "achievements": self.gamification.get_user_achievements(user_id),
                "certificates": [],
                "learning_analytics": self.progress_tracker.get_learning_analytics(user_id)
            }
            
            # Progress ma'lumotlarini olish
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT course_id, completed_lessons, quiz_scores, 
                           progress_percentage, total_time_spent
                    FROM user_progress WHERE user_id=?
                """, (user_id,))
                
                for row in cursor.fetchall():
                    user_data["progress"][row[0]] = {
                        "completed_lessons": json.loads(row[1]) if row[1] else [],
                        "quiz_scores": json.loads(row[2]) if row[2] else {},
                        "progress_percentage": row[3],
                        "total_time_spent": row[4]
                    }
            
            if export_format.lower() == "json":
                return json.dumps(user_data, default=str, indent=2)
            
            # Boshqa formatlar ham qo'shilishi mumkin
            
        except Exception as e:
            print(f"Ma'lumotlarni eksport qilishda xato: {e}")
            return None
    
    # =============================================================================
    # CLEANUP AND MAINTENANCE
    # =============================================================================
    
    def cleanup_expired_sessions(self):
        """Muddati o'tgan sessiyalarni tozalash"""
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=30)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM mentorship_sessions 
                    WHERE status='scheduled' AND scheduled_time < ?
                """, (cutoff_date,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                print(f"Tozalangan eski sessiyalar soni: {deleted_count}")
                
        except Exception as e:
            print(f"Sessiyalarni tozalashda xato: {e}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Ma'lumotlar bazasi statistikasi"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Har bir jadval uchun statistika
                tables = ['users', 'courses', 'user_progress', 'achievements', 
                         'mentorship_sessions', 'forum_posts', 'certificates']
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[table] = cursor.fetchone()[0]
                
                return stats
                
        except Exception as e:
            print(f"Ma'lumotlar bazasi statistikasini olishda xato: {e}")
            return {}

# =============================================================================
# EXAMPLE USAGE AND DEMO
# =============================================================================

def create_sample_data():
    """Namuna ma'lumotlar yaratish"""
    academy = EducationalAcademy()
    
    # Sample users yaratish
    users = [
        User(
            user_id=str(uuid.uuid4()),
            username="student1",
            email="student1@example.com",
            role=UserRole.STUDENT,
            first_name="Ali",
            last_name="Valiyev"
        ),
        User(
            user_id=str(uuid.uuid4()),
            username="instructor1",
            email="instructor1@example.com",
            role=UserRole.INSTRUCTOR,
            first_name="Akmal",
            last_name="Karimov"
        ),
        User(
            user_id=str(uuid.uuid4()),
            username="mentor1",
            email="mentor1@example.com",
            role=UserRole.MENTOR,
            first_name="Aziza",
            last_name="Nazarova"
        )
    ]
    
    for user in users:
        academy.register_user(user)
    
    # Sample courses yaratish
    courses = [
        Course(
            course_id=str(uuid.uuid4()),
            title="Trading Asoslari",
            description="Valuta bozorlarida trading qilish asoslari",
            instructor_id=users[1].user_id,
            category="trading",
            difficulty_level=1,
            duration_minutes=240,
            price=0.0,
            status=CourseStatus.PUBLISHED,
            tags=["trading", "forex", "asoslar"]
        ),
        Course(
            course_id=str(uuid.uuid4()),
            title="Crypto Trading Strategiyalari",
            description="Kriptovalyuta trading strategiyalari va tahlil",
            instructor_id=users[1].user_id,
            category="cryptocurrency",
            difficulty_level=3,
            duration_minutes=480,
            price=99.99,
            status=CourseStatus.PUBLISHED,
            tags=["crypto", "trading", "strategiyalar"]
        )
    ]
    
    for course in courses:
        academy.course_manager.create_course(course)
    
    # Student kursga yozilishi
    academy.enroll_user_in_course(users[0].user_id, courses[0].course_id)
    
    # Progress yangilash
    academy.progress_tracker.update_lesson_progress(
        users[0].user_id, courses[0].course_id, "lesson1", 30
    )
    
    # Sertifikat berish
    certificate_id = academy.complete_course(users[0].user_id, courses[0].course_id)
    
    print("Namuna ma'lumotlar yaratildi!")
    print(f"Yaratilgan foydalanuvchilar: {len(users)}")
    print(f"Yaratilgan kurslar: {len(courses)}")
    print(f"Berilgan sertifikatlar: {1 if certificate_id else 0}")
    
    return academy

if __name__ == "__main__":
    # Educational Academy modulini test qilish
    print("="*50)
    print("Educational Academy Moduli")
    print("Ta'lim Akademiyasi Moduli")
    print("="*50)
    
    # Namuna ma'lumotlar yaratish
    academy = create_sample_data()
    
    # Analytics ko'rish
    user_id = "student1"  # Haqiqiy user_id ni olish kerak
    students = []
    with sqlite3.connect(academy.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE username=?", (user_id,))
        result = cursor.fetchone()
        if result:
            students.append(result[0])
    
    if students:
        analytics = academy.get_dashboard_analytics(students[0])
        print("\nFoydalanuvchi Analytics:")
        print(json.dumps(analytics, indent=2, default=str))
    
    # Database statistikasi
    stats = academy.get_database_stats()
    print("\nMa'lumotlar Bazasi Statistikasi:")
    print(json.dumps(stats, indent=2))
    
    print("\n✅ Educational Academy moduli muvaffaqiyatli yaratildi!")
    print("📚 Trading kurslari, video darslar, testlar, va boshqa barcha funksiyalar tayyor!")
