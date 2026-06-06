"""
增量权限脚本：标语和活动 CRUD 权限
仅追加 init_data.py 中未包含的新权限和角色权限关联
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
        (27, "slogan:create",  "创建标语",  None),
        (28, "slogan:edit",    "编辑标语",  None),
        (29, "slogan:delete",  "删除标语",  None),
        (30, "activity:create", "创建活动", None),
        (31, "activity:edit",   "编辑活动", None),
        (32, "activity:delete", "删除活动", None),
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

    # ========== 2. 为超级管理员和运营管理员分配新权限 ==========
    target_roles = [1, 2]  # super_admin, operator
    new_perm_ids = [p[0] for p in new_permissions]

    for role_id in target_roles:
        for perm_id in new_perm_ids:
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

    conn.commit()
    print("\n[OK] 标语/活动 CRUD 权限写入成功")

    # ========== 统计 ==========
    cur.execute("SELECT COUNT(*) FROM sys_permission")
    perm_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM sys_role_permission WHERE role_id IN (1,2) AND permission_id >= 27")
    rp_count = cur.fetchone()[0]
    print(f"  sys_permission 总计: {perm_count} 条")
    print(f"  新增角色权限关联(role 1,2): {rp_count} 条")

except Exception as e:
    conn.rollback()
    print(f"写入失败，已回滚: {e}")
    raise
finally:
    cur.close()
    conn.close()
