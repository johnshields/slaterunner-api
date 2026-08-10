-- Partial unique indexes (enforce uniqueness for non-deleted records only)
CREATE UNIQUE INDEX IF NOT EXISTS idx_projects_name_unique
    ON projects(name) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_assets_project_name_unique
    ON assets(project_uid, name) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_shots_project_seq_shot_unique
    ON shots(project_uid, seq, shot) WHERE deleted_at IS NULL;

-- Soft delete cascades
CREATE TRIGGER IF NOT EXISTS trg_cascade_soft_delete_project
    AFTER UPDATE OF deleted_at ON projects
    WHEN NEW.deleted_at IS NOT NULL AND OLD.deleted_at IS NULL
BEGIN
    UPDATE assets      SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE shots       SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE tasks       SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE versions    SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE publishes   SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE render_jobs SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE events      SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
END;

CREATE TRIGGER IF NOT EXISTS trg_cascade_soft_delete_task
    AFTER UPDATE OF deleted_at ON tasks
    WHEN NEW.deleted_at IS NOT NULL AND OLD.deleted_at IS NULL
BEGIN
    UPDATE versions SET deleted_at = NEW.deleted_at WHERE task_uid = NEW.uid AND deleted_at IS NULL;
END;

CREATE TRIGGER IF NOT EXISTS trg_cascade_soft_delete_version
    AFTER UPDATE OF deleted_at ON versions
    WHEN NEW.deleted_at IS NOT NULL AND OLD.deleted_at IS NULL
BEGIN
    UPDATE publishes   SET deleted_at = NEW.deleted_at WHERE version_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE render_jobs SET deleted_at = NEW.deleted_at WHERE version_uid = NEW.uid AND deleted_at IS NULL;
END;
