import sqlite3


def get_connection():
    # 使用SQLite数据库替代SQL Server
    database_path = 'financial_analysis.db'
    return sqlite3.connect(database_path)


# 日志写入数据库
def Log(lx, page, action, msg):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        sql_string = "insert into t_hz_spyder_dd_log(lx,page,action,msg) values(?, ?, ?, ?)"
        lst = [lx, page, action, msg]
        connection.execute(sql_string, lst)
        connection.commit()
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()


def insert_zcfzb(data):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        # 创建唯一索引，防止code和disclosure_date重复
        cursor.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS idx_zcfzb_code_disclosure_date 
            ON 资产负债表temp(code, disclosure_date)
        ''')
        
        # 使用INSERT OR IGNORE防止重复插入
        sql_string = """INSERT OR IGNORE INTO 资产负债表temp
                    (   code,name,total_assets,total_liabilities,paid_in_capital,capital_reserve,
                        other_comprehensive_income,surplus_reserve,undistributed_profits,
                        minority_shareholder_equity,disclosure_date,insert_batch,accounts_receivable
                    )
                    VALUES
                    (   ?,?,?,?,?,?,?,?,?,?,?,?,?)"""
        cursor.executemany(sql_string, data)
        connection.commit()
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()

def insert_lrb(data):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        # 创建唯一索引，防止code和disclosure_date重复
        cursor.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS idx_lrb_code_disclosure_date 
            ON 利润表temp(code, disclosure_date)
        ''')
        
        # 使用INSERT OR IGNORE防止重复插入
        sql_string = """INSERT OR IGNORE INTO 利润表temp
                    (   code,name,net_profit,total_operating_income,total_operating_cost,sales_expenses,
                        management_expenses,financial_expenses,operating_costs,operating_profit,
                        total_profit,disclosure_date,RandD_expenses,business_tax_and_surcharges,insert_batch,interest_expenses
                        ,interest_income,gross_profit,gross_profit_margin,netProfitFromOngoingOperations,netProfitAttributableToTheParentCompany,netProfitAfterDeductingNonRecurringGainsAndLosses
                        ,yearOnYearGrowthInTotalOperatingRevenue
                    )
                    VALUES
                    (   ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
        cursor.executemany(sql_string, data)
        connection.commit()
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()