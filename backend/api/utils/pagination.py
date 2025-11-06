"""
AI Trading System - Pagination Utilities
Sahifalash va filtrlash yordamchi funksiyalar
"""

from typing import List, Any, Dict, Optional, TypeVar, Generic
from math import ceil
from datetime import datetime
from fastapi import Query, HTTPException
from ..models.schemas import PaginationInfo, PaginationParams

T = TypeVar('T')

class PaginatedResponse(Generic[T]):
    """Sahifalangan javob modeli"""
    
    def __init__(self, data: List[T], page: int, size: int, total: int):
        self.data = data
        self.page = page
        self.size = size
        self.total = total
        self.pages = ceil(total / size) if size > 0 else 0
        self.has_next = page < self.pages
        self.has_prev = page > 1
        self.next_page = page + 1 if self.has_next else None
        self.prev_page = page - 1 if self.has_prev else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Response ni dictionary ga o'tkazish"""
        return {
            "data": self.data,
            "pagination": {
                "page": self.page,
                "size": self.size,
                "total": self.total,
                "pages": self.pages,
                "has_next": self.has_next,
                "has_prev": self.has_prev,
                "next_page": self.next_page,
                "prev_page": self.prev_page
            }
        }

def paginate_response(
    data: List[Any],
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
) -> PaginatedResponse[Any]:
    """Ma'lumotlarni sahifalash"""
    return PaginatedResponse(data, page, size, len(data))

def apply_pagination(
    query_result: List[Any],
    page: int = 1,
    size: int = 20
) -> tuple[List[Any], PaginationInfo]:
    """Query natijasiga sahifalash qo'llash"""
    total = len(query_result)
    start = (page - 1) * size
    end = start + size
    paginated_data = query_result[start:end]
    
    pagination = PaginationInfo(
        page=page,
        size=size,
        total=total,
        pages=ceil(total / size) if size > 0 else 0
    )
    
    return paginated_data, pagination

def create_pagination_params(
    page: Optional[int] = Query(1, ge=1),
    size: Optional[int] = Query(20, ge=1, le=100),
    sort_by: Optional[str] = Query(None),
    sort_order: Optional[str] = Query("desc", pattern="^(asc|desc)$"),
    filters: Optional[Dict[str, Any]] = None
) -> PaginationParams:
    """Pagination parametrlarini yaratish"""
    return PaginationParams(
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )

def validate_pagination_params(page: int, size: int, max_size: int = 100):
    """Pagination parametrlarini validatsiya qilish"""
    if page < 1:
        raise HTTPException(status_code=400, detail="Sahifa raqami 1 dan kichik bo'lishi mumkin emas")
    
    if size < 1:
        raise HTTPException(status_code=400, detail="O'lcham 1 dan kichik bo'lishi mumkin emas")
    
    if size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"O'lcham {max_size} dan katta bo'lishi mumkin emas"
        )
    
    return True

def get_pagination_headers(total: int, page: int, size: int) -> Dict[str, str]:
    """Pagination header'larini yaratish"""
    pages = ceil(total / size) if size > 0 else 0
    
    return {
        "X-Total-Count": str(total),
        "X-Total-Pages": str(pages),
        "X-Current-Page": str(page),
        "X-Page-Size": str(size),
        "X-Has-Next": str(page < pages),
        "X-Has-Prev": str(page > 1)
    }

class FilterBuilder:
    """Filtrlash yordamchisi"""
    
    def __init__(self):
        self.filters = {}
        self.sort_params = {}
        self.search_params = {}
    
    def add_filter(self, field: str, operator: str, value: Any):
        """Filtr qo'shish"""
        self.filters[field] = {
            "operator": operator,
            "value": value
        }
        return self
    
    def add_text_search(self, fields: List[str], query: str):
        """Matn qidiruvi qo'shish"""
        self.search_params = {
            "fields": fields,
            "query": query
        }
        return self
    
    def add_sort(self, field: str, order: str = "asc"):
        """Sort qo'shish"""
        self.sort_params = {
            "field": field,
            "order": order
        }
        return self
    
    def build(self) -> Dict[str, Any]:
        """Filter qurilmasini qurish"""
        return {
            "filters": self.filters,
            "sort": self.sort_params,
            "search": self.search_params
        }

class SortingHelper:
    """Saralash yordamchisi"""
    
    @staticmethod
    def sort_data(
        data: List[Any],
        sort_by: Optional[str] = None,
        sort_order: str = "desc"
    ) -> List[Any]:
        """Ma'lumotlarni saralash"""
        if not sort_by or not data:
            return data
        
        try:
            reverse = sort_order.lower() == "desc"
            return sorted(data, key=lambda x: getattr(x, sort_by, ""), reverse=reverse)
        except AttributeError:
            # Fallback for dictionary access
            try:
                return sorted(data, key=lambda x: x.get(sort_by, ""), reverse=reverse)
            except Exception:
                return data
    
    @staticmethod
    def sort_dict_list(
        data: List[Dict[str, Any]],
        sort_by: str,
        sort_order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """Dictionary ro'yxatini saralash"""
        if not data or sort_by not in data[0]:
            return data
        
        reverse = sort_order.lower() == "desc"
        return sorted(data, key=lambda x: x.get(sort_by, ""), reverse=reverse)

class DateRangeFilter:
    """Sana oralig'i filteri"""
    
    def __init__(self, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None):
        self.date_from = date_from
        self.date_to = date_to
    
    def apply(self, data: List[Any], date_field: str = "created_at") -> List[Any]:
        """Filtrni qo'llash"""
        filtered_data = data
        
        if self.date_from:
            filtered_data = [
                item for item in filtered_data
                if getattr(item, date_field, datetime.min) >= self.date_from
            ]
        
        if self.date_to:
            filtered_data = [
                item for item in filtered_data
                if getattr(item, date_field, datetime.min) <= self.date_to
            ]
        
        return filtered_data
    
    def apply_to_dict(self, data: List[Dict[str, Any]], date_field: str = "created_at") -> List[Dict[str, Any]]:
        """Dictionary list uchun filtr"""
        filtered_data = data
        
        if self.date_from:
            filtered_data = [
                item for item in filtered_data
                if item.get(date_field, datetime.min) >= self.date_from
            ]
        
        if self.date_to:
            filtered_data = [
                item for item in filtered_data
                if item.get(date_field, datetime.min) <= self.date_to
            ]
        
        return filtered_data

class SearchHelper:
    """Qidiruv yordamchisi"""
    
    @staticmethod
    def search_text(data: List[Any], query: str, fields: List[str]) -> List[Any]:
        """Matn qidiruvi"""
        if not query or not fields:
            return data
        
        query_lower = query.lower()
        results = []
        
        for item in data:
            for field in fields:
                field_value = getattr(item, field, "")
                if isinstance(field_value, str) and query_lower in field_value.lower():
                    results.append(item)
                    break
                elif hasattr(item, field) and hasattr(getattr(item, field), 'lower'):
                    field_str = str(getattr(item, field))
                    if query_lower in field_str.lower():
                        results.append(item)
                        break
        
        return results
    
    @staticmethod
    def search_dict_list(data: List[Dict[str, Any]], query: str, fields: List[str]) -> List[Dict[str, Any]]:
        """Dictionary list uchun qidiruv"""
        if not query or not fields:
            return data
        
        query_lower = query.lower()
        results = []
        
        for item in data:
            for field in fields:
                field_value = item.get(field, "")
                if isinstance(field_value, str) and query_lower in field_value.lower():
                    results.append(item)
                    break
        
        return results

class AdvancedPagination:
    """Murakkab sahifalash yordamchisi"""
    
    def __init__(
        self,
        data: List[Any],
        page: int = 1,
        size: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "desc"
    ):
        self.original_data = data
        self.page = page
        self.size = size
        self.sort_by = sort_by
        self.sort_order = sort_order
    
    def filter(self, **filters) -> 'AdvancedPagination':
        """Filtrlash"""
        filtered_data = self.original_data
        
        for field, value in filters.items():
            if value is not None:
                filtered_data = [
                    item for item in filtered_data
                    if getattr(item, field, None) == value
                ]
        
        self.original_data = filtered_data
        return self
    
    def search(self, query: str, fields: List[str]) -> 'AdvancedPagination':
        """Qidiruv"""
        if query and fields:
            self.original_data = SearchHelper.search_text(self.original_data, query, fields)
        return self
    
    def sort(self, sort_by: Optional[str] = None, sort_order: str = "desc") -> 'AdvancedPagination':
        """Saralash"""
        if sort_by:
            self.original_data = SortingHelper.sort_data(self.original_data, sort_by, sort_order)
        return self
    
    def paginate(self) -> PaginatedResponse[Any]:
        """Sahifalash"""
        total = len(self.original_data)
        start = (self.page - 1) * self.size
        end = start + self.size
        paginated_data = self.original_data[start:end]
        
        return PaginatedResponse(paginated_data, self.page, self.size, total)
    
    def execute(self) -> Dict[str, Any]:
        """Barcha amallarni bajarish va natijani qaytarish"""
        result = self.paginate()
        return result.to_dict()

def create_cursor_pagination(cursor: Optional[str] = None, size: int = 20) -> Dict[str, Any]:
    """Cursor-based pagination uchun parametrlar"""
    return {
        "cursor": cursor,
        "size": size,
        "has_more": True,  # Will be determined by actual data
        "next_cursor": f"cursor_{cursor}_next" if cursor else None
    }

def parse_pagination_query(
    page: Optional[int] = Query(1, ge=1, description="Sahifa raqami"),
    size: Optional[int] = Query(20, ge=1, le=100, description="Sahifa o'lchami"),
    sort_by: Optional[str] = Query(None, description="Saralash maydoni"),
    sort_order: Optional[str] = Query("desc", pattern="^(asc|desc)$", description="Saralash tartibi"),
    search: Optional[str] = Query(None, description="Qidiruv so'rovi"),
    filters: Optional[str] = Query(None, description="JSON formatda filterlar")
) -> PaginationParams:
    """URL parametrlaridan pagination parametrlarini olish"""
    
    # Parse filters if provided
    parsed_filters = {}
    if filters:
        try:
            import json
            parsed_filters = json.loads(filters)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Filter parametri JSON formatda bo'lishi kerak")
    
    return PaginationParams(
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )

# Export utility functions
__all__ = [
    "PaginatedResponse",
    "paginate_response", 
    "apply_pagination",
    "create_pagination_params",
    "validate_pagination_params",
    "get_pagination_headers",
    "FilterBuilder",
    "SortingHelper", 
    "DateRangeFilter",
    "SearchHelper",
    "AdvancedPagination",
    "create_cursor_pagination",
    "parse_pagination_query"
]