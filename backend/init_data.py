"""
健身管理系统初始化数据脚本
为全部 16 张表写入标准测试数据
"""
import pymysql
from app.core.auth import hash_password
from app.core.config import settings

conn = pymysql.connect(
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    database=settings.DB_NAME,
    charset="utf8mb4",
    autocommit=False,
)
cur = conn.cursor()

try:
    # ========== 清空旧数据（按外键依赖顺序） ==========
    tables_delete = [
        "y_user_action_favorite", "y_user_course_favorite", "y_user_store",
        "sys_role_permission", "sys_user_profile", "sys_user",
        "t_action", "t_action_category",
        "t_course", "t_course_category",
        "t_store", "t_store_province",
        "t_activity_event", "t_slogan_info",
        "sys_role", "sys_permission",
    ]
    for t in tables_delete:
        cur.execute(f"DELETE FROM `{t}`")
    print("[1/2] 旧数据已清空")

    # ========== 1. sys_permission 权限定义 ==========
    permissions = [
        (1,  "user:list",              "用户列表",       "/system/users"),
        (2,  "user:create",            "创建用户",       None),
        (3,  "user:edit",              "编辑用户",       None),
        (4,  "user:delete",            "删除用户",       None),
        (5,  "role:list",              "角色列表",       "/system/roles"),
        (6,  "role:create",            "创建角色",       None),
        (7,  "role:edit",              "编辑角色",       None),
        (8,  "role:delete",            "删除角色",       None),
        (9,  "permission:list",        "权限列表",       "/system/permissions"),
        (10, "permission:create",      "创建权限",       None),
        (11, "permission:edit",        "编辑权限",       None),
        (12, "permission:delete",      "删除权限",       None),
        (13, "role_permission:list",   "角色权限列表",   "/system/role-permissions"),
        (14, "role_permission:create", "分配角色权限",   None),
        (15, "role_permission:delete", "取消角色权限",   None),
        (16, "user:view_own",          "查看自身信息",   None),
        (17, "store:list",             "门店列表",       "/store/list"),
        (18, "store:manage",           "门店管理",       None),
        (19, "course:list",            "课程列表",       "/course/list"),
        (20, "course:manage",          "课程管理",       None),
        (21, "action:list",            "动作列表",       "/action/list"),
        (22, "action:manage",          "动作管理",       None),
        (23, "activity:list",          "活动列表",       "/activity/list"),
        (24, "activity:manage",        "活动管理",       None),
        (25, "slogan:list",            "标语列表",       "/slogan/list"),
        (26, "slogan:manage",          "标语管理",       None),
    ]
    cur.executemany(
        "INSERT INTO sys_permission (id, permission_code, permission_name, menu_path) VALUES (%s,%s,%s,%s)",
        permissions,
    )

    # ========== 2. sys_role 角色 ==========
    roles = [
        (1, "super_admin", "超级管理员"),
        (2, "operator",    "运营管理员"),
        (3, "coach",       "教练"),
        (4, "member",      "会员"),
    ]
    cur.executemany("INSERT INTO sys_role (id, role_code, role_name) VALUES (%s,%s,%s)", roles)

    # ========== 3. sys_role_permission 角色-权限 ==========
    all_perm_ids = [p[0] for p in permissions]
    rp = []
    # 超级管理员: 全部权限
    for pid in all_perm_ids:
        rp.append((1, pid))
    # 运营管理员: 除 user:delete(4) 外全部
    for pid in all_perm_ids:
        if pid != 4:
            rp.append((2, pid))
    # 教练: user:list + 课程CRUD + 动作CRUD + 活动/标语查看
    for pid in [1, 19, 20, 21, 22, 23, 25]:
        rp.append((3, pid))
    # 会员: user:view_own + 课程查看 + 动作查看 + 活动/标语查看
    for pid in [16, 19, 21, 23, 25]:
        rp.append((4, pid))
    cur.executemany(
        "INSERT INTO sys_role_permission (role_id, permission_id) VALUES (%s,%s)", rp
    )

    # ========== 4. sys_user 用户 ==========
    users = [
        (1, 1, "admin",    hash_password("admin123"),   "张三", "13800000001", 1),
        (2, 2, "operator", hash_password("oper123"),    "李四", "13800000002", 1),
        (3, 3, "coach_w",  hash_password("coach123"),   "王五", "13800000003", 1),
        (4, 3, "coach_z",  hash_password("coach123"),   "赵六", "13800000004", 1),
        (5, 4, "member_q", hash_password("member123"),  "钱七", "13800000005", 1),
        (6, 4, "member_s", hash_password("member123"),  "孙八", "13800000006", 1),
        (7, 4, "member_z", hash_password("member123"),  "周九", "13800000007", 1),
        (8, 4, "member_w", hash_password("member123"),  "吴十", "13800000008", 1),
    ]
    cur.executemany(
        "INSERT INTO sys_user (user_id, role_id, username, password, real_name, phone, status) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        users,
    )

    # ========== 5. sys_user_profile 用户档案 ==========
    profiles = [
        (1, 1, 10, 1, "1990-03-15", 178.00, 75.00, None, "系统超级管理员", "2024-01-01 09:00:00", "2024-01-01 09:00:00", None),
        (2, 2,  8, 1, "1992-07-22", 172.00, 65.00, None, "运营负责人",     "2024-02-15 10:00:00", "2024-02-15 10:00:00", None),
        (3, 3,  7, 1, "1995-01-10", 180.00, 82.00, None, "力量训练教练",   "2024-03-01 08:00:00", "2024-03-01 08:00:00", "2026-03-01"),
        (4, 4,  6, 2, "1993-11-05", 168.00, 58.00, None, "瑜伽/有氧教练", "2024-03-10 08:00:00", "2024-03-10 08:00:00", "2026-03-10"),
        (5, 5,  3, 1, "1998-05-20", 175.00, 70.00, None, "健身爱好者",     "2025-01-10 14:00:00", "2025-01-10 14:00:00", "2026-01-10"),
        (6, 6,  2, 2, "2000-09-08", 162.00, 52.00, None, "瑜伽爱好者",     "2025-02-20 16:00:00", "2025-02-20 16:00:00", "2026-02-20"),
        (7, 7,  1, 1, "1997-12-01", 182.00, 88.00, None, "新手会员",       "2025-06-01 11:00:00", "2025-06-01 11:00:00", "2026-06-01"),
        (8, 8,  1, 2, "2001-04-18", 160.00, 50.00, None, "新手会员",       "2025-06-15 09:00:00", "2025-06-15 09:00:00", "2026-06-15"),
    ]
    cur.executemany(
        "INSERT INTO sys_user_profile (profile_id, user_id, `level`, gender, birthday, height_cm, weight_kg, avatar_url, intro, create_time, join_time, expire_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        profiles,
    )

    # ========== 6. t_store_province 省份 ==========
    provinces = [
        (1, "北京市", 116.407526, 39.904030),
        (2, "上海市", 121.473701, 31.230416),
        (3, "广东省", 113.264385, 23.129112),
        (4, "四川省", 104.065735, 30.659462),
    ]
    cur.executemany(
        "INSERT INTO t_store_province (province_id, province_name, center_lng, center_lat) VALUES (%s,%s,%s,%s)",
        provinces,
    )

    # ========== 7. t_store 门店 ==========
    stores = [
        (1, "IronForge 北京旗舰店", 1, 1, "北京市", "朝阳区", "建国路88号", "010-88886666", None, None, "2000㎡旗舰铁馆，器械齐全", "06:00-23:00", 1, 116.461770, 39.909187),
        (2, "IronForge 上海中心店", 1, 2, "上海市", "浦东新区", "陆家嘴环路100号", "021-66668888", None, None, "陆家嘴核心商圈铁馆", "07:00-22:00", 1, 121.500485, 31.235490),
        (3, "FitLife 广州天河私教馆", 2, 3, "广东省", "广州市", "天河区天河路200号", "020-33334444", None, None, "精品私教工作室", "08:00-21:00", 1, 113.328945, 23.136812),
        (4, "FitLife 深圳南山私教馆", 2, 3, "广东省", "深圳市", "南山区科技园路50号", "0755-22223333", None, None, "科技感私教空间", "08:00-22:00", 1, 113.930586, 22.540150),
        (5, "IronForge 成都春熙店", 1, 4, "四川省", "成都市", "锦江区春熙路66号", "028-55556666", None, None, "潮流铁馆，年轻人的健身聚集地", "06:30-23:30", 1, 104.080872, 30.657340),
    ]
    cur.executemany(
        "INSERT INTO t_store (store_id, store_name, store_type, province_id, province_name, city, district, address, store_phone, store_image_url, store_introduction, business_hours, is_operating, store_lng, store_lat) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        stores,
    )

    # ========== 8. y_user_store 用户-门店关联 ==========
    user_stores = [
        (1, 1, 1, 1),   # admin → 北京旗舰店 (超级管理员)
        (2, 2, 2, 2),   # operator → 上海中心店 (运营管理员)
        (3, 3, 3, 1),   # coach_w → 北京旗舰店 (教练)
        (4, 4, 3, 3),   # coach_z → 广州天河私教馆 (教练)
        (5, 5, 4, 1),   # member_q → 北京旗舰店 (会员)
        (6, 6, 4, 3),   # member_s → 广州天河私教馆 (会员)
        (7, 7, 4, 5),   # member_z → 成都春熙店 (会员)
        (8, 8, 4, 2),   # member_w → 上海中心店 (会员)
    ]
    cur.executemany(
        "INSERT INTO y_user_store (id, user_id, role_id, store_id) VALUES (%s,%s,%s,%s)",
        user_stores,
    )

    # ========== 9. t_course_category 课程分类 ==========
    course_cats = [
        (1, "力量训练", None, "提升肌肉力量和耐力的训练课程", 1),
        (2, "有氧训练", None, "提高心肺功能和燃烧脂肪的训练", 1),
        (3, "柔韧训练", None, "提升身体柔韧性和关节活动度", 1),
        (4, "功能性训练", None, "提升日常运动能力和核心稳定性", 1),
    ]
    cur.executemany(
        "INSERT INTO t_course_category (category_id, category_name, category_url, description, status) VALUES (%s,%s,%s,%s,%s)",
        course_cats,
    )

    # ========== 10. t_course 课程 ==========
    courses = [
        (1,  "杠铃深蹲入门",     1, 2, 45, 20, "每周一/三/五 10:00", "从零开始学习杠铃深蹲，掌握正确姿势和发力技巧", 1),
        (2,  "卧推力量提升",     1, 3, 60, 15, "每周二/四 14:00",     "系统性卧推训练计划，适合有一定基础的训练者", 1),
        (3,  "HIIT 燃脂风暴",    2, 3, 30, 30, "每天 09:00/19:00",    "高强度间歇训练，30分钟高效燃脂", 1),
        (4,  "动感单车进阶",     2, 2, 45, 25, "每周一/三/五 18:00", "模拟户外骑行的室内有氧课程", 1),
        (5,  "流瑜伽基础",       3, 1, 60, 20, "每周二/四/六 08:00", "以呼吸串联体式的瑜伽入门课程", 1),
        (6,  "普拉提核心",       3, 2, 50, 15, "每周一/三 16:00",     "强化核心肌群，改善体态的普拉提课程", 1),
        (7,  "壶铃功能性训练",   4, 3, 45, 12, "每周三/五 17:00",     "使用壶铃进行全身功能性训练", 1),
        (8,  "TRX 悬挂训练",     4, 2, 40, 10, "每周二/四 11:00",     "利用自身体重的悬挂式全身训练", 1),
    ]
    cur.executemany(
        "INSERT INTO t_course (course_id, course_name, category_id, course_difficulty, duration_minutes, max_participants, schedule_info, description, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        courses,
    )

    # ========== 11. y_user_course_favorite 课程收藏 ==========
    course_favs = [
        (1, 5, 1),   # member_q 收藏 杠铃深蹲入门
        (2, 5, 3),   # member_q 收藏 HIIT 燃脂风暴
        (3, 6, 5),   # member_s 收藏 流瑜伽基础
        (4, 6, 6),   # member_s 收藏 普拉提核心
        (5, 7, 7),   # member_z 收藏 壶铃功能性训练
        (6, 8, 3),   # member_w 收藏 HIIT 燃脂风暴
    ]
    cur.executemany(
        "INSERT INTO y_user_course_favorite (favorite_id, user_id, course_id) VALUES (%s,%s,%s)",
        course_favs,
    )

    # ========== 12. t_action_category 动作分类 ==========
    action_cats = [
        (1, "胸部", None),
        (2, "背部", None),
        (3, "腿部", None),
        (4, "肩部", None),
    ]
    cur.executemany(
        "INSERT INTO t_action_category (category_id, category_name, category_image_url) VALUES (%s,%s,%s)",
        action_cats,
    )

    # ========== 13. t_action 动作 ==========
    actions = [
        (1,  "平板杠铃卧推",   1, 2, None, "仰卧于平板凳，双手握杠铃下放至胸部上方后推起", "肩胛骨收紧下沉，手腕保持中立位", "杠铃、平板卧推凳", 1),
        (2,  "上斜哑铃卧推",   1, 2, None, "仰卧于30-45°上斜凳，双手持哑铃推举", "控制下放速度，顶部不要完全锁死肘关节", "哑铃、上斜卧推凳", 1),
        (3,  "龙门架夹胸",     1, 1, None, "站在龙门架中间，双手握住把手向中间合拢", "保持微屈肘，感受胸肌收缩", "龙门架", 1),
        (4,  "引体向上",       2, 3, None, "双手正握单杠，身体悬垂后拉起至下巴过杠", "核心收紧避免摆动，全程控制", "单杠", 1),
        (5,  "杠铃划船",       2, 2, None, "俯身45°，双手握杠铃沿大腿拉向腹部", "保持背部平直，用背阔肌发力", "杠铃", 1),
        (6,  "坐姿绳索划船",   2, 1, None, "坐在绳索机前，双手握住把手拉向腹部", "挺胸收腹，肩胛骨后缩", "绳索机", 1),
        (7,  "杠铃深蹲",       3, 3, None, "杠铃置于斜方肌上方，下蹲至大腿平行地面后站起", "膝盖方向与脚尖一致，核心全程收紧", "杠铃、深蹲架", 1),
        (8,  "罗马尼亚硬拉",   3, 2, None, "双手握杠铃，微屈膝，屈髋下放杠铃至膝盖下方", "保持背部平直，感受腘绳肌拉伸", "杠铃", 1),
        (9,  "保加利亚分腿蹲", 3, 2, None, "后脚搭在凳上，前脚单腿蹲起", "躯干保持直立，重心在前脚", "哑铃、训练凳", 1),
        (10, "哑铃推举",       4, 2, None, "坐姿，双手持哑铃从肩部向上推举", "不要过度后仰，控制下放速度", "哑铃、训练凳", 1),
        (11, "哑铃侧平举",     4, 1, None, "站立，双手持哑铃向两侧平举至肩高", "肘部微屈，不要耸肩", "哑铃", 1),
        (12, "面拉",           4, 1, None, "使用绳索面向机器，双手拉向面部两侧", "外旋肩关节，挤压后三角肌", "绳索机、绳索", 1),
    ]
    cur.executemany(
        "INSERT INTO t_action (action_id, action_name, category_id, action_difficulty, action_image_url, action_steps, attention_points, applicable_equipment, applicable_store_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        actions,
    )

    # ========== 14. y_user_action_favorite 动作收藏 ==========
    action_favs = [
        (1, 5, 1),    # member_q 收藏 平板杠铃卧推
        (2, 5, 7),    # member_q 收藏 杠铃深蹲
        (3, 6, 5),    # member_s 收藏 杠铃划船
        (4, 7, 10),   # member_z 收藏 哑铃推举
        (5, 7, 11),   # member_z 收藏 哑铃侧平举
        (6, 8, 3),    # member_w 收藏 龙门架夹胸
    ]
    cur.executemany(
        "INSERT INTO y_user_action_favorite (favorite_id, user_id, action_id) VALUES (%s,%s,%s)",
        action_favs,
    )

    # ========== 15. t_slogan_info 标语 ==========
    slogans = [
        (1, "坚持铸就卓越",   "每一次举起，都是对自我的超越。坚持，让平凡变非凡。", None, 1),
        (2, "科学训练 健康生活", "用科学的方法训练，用健康的态度生活。", None, 1),
        (3, "今天流汗 明天发光", "汗水不会骗人，每一滴都在为未来的你蓄力。", None, 1),
    ]
    cur.executemany(
        "INSERT INTO t_slogan_info (slogan_id, slogan_name, slogan_content, slogan_image_url, status) VALUES (%s,%s,%s,%s,%s)",
        slogans,
    )

    # ========== 16. t_activity_event 赛事活动 ==========
    events = [
        (1, "2025 IronForge 力量挑战赛", "2025-08-15", "北京旗舰店", "报名中", "年度力量举比赛，设深蹲、卧推、硬拉三个项目，分男女组别竞技。", "力量举,比赛,竞技", "冠军奖金 5000 元 + 年度会员卡", "200人规模"),
        (2, "夏日燃脂 30 天挑战",        "2025-07-01", "全门店线上", "早鸟票", "为期30天的线上燃脂挑战，每日打卡记录体重变化，最终减脂比例最高者获胜。", "减脂,挑战,线上", "冠军奖金 2000 元 + 私教课 10 节", "不限人数"),
        (3, "瑜伽冥想周末工作坊",        "2025-09-20", "广州天河私教馆", "预告", "邀请知名瑜伽导师带领的两天深度工作坊，涵盖流瑜伽、阴瑜伽和冥想。", "瑜伽,冥想,工作坊", "参与者获赠瑜伽垫 + 水壶", "30人小班"),
    ]
    cur.executemany(
        "INSERT INTO t_activity_event (event_id, title, event_date, location, status, description, tags, prize, `scale`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        events,
    )

    conn.commit()
    print("[2/2] 全部数据写入成功")

    # ========== 统计 ==========
    stats = []
    for t in ["sys_permission","sys_role","sys_role_permission","sys_user","sys_user_profile",
              "t_store_province","t_store","y_user_store","t_course_category","t_course",
              "y_user_course_favorite","t_action_category","t_action","y_user_action_favorite",
              "t_slogan_info","t_activity_event"]:
        cur.execute(f"SELECT COUNT(*) FROM `{t}`")
        count = cur.fetchone()[0]
        stats.append(f"  {t:30s} {count:>4} 条")
    print("\n数据统计:")
    print("\n".join(stats))

except Exception as e:
    conn.rollback()
    print(f"写入失败，已回滚: {e}")
    raise
finally:
    cur.close()
    conn.close()
