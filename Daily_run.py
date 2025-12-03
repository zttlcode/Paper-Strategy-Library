import pandas as pd
import numpy as np
import baostock as bs
import warnings
import Data.Asset as PSLAsset
import Data.HistoryData as PSLHistoryData

import Strategy.Fuzzy as Strategy_Fuzzy

warnings.filterwarnings("ignore", category=FutureWarning, module="pandas")


def run_daily(asset, df):
    # 确保索引是时间类型，250个交易日的数据对策略来说够用，因此截取之前的
    live_df = df[-250:].copy()
    live_df.set_index('time', inplace=True)
    live_df.index = pd.to_datetime(live_df.index)
    live_df = df[-250:].reset_index(drop=True)
    # 提取最新价格、时间、成交量
    asset.tick_close = live_df.iloc[-1]['close']
    asset.tick_time = live_df.iloc[-1]['time']
    asset.tick_volume = live_df.iloc[-1]['volume']

    # 运行策略
    if asset.strategy_name == 'fuzzy':
        Strategy_Fuzzy.strategy_fuzzy(asset, live_df)
    else:
        print("未指定策略")
    # 有交易，则打印信息
    if asset.positionEntity.trade_point_list:
        print(asset.assetsCode, strategy_name, asset.positionEntity.trade_point_list)


if __name__ == '__main__':
    """
    调用时间：交易日每天17:30后运行
    """
    strategy_name = "fuzzy"  # 这里填策略

    # 读取股票代码。沪深300+中证500
    allStockCode = pd.read_csv("./QuantData/asset_code/a800_stocks.csv", dtype={'code': str})
    # 调用证券宝获取每个股票的历史行情数据
    bs.login()
    for index, row in allStockCode.iterrows():
        # 把股票信息、选取的策略、仓位记录都放在Asset对象中。
        asset = PSLAsset.Asset(row['code'][3:], row['code_name'], strategy_name, 'stock')
        # 获取今天日期
        today = pd.Timestamp.today().normalize()
        # 获取行情数据
        df = PSLHistoryData.getData_BaoStock_live(asset, '', today.strftime('%Y-%m-%d'), 'd')
        # 判断行情数据是今天的，再执行策略，否则跳过此股
        df_tmp = df.copy()
        df_tmp['time'] = pd.to_datetime(df_tmp['time'])
        last_date = df_tmp['time'].iloc[-1]
        if last_date != today:
            print(asset.assetsCode, last_date, "日期不是今天，跳过")
            continue
        # 行情数据没问题，调整数据格式
        # 将指定列转换为 float 类型
        df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
        # 将 volume 列转换为 int 类型
        df['volume'] = df['volume'].replace('', np.nan)
        df['volume'] = df['volume'].fillna(0)  # 用 0 填充缺失值
        df['volume'] = df['volume'].astype('int64')
        # 运行策略
        run_daily(asset, df)
    bs.logout()
