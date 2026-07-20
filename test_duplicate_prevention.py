import sqlserver_operation as db
import sqlite3

# 连接数据库并准备表结构
def setup_tables():
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # 创建资产负债表temp表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS 资产负债表temp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT,
            name TEXT,
            total_assets REAL,
            total_liabilities REAL,
            paid_in_capital REAL,
            capital_reserve REAL,
            other_comprehensive_income REAL,
            surplus_reserve REAL,
            undistributed_profits REAL,
            minority_shareholder_equity REAL,
            disclosure_date TEXT,
            insert_batch INTEGER,
            accounts_receivable REAL
        )
    ''')
    
    # 创建利润表temp表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS 利润表temp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT,
            name TEXT,
            net_profit REAL,
            total_operating_income REAL,
            total_operating_cost REAL,
            sales_expenses REAL,
            management_expenses REAL,
            financial_expenses REAL,
            operating_costs REAL,
            operating_profit REAL,
            total_profit REAL,
            disclosure_date TEXT,
            RandD_expenses REAL,
            business_tax_and_surcharges REAL,
            insert_batch INTEGER,
            interest_expenses REAL,
            interest_income REAL,
            gross_profit REAL,
            gross_profit_margin REAL,
            netProfitFromOngoingOperations REAL,
            netProfitAttributableToTheParentCompany REAL,
            netProfitAfterDeductingNonRecurringGainsAndLosses REAL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("表结构准备完成")

# 测试资产负债表重复插入预防
def test_zcfzb_duplicate_prevention():
    print("\n测试资产负债表重复插入预防...")
    
    # 测试数据
    zcfzb_data = [
        ('600000', '浦发银行', 1000000, 800000, 100000, 50000, 10000, 20000, 10000, 10000, '2023-12-31', 1, 50000),
        ('600000', '浦发银行', 1000000, 800000, 100000, 50000, 10000, 20000, 10000, 10000, '2023-12-31', 1, 50000),  # 重复记录
        ('600001', '邯郸钢铁', 2000000, 1500000, 200000, 100000, 20000, 40000, 20000, 20000, '2023-12-31', 1, 100000)
    ]
    
    # 插入数据
    db.insert_zcfzb(zcfzb_data)
    
    # 检查插入结果
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM 资产负债表temp")
    count = cursor.fetchone()[0]
    print(f"资产负债表temp表中记录数: {count}")
    print(f"预期记录数: 2 (应过滤掉1条重复记录)")
    
    # 显示所有记录
    cursor.execute("SELECT code, name, disclosure_date FROM 资产负债表temp")
    records = cursor.fetchall()
    print("插入的记录:")
    for record in records:
        print(f"  {record}")
    
    conn.close()
    return count == 2

# 测试利润表重复插入预防
def test_lrb_duplicate_prevention():
    print("\n测试利润表重复插入预防...")
    
    # 测试数据
    lrb_data = [
        ('600000', '浦发银行', 50000, 200000, 150000, 10000, 15000, 5000, 100000, 30000, 40000, '2023-12-31', 8000, 2000, 1, 3000, 2000, 100000, 0.5, 45000, 48000, 42000),
        ('600000', '浦发银行', 50000, 200000, 150000, 10000, 15000, 5000, 100000, 30000, 40000, '2023-12-31', 8000, 2000, 1, 3000, 2000, 100000, 0.5, 45000, 48000, 42000),  # 重复记录
        ('600001', '邯郸钢铁', 80000, 300000, 220000, 15000, 20000, 8000, 150000, 50000, 60000, '2023-12-31', 12000, 3000, 1, 5000, 3000, 180000, 0.6, 70000, 75000, 65000)
    ]
    
    # 插入数据
    db.insert_lrb(lrb_data)
    
    # 检查插入结果
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM 利润表temp")
    count = cursor.fetchone()[0]
    print(f"利润表temp表中记录数: {count}")
    print(f"预期记录数: 2 (应过滤掉1条重复记录)")
    
    # 显示所有记录
    cursor.execute("SELECT code, name, disclosure_date FROM 利润表temp")
    records = cursor.fetchall()
    print("插入的记录:")
    for record in records:
        print(f"  {record}")
    
    conn.close()
    return count == 2

# 清理测试数据
def cleanup():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM 资产负债表temp")
    cursor.execute("DELETE FROM 利润表temp")
    conn.commit()
    conn.close()
    print("\n测试数据清理完成")

# 运行测试
if __name__ == "__main__":
    setup_tables()
    
    try:
        zcfzb_test_passed = test_zcfzb_duplicate_prevention()
        lrb_test_passed = test_lrb_duplicate_prevention()
        
        print("\n" + "="*50)
        if zcfzb_test_passed and lrb_test_passed:
            print("✅ 所有测试通过！重复插入预防功能正常工作")
        else:
            print("❌ 部分测试失败！重复插入预防功能存在问题")
    finally:
        cleanup()
