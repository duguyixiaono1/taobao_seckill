#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试增强版秒杀功能 - 专门测试结算按钮查找
"""

import sys
from datetime import datetime, timedelta
from seckill.seckill_taobao import ChromeDrive
from optimized_sec_kill import optimized_sec_kill_method

def test_enhanced_settlement():
    """测试增强版结算按钮查找功能"""
    print("🧪 测试增强版结算按钮查找功能")
    print("=" * 50)
    
    # 设置测试时间（1分钟后）
    seckill_time = (datetime.now() + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
    print(f"📅 设置测试时间: {seckill_time}")
    
    try:
        # 创建ChromeDrive实例
        driver = ChromeDrive(seckill_time=seckill_time, password=None)
        
        # 替换秒杀方法为优化版
        driver.sec_kill = lambda: optimized_sec_kill_method(driver)
        
        print("🌐 启动浏览器并登录...")
        driver.login("https://cart.taobao.com/cart.htm")
        
        # 等待用户确认
        print("⏳ 请确保购物车中有商品...")
        print("⏳ 准备就绪后程序将在设定时间自动开始测试...")
        
        # 开始秒杀测试
        driver.sec_kill()
        
    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            input("\n按回车键关闭浏览器...")
            driver.driver.quit()
        except:
            pass

if __name__ == '__main__':
    test_enhanced_settlement() 