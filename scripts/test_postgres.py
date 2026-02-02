#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试PostgreSQL连接
"""

import psycopg2
from psycopg2 import sql
from typing import Optional

def test_postgres_connection(
        host: str = "localhost",
        port: int = 5432,
        database: str = "a_stock_data",
        user: str = "parallels",
        password: str = "Zy511522@1"
) -> Optional[str]:
    """
    测试PostgreSQL连接

    Returns:
        错误信息（如果失败），否则None
    """
    try:
        print("🔗 正在连接PostgreSQL...")
        print(f"  主机: {host}")
        print(f"  端口: {port}")
        print(f"  数据库: {database}")
        print(f"  用户: {user}")

        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )

        cursor = conn.cursor()

        # 执行查询
        cursor.execute("SELECT version();")
        version = cursor.fetchone()

        cursor.execute("SELECT current_database(), current_user;")
        db_info = cursor.fetchone()

        print(f"\n✅ 连接成功！")
        print(f"  PostgreSQL版本: {version[0]}")
        print(f"  当前数据库: {db_info[0]}")
        print(f"  当前用户: {db_info[1]}")

        cursor.close()
        conn.close()

        return None

    except psycopg2.Error as e:
        error_msg = f"❌ 数据库连接失败: {e}"
        print(error_msg)
        return error_msg

    except Exception as e:
        error_msg = f"❌ 未知错误: {e}"
        print(error_msg)
        return error_msg

def test_database_tables() -> bool:
    """检查数据库表"""
    try:
        print("\n📊 检查数据库表...")

        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="a_stock_data",
            user="parallels",
            password="Zy511522@1"
        )

        cursor = conn.cursor()

        # 获取所有表
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()

        if tables:
            print(f"\n✅ 找到 {len(tables)} 个表:")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("\n⚠️ 数据库为空，没有表")

        cursor.close()
        conn.close()

        return True

    except psycopg2.Error as e:
        print(f"\n❌ 检查表失败: {e}")
        return False

if __name__ == "__main__":
    print("="*80)
    print("🧪 测试PostgreSQL连接")
    print("="*80)

    # 测试连接
    error = test_postgres_connection()

    if error:
        print(f"\n❌ 请检查:")
        print("  1. PostgreSQL是否已安装")
        print("  2. 服务是否已启动: sudo systemctl status postgresql")
        print("  3. 数据库是否已创建")
        print("  4. 用户和密码是否正确")
        print("  5. 配置文件是否允许本地连接: /etc/postgresql/16/main/pg_hba.conf")
        print("\n🔧 修复命令:")
        print("  # 启动服务")
        print("  sudo systemctl start postgresql")
        print("  # 重启服务")
        print("  sudo systemctl restart postgresql")
        print("  # 检查配置")
        print("  sudo nano /etc/postgresql/16/main/pg_hba.conf")
    else:
        # 测试表
        test_database_tables()

        print("\n" + "="*80)
        print("✅ 数据库验证完成！")
        print("="*80)
