import sqlite3


# 连接数据库
def connect_db():
    return sqlite3.connect('fundsdb.sqlite')


# 查询某个基金的所有已成交交易记录
def fetch_confirmed_transactions(fund_code):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT transaction_type, transaction_amount, confirmed_shares
        FROM transactions
        WHERE fund_code = ? AND confirmed_shares IS NOT NULL
    ''', (fund_code,))
    transactions = cursor.fetchall()
    conn.close()
    return transactions


# 计算基金的持有份额和持仓成本价
def calculate_fund_holdings(fund_code):
    transactions = fetch_confirmed_transactions(fund_code)

    if not transactions:
        print(f"基金 {fund_code} 没有已成交的交易记录。")
        return

    total_shares = 0.0  # 持有份额
    total_amount = 0.0  # 购入金额

    for transaction_type, transaction_amount, confirmed_shares in transactions:
        if transaction_type in ["买入", "定投"]:  # 买入或定投
            total_shares += confirmed_shares
            total_amount += transaction_amount
        elif transaction_type in ["卖出", "转换"]:  # 卖出或转换
            total_shares -= transaction_amount
            total_amount -= confirmed_shares

    # 计算持仓成本价
    if total_shares > 0:
        cost_price = total_amount / total_shares  # 保留小数点后四位
        cost_price = round(cost_price, 4)
        print(f"基金 {fund_code} 的持有份额为: {total_shares} 份，持仓成本价为: {cost_price} 元")
    else:
        print(f"基金 {fund_code} 当前没有持有份额，无法计算持仓成本价。")


# 查询所有基金并计算每个基金的持有份额和持仓成本价
def calculate_all_funds():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT fund_code FROM funds')
    funds = cursor.fetchall()
    conn.close()

    for fund_code_tuple in funds:
        fund_code = fund_code_tuple[0]
        calculate_fund_holdings(fund_code)


if __name__ == "__main__":
    calculate_all_funds()