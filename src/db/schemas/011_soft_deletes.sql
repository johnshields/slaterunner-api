-- Partial unique indexes (enforce uniqueness only for non-deleted records)
CREATE UNIQUE INDEX IF NOT EXISTS idx_projects_name_unique ON projects(name)
    WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_assets_project_name_unique ON assets(project_uid, name)
    WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_shots_project_seq_shot_unique ON shots(project_uid, seq, shot)
    WHERE deleted_at IS NULL;

-- Soft delete cascade: projects -> all child tables
CREATE OR REPLACE FUNCTION cascade_soft_delete_project() RETURNS TRIGGER AS $$
BEGIN
  IF NEW.deleted_at IS NOT NULL AND OLD.deleted_at IS NULL THEN
    UPDATE assets     SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE shots      SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE tasks      SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE versions   SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE publishes  SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE render_jobs SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE events     SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Soft delete cascade: tasks -> versions
CREATE OR REPLACE FUNCTION cascade_soft_delete_task() RETURNS TRIGGER AS $$
BEGIN
  IF NEW.deleted_at IS NOT NULL AND OLD.deleted_at IS NULL THEN
    UPDATE versions SET deleted_at = NEW.deleted_at WHERE task_uid = NEW.uid AND deleted_at IS NULL;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Soft delete cascade: versions -> publishes, render_jobs
CREATE OR REPLACE FUNCTION cascade_soft_delete_version() RETURNS TRIGGER AS $$
BEGIN
  IF NEW.deleted_at IS NOT NULL AND OLD.deleted_at IS NULL THEN
    UPDATE publishes  SET deleted_at = NEW.deleted_at WHERE version_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE render_jobs SET deleted_at = NEW.deleted_at WHERE version_uid = NEW.uid AND deleted_at IS NULL;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cascade_soft_delete_project
    AFTER UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION cascade_soft_delete_project();

CREATE TRIGGER trg_cascade_soft_delete_task
    AFTER UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION cascade_soft_delete_task();

CREATE TRIGGER trg_cascade_soft_delete_version
    AFTER UPDATE ON versions
    FOR EACH ROW EXECUTE FUNCTION cascade_soft_delete_version();
