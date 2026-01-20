-- Todo read projection schema
-- This table stores the read-side projections of todos optimized for querying

-- Create the todo_read_projection table
CREATE TABLE IF NOT EXISTS todo_read_projection (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    due_date DATE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('pending', 'completed'))
);

-- Add comment to table
COMMENT ON TABLE todo_read_projection IS 'Read-side projection of todos optimized for querying with pagination, filtering, and sorting';

-- Add comments to columns
COMMENT ON COLUMN todo_read_projection.id IS 'Unique identifier for the todo (primary key)';
COMMENT ON COLUMN todo_read_projection.title IS 'Todo title';
COMMENT ON COLUMN todo_read_projection.description IS 'Optional todo description';
COMMENT ON COLUMN todo_read_projection.status IS 'Completion status: pending or completed';
COMMENT ON COLUMN todo_read_projection.created_at IS 'Creation timestamp';
COMMENT ON COLUMN todo_read_projection.updated_at IS 'Last update timestamp';
COMMENT ON COLUMN todo_read_projection.due_date IS 'Optional due date';
COMMENT ON COLUMN todo_read_projection.deleted_at IS 'Soft delete timestamp (NULL = not deleted)';


-- Indexes for efficient querying
-- All indexes are partial indexes excluding soft-deleted todos

-- Index for default sort (created_at DESC) without filter
CREATE INDEX IF NOT EXISTS idx_todo_created_at ON todo_read_projection (created_at DESC) 
WHERE deleted_at IS NULL;

-- Index for status filter + created_at sort
CREATE INDEX IF NOT EXISTS idx_todo_status_created_at ON todo_read_projection (status, created_at DESC) 
WHERE deleted_at IS NULL;

-- Index for status filter + due_date sort (NULLS LAST for ascending)
CREATE INDEX IF NOT EXISTS idx_todo_status_due_date ON todo_read_projection (status, due_date ASC NULLS LAST) 
WHERE deleted_at IS NULL;

-- Index for due_date sort without status filter (NULLS LAST for ascending)
CREATE INDEX IF NOT EXISTS idx_todo_due_date ON todo_read_projection (due_date ASC NULLS LAST) 
WHERE deleted_at IS NULL;

-- Add comments to indexes
COMMENT ON INDEX idx_todo_created_at IS 'Default sort by creation date descending (newest first)';
COMMENT ON INDEX idx_todo_status_created_at IS 'Status filter with creation date sort';
COMMENT ON INDEX idx_todo_status_due_date IS 'Status filter with due date sort (nulls last)';
COMMENT ON INDEX idx_todo_due_date IS 'Due date sort without status filter (nulls last)';