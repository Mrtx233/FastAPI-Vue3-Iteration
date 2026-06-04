CREATE DATABASE IF NOT EXISTS `FastAPI_Vue3` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `FastAPI_Vue3`;

-- =================================================================
-- 1. 系统功能权限定义表
-- =================================================================
CREATE TABLE `sys_permission` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '权限ID',
    `permission_code` VARCHAR(64) NOT NULL COMMENT '权限标识符',
    `permission_name` VARCHAR(64) NOT NULL COMMENT '权限名称',
    `menu_path` VARCHAR(255) DEFAULT NULL COMMENT '前端路由路径',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB COMMENT='系统功能权限定义';

-- =================================================================
-- 2. 角色元数据表
-- =================================================================
CREATE TABLE `sys_role` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '角色ID',
    `role_code` VARCHAR(64) NOT NULL COMMENT '角色代码',
    `role_name` VARCHAR(64) NOT NULL COMMENT '角色名称',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB COMMENT='角色元数据';

-- =================================================================
-- 3. 角色与权限关联表
-- =================================================================
CREATE TABLE `sys_role_permission` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '关联ID',
    `role_id` BIGINT NOT NULL COMMENT '角色ID',
    `permission_id` BIGINT NOT NULL COMMENT '权限ID',
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_rp_role` FOREIGN KEY (`role_id`) REFERENCES `sys_role` (`id`),
    CONSTRAINT `fk_rp_permission` FOREIGN KEY (`permission_id`) REFERENCES `sys_permission` (`id`)
) ENGINE=InnoDB COMMENT='角色与权限关联';

-- =================================================================
-- 4. 系统用户基础信息表
-- =================================================================
CREATE TABLE `sys_user` (
    `user_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `role_id` BIGINT NOT NULL COMMENT '角色ID',
    `username` VARCHAR(64) NOT NULL COMMENT '用户名',
    `password` VARCHAR(128) NOT NULL COMMENT '密码',
    `real_name` VARCHAR(64) DEFAULT NULL COMMENT '真实姓名',
    `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号',
    `status` INT DEFAULT 1 COMMENT '状态',
    PRIMARY KEY (`user_id`),
    CONSTRAINT `fk_user_role` FOREIGN KEY (`role_id`) REFERENCES `sys_role` (`id`)
) ENGINE=InnoDB COMMENT='系统用户基础信息';

-- =================================================================
-- 5. 用户扩展档案信息表
-- =================================================================
CREATE TABLE `sys_user_profile` (
    `profile_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '档案ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `level` INT DEFAULT NULL COMMENT '等级',
    `gender` INT DEFAULT NULL COMMENT '性别',
    `birthday` DATE DEFAULT NULL COMMENT '生日',
    `height_cm` DECIMAL(5,2) DEFAULT NULL COMMENT '身高(cm)',
    `weight_kg` DECIMAL(5,2) DEFAULT NULL COMMENT '体重(kg)',
    `avatar_url` VARCHAR(255) DEFAULT NULL COMMENT '头像地址',
    `intro` TEXT DEFAULT NULL COMMENT '简介',
    `create_time` DATETIME DEFAULT NULL COMMENT '账号创建时间',
    `join_time` DATETIME DEFAULT NULL COMMENT '入职/开卡时间',
    `expire_date` DATE DEFAULT NULL COMMENT '到期/停卡时间',
    PRIMARY KEY (`profile_id`),
    CONSTRAINT `fk_profile_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`user_id`)
) ENGINE=InnoDB COMMENT='用户扩展档案信息';

-- =================================================================
-- 6. Slogan标语信息表 (t_slogan_info)
-- =================================================================
CREATE TABLE `t_slogan_info` (
    `slogan_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '标语ID',
    `slogan_name` VARCHAR(64) NOT NULL COMMENT '标语名称',
    `slogan_content` VARCHAR(255) NOT NULL COMMENT '标语内容',
    `slogan_image_url` VARCHAR(255) DEFAULT NULL COMMENT '图片链接',
    `status` INT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    PRIMARY KEY (`slogan_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Slogan标语信息';

-- =================================================================
-- 7. 赛事与活动表（t_activity_event）
-- =================================================================
CREATE TABLE `t_activity_event` (
    `event_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '活动ID',
    `title` VARCHAR(255) NOT NULL COMMENT '活动标题',
    `event_date` DATE NOT NULL COMMENT '活动日期',
    `location` VARCHAR(255) NOT NULL COMMENT '活动地点',
    `status` VARCHAR(32) NOT NULL COMMENT '状态（如：报名中/即将开始/早鸟票/预告）',
    `description` TEXT NOT NULL COMMENT '活动描述',
    `tags` VARCHAR(255) DEFAULT NULL COMMENT '标签（逗号分隔）',
    `prize` VARCHAR(100) DEFAULT NULL COMMENT '奖金/奖品描述',
    `scale` VARCHAR(100) DEFAULT NULL COMMENT '活动规模',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`event_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='赛事与活动';

-- =================================================================
-- 8. 门店所属省份/区域表 (t_store_province)
-- =================================================================
CREATE TABLE `t_store_province` (
    `province_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '省份ID',
    `province_name` VARCHAR(64) NOT NULL COMMENT '省份名称',
    `center_lng` DECIMAL(10, 6) DEFAULT NULL COMMENT '省份中心经度',
    `center_lat` DECIMAL(10, 6) DEFAULT NULL COMMENT '省份中心纬度',
    PRIMARY KEY (`province_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='门店所属省份/区域信息';

-- =================================================================
-- 9. 门店基础信息表 (t_store)
-- =================================================================
CREATE TABLE `t_store` (
    `store_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '门店ID',
    `store_name` VARCHAR(64) NOT NULL COMMENT '门店名称',
    `store_type` INT NOT NULL COMMENT '门店类型：1-铁馆，2-商业私教馆',
    `province_id` BIGINT NOT NULL COMMENT '省份ID',
    `province_name` VARCHAR(64) DEFAULT NULL COMMENT '省份名称',
    `city` VARCHAR(64) DEFAULT NULL COMMENT '城市',
    `district` VARCHAR(64) DEFAULT NULL COMMENT '区/县',
    `address` VARCHAR(255) DEFAULT NULL COMMENT '详细地址',
    `store_phone` VARCHAR(20) DEFAULT NULL COMMENT '门店电话',
    `store_image_url` VARCHAR(255) DEFAULT NULL COMMENT '门店图片',
    `store_introduction` TEXT DEFAULT NULL COMMENT '门店介绍',
    `business_hours` VARCHAR(64) DEFAULT NULL COMMENT '营业时间（如：06:00-22:00）',
    `is_operating` INT DEFAULT 1 COMMENT '是否营业：1-营业，0-停业',
    `store_lng` DECIMAL(10, 6) DEFAULT NULL COMMENT '门店经度',
    `store_lat` DECIMAL(10, 6) DEFAULT NULL COMMENT '门店纬度',
    PRIMARY KEY (`store_id`),
    CONSTRAINT `fk_store_province` FOREIGN KEY (`province_id`) REFERENCES `t_store_province` (`province_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='门店基础信息';

-- =================================================================
-- 10. 用户与门店关联表（y_user_store）
-- =================================================================
CREATE TABLE `y_user_store` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '记录ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `role_id` BIGINT NOT NULL COMMENT '角色ID',
    `store_id` BIGINT NOT NULL COMMENT '门店ID',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '关联时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_time` (`user_id`, `created_at`),
    KEY `idx_user_store` (`user_id`, `store_id`),
    KEY `idx_user_role_store` (`user_id`, `role_id`, `store_id`),
    CONSTRAINT `fk_user_store_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`user_id`),
    CONSTRAINT `fk_user_store_store` FOREIGN KEY (`store_id`) REFERENCES `t_store` (`store_id`),
    CONSTRAINT `fk_user_store_role` FOREIGN KEY (`role_id`) REFERENCES `sys_role` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户关联门店记录';

-- =================================================================
-- 11. 课程分类表 (t_course_category)
-- =================================================================
CREATE TABLE `t_course_category` (
    `category_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '分类ID',
    `category_name` VARCHAR(64) NOT NULL COMMENT '分类名称',
    `category_url` VARCHAR(255) DEFAULT NULL COMMENT '分类图片URL',
    `description` VARCHAR(500) DEFAULT NULL COMMENT '分类描述',
    `status` INT DEFAULT 1 COMMENT '状态',
    PRIMARY KEY (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程分类';

-- =================================================================
-- 12. 健身课程主数据表 (t_course)
-- =================================================================
CREATE TABLE `t_course` (
    `course_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '课程ID',
    `course_name` VARCHAR(64) NOT NULL COMMENT '课程名称',
    `category_id` BIGINT NOT NULL COMMENT '课程分类ID',
    `course_difficulty` INT DEFAULT NULL COMMENT '课程难度',
    `duration_minutes` INT DEFAULT NULL COMMENT '课程时长(分钟)',
    `max_participants` INT DEFAULT NULL COMMENT '最大参与人数',
    `schedule_info` TEXT DEFAULT NULL COMMENT '排期信息(JSON或描述)',
    `description` TEXT DEFAULT NULL COMMENT '课程详细描述',
    `status` INT DEFAULT 1 COMMENT '状态',
    PRIMARY KEY (`course_id`),
    CONSTRAINT `fk_course_category` FOREIGN KEY (`category_id`) REFERENCES `t_course_category` (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='健身课程主数据';

-- =================================================================
-- 13. 用户收藏课程表 (y_user_course_favorite)
-- =================================================================
CREATE TABLE `y_user_course_favorite` (
    `favorite_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '收藏记录ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `course_id` BIGINT NOT NULL COMMENT '课程ID',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
    PRIMARY KEY (`favorite_id`),
    UNIQUE KEY `uk_user_course` (`user_id`, `course_id`),
    CONSTRAINT `fk_course_fav_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`user_id`),
    CONSTRAINT `fk_course_fav_course` FOREIGN KEY (`course_id`) REFERENCES `t_course` (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户收藏的课程';

-- =================================================================
-- 14. 动作分类表 (t_action_category)
-- =================================================================
CREATE TABLE `t_action_category` (
    `category_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '分类ID',
    `category_name` VARCHAR(64) NOT NULL COMMENT '分类名称',
    `category_image_url` VARCHAR(255) DEFAULT NULL COMMENT '分类图标/图片',
    PRIMARY KEY (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='动作分类';

-- =================================================================
-- 15. 动作库条目表 (t_action)
-- =================================================================
CREATE TABLE `t_action` (
    `action_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '动作ID',
    `action_name` VARCHAR(64) NOT NULL COMMENT '动作名称',
    `category_id` BIGINT NOT NULL COMMENT '动作分类ID',
    `action_difficulty` INT DEFAULT NULL COMMENT '动作难度',
    `action_image_url` VARCHAR(255) DEFAULT NULL COMMENT '动作演示图/视频封面',
    `action_steps` TEXT DEFAULT NULL COMMENT '动作步骤文案',
    `attention_points` TEXT DEFAULT NULL COMMENT '注意事项',
    `applicable_equipment` VARCHAR(255) DEFAULT NULL COMMENT '适用器械',
    `applicable_store_type` INT DEFAULT NULL COMMENT '适用门店类型',
    PRIMARY KEY (`action_id`),
    CONSTRAINT `fk_action_category` FOREIGN KEY (`category_id`) REFERENCES `t_action_category` (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='动作库条目';

-- =================================================================
-- 16. 用户动作收藏表 (y_user_action_favorite)
-- =================================================================
CREATE TABLE `y_user_action_favorite` (
    `favorite_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '收藏记录ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `action_id` BIGINT NOT NULL COMMENT '动作ID',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
    PRIMARY KEY (`favorite_id`),
    UNIQUE KEY `uk_user_action` (`user_id`, `action_id`),
    CONSTRAINT `fk_fav_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`user_id`),
    CONSTRAINT `fk_fav_action` FOREIGN KEY (`action_id`) REFERENCES `t_action` (`action_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户收藏的动作';