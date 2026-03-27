-- Clear existing data
TRUNCATE publishes, versions, tasks, shots, assets, projects, render_jobs, events RESTART IDENTITY CASCADE;

-- Helper: generate a random timestamp within the past N days
CREATE OR REPLACE FUNCTION random_time(days INT DEFAULT 30)
RETURNS TIMESTAMPTZ AS $$
BEGIN
  RETURN now() - (random() * (days || ' days')::interval);
END;
$$ LANGUAGE plpgsql;

-- API Keys (dev tokens)
INSERT INTO api_keys (token, description, role, is_admin, expires_at) VALUES
  ('dev-admin-token',      'Admin (full access)',         'admin',      true,  NULL),
  ('dev-td-token',         'TD (pipeline full access)',   'td',         true,  NULL),
  ('dev-atd-token',        'ATD (read-only)',             'atd',        false, NULL),
  ('dev-artist-token',     'Artist (versions/publishes)', 'artist',     false, NULL),
  ('dev-producer-token',   'Producer (read-only)',        'producer',   false, NULL),
  ('dev-supervisor-token', 'Supervisor (approve tasks)',  'supervisor', false, NULL),
  ('dev-service-token',    'Service (render farm)',       'service',    false, NULL),
  ('dev-system-token',     'System (events/logging)',     'system',     false, NULL),
  ('dev-client-token',     'Client (read-only)',          'client',     false, NULL);

-- Projects
INSERT INTO projects (uid, name) VALUES
  ('PROJ_AL13N5', 'Alien'),
  ('PROJ_ARR1VL', 'Arrival'),
  ('PROJ_AV4TAR', 'Avatar'),
  ('PROJ_BL4DER', 'BladeRunner'),
  ('PROJ_EV3RYT', 'EverythingEverywhere'),
  ('PROJ_GR4VIT', 'Gravity'),
  ('PROJ_GR33NK', 'GreenKnight'),
  ('PROJ_1NTER5', 'Interstellar'),
  ('PROJ_K1NGK0', 'KingKong'),
  ('PROJ_OPP3NH', 'Oppenheimer');

-- Assets
INSERT INTO assets (uid, project_uid, name, type) VALUES
  ('ASSET_HEPTA1', 'PROJ_ARR1VL', 'HeptapodShip',     'Vehicle'),
  ('ASSET_KSP1NN', 'PROJ_BL4DER', 'KSpinner',         'Vehicle'),
  ('ASSET_X3N0MO', 'PROJ_AL13N5', 'Xenomorph',        'Creature'),
  ('ASSET_T4RS1X', 'PROJ_1NTER5', 'TARS',             'Character'),
  ('ASSET_NEYT1R', 'PROJ_AV4TAR', 'Neytiri',          'Character'),
  ('ASSET_NUKEFX', 'PROJ_OPP3NH', 'NuclearBombFX',    'Effect'),
  ('ASSET_GRNKT1', 'PROJ_GR33NK', 'GreenKnight',      'Character'),
  ('ASSET_B4GELF', 'PROJ_EV3RYT', 'BagelFX',          'Effect'),
  ('ASSET_EMPSC1', 'PROJ_K1NGK0', 'EmpireStateScene', 'Environment'),
  ('ASSET_DEBR15', 'PROJ_GR4VIT', 'DebrisField',      'Environment');

-- Shots
INSERT INTO shots (uid, project_uid, seq, shot, frame_in, frame_out, fps, colorspace) VALUES
  ('SHOT_ARR010', 'PROJ_ARR1VL', 'SEQ01', 'SHOTN_010', 1001,  1060,  24.000, 'sRGB'),
  ('SHOT_BLD020', 'PROJ_BL4DER', 'SEQ02', 'SHOTN_020', 2001,  2080,  24.000, 'sRGB'),
  ('SHOT_ALN030', 'PROJ_AL13N5', 'SEQ03', 'SHOTN_030', 3001,  3050,  24.000, 'sRGB'),
  ('SHOT_INT040', 'PROJ_1NTER5', 'SEQ01', 'SHOTN_040', 4001,  4100,  24.000, 'sRGB'),
  ('SHOT_AVT050', 'PROJ_AV4TAR', 'SEQ05', 'SHOTN_050', 5001,  5120,  24.000, 'sRGB'),
  ('SHOT_EVE060', 'PROJ_EV3RYT', 'SEQ07', 'SHOTN_060', 6001,  6100,  24.000, 'sRGB'),
  ('SHOT_GRV070', 'PROJ_GR4VIT', 'SEQ01', 'SHOTN_070', 7001,  7060,  24.000, 'sRGB'),
  ('SHOT_KNG080', 'PROJ_K1NGK0', 'SEQ03', 'SHOTN_080', 8001,  8080,  24.000, 'sRGB'),
  ('SHOT_OPP090', 'PROJ_OPP3NH', 'SEQ04', 'SHOTN_090', 9001,  9060,  24.000, 'sRGB'),
  ('SHOT_GRN100', 'PROJ_GR33NK', 'SEQ02', 'SHOTN_100', 10001, 10080, 24.000, 'sRGB');

-- Tasks
INSERT INTO tasks (uid, parent_type, parent_uid, name, assignee, status, project_uid) VALUES
  ('TASK_MD1ALN', 'asset', 'ASSET_HEPTA1', 'Modeling',     'j.doe',      'WIP',   'PROJ_ARR1VL'),
  ('TASK_RG1XEN', 'asset', 'ASSET_X3N0MO', 'Rigging',     'a.lee',      'READY', 'PROJ_AL13N5'),
  ('TASK_CP1ALN', 'shot',  'SHOT_ALN030',  'Compositing',  'g.lucas',   'WIP',   'PROJ_AL13N5'),
  ('TASK_FX1INT', 'shot',  'SHOT_INT040',  'FXSim',        'a.claire',  'HOLD',  'PROJ_1NTER5'),
  ('TASK_AN1BGL', 'asset', 'ASSET_B4GELF', 'Animation',    'e.mosby',   'WIP',   'PROJ_EV3RYT'),
  ('TASK_LY1DBR', 'asset', 'ASSET_DEBR15', 'Layout',       'd.kowalski','READY', 'PROJ_GR4VIT'),
  ('TASK_FX1KNG', 'shot',  'SHOT_KNG080',  'FXExplosion',  'j.jameson', 'WIP',   'PROJ_K1NGK0'),
  ('TASK_CP1GRN', 'shot',  'SHOT_GRN100',  'CompPrep',     'j.reynolds','READY', 'PROJ_GR33NK'),
  ('TASK_SM1OPP', 'shot',  'SHOT_OPP090',  'SimExplosion', 'c.nolan',   'HOLD',  'PROJ_OPP3NH'),
  ('TASK_TX1NEY', 'asset', 'ASSET_NEYT1R', 'TexturePaint', 's.riley',   'WIP',   'PROJ_AV4TAR');

-- Versions
INSERT INTO versions (uid, project_uid, task_uid, vnum, status, created_by, created_at) VALUES
  ('VER_HEP001', 'PROJ_ARR1VL', 'TASK_MD1ALN', 1, 'draft',    'j.doe',      random_time(30)),
  ('VER_XEN001', 'PROJ_AL13N5', 'TASK_RG1XEN', 1, 'review',   'a.lee',      random_time(30)),
  ('VER_ALN001', 'PROJ_AL13N5', 'TASK_CP1ALN', 1, 'approved', 'g.lucas',    random_time(30)),
  ('VER_INT001', 'PROJ_1NTER5', 'TASK_FX1INT', 1, 'rejected', 'a.claire',   random_time(30)),
  ('VER_BGL001', 'PROJ_EV3RYT', 'TASK_AN1BGL', 1, 'draft',    'e.mosby',   random_time(30)),
  ('VER_DBR001', 'PROJ_GR4VIT', 'TASK_LY1DBR', 1, 'review',   'd.kowalski', random_time(30)),
  ('VER_KNG001', 'PROJ_K1NGK0', 'TASK_FX1KNG', 1, 'approved', 'j.jameson',  random_time(30)),
  ('VER_GRN001', 'PROJ_GR33NK', 'TASK_CP1GRN', 1, 'review',   'j.reynolds', random_time(30)),
  ('VER_OPP001', 'PROJ_OPP3NH', 'TASK_SM1OPP', 1, 'rejected', 'c.nolan',    random_time(30)),
  ('VER_NEY001', 'PROJ_AV4TAR', 'TASK_TX1NEY', 1, 'draft',    's.riley',    random_time(30));

-- Publishes
INSERT INTO publishes (uid, project_uid, version_uid, type, representation, path, metadata, created_at) VALUES
  ('PUB_HEP001', 'PROJ_ARR1VL', 'VER_HEP001', 'geo',    'usd', '/assets/heptapod_ship/v001/heptapod.usd',       '{"software":"Houdini","submitted_by":"j.doe","department":"Model","purpose":"render"}'::jsonb,       random_time(30)),
  ('PUB_XEN001', 'PROJ_AL13N5', 'VER_XEN001', 'rig',    'abc', '/assets/xenomorph/v001/xeno_rig.abc',            '{"software":"Maya","submitted_by":"a.lee","department":"Rigging"}'::jsonb,                          random_time(30)),
  ('PUB_ALN001', 'PROJ_AL13N5', 'VER_ALN001', 'comp',   'exr', '/shots/alien/shot030/v001/final_comp.exr',       '{"software":"Nuke","submitted_by":"g.lucas","department":"Comp"}'::jsonb,                           random_time(30)),
  ('PUB_INT001', 'PROJ_1NTER5', 'VER_INT001', 'fx',     'vdb', '/shots/interstellar/shot040/v001/nuke.vdb',      '{"software":"Houdini","submitted_by":"a.claire","department":"FX"}'::jsonb,                         random_time(30)),
  ('PUB_BGL001', 'PROJ_EV3RYT', 'VER_BGL001', 'fx',     'mov', '/assets/everything/bagel/v001/bagelfx.mov',      '{"software":"AfterEffects","submitted_by":"e.mosby","department":"FX"}'::jsonb,                     random_time(30)),
  ('PUB_DBR001', 'PROJ_GR4VIT', 'VER_DBR001', 'layout', 'usd', '/shots/gravity/debrisfield/v001/layout.usd',     '{"software":"Maya","submitted_by":"d.kowalski","department":"Layout"}'::jsonb,                      random_time(30)),
  ('PUB_KNG001', 'PROJ_K1NGK0', 'VER_KNG001', 'fx',     'vdb', '/shots/kingkong/shot080/v001/explosion.vdb',     '{"software":"Houdini","submitted_by":"j.jameson","department":"FX"}'::jsonb,                        random_time(30)),
  ('PUB_GRN001', 'PROJ_GR33NK', 'VER_GRN001', 'prep',   'exr', '/shots/greenknight/shot100/v001/prep.exr',       '{"software":"Photoshop","submitted_by":"j.reynolds","department":"Prep"}'::jsonb,                   random_time(30)),
  ('PUB_OPP001', 'PROJ_OPP3NH', 'VER_OPP001', 'fx',     'mov', '/shots/oppenheimer/shot090/v001/explosion.mov',  '{"software":"Houdini","submitted_by":"c.nolan","department":"FX"}'::jsonb,                          random_time(30)),
  ('PUB_NEY001', 'PROJ_AV4TAR', 'VER_NEY001', 'tex',    'png', '/assets/avatar/neytiri/v001/skin_diff.png',      '{"software":"SubstancePainter","submitted_by":"s.riley","department":"Texture"}'::jsonb,            random_time(30));

-- Render Jobs
INSERT INTO render_jobs (project_uid, version_uid, context, adapter, status, logs, submitted_at, created_at) VALUES
  ('PROJ_ARR1VL', 'VER_HEP001', '{"asset":"ASSET_HEPTA1","task":"TASK_MD1ALN"}'::jsonb, 'tractor',  'queued',    'Queued by j.doe',          random_time(30), random_time(30)),
  ('PROJ_AL13N5', 'VER_XEN001', '{"asset":"ASSET_X3N0MO","task":"TASK_RG1XEN"}'::jsonb, 'deadline', 'running',   'Started worker ip-10-0-1-23', random_time(30), random_time(30)),
  ('PROJ_AL13N5', 'VER_ALN001', '{"shot":"SHOT_ALN030","task":"TASK_CP1ALN"}'::jsonb,   'tractor',  'succeeded', 'All frames complete',      random_time(30), random_time(30)),
  ('PROJ_1NTER5', 'VER_INT001', '{"shot":"SHOT_INT040","task":"TASK_FX1INT"}'::jsonb,   'tractor',  'failed',    'Node crashed at f4072',    random_time(30), random_time(30)),
  ('PROJ_GR4VIT', 'VER_DBR001', '{"asset":"ASSET_DEBR15","task":"TASK_LY1DBR"}'::jsonb, 'deadline', 'succeeded', 'Approved layout publish',  random_time(30), random_time(30)),
  ('PROJ_K1NGK0', 'VER_KNG001', '{"shot":"SHOT_KNG080","task":"TASK_FX1KNG"}'::jsonb,   'deadline', 'queued',    'Awaiting farm capacity',   random_time(30), random_time(30)),
  ('PROJ_GR33NK', 'VER_GRN001', '{"shot":"SHOT_GRN100","task":"TASK_CP1GRN"}'::jsonb,   'tractor',  'running',   'Comp prep in progress',    random_time(30), random_time(30)),
  ('PROJ_AV4TAR', 'VER_NEY001', '{"asset":"ASSET_NEYT1R","task":"TASK_TX1NEY"}'::jsonb, 'tractor',  'succeeded', 'Texture bake done',        random_time(30), random_time(30));

-- Events
INSERT INTO events (project_uid, kind, payload, created_at, updated_at) VALUES
  ('PROJ_ARR1VL', 'publish.created',       '{"publish":"PUB_HEP001","version":"VER_HEP001","type":"geo"}'::jsonb,    random_time(30), now()),
  ('PROJ_AL13N5', 'render.started',        '{"version":"VER_XEN001","task":"TASK_RG1XEN"}'::jsonb,                   random_time(30), now()),
  ('PROJ_AL13N5', 'publish.created',       '{"publish":"PUB_ALN001","version":"VER_ALN001","type":"comp"}'::jsonb,   random_time(30), now()),
  ('PROJ_1NTER5', 'render.failed',         '{"version":"VER_INT001","task":"TASK_FX1INT"}'::jsonb,                   random_time(30), now()),
  ('PROJ_GR4VIT', 'publish.created',       '{"publish":"PUB_DBR001","version":"VER_DBR001","type":"layout"}'::jsonb, random_time(30), now()),
  ('PROJ_K1NGK0', 'task.status_changed',   '{"task":"TASK_FX1KNG","from":"WIP","to":"WIP"}'::jsonb,                 random_time(30), now()),
  ('PROJ_GR33NK', 'render.started',        '{"version":"VER_GRN001","task":"TASK_CP1GRN"}'::jsonb,                   random_time(30), now()),
  ('PROJ_AV4TAR', 'publish.created',       '{"publish":"PUB_NEY001","version":"VER_NEY001","type":"tex"}'::jsonb,    random_time(30), now()),
  ('PROJ_OPP3NH', 'publish.created',       '{"publish":"PUB_OPP001","version":"VER_OPP001","type":"fx"}'::jsonb,     random_time(30), now());
