import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import BlogPost, BlogPostUpdate

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PostOut(BaseModel):
    id: str
    title: str
    subtitle: Optional[str] = None
    content: str
    author: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    cover_image: Optional[str] = None
    status: str
    published_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


def serialize_post(doc) -> PostOut:
    return PostOut(
        id=str(doc.get("_id")),
        title=doc.get("title"),
        subtitle=doc.get("subtitle"),
        content=doc.get("content"),
        author=doc.get("author"),
        category=doc.get("category"),
        tags=doc.get("tags"),
        cover_image=str(doc.get("cover_image")) if doc.get("cover_image") else None,
        status=doc.get("status", "published"),
        published_at=(doc.get("published_at").isoformat() if doc.get("published_at") else None),
        created_at=(doc.get("created_at").isoformat() if doc.get("created_at") else None),
        updated_at=(doc.get("updated_at").isoformat() if doc.get("updated_at") else None),
    )


@app.get("/")
def read_root():
    return {"message": "News API running"}


@app.get("/api/posts", response_model=List[PostOut])
def list_posts(status: Optional[str] = None, limit: int = 20):
    filt = {}
    if status:
        filt["status"] = status
    docs = db["blogpost"].find(filt).sort("published_at", -1).limit(limit)
    return [serialize_post(d) for d in docs]


@app.post("/api/posts", response_model=PostOut)
def create_post(post: BlogPost):
    inserted_id = create_document("blogpost", post)
    doc = db["blogpost"].find_one({"_id": ObjectId(inserted_id)})
    return serialize_post(doc)


@app.get("/api/posts/{post_id}", response_model=PostOut)
def get_post(post_id: str):
    try:
        oid = ObjectId(post_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")
    doc = db["blogpost"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return serialize_post(doc)


@app.put("/api/posts/{post_id}", response_model=PostOut)
def update_post(post_id: str, patch: BlogPostUpdate):
    try:
        oid = ObjectId(post_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")
    update_data = {k: v for k, v in patch.model_dump(exclude_unset=True).items()}
    if not update_data:
        raise HTTPException(status_code=400, detail="No changes provided")
    update_data["updated_at"] = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    res = db["blogpost"].update_one({"_id": oid}, {"$set": update_data})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    doc = db["blogpost"].find_one({"_id": oid})
    return serialize_post(doc)


@app.delete("/api/posts/{post_id}")
def delete_post(post_id: str):
    try:
        oid = ObjectId(post_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")
    res = db["blogpost"].delete_one({"_id": oid})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            response["collections"] = db.list_collection_names()
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
