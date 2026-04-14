from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db import get_session
from uuid import UUID
from models import User
from models.blog import BlogPost
from schemas.blog import BlogCreateSchema, BlogUpdateSchema, BlogResponseSchema, BlogPublicSchema
from utils.security import get_current_user
from typing import List

router = APIRouter(prefix="/blog", tags=["Blog"])


@router.get("/public/", response_model=List[BlogPublicSchema], status_code=status.HTTP_200_OK)
def get_published_blogs(db: Session = Depends(get_session)):
    rows = (
        db.query(BlogPost, User)
        .join(User, BlogPost.author_id == User.id)
        .filter(BlogPost.is_published == True)
        .order_by(BlogPost.created_at.desc())
        .all()
    )
    result = []
    for post, user in rows:
        author_name = " ".join(filter(None, [user.first_name, user.last_name])) or user.username
        result.append(
            BlogPublicSchema(
                id=post.id,
                title=post.title,
                content=post.content,
                excerpt=post.excerpt,
                author_name=author_name,
                created_at=post.created_at,
                updated_at=post.updated_at,
            )
        )
    return result


@router.get("/public/{blog_id}", response_model=BlogPublicSchema, status_code=status.HTTP_200_OK)
def get_published_blog(blog_id: UUID, db: Session = Depends(get_session)):
    row = (
        db.query(BlogPost, User)
        .join(User, BlogPost.author_id == User.id)
        .filter(BlogPost.id == blog_id, BlogPost.is_published == True)
        .first()
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found.")
    post, user = row
    author_name = " ".join(filter(None, [user.first_name, user.last_name])) or user.username
    return BlogPublicSchema(
        id=post.id,
        title=post.title,
        content=post.content,
        excerpt=post.excerpt,
        author_name=author_name,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


@router.post("/", response_model=BlogResponseSchema, status_code=status.HTTP_201_CREATED)
def create_blog(
    blog_data: BlogCreateSchema,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    new_post = BlogPost(
        author_id=current_user.id,
        title=blog_data.title,
        content=blog_data.content,
        excerpt=blog_data.excerpt,
        is_published=blog_data.is_published,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/", response_model=List[BlogResponseSchema], status_code=status.HTTP_200_OK)
def get_my_blogs(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    posts = (
        db.query(BlogPost)
        .filter(BlogPost.author_id == current_user.id)
        .order_by(BlogPost.updated_at.desc())
        .all()
    )
    return posts


@router.get("/{blog_id}", response_model=BlogResponseSchema, status_code=status.HTTP_200_OK)
def get_blog(
    blog_id: UUID,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    post = db.query(BlogPost).filter(
        BlogPost.id == blog_id,
        BlogPost.author_id == current_user.id,
    ).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found.")
    return post


@router.patch("/{blog_id}", response_model=BlogResponseSchema, status_code=status.HTTP_200_OK)
def update_blog(
    blog_id: UUID,
    blog_update: BlogUpdateSchema,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    post = db.query(BlogPost).filter(
        BlogPost.id == blog_id,
        BlogPost.author_id == current_user.id,
    ).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found or you don't have permission to edit it.",
        )
    update_data = blog_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(post, key, value)
    db.commit()
    db.refresh(post)
    return post


@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(
    blog_id: UUID,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    post = db.query(BlogPost).filter(
        BlogPost.id == blog_id,
        BlogPost.author_id == current_user.id,
    ).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found or you don't have permission to delete it.",
        )
    db.delete(post)
    db.commit()
