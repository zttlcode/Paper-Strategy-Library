import json
import Tools as RMTTools


class Asset:
    def __init__(self, assetsCode, assetsName, strategy_name, assetsType):
        # 股票信息
        self.assetsCode = assetsCode
        self.assetsName = assetsName
        self.assetsType = assetsType  # 资产类型，stock表示股票，index表示指数
        self.strategy_name = strategy_name
        # 计算相关数据
        self.tick_close = 0
        self.tick_time = None
        self.tick_volume = 0
        # 仓位相关数据
        self.positionEntity = PositionEntity(self)


class PositionEntity:
    def __init__(self, asset):
        # 订单数据 二维的字典结构
        self.currentOrders = {}  # 记录买入订单 用于在策略里判断是否有仓位可以卖
        self.historyOrders = {}  # 记录已完成订单，卖出时更新，计算收益
        self.orderNumber = 0  # 每买一单+1
        self.money = 1000000  # 总资产100万
        self.trade_point_list = []  # 记录策略所有买卖点  格式 [["2021-04-26", 47, "buy"], ["2021-06-15", 55.1, "sell"]]

        # 尝试读取currentOrders JSON文件
        try:
            with open(RMTTools.read_config("PSLData", "position_currentOrders")
                      + "position_"
                      + asset.strategy_name
                      + "_"
                      + asset.assetsCode
                      + ".json", 'r') as file:
                self.currentOrders = json.load(file)
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            pass

        # 尝试读取historyOrders JSON文件
        try:
            with open(RMTTools.read_config("PSLData", "position_historyOrders")
                      + "position_"
                      + asset.strategy_name
                      + "_"
                      + asset.assetsCode
                      + ".json", 'r') as file:
                self.historyOrders = json.load(file)
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            pass


def buy(asset, volume):
    asset.positionEntity.orderNumber += 1  # 订单编号更新
    key = "order" + str(asset.positionEntity.orderNumber)  # 准备key
    asset.positionEntity.currentOrders[key] = {'openPrice': asset.tick_close,
                                               'openDateTime': asset.tick_time.strftime('%Y-%m-%d %H:%M:%S'),
                                               'volume': volume}
    # 将仓位信息保存到文件
    with open(RMTTools.read_config("PSLData", "position_currentOrders")
              + "position_"
              + asset.strategy_name
              + "_"
              + asset.assetsCode
              + ".json", 'w') as file:
        json.dump(asset.positionEntity.currentOrders, file)


def sell(asset):
    key = list(asset.positionEntity.currentOrders.keys())[0]  # 把当前仓位的第一个卖掉
    price = asset.tick_close
    # 给这个要卖的key，增加关闭价格、交易时间
    asset.positionEntity.currentOrders[key]['closePrice'] = price
    asset.positionEntity.currentOrders[key]['closeDateTime'] = asset.tick_time.strftime('%Y-%m-%d %H:%M:%S')
    # 计算本单收益 =（卖价-买入价）* 交易量 - 千分之一印花税 - 买卖两次的手续费万分之3
    asset.positionEntity.currentOrders[key]['pnl'] = ((price - asset.positionEntity.currentOrders[key]['openPrice'])
                                                      * asset.positionEntity.currentOrders[key]['volume']
                                                      - price * asset.positionEntity.currentOrders[key][
                                                          'volume'] * 1 / 1000
                                                      - (price + asset.positionEntity.currentOrders[key]['openPrice'])
                                                      * asset.positionEntity.currentOrders[key]['volume'] * 3 / 10000)
    asset.positionEntity.historyOrders[asset.tick_time.strftime('%Y%m%d%H%M')] = asset.positionEntity.currentOrders.pop(
        key)  # 把卖的订单，从当前仓位列表里，复制到历史仓位列表里

    # 将交易记录保存到文件
    with open(RMTTools.read_config("PSLData", "position_historyOrders")
              + "position_"
              + asset.strategy_name
              + "_"
              + asset.assetsCode
              + ".json", 'w') as file:
        json.dump(asset.positionEntity.historyOrders, file)

    # 清空仓位信息
    with open(RMTTools.read_config("PSLData", "position_currentOrders")
              + "position_"
              + asset.strategy_name
              + "_"
              + asset.assetsCode
              + ".json", 'w') as file:
        json.dump({}, file)
