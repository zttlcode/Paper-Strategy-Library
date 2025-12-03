# Paper-Strategy-Library

**论文量化策略代码复现项目**

本项目旨在复现学术论文中提出的量化交易策略。目前支持 **A股市场**，每日收盘后（17:30 以后）运行 **日线级别** 的股票策略。

- **覆盖股票池**：沪深300 + 中证500，共约 800 只股票（代码见 `QuantData/asset_code/a800_stocks.csv`）  
- **运行方式**：交易日下午 17:30 后执行 `Daily_run.py` 脚本，自动拉取当日行情并运行策略  
- **策略管理**：所有策略均存放于 `Strategy/` 目录下，将陆续更新。截至 **2025 年 12 月 2 日**，已上线首个策略 [`Fuzzy.py`](Strategy/Fuzzy.py)

---

### 快速开始

1. 克隆项目：
   ```bash
   git clone https://github.com/zttlcode/Paper-Strategy-Library.git
   cd Paper-Strategy-Library

2. 创建 Python 3.12.12 环境（推荐使用 conda 或 venv），并安装依赖：
   ```bash
   pip install -r requirements.txt

3. 在交易日 17:30 之后 运行：
   ```bash
   python Daily_run.py
