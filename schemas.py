"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- BlogPost -> "blogpost" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime

class BlogPost(BaseModel):
    """
    Blog posts/news articles
    Collection name: "blogpost"
    """
    title: str = Field(..., min_length=3, max_length=200)
    subtitle: Optional[str] = Field(None, max_length=300)
    content: str = Field(..., min_length=10)
    author: Optional[str] = Field(None, max_length=120)
    category: Optional[str] = Field(None, max_length=60)
    tags: Optional[List[str]] = None
    cover_image: Optional[HttpUrl] = None
    status: str = Field("published", pattern="^(draft|published)$")
    published_at: Optional[datetime] = None

class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    cover_image: Optional[HttpUrl] = None
    status: Optional[str] = Field(None, pattern="^(draft|published)$")
    published_at: Optional[datetime] = None
