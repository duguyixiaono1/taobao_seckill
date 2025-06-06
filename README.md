# 淘宝秒杀助手 - 2024优化版

> 基于现代React页面结构优化的淘宝秒杀工具，支持自动登录、商品选择、结算和订单提交。

## ✨ 特性

- 🚀 **现代化架构**: 模块化设计，代码清晰易维护
- ⚡ **React优化**: 专门针对2024年淘宝React页面优化
- 🎯 **智能等待**: 精确的页面加载检测和等待机制  
- 🛡️ **稳定可靠**: 多种策略确保操作成功率
- 🔧 **易于测试**: 完整的测试框架，便于验证功能

## 📁 项目结构

```
taobao_seckill/
├── main.py                    # 主程序入口（GUI界面）
├── optimized_sec_kill.py      # 优化版秒杀核心模块
├── requirements.txt           # 依赖列表
├── seckill/                   # 核心模块
│   ├── seckill_taobao.py     # 基础浏览器驱动
│   ├── react_utils.py        # React页面工具
│   ├── page_loader.py        # 页面加载工具
│   └── settings.py           # 配置文件
├── utils/                     # 工具模块
│   └── utils.py              # 通用工具函数
└── test_optimized_complete_flow.py  # 完整测试套件
```

## 🚀 快速开始

### 环境要求

- Python 3.7+
- Chrome浏览器
- ChromeDriver

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基础使用

1. **GUI模式**（推荐新手）：
```bash
python main.py
```

2. **命令行模式**：
```python
from seckill.seckill_taobao import ChromeDrive
from optimized_sec_kill import optimized_sec_kill_method

# 设置抢购时间和支付密码
driver = ChromeDrive(
    seckill_time="2024-12-29 12:00:00", 
    password="123456"
)

# 使用优化版秒杀
driver.sec_kill = lambda: optimized_sec_kill_method(driver)
driver.sec_kill()
```

### 测试功能

运行完整测试验证功能：
```bash
python test_optimized_complete_flow.py
```

## 📋 使用说明

### 准备工作

1. **清空购物车**: 确保购物车中只有想要抢购的商品
2. **预先登录**: 建议先手动登录淘宝账号
3. **设置时间**: 准确设置抢购开始时间
4. **支付密码**: 如需自动支付，输入6位支付密码

### 抢购流程

1. **页面加载**: 自动等待React页面完全渲染
2. **商品选择**: 智能选择购物车中的所有商品
3. **快速结算**: 精确定位并点击结算按钮
4. **订单提交**: 高速提交订单到支付页面
5. **自动支付**: （可选）自动输入密码完成支付

## 🔧 高级配置

### 自定义重试次数

```python
optimizer = OptimizedSecKill(
    driver=driver,
    seckill_time_obj=seckill_time_obj,
    password=password,
    max_retry_count=50  # 自定义重试次数
)
```

### 调试模式

程序会自动保存调试信息到 `debug_seckill.json`，包含：
- 时间戳和执行步骤
- 当前页面URL和标题
- 错误信息（如有）

## 🧪 测试框架

### 完整测试
```bash
python test_optimized_complete_flow.py
# 选择 1 进行完整测试
```

### 快速测试
```bash
python test_optimized_complete_flow.py  
# 选择 2 进行快速测试
```

测试包含：
- ✅ 页面加载检测
- ✅ 登录状态验证  
- ✅ 商品选择功能
- ✅ 结算按钮定位
- ✅ 订单提交流程

## ⚠️ 注意事项

1. **仅供学习**: 本项目仅用于技术学习和交流
2. **遵守规则**: 请遵守淘宝平台的使用规则
3. **风险自负**: 使用本工具的风险由用户自行承担
4. **及时更新**: 淘宝页面可能更新，需要相应调整代码

## 🔄 更新日志

### v2.0.0 (2024-12-29)
- 🚀 完全重构代码架构
- ⚡ 新增React页面专用处理
- 🛡️ 提升操作稳定性和成功率
- 🧪 完善测试框架
- 📚 优化文档和使用指南

### v1.x.x
- 基础功能实现
- 传统页面支持

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

本项目基于MIT许可证开源，详见LICENSE文件。


