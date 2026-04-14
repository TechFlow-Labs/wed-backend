CREATE TABLE IF NOT EXISTS weddingplan.blog_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id UUID NOT NULL REFERENCES weddingplan.users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    excerpt VARCHAR(500),
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_blog_posts_author_id ON weddingplan.blog_posts(author_id);
CREATE INDEX IF NOT EXISTS idx_blog_posts_is_published ON weddingplan.blog_posts(is_published);
