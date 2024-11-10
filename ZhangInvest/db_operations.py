import sqlite3

# 连接数据库
def connect_db():
    return sqlite3.connect('fundsdb.sqlite')

# 查询所有基金信息
def fetch_all_funds():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM funds')
    funds = cursor.fetchall()
    conn.close()
    return funds

# 插入基金信息
def insert_fund(fund_code, fund_name, is_domestic):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO funds (fund_code, fund_name, is_domestic)
        VALUES (?, ?, ?)
    ''', (fund_code, fund_name, is_domestic))
    conn.commit()
    conn.close()

# 删除基金信息
def remove_fund(fund_code):
    conn = connect_db()
    cursor = conn.cursor()
    # 删除基金的所有交易记录
    cursor.execute('DELETE FROM transactions WHERE fund_code = ?', (fund_code,))
    # 删除基金信息
    cursor.execute('DELETE FROM funds WHERE fund_code = ?', (fund_code,))
    conn.commit()
    conn.close()

# 查询某个基金的所有交易记录
def fetch_transactions_by_fund(fund_code):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT transaction_time, transaction_type, transaction_amount, confirmed_shares, transaction_fee
        FROM transactions
        WHERE fund_code = ?
        ORDER BY transaction_time
    ''', (fund_code,))
    transactions = cursor.fetchall()
    conn.close()
    return transactions

# 插入交易记录
def insert_transaction(fund_code, transaction_type, transaction_time, transaction_amount, confirmed_shares=None, transaction_fee=None):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (fund_code, transaction_type, transaction_time, transaction_amount, confirmed_shares, transaction_fee)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (fund_code, transaction_type, transaction_time, transaction_amount, confirmed_shares, transaction_fee))
    conn.commit()
    conn.close()

# 删除交易记录
def delete_transaction(fund_code, transaction_time, transaction_type, transaction_amount):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM transactions
        WHERE fund_code = ? AND transaction_time = ? AND transaction_type = ? AND transaction_amount = ?
    ''', (fund_code, transaction_time, transaction_type, transaction_amount))
    conn.commit()
    conn.close()