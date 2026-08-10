-- slaterunner seed data

-- Projects
INSERT OR IGNORE INTO projects (uid, name) VALUES
  ('PRJ_AL13N5', 'Alien'),
  ('PRJ_ARR1VL', 'Arrival'),
  ('PRJ_AV4TAR', 'Avatar'),
  ('PRJ_BL4DER', 'BladeRunner'),
  ('PRJ_EV3RYT', 'EverythingEverywhere'),
  ('PRJ_GR4VIT', 'Gravity'),
  ('PRJ_GR33NK', 'GreenKnight'),
  ('PRJ_1NTER5', 'Interstellar'),
  ('PRJ_K1NGK0', 'KingKong'),
  ('PRJ_OPP3NH', 'Oppenheimer');

-- Assets
INSERT OR IGNORE INTO assets (uid, project_uid, name, type) VALUES
  ('AST_HEPTA1', 'PRJ_ARR1VL', 'HeptapodShip',     'Vehicle'),
  ('AST_KSP1NN', 'PRJ_BL4DER', 'KSpinner',         'Vehicle'),
  ('AST_X3N0MO', 'PRJ_AL13N5', 'Xenomorph',        'Creature'),
  ('AST_T4RS1X', 'PRJ_1NTER5', 'TARS',             'Character'),
  ('AST_NEYT1R', 'PRJ_AV4TAR', 'Neytiri',          'Character'),
  ('AST_NUKEFX', 'PRJ_OPP3NH', 'NuclearBombFX',    'Effect'),
  ('AST_GRNKT1', 'PRJ_GR33NK', 'GreenKnight',      'Character'),
  ('AST_B4GELF', 'PRJ_EV3RYT', 'BagelFX',          'Effect'),
  ('AST_EMPSC1', 'PRJ_K1NGK0', 'EmpireStateScene', 'Environment'),
  ('AST_DEBR15', 'PRJ_GR4VIT', 'DebrisField',      'Environment');

-- Shots
INSERT OR IGNORE INTO shots (uid, project_uid, seq, shot, frame_in, frame_out, fps, colorspace) VALUES
  ('SHT_ARR010', 'PRJ_ARR1VL', 'SEQ01', 'SHOTN_010', 1001,  1060,  24.0, 'sRGB'),
  ('SHT_BLD020', 'PRJ_BL4DER', 'SEQ02', 'SHOTN_020', 2001,  2080,  24.0, 'sRGB'),
  ('SHT_ALN030', 'PRJ_AL13N5', 'SEQ03', 'SHOTN_030', 3001,  3050,  24.0, 'sRGB'),
  ('SHT_INT040', 'PRJ_1NTER5', 'SEQ01', 'SHOTN_040', 4001,  4100,  24.0, 'sRGB'),
  ('SHT_AVT050', 'PRJ_AV4TAR', 'SEQ05', 'SHOTN_050', 5001,  5120,  24.0, 'sRGB'),
  ('SHT_EVE060', 'PRJ_EV3RYT', 'SEQ07', 'SHOTN_060', 6001,  6100,  24.0, 'sRGB'),
  ('SHT_GRV070', 'PRJ_GR4VIT', 'SEQ01', 'SHOTN_070', 7001,  7060,  24.0, 'sRGB'),
  ('SHT_KNG080', 'PRJ_K1NGK0', 'SEQ03', 'SHOTN_080', 8001,  8080,  24.0, 'sRGB'),
  ('SHT_OPP090', 'PRJ_OPP3NH', 'SEQ04', 'SHOTN_090', 9001,  9060,  24.0, 'sRGB'),
  ('SHT_GRN100', 'PRJ_GR33NK', 'SEQ02', 'SHOTN_100', 10001, 10080, 24.0, 'sRGB');

-- Tasks
INSERT OR IGNORE INTO tasks (uid, parent_type, parent_uid, name, assignee, status, project_uid) VALUES
  ('TSK_MD1ALN', 'asset', 'AST_HEPTA1', 'Modeling',     'j.doe',       'WIP',   'PRJ_ARR1VL'),
  ('TSK_RG1XEN', 'asset', 'AST_X3N0MO', 'Rigging',     'a.lee',       'READY', 'PRJ_AL13N5'),
  ('TSK_CP1ALN', 'shot',  'SHT_ALN030',  'Compositing',  'g.lucas',    'WIP',   'PRJ_AL13N5'),
  ('TSK_FX1INT', 'shot',  'SHT_INT040',  'FXSim',        'a.claire',   'HOLD',  'PRJ_1NTER5'),
  ('TSK_AN1BGL', 'asset', 'AST_B4GELF', 'Animation',    'e.mosby',    'WIP',   'PRJ_EV3RYT'),
  ('TSK_LY1DBR', 'asset', 'AST_DEBR15', 'Layout',       'd.kowalski', 'READY', 'PRJ_GR4VIT'),
  ('TSK_FX1KNG', 'shot',  'SHT_KNG080',  'FXExplosion',  'j.jameson',  'WIP',   'PRJ_K1NGK0'),
  ('TSK_CP1GRN', 'shot',  'SHT_GRN100',  'CompPrep',     'j.reynolds', 'READY', 'PRJ_GR33NK'),
  ('TSK_SM1OPP', 'shot',  'SHT_OPP090',  'SimExplosion', 'c.nolan',    'HOLD',  'PRJ_OPP3NH'),
  ('TSK_TX1NEY', 'asset', 'AST_NEYT1R', 'TexturePaint', 's.riley',    'WIP',   'PRJ_AV4TAR');

-- Versions
INSERT OR IGNORE INTO versions (uid, project_uid, task_uid, vnum, status, created_by) VALUES
  ('VER_HEP001', 'PRJ_ARR1VL', 'TSK_MD1ALN', 1, 'draft',    'j.doe'),
  ('VER_XEN001', 'PRJ_AL13N5', 'TSK_RG1XEN', 1, 'review',   'a.lee'),
  ('VER_ALN001', 'PRJ_AL13N5', 'TSK_CP1ALN', 1, 'approved', 'g.lucas'),
  ('VER_INT001', 'PRJ_1NTER5', 'TSK_FX1INT', 1, 'rejected', 'a.claire'),
  ('VER_BGL001', 'PRJ_EV3RYT', 'TSK_AN1BGL', 1, 'draft',    'e.mosby'),
  ('VER_DBR001', 'PRJ_GR4VIT', 'TSK_LY1DBR', 1, 'review',   'd.kowalski'),
  ('VER_KNG001', 'PRJ_K1NGK0', 'TSK_FX1KNG', 1, 'approved', 'j.jameson'),
  ('VER_GRN001', 'PRJ_GR33NK', 'TSK_CP1GRN', 1, 'review',   'j.reynolds'),
  ('VER_OPP001', 'PRJ_OPP3NH', 'TSK_SM1OPP', 1, 'rejected', 'c.nolan'),
  ('VER_NEY001', 'PRJ_AV4TAR', 'TSK_TX1NEY', 1, 'draft',    's.riley');

-- Publishes
INSERT OR IGNORE INTO publishes (uid, project_uid, version_uid, type, representation, path, metadata) VALUES
  ('PUB_HEP001', 'PRJ_ARR1VL', 'VER_HEP001', 'geo',    'usd', '/assets/heptapod_ship/v001/heptapod.usd',      '{"software":"Houdini","submitted_by":"j.doe","department":"Model","purpose":"render"}'),
  ('PUB_XEN001', 'PRJ_AL13N5', 'VER_XEN001', 'rig',    'abc', '/assets/xenomorph/v001/xeno_rig.abc',           '{"software":"Maya","submitted_by":"a.lee","department":"Rigging"}'),
  ('PUB_ALN001', 'PRJ_AL13N5', 'VER_ALN001', 'comp',   'exr', '/shots/alien/shot030/v001/final_comp.exr',      '{"software":"Nuke","submitted_by":"g.lucas","department":"Comp"}'),
  ('PUB_INT001', 'PRJ_1NTER5', 'VER_INT001', 'fx',     'vdb', '/shots/interstellar/shot040/v001/nuke.vdb',     '{"software":"Houdini","submitted_by":"a.claire","department":"FX"}'),
  ('PUB_BGL001', 'PRJ_EV3RYT', 'VER_BGL001', 'fx',     'mov', '/assets/everything/bagel/v001/bagelfx.mov',     '{"software":"AfterEffects","submitted_by":"e.mosby","department":"FX"}'),
  ('PUB_DBR001', 'PRJ_GR4VIT', 'VER_DBR001', 'layout', 'usd', '/shots/gravity/debrisfield/v001/layout.usd',    '{"software":"Maya","submitted_by":"d.kowalski","department":"Layout"}'),
  ('PUB_KNG001', 'PRJ_K1NGK0', 'VER_KNG001', 'fx',     'vdb', '/shots/kingkong/shot080/v001/explosion.vdb',    '{"software":"Houdini","submitted_by":"j.jameson","department":"FX"}'),
  ('PUB_GRN001', 'PRJ_GR33NK', 'VER_GRN001', 'prep',   'exr', '/shots/greenknight/shot100/v001/prep.exr',      '{"software":"Photoshop","submitted_by":"j.reynolds","department":"Prep"}'),
  ('PUB_OPP001', 'PRJ_OPP3NH', 'VER_OPP001', 'fx',     'mov', '/shots/oppenheimer/shot090/v001/explosion.mov', '{"software":"Houdini","submitted_by":"c.nolan","department":"FX"}'),
  ('PUB_NEY001', 'PRJ_AV4TAR', 'VER_NEY001', 'tex',    'png', '/assets/avatar/neytiri/v001/skin_diff.png',     '{"software":"SubstancePainter","submitted_by":"s.riley","department":"Texture"}');

-- Render jobs
INSERT OR IGNORE INTO render_jobs (uid, project_uid, version_uid, context, adapter, status, logs) VALUES
  ('RJB_HEP001', 'PRJ_ARR1VL', 'VER_HEP001', '{"asset":"AST_HEPTA1","task":"TSK_MD1ALN"}', 'tractor',  'queued',    'Queued by j.doe'),
  ('RJB_XEN001', 'PRJ_AL13N5', 'VER_XEN001', '{"asset":"AST_X3N0MO","task":"TSK_RG1XEN"}', 'deadline', 'running',   'Started worker ip-10-0-1-23'),
  ('RJB_ALN001', 'PRJ_AL13N5', 'VER_ALN001', '{"shot":"SHT_ALN030","task":"TSK_CP1ALN"}',   'tractor',  'succeeded', 'All frames complete'),
  ('RJB_INT001', 'PRJ_1NTER5', 'VER_INT001', '{"shot":"SHT_INT040","task":"TSK_FX1INT"}',   'tractor',  'failed',    'Node crashed at f4072'),
  ('RJB_DBR001', 'PRJ_GR4VIT', 'VER_DBR001', '{"asset":"AST_DEBR15","task":"TSK_LY1DBR"}', 'deadline', 'succeeded', 'Approved layout publish'),
  ('RJB_KNG001', 'PRJ_K1NGK0', 'VER_KNG001', '{"shot":"SHT_KNG080","task":"TSK_FX1KNG"}',   'deadline', 'queued',    'Awaiting farm capacity'),
  ('RJB_GRN001', 'PRJ_GR33NK', 'VER_GRN001', '{"shot":"SHT_GRN100","task":"TSK_CP1GRN"}',   'tractor',  'running',   'Comp prep in progress'),
  ('RJB_NEY001', 'PRJ_AV4TAR', 'VER_NEY001', '{"asset":"AST_NEYT1R","task":"TSK_TX1NEY"}', 'tractor',  'succeeded', 'Texture bake done');

-- Events
INSERT OR IGNORE INTO events (uid, project_uid, kind, payload) VALUES
  ('EVN_PUB001', 'PRJ_ARR1VL', 'publish.created',     '{"publish":"PUB_HEP001","version":"VER_HEP001","type":"geo"}'),
  ('EVN_RND001', 'PRJ_AL13N5', 'render.started',      '{"version":"VER_XEN001","task":"TSK_RG1XEN"}'),
  ('EVN_PUB002', 'PRJ_AL13N5', 'publish.created',     '{"publish":"PUB_ALN001","version":"VER_ALN001","type":"comp"}'),
  ('EVN_RND002', 'PRJ_1NTER5', 'render.failed',       '{"version":"VER_INT001","task":"TSK_FX1INT"}'),
  ('EVN_PUB003', 'PRJ_GR4VIT', 'publish.created',     '{"publish":"PUB_DBR001","version":"VER_DBR001","type":"layout"}'),
  ('EVN_TSK001', 'PRJ_K1NGK0', 'task.status_changed', '{"task":"TSK_FX1KNG","from":"WIP","to":"WIP"}'),
  ('EVN_RND003', 'PRJ_GR33NK', 'render.started',      '{"version":"VER_GRN001","task":"TSK_CP1GRN"}'),
  ('EVN_PUB004', 'PRJ_AV4TAR', 'publish.created',     '{"publish":"PUB_NEY001","version":"VER_NEY001","type":"tex"}'),
  ('EVN_PUB005', 'PRJ_OPP3NH', 'publish.created',     '{"publish":"PUB_OPP001","version":"VER_OPP001","type":"fx"}');
