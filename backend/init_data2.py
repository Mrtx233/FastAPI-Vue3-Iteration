"""
增量权限脚本：省份区域、门店、用户门店关联、课程收藏、动作收藏、
课程/课程分类/动作/动作分类 CRUD 权限
仅追加 init_data.py / init_data1.py 中未包含的新权限和角色权限关联
"""
import pymysql
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
    # ========== 1. 新增权限定义 ==========
    new_permissions = [
        (33, "province:create",         "创建省份区域",       None),
        (34, "province:edit",           "编辑省份区域",       None),
        (35, "province:delete",         "删除省份区域",       None),
        (36, "store:create",            "创建门店",           None),
        (37, "store:edit",              "编辑门店",           None),
        (38, "store:delete",            "删除门店",           None),
        (39, "user_store:create",       "创建用户门店关联",   None),
        (40, "user_store:edit",         "编辑用户门店关联",   None),
        (41, "user_store:delete",       "删除用户门店关联",   None),
        (42, "course_favorite:create",  "收藏课程",           None),
        (43, "course_favorite:edit",    "编辑课程收藏",       None),
        (44, "course_favorite:delete",  "删除课程收藏",       None),
        (45, "action_favorite:create",  "收藏动作",           None),
        (46, "action_favorite:edit",    "编辑动作收藏",       None),
        (47, "action_favorite:delete",  "删除动作收藏",       None),
        # --- 课程 / 课程分类 CRUD ---
        (48, "course:create",           "创建课程",           None),
        (49, "course:edit",             "编辑课程",           None),
        (50, "course:delete",           "删除课程",           None),
        (51, "course_category:create",  "创建课程分类",       None),
        (52, "course_category:edit",    "编辑课程分类",       None),
        (53, "course_category:delete",  "删除课程分类",       None),
        # --- 动作 / 动作分类 CRUD ---
        (54, "action:create",           "创建动作",           None),
        (55, "action:edit",             "编辑动作",           None),
        (56, "action:delete",           "删除动作",           None),
        (57, "action_category:create",  "创建动作分类",       None),
        (58, "action_category:edit",    "编辑动作分类",       None),
        (59, "action_category:delete",  "删除动作分类",       None),
        # --- 文件上传 ---
        (60, "file:upload",             "上传文件",           None),
    ]

    for perm in new_permissions:
        cur.execute(
            "SELECT 1 FROM sys_permission WHERE id = %s", (perm[0],)
        )
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO sys_permission (id, permission_code, permission_name, menu_path) VALUES (%s,%s,%s,%s)",
                perm,
            )
            print(f"  新增权限: {perm[1]} (id={perm[0]})")
        else:
            print(f"  已存在跳过: {perm[1]} (id={perm[0]})")

    # ========== 2. 为超级管理员和运营管理员分配全部新权限 ==========
    admin_roles = [1, 2]  # super_admin, operator
    all_new_perm_ids = [p[0] for p in new_permissions]

    for role_id in admin_roles:
        for perm_id in all_new_perm_ids:
            cur.execute(
                "SELECT 1 FROM sys_role_permission WHERE role_id = %s AND permission_id = %s",
                (role_id, perm_id),
            )
            if cur.fetchone() is None:
                cur.execute(
                    "INSERT INTO sys_role_permission (role_id, permission_id) VALUES (%s,%s)",
                    (role_id, perm_id),
                )
                print(f"  角色 {role_id} 分配权限 {perm_id}")
            else:
                print(f"  角色 {role_id} 已拥有权限 {perm_id}，跳过")

    # ========== 3. 为教练和会员分配收藏的增删权限（不含 edit） ==========
    user_roles = [3, 4]  # coach, member
    favorite_user_perm_ids = [42, 44, 45, 47]  # create + delete only

    for role_id in user_roles:
        for perm_id in favorite_user_perm_ids:
            cur.execute(
                "SELECT 1 FROM sys_role_permission WHERE role_id = %s AND permission_id = %s",
                (role_id, perm_id),
            )
            if cur.fetchone() is None:
                cur.execute(
                    "INSERT INTO sys_role_permission (role_id, permission_id) VALUES (%s,%s)",
                    (role_id, perm_id),
                )
                print(f"  角色 {role_id} 分配收藏权限 {perm_id}")
            else:
                print(f"  角色 {role_id} 已拥有权限 {perm_id}，跳过")

    # ========== 4. 为所有角色分配文件上传权限 ==========
    all_roles = [1, 2, 3, 4]
    upload_perm_id = 60

    for role_id in all_roles:
        cur.execute(
            "SELECT 1 FROM sys_role_permission WHERE role_id = %s AND permission_id = %s",
            (role_id, upload_perm_id),
        )
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO sys_role_permission (role_id, permission_id) VALUES (%s,%s)",
                (role_id, upload_perm_id),
            )
            print(f"  角色 {role_id} 分配上传权限 {upload_perm_id}")
        else:
            print(f"  角色 {role_id} 已拥有权限 {upload_perm_id}，跳过")

    conn.commit()
    print("\n[OK] 省份/门店/用户门店/收藏/课程/动作 CRUD 权限写入成功")

    # ========== 统计 ==========
    cur.execute("SELECT COUNT(*) FROM sys_permission")
    perm_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM sys_role_permission WHERE role_id IN (1,2) AND permission_id >= 33")
    rp_admin = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM sys_role_permission WHERE role_id IN (3,4) AND permission_id >= 42")
    rp_user = cur.fetchone()[0]
    print(f"  sys_permission 总计: {perm_count} 条")
    print(f"  管理员角色权限关联(role 1,2, perm>=33): {rp_admin} 条")
    print(f"  用户收藏权限关联(role 3,4, perm>=42): {rp_user} 条")

except Exception as e:
    conn.rollback()
    print(f"写入失败，已回滚: {e}")
    raise
finally:
    cur.close()
    conn.close()
