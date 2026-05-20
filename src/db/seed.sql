-- slaterunner seed data

-- Projects
INSERT OR IGNORE INTO projects (uid, name) VALUES
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
INSERT OR IGNORE INTO assets (uid, project_uid, name, type) VALUES
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
INSERT OR IGNORE INTO shots (uid, project_uid, seq, shot, frame_in, frame_out, fps, colorspace) VALUES
  ('SHOT_ARR010', 'PROJ_ARR1VL', 'SEQ01', 'SHOTN_010', 1001,  1060,  24.0, 'sRGB'),
  ('SHOT_BLD020', 'PROJ_BL4DER', 'SEQ02', 'SHOTN_020', 2001,  2080,  24.0, 'sRGB'),
  ('SHOT_ALN030', 'PROJ_AL13N5', 'SEQ03', 'SHOTN_030', 3001,  3050,  24.0, 'sRGB'),
  ('SHOT_INT040', 'PROJ_1NTER5', 'SEQ01', 'SHOTN_040', 4001,  4100,  24.0, 'sRGB'),
  ('SHOT_AVT050', 'PROJ_AV4TAR', 'SEQ05', 'SHOTN_050', 5001,  5120,  24.0, 'sRGB'),
  ('SHOT_EVE060', 'PROJ_EV3RYT', 'SEQ07', 'SHOTN_060', 6001,  6100,  24.0, 'sRGB'),
  ('SHOT_GRV070', 'PROJ_GR4VIT', 'SEQ01', 'SHOTN_070', 7001,  7060,  24.0, 'sRGB'),
  ('SHOT_KNG080', 'PROJ_K1NGK0', 'SEQ03', 'SHOTN_080', 8001,  8080,  24.0, 'sRGB'),
  ('SHOT_OPP090', 'PROJ_OPP3NH', 'SEQ04', 'SHOTN_090', 9001,  9060,  24.0, 'sRGB'),
  ('SHOT_GRN100', 'PROJ_GR33NK', 'SEQ02', 'SHOTN_100', 10001, 10080, 24.0, 'sRGB');

-- Tasks
INSERT OR IGNORE INTO tasks (uid, parent_type, parent_uid, name, assignee, status, project_uid) VALUES
  ('TASK_MD1ALN', 'asset', 'ASSET_HEPTA1', 'Modeling',     'j.doe',       'WIP',   'PROJ_ARR1VL'),
  ('TASK_RG1XEN', 'asset', 'ASSET_X3N0MO', 'Rigging',     'a.lee',       'READY', 'PROJ_AL13N5'),
  ('TASK_CP1ALN', 'shot',  'SHOT_ALN030',  'Compositing',  'g.lucas',    'WIP',   'PROJ_AL13N5'),
  ('TASK_FX1INT', 'shot',  'SHOT_INT040',  'FXSim',        'a.claire',   'HOLD',  'PROJ_1NTER5'),
  ('TASK_AN1BGL', 'asset', 'ASSET_B4GELF', 'Animation',    'e.mosby',    'WIP',   'PROJ_EV3RYT'),
  ('TASK_LY1DBR', 'asset', 'ASSET_DEBR15', 'Layout',       'd.kowalski', 'READY', 'PROJ_GR4VIT'),
  ('TASK_FX1KNG', 'shot',  'SHOT_KNG080',  'FXExplosion',  'j.jameson',  'WIP',   'PROJ_K1NGK0'),
  ('TASK_CP1GRN', 'shot',  'SHOT_GRN100',  'CompPrep',     'j.reynolds', 'READY', 'PROJ_GR33NK'),
  ('TASK_SM1OPP', 'shot',  'SHOT_OPP090',  'SimExplosion', 'c.nolan',    'HOLD',  'PROJ_OPP3NH'),
  ('TASK_TX1NEY', 'asset', 'ASSET_NEYT1R', 'TexturePaint', 's.riley',    'WIP',   'PROJ_AV4TAR');

-- Versions
INSERT OR IGNORE INTO versions (uid, project_uid, task_uid, vnum, status, created_by) VALUES
  ('VER_HEP001', 'PROJ_ARR1VL', 'TASK_MD1ALN', 1, 'draft',    'j.doe'),
  ('VER_XEN001', 'PROJ_AL13N5', 'TASK_RG1XEN', 1, 'review',   'a.lee'),
  ('VER_ALN001', 'PROJ_AL13N5', 'TASK_CP1ALN', 1, 'approved', 'g.lucas'),
  ('VER_INT001', 'PROJ_1NTER5', 'TASK_FX1INT', 1, 'rejected', 'a.claire'),
  ('VER_BGL001', 'PROJ_EV3RYT', 'TASK_AN1BGL', 1, 'draft',    'e.mosby'),
  ('VER_DBR001', 'PROJ_GR4VIT', 'TASK_LY1DBR', 1, 'review',   'd.kowalski'),
  ('VER_KNG001', 'PROJ_K1NGK0', 'TASK_FX1KNG', 1, 'approved', 'j.jameson'),
  ('VER_GRN001', 'PROJ_GR33NK', 'TASK_CP1GRN', 1, 'review',   'j.reynolds'),
  ('VER_OPP001', 'PROJ_OPP3NH', 'TASK_SM1OPP', 1, 'rejected', 'c.nolan'),
  ('VER_NEY001', 'PROJ_AV4TAR', 'TASK_TX1NEY', 1, 'draft',    's.riley');

-- Publishes
INSERT OR IGNORE INTO publishes (uid, project_uid, version_uid, type, representation, path, metadata) VALUES
  ('PUB_HEP001', 'PROJ_ARR1VL', 'VER_HEP001', 'geo',    'usd', '/assets/heptapod_ship/v001/heptapod.usd',      '{"software":"Houdini","submitted_by":"j.doe","department":"Model","purpose":"render"}'),
  ('PUB_XEN001', 'PROJ_AL13N5', 'VER_XEN001', 'rig',    'abc', '/assets/xenomorph/v001/xeno_rig.abc',           '{"software":"Maya","submitted_by":"a.lee","department":"Rigging"}'),
  ('PUB_ALN001', 'PROJ_AL13N5', 'VER_ALN001', 'comp',   'exr', '/shots/alien/shot030/v001/final_comp.exr',      '{"software":"Nuke","submitted_by":"g.lucas","department":"Comp"}'),
  ('PUB_INT001', 'PROJ_1NTER5', 'VER_INT001', 'fx',     'vdb', '/shots/interstellar/shot040/v001/nuke.vdb',     '{"software":"Houdini","submitted_by":"a.claire","department":"FX"}'),
  ('PUB_BGL001', 'PROJ_EV3RYT', 'VER_BGL001', 'fx',     'mov', '/assets/everything/bagel/v001/bagelfx.mov',     '{"software":"AfterEffects","submitted_by":"e.mosby","department":"FX"}'),
  ('PUB_DBR001', 'PROJ_GR4VIT', 'VER_DBR001', 'layout', 'usd', '/shots/gravity/debrisfield/v001/layout.usd',    '{"software":"Maya","submitted_by":"d.kowalski","department":"Layout"}'),
  ('PUB_KNG001', 'PROJ_K1NGK0', 'VER_KNG001', 'fx',     'vdb', '/shots/kingkong/shot080/v001/explosion.vdb',    '{"software":"Houdini","submitted_by":"j.jameson","department":"FX"}'),
  ('PUB_GRN001', 'PROJ_GR33NK', 'VER_GRN001', 'prep',   'exr', '/shots/greenknight/shot100/v001/prep.exr',      '{"software":"Photoshop","submitted_by":"j.reynolds","department":"Prep"}'),
  ('PUB_OPP001', 'PROJ_OPP3NH', 'VER_OPP001', 'fx',     'mov', '/shots/oppenheimer/shot090/v001/explosion.mov', '{"software":"Houdini","submitted_by":"c.nolan","department":"FX"}'),
  ('PUB_NEY001', 'PROJ_AV4TAR', 'VER_NEY001', 'tex',    'png', '/assets/avatar/neytiri/v001/skin_diff.png',     '{"software":"SubstancePainter","submitted_by":"s.riley","department":"Texture"}');

-- Render jobs
INSERT OR IGNORE INTO render_jobs (uid, project_uid, version_uid, context, adapter, status, logs) VALUES
  ('RJB_HEP001', 'PROJ_ARR1VL', 'VER_HEP001', '{"asset":"ASSET_HEPTA1","task":"TASK_MD1ALN"}', 'tractor',  'queued',    'Queued by j.doe'),
  ('RJB_XEN001', 'PROJ_AL13N5', 'VER_XEN001', '{"asset":"ASSET_X3N0MO","task":"TASK_RG1XEN"}', 'deadline', 'running',   'Started worker ip-10-0-1-23'),
  ('RJB_ALN001', 'PROJ_AL13N5', 'VER_ALN001', '{"shot":"SHOT_ALN030","task":"TASK_CP1ALN"}',   'tractor',  'succeeded', 'All frames complete'),
  ('RJB_INT001', 'PROJ_1NTER5', 'VER_INT001', '{"shot":"SHOT_INT040","task":"TASK_FX1INT"}',   'tractor',  'failed',    'Node crashed at f4072'),
  ('RJB_DBR001', 'PROJ_GR4VIT', 'VER_DBR001', '{"asset":"ASSET_DEBR15","task":"TASK_LY1DBR"}', 'deadline', 'succeeded', 'Approved layout publish'),
  ('RJB_KNG001', 'PROJ_K1NGK0', 'VER_KNG001', '{"shot":"SHOT_KNG080","task":"TASK_FX1KNG"}',   'deadline', 'queued',    'Awaiting farm capacity'),
  ('RJB_GRN001', 'PROJ_GR33NK', 'VER_GRN001', '{"shot":"SHOT_GRN100","task":"TASK_CP1GRN"}',   'tractor',  'running',   'Comp prep in progress'),
  ('RJB_NEY001', 'PROJ_AV4TAR', 'VER_NEY001', '{"asset":"ASSET_NEYT1R","task":"TASK_TX1NEY"}', 'tractor',  'succeeded', 'Texture bake done');

-- Events
INSERT OR IGNORE INTO events (uid, project_uid, kind, payload) VALUES
  ('EVN_PUB001', 'PROJ_ARR1VL', 'publish.created',     '{"publish":"PUB_HEP001","version":"VER_HEP001","type":"geo"}'),
  ('EVN_RND001', 'PROJ_AL13N5', 'render.started',      '{"version":"VER_XEN001","task":"TASK_RG1XEN"}'),
  ('EVN_PUB002', 'PROJ_AL13N5', 'publish.created',     '{"publish":"PUB_ALN001","version":"VER_ALN001","type":"comp"}'),
  ('EVN_RND002', 'PROJ_1NTER5', 'render.failed',       '{"version":"VER_INT001","task":"TASK_FX1INT"}'),
  ('EVN_PUB003', 'PROJ_GR4VIT', 'publish.created',     '{"publish":"PUB_DBR001","version":"VER_DBR001","type":"layout"}'),
  ('EVN_TSK001', 'PROJ_K1NGK0', 'task.status_changed', '{"task":"TASK_FX1KNG","from":"WIP","to":"WIP"}'),
  ('EVN_RND003', 'PROJ_GR33NK', 'render.started',      '{"version":"VER_GRN001","task":"TASK_CP1GRN"}'),
  ('EVN_PUB004', 'PROJ_AV4TAR', 'publish.created',     '{"publish":"PUB_NEY001","version":"VER_NEY001","type":"tex"}'),
  ('EVN_PUB005', 'PROJ_OPP3NH', 'publish.created',     '{"publish":"PUB_OPP001","version":"VER_OPP001","type":"fx"}');
