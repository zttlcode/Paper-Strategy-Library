import baostock as bs
import pandas as pd


def getData_BaoStock_live(asset, start_date, end_date, timeLevel):
    # 股票所有数据都能拿到，指数只有日线
    code = None
    # 股票：6开头sh，0或3开头sz
    # 指数：3开头是sz
    if asset.assetCode.startswith('6'):
        code = 'sh.' + asset.assetCode
    elif asset.assetCode.startswith('0') or asset.assetCode.startswith('3'):
        code = 'sz.' + asset.assetCode
        if asset.assetsType == 'index':
            # 如果只根据名字判断，0,3以外全是sh，那指数0开头的代码只能加sh.前缀，才满足else，但文件名多了个sh.不好看，所以加这个assetsType
            # 当然影响不只是csv文件名，如果用mysql存，存表名是000001是股票，还是指数，还得区分，因此这个变量得加
            code = 'sh.' + asset.assetCode
    if timeLevel == 'd':
        # 日线数据，股票和指数接口一样
        rs = bs.query_history_k_data_plus(code,
                                          "date,open,high,low,close,volume",
                                          start_date=start_date, end_date=end_date,
                                          frequency="d", adjustflag="3")
    # 打印结果集
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    if 0 != len(data_list):
        if 'd' == timeLevel:
            result.loc[:, 'date'] = pd.to_datetime(result.loc[:, 'date'])
            result.rename(columns={'date': 'time'}, inplace=True)  # 为了和分钟级bar保持一致，修改列名为time
    windowDF = cut_by_bar_num(result, 250)
    # 登出系统
    return windowDF


def cut_by_bar_num(df, bar_num):
    # 实盘只要bar_num条，最新的数据，够算指标就行，所以这里截断没用的旧数据
    length = len(df)
    if length >= bar_num:
        window = length - bar_num  # 起始下标比如是0~250，bar_num是250，iloc含头不含尾
        windowDF = df.iloc[window:length].copy()  # copy不改变原对象，不加copy会有改变临时对象的警告
        return windowDF
    else:
        # 数据不够bar_num条，就不用截取了
        return df

