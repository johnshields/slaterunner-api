-- RLS for pipeline tables
-- SELECT: all valid tokens, WRITE: role-restricted

-- Projects (admin, td, supervisor)
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects FORCE ROW LEVEL SECURITY;

CREATE POLICY projects_select_policy ON projects
  FOR SELECT USING (is_valid_api_token());
CREATE POLICY projects_write_policy ON projects
  FOR ALL USING (
    is_valid_api_token() AND (has_role('admin') OR has_role('td') OR has_role('supervisor'))
  ) WITH CHECK (
    is_valid_api_token() AND (has_role('admin') OR has_role('td') OR has_role('supervisor'))
  );

-- Assets (admin, td, supervisor)
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE assets FORCE ROW LEVEL SECURITY;

CREATE POLICY assets_select_policy ON assets
  FOR SELECT USING (is_valid_api_token());
CREATE POLICY assets_write_policy ON assets
  FOR ALL USING (
    is_valid_api_token() AND (has_role('admin') OR has_role('td') OR has_role('supervisor'))
  ) WITH CHECK (
    is_valid_api_token() AND (has_role('admin') OR has_role('td') OR has_role('supervisor'))
  );

-- Shots (admin, td, supervisor)
ALTER TABLE shots ENABLE ROW LEVEL SECURITY;
ALTER TABLE shots FORCE ROW LEVEL SECURITY;

CREATE POLICY shots_select_policy ON shots
  FOR SELECT USING (is_valid_api_token());
CREATE POLICY shots_write_policy ON shots
  FOR ALL USING (
    is_valid_api_token() AND (has_role('admin') OR has_role('td') OR has_role('supervisor'))
  ) WITH CHECK (
    is_valid_api_token() AND (has_role('admin') OR has_role('td') OR has_role('supervisor'))
  );

-- Tasks (admin, td, supervisor)
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks FORCE ROW LEVEL SECURITY;

CREATE POLICY tasks_select_policy ON tasks
  FOR SELECT USING (is_valid_api_token());
CREATE POLICY tasks_write_policy ON tasks
  FOR ALL USING (
    is_valid_api_token() AND (has_role('admin') OR has_role('td') OR has_role('supervisor'))
  ) WITH CHECK (
    is_valid_api_token() AND (has_role('admin') OR has_role('td') OR has_role('supervisor'))
  );

-- Versions (admin, td, supervisor, artist)
ALTER TABLE versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE versions FORCE ROW LEVEL SECURITY;

CREATE POLICY versions_select_policy ON versions
  FOR SELECT USING (is_valid_api_token());
CREATE POLICY versions_write_policy ON versions
  FOR ALL USING (
    is_valid_api_token() AND (has_role('admin') OR has_role('td') OR has_role('supervisor') OR has_role('artist'))
  ) WITH CHECK (
    is_valid_api_token() AND (has_role('admin') OR has_role('td') OR has_role('supervisor') OR has_role('artist'))
  );

-- Publishes (admin, td, supervisor, artist)
ALTER TABLE publishes ENABLE ROW LEVEL SECURITY;
ALTER TABLE publishes FORCE ROW LEVEL SECURITY;

CREATE POLICY publishes_select_policy ON publishes
  FOR SELECT USING (is_valid_api_token());
CREATE POLICY publishes_write_policy ON publishes
  FOR ALL USING (
    is_valid_api_token() AND (has_role('admin') OR has_role('td') OR has_role('supervisor') OR has_role('artist'))
  ) WITH CHECK (
    is_valid_api_token() AND (has_role('admin') OR has_role('td') OR has_role('supervisor') OR has_role('artist'))
  );

-- Render Jobs (admin, td, service)
ALTER TABLE render_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE render_jobs FORCE ROW LEVEL SECURITY;

CREATE POLICY render_jobs_select_policy ON render_jobs
  FOR SELECT USING (is_valid_api_token());
CREATE POLICY render_jobs_write_policy ON render_jobs
  FOR ALL USING (
    is_valid_api_token() AND (has_role('admin') OR has_role('td') OR has_role('service'))
  ) WITH CHECK (
    is_valid_api_token() AND (has_role('admin') OR has_role('td') OR has_role('service'))
  );

-- Events (admin, td, system)
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE events FORCE ROW LEVEL SECURITY;

CREATE POLICY events_select_policy ON events
  FOR SELECT USING (is_valid_api_token());
CREATE POLICY events_write_policy ON events
  FOR ALL USING (
    is_valid_api_token() AND (has_role('admin') OR has_role('td') OR has_role('system'))
  ) WITH CHECK (
    is_valid_api_token() AND (has_role('admin') OR has_role('td') OR has_role('system'))
  );
