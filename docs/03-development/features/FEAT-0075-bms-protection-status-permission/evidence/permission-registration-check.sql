CREATE TABLE public.sys_ui_elements (
	id varchar(36) NOT NULL, -- 主键ID
	parent_id varchar(36) NOT NULL, -- 父元素id
	element_code varchar(100) NOT NULL, -- 元素标识符
	element_type int2 NOT NULL, -- 元素类型1-菜单 2-目录 3-路由 4-按钮
	orders int2 NULL, -- 排序
	param1 varchar(255) NULL,
	param2 varchar(255) NULL,
	param3 varchar(255) NULL,
	authority json NOT NULL, -- 权限(多选)1-系统管理员 2-租户 例如[1,2]
	description varchar(255) NULL, -- 描述
	created_at timestamptz(6) NOT NULL,
	remark varchar(255) NULL,
	multilingual varchar(100) NULL, -- 多语言标识符
	route_path varchar(255) NULL,
	CONSTRAINT sys_ui_elements_pkey PRIMARY KEY (id)
);
CREATE TABLE org_type_permissions (tenant_id text, org_type text, ui_codes jsonb, updated_at timestamptz);
INSERT INTO org_type_permissions VALUES ('isolated', 'APP_USER', '["app_device_detail_history"]', NOW()), ('isolated', 'PACK_FACTORY', '["app_device_detail_history","some_other_permission"]', NOW());
CREATE TEMP TABLE permission_snapshot AS SELECT * FROM org_type_permissions;
INSERT INTO sys_ui_elements (id, parent_id, element_code, element_type, authority, description, created_at) VALUES ('existing-root', '0', 'app_mobile_permissions', 2, '[]', '保留根节点', NOW()), ('existing-history', 'existing-root', 'app_device_detail_history', 4, '[]', '历史记录', NOW());
-- FEAT-0075: 移动端与 Web 共用的 BMS 保护状态整块显示权限；不自动授权。

DO $$
DECLARE
  mobile_root_id varchar(36);
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM public.sys_ui_elements WHERE element_code = 'app_mobile_permissions'
  ) THEN
    INSERT INTO public.sys_ui_elements (
      id, parent_id, element_code, element_type, orders,
      param1, param2, param3, authority, description,
      created_at, remark, multilingual, route_path
    ) VALUES (
      '9a2f86c4-1b45-4f85-9c4d-8b92b7d6c301', '0', 'app_mobile_permissions', 2, 19990,
      '', 'mdi:cellphone-cog', '', '["TENANT_ADMIN","SYS_ADMIN"]'::json, '移动端权限',
      NOW(), '移动端与 Web 共用显示权限', 'perm.app_mobile_permissions', ''
    );
  END IF;

  SELECT id INTO mobile_root_id
  FROM public.sys_ui_elements
  WHERE element_code = 'app_mobile_permissions'
  LIMIT 1;

  IF NOT EXISTS (
    SELECT 1 FROM public.sys_ui_elements WHERE element_code = 'app_device_detail_protection_status'
  ) THEN
    INSERT INTO public.sys_ui_elements (
      id, parent_id, element_code, element_type, orders,
      param1, param2, param3, authority, description,
      created_at, remark, multilingual, route_path
    ) VALUES (
      '9a2f86c4-1b45-4f85-9c4d-8b92b7d6c303', mobile_root_id, 'app_device_detail_protection_status', 4, 19992,
      'app_device_detail_protection_status', '', '1', '["TENANT_ADMIN","SYS_ADMIN"]'::json, 'BMS保护状态',
      NOW(), 'FEAT-0075：移动端与 Web 共用', 'perm.app_device_detail_protection_status', ''
    );
  END IF;

  UPDATE public.sys_ui_elements
  SET parent_id = mobile_root_id,
      element_type = 4,
      orders = 19992,
      param1 = 'app_device_detail_protection_status',
      param2 = '',
      param3 = '1',
      authority = '["TENANT_ADMIN","SYS_ADMIN"]'::json,
      description = 'BMS保护状态',
      remark = 'FEAT-0075：移动端与 Web 共用',
      multilingual = 'perm.app_device_detail_protection_status',
      route_path = ''
  WHERE element_code = 'app_device_detail_protection_status';
END $$;
-- FEAT-0075: 移动端与 Web 共用的 BMS 保护状态整块显示权限；不自动授权。

DO $$
DECLARE
  mobile_root_id varchar(36);
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM public.sys_ui_elements WHERE element_code = 'app_mobile_permissions'
  ) THEN
    INSERT INTO public.sys_ui_elements (
      id, parent_id, element_code, element_type, orders,
      param1, param2, param3, authority, description,
      created_at, remark, multilingual, route_path
    ) VALUES (
      '9a2f86c4-1b45-4f85-9c4d-8b92b7d6c301', '0', 'app_mobile_permissions', 2, 19990,
      '', 'mdi:cellphone-cog', '', '["TENANT_ADMIN","SYS_ADMIN"]'::json, '移动端权限',
      NOW(), '移动端与 Web 共用显示权限', 'perm.app_mobile_permissions', ''
    );
  END IF;

  SELECT id INTO mobile_root_id
  FROM public.sys_ui_elements
  WHERE element_code = 'app_mobile_permissions'
  LIMIT 1;

  IF NOT EXISTS (
    SELECT 1 FROM public.sys_ui_elements WHERE element_code = 'app_device_detail_protection_status'
  ) THEN
    INSERT INTO public.sys_ui_elements (
      id, parent_id, element_code, element_type, orders,
      param1, param2, param3, authority, description,
      created_at, remark, multilingual, route_path
    ) VALUES (
      '9a2f86c4-1b45-4f85-9c4d-8b92b7d6c303', mobile_root_id, 'app_device_detail_protection_status', 4, 19992,
      'app_device_detail_protection_status', '', '1', '["TENANT_ADMIN","SYS_ADMIN"]'::json, 'BMS保护状态',
      NOW(), 'FEAT-0075：移动端与 Web 共用', 'perm.app_device_detail_protection_status', ''
    );
  END IF;

  UPDATE public.sys_ui_elements
  SET parent_id = mobile_root_id,
      element_type = 4,
      orders = 19992,
      param1 = 'app_device_detail_protection_status',
      param2 = '',
      param3 = '1',
      authority = '["TENANT_ADMIN","SYS_ADMIN"]'::json,
      description = 'BMS保护状态',
      remark = 'FEAT-0075：移动端与 Web 共用',
      multilingual = 'perm.app_device_detail_protection_status',
      route_path = ''
  WHERE element_code = 'app_device_detail_protection_status';
END $$;

DO $$ BEGIN
  IF (SELECT count(*) FROM sys_ui_elements WHERE element_code = 'app_mobile_permissions') <> 1 OR
     (SELECT count(*) FROM sys_ui_elements WHERE element_code = 'app_device_detail_protection_status') <> 1 THEN
    RAISE EXCEPTION 'duplicate or missing permission nodes';
  END IF;
  IF EXISTS ((SELECT * FROM permission_snapshot EXCEPT SELECT * FROM org_type_permissions) UNION ALL
             (SELECT * FROM org_type_permissions EXCEPT SELECT * FROM permission_snapshot)) THEN
    RAISE EXCEPTION 'existing grants changed';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM sys_ui_elements leaf JOIN sys_ui_elements root ON leaf.parent_id = root.id
    WHERE leaf.element_code = 'app_device_detail_protection_status' AND leaf.description = 'BMS保护状态'
      AND leaf.element_type = 4 AND root.element_code = 'app_mobile_permissions') THEN
    RAISE EXCEPTION 'permission parent or metadata invalid';
  END IF;
END $$;

DO $$ BEGIN
 IF NOT EXISTS (SELECT 1 FROM sys_ui_elements WHERE id='existing-root' AND description='保留根节点') OR
    NOT EXISTS (SELECT 1 FROM sys_ui_elements WHERE id='existing-history' AND parent_id='existing-root' AND description='历史记录') THEN
   RAISE EXCEPTION 'existing mobile root/history changed';
 END IF;
END $$;
SELECT 'SQL67 twice: unique node, existing parent/history/grants preserved' AS result;
TRUNCATE sys_ui_elements;
-- FEAT-0075: 移动端与 Web 共用的 BMS 保护状态整块显示权限；不自动授权。

DO $$
DECLARE
  mobile_root_id varchar(36);
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM public.sys_ui_elements WHERE element_code = 'app_mobile_permissions'
  ) THEN
    INSERT INTO public.sys_ui_elements (
      id, parent_id, element_code, element_type, orders,
      param1, param2, param3, authority, description,
      created_at, remark, multilingual, route_path
    ) VALUES (
      '9a2f86c4-1b45-4f85-9c4d-8b92b7d6c301', '0', 'app_mobile_permissions', 2, 19990,
      '', 'mdi:cellphone-cog', '', '["TENANT_ADMIN","SYS_ADMIN"]'::json, '移动端权限',
      NOW(), '移动端与 Web 共用显示权限', 'perm.app_mobile_permissions', ''
    );
  END IF;

  SELECT id INTO mobile_root_id
  FROM public.sys_ui_elements
  WHERE element_code = 'app_mobile_permissions'
  LIMIT 1;

  IF NOT EXISTS (
    SELECT 1 FROM public.sys_ui_elements WHERE element_code = 'app_device_detail_protection_status'
  ) THEN
    INSERT INTO public.sys_ui_elements (
      id, parent_id, element_code, element_type, orders,
      param1, param2, param3, authority, description,
      created_at, remark, multilingual, route_path
    ) VALUES (
      '9a2f86c4-1b45-4f85-9c4d-8b92b7d6c303', mobile_root_id, 'app_device_detail_protection_status', 4, 19992,
      'app_device_detail_protection_status', '', '1', '["TENANT_ADMIN","SYS_ADMIN"]'::json, 'BMS保护状态',
      NOW(), 'FEAT-0075：移动端与 Web 共用', 'perm.app_device_detail_protection_status', ''
    );
  END IF;

  UPDATE public.sys_ui_elements
  SET parent_id = mobile_root_id,
      element_type = 4,
      orders = 19992,
      param1 = 'app_device_detail_protection_status',
      param2 = '',
      param3 = '1',
      authority = '["TENANT_ADMIN","SYS_ADMIN"]'::json,
      description = 'BMS保护状态',
      remark = 'FEAT-0075：移动端与 Web 共用',
      multilingual = 'perm.app_device_detail_protection_status',
      route_path = ''
  WHERE element_code = 'app_device_detail_protection_status';
END $$;
-- FEAT-0075: 移动端与 Web 共用的 BMS 保护状态整块显示权限；不自动授权。

DO $$
DECLARE
  mobile_root_id varchar(36);
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM public.sys_ui_elements WHERE element_code = 'app_mobile_permissions'
  ) THEN
    INSERT INTO public.sys_ui_elements (
      id, parent_id, element_code, element_type, orders,
      param1, param2, param3, authority, description,
      created_at, remark, multilingual, route_path
    ) VALUES (
      '9a2f86c4-1b45-4f85-9c4d-8b92b7d6c301', '0', 'app_mobile_permissions', 2, 19990,
      '', 'mdi:cellphone-cog', '', '["TENANT_ADMIN","SYS_ADMIN"]'::json, '移动端权限',
      NOW(), '移动端与 Web 共用显示权限', 'perm.app_mobile_permissions', ''
    );
  END IF;

  SELECT id INTO mobile_root_id
  FROM public.sys_ui_elements
  WHERE element_code = 'app_mobile_permissions'
  LIMIT 1;

  IF NOT EXISTS (
    SELECT 1 FROM public.sys_ui_elements WHERE element_code = 'app_device_detail_protection_status'
  ) THEN
    INSERT INTO public.sys_ui_elements (
      id, parent_id, element_code, element_type, orders,
      param1, param2, param3, authority, description,
      created_at, remark, multilingual, route_path
    ) VALUES (
      '9a2f86c4-1b45-4f85-9c4d-8b92b7d6c303', mobile_root_id, 'app_device_detail_protection_status', 4, 19992,
      'app_device_detail_protection_status', '', '1', '["TENANT_ADMIN","SYS_ADMIN"]'::json, 'BMS保护状态',
      NOW(), 'FEAT-0075：移动端与 Web 共用', 'perm.app_device_detail_protection_status', ''
    );
  END IF;

  UPDATE public.sys_ui_elements
  SET parent_id = mobile_root_id,
      element_type = 4,
      orders = 19992,
      param1 = 'app_device_detail_protection_status',
      param2 = '',
      param3 = '1',
      authority = '["TENANT_ADMIN","SYS_ADMIN"]'::json,
      description = 'BMS保护状态',
      remark = 'FEAT-0075：移动端与 Web 共用',
      multilingual = 'perm.app_device_detail_protection_status',
      route_path = ''
  WHERE element_code = 'app_device_detail_protection_status';
END $$;

DO $$ BEGIN
  IF (SELECT count(*) FROM sys_ui_elements WHERE element_code = 'app_mobile_permissions') <> 1 OR
     (SELECT count(*) FROM sys_ui_elements WHERE element_code = 'app_device_detail_protection_status') <> 1 THEN
    RAISE EXCEPTION 'duplicate or missing permission nodes';
  END IF;
  IF EXISTS ((SELECT * FROM permission_snapshot EXCEPT SELECT * FROM org_type_permissions) UNION ALL
             (SELECT * FROM org_type_permissions EXCEPT SELECT * FROM permission_snapshot)) THEN
    RAISE EXCEPTION 'existing grants changed';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM sys_ui_elements leaf JOIN sys_ui_elements root ON leaf.parent_id = root.id
    WHERE leaf.element_code = 'app_device_detail_protection_status' AND leaf.description = 'BMS保护状态'
      AND leaf.element_type = 4 AND root.element_code = 'app_mobile_permissions') THEN
    RAISE EXCEPTION 'permission parent or metadata invalid';
  END IF;
END $$;
SELECT 'bootstrap registration twice: root ensured, node unique, no automatic grants' AS result;
