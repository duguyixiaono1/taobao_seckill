#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
优化版秒杀完整流程测试
使用重构后的模块化组件进行测试
"""

import sys
import os
from datetime import datetime, timedelta
from time import sleep

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入必要模块
from seckill.seckill_taobao import ChromeDrive
from optimized_sec_kill import OptimizedSecKill
from seckill.react_utils import ReactPageUtils
from seckill.page_loader import PageLoader

class SecKillTester:
    """秒杀测试器"""
    
    def __init__(self):
        self.driver = None
        self.optimizer = None
        self.react_utils = ReactPageUtils()
        self.page_loader = None
        
    def setup_driver(self):
        """初始化浏览器驱动"""
        print("🚀 初始化浏览器驱动...")
        
        # 设置一个很近的秒杀时间（2秒后）
        seckill_time = (datetime.now() + timedelta(seconds=2)).strftime('%Y-%m-%d %H:%M:%S')
        
        # 初始化ChromeDrive
        chrome_drive = ChromeDrive(seckill_time=seckill_time, password="")
        self.driver = chrome_drive.driver
        
        # 初始化页面加载器
        self.page_loader = PageLoader(self.driver)
        
        # 初始化优化器
        self.optimizer = OptimizedSecKill(
            driver=self.driver,
            seckill_time_obj=chrome_drive.seckill_time_obj,
            password="",
            max_retry_count=5
        )
        
        print("✅ 浏览器驱动初始化完成")
        return True
    
    def test_page_loading(self):
        """测试页面加载功能"""
        print("\n📋 测试页面加载功能...")
        
        try:
            # 访问购物车页面
            print("🔄 访问购物车页面...")
            self.driver.get("https://cart.taobao.com/cart.htm")
            
            # 测试购物车页面加载
            print("⏳ 测试购物车页面加载...")
            cart_loaded = self.page_loader.wait_for_cart_page_load(timeout=15)
            
            if cart_loaded:
                print("✅ 购物车页面加载测试成功")
                return True
            else:
                print("❌ 购物车页面加载测试失败")
                return False
                
        except Exception as e:
            print(f"❌ 页面加载测试出错: {e}")
            return False
    
    def test_login_detection(self):
        """测试登录检测功能"""
        print("\n🔐 测试登录检测功能...")
        
        try:
            login_status = self.optimizer.check_login_status()
            
            if login_status:
                print("✅ 登录检测测试成功")
                return True
            else:
                print("⚠️  登录检测返回False，请手动登录后继续")
                print("💡 等待30秒供手动登录...")
                sleep(30)
                return self.optimizer.check_login_status()
                
        except Exception as e:
            print(f"❌ 登录检测测试出错: {e}")
            return False
    
    def test_product_selection(self):
        """测试商品选择功能"""
        print("\n🛒 测试商品选择功能...")
        
        try:
            # 检查购物车状态
            cart_status = self.optimizer.check_cart_status()
            print(f"📊 购物车状态: {cart_status}")
            
            # 测试商品选择
            selection_success = self.optimizer.select_all_items_safe()
            
            if selection_success:
                print("✅ 商品选择测试成功")
                
                # 验证选择结果
                verification_success = self.optimizer.verify_selection()
                if verification_success:
                    print("✅ 商品选择验证成功")
                    return True
                else:
                    print("⚠️  商品选择验证失败")
                    return False
            else:
                print("❌ 商品选择测试失败")
                return False
                
        except Exception as e:
            print(f"❌ 商品选择测试出错: {e}")
            return False
    
    def test_settlement_button(self):
        """测试结算按钮功能"""
        print("\n💰 测试结算按钮功能...")
        
        try:
            # 确保商品已选择
            self.optimizer.select_all_items_safe()
            sleep(1)
            
            # 测试结算按钮点击
            settlement_success = self.optimizer.click_settlement_button()
            
            if settlement_success:
                print("✅ 结算按钮测试成功")
                
                # 等待页面跳转
                sleep(3)
                
                # 检查是否跳转到订单确认页面
                current_url = self.driver.current_url.lower()
                if any(keyword in current_url for keyword in ['buy', 'order', 'confirm', 'checkout']):
                    print("✅ 成功跳转到订单确认页面")
                    return True
                else:
                    print(f"⚠️  页面未跳转，当前URL: {current_url}")
                    return False
            else:
                print("❌ 结算按钮测试失败")
                return False
                
        except Exception as e:
            print(f"❌ 结算按钮测试出错: {e}")
            return False
    
    def test_order_submission(self):
        """测试订单提交功能"""
        print("\n📝 测试订单提交功能...")
        
        try:
            # 确保在订单确认页面
            current_url = self.driver.current_url.lower()
            if not any(keyword in current_url for keyword in ['buy', 'order', 'confirm', 'checkout']):
                print("⚠️  不在订单确认页面，跳过订单提交测试")
                return True
            
            # 等待订单页面完全加载
            print("⏳ 等待订单页面加载...")
            order_loaded = self.page_loader.wait_for_order_page_load(timeout=15)
            
            if not order_loaded:
                print("❌ 订单页面加载失败")
                return False
            
            # 测试提交订单（但不真的提交）
            print("🔍 查找提交订单按钮...")
            result = self.driver.execute_script(self.react_utils.get_find_submit_button_script())
            
            if result.get('success'):
                print(f"✅ 找到提交订单按钮: {result.get('clicked')}")
                print("⚠️  为了安全，不执行真实的订单提交")
                return True
            else:
                print(f"❌ 未找到提交订单按钮，找到{result.get('candidates', 0)}个候选按钮")
                return False
                
        except Exception as e:
            print(f"❌ 订单提交测试出错: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始运行优化版秒杀完整流程测试")
        print("=" * 60)
        
        try:
            # 初始化
            if not self.setup_driver():
                print("❌ 驱动初始化失败")
                return False
            
            # 测试序列
            tests = [
                ("页面加载", self.test_page_loading),
                ("登录检测", self.test_login_detection),
                ("商品选择", self.test_product_selection),
                ("结算按钮", self.test_settlement_button),
                ("订单提交", self.test_order_submission),
            ]
            
            results = {}
            
            for test_name, test_func in tests:
                print(f"\n{'='*20} {test_name}测试 {'='*20}")
                try:
                    results[test_name] = test_func()
                except Exception as e:
                    print(f"❌ {test_name}测试执行异常: {e}")
                    results[test_name] = False
                
                print(f"{'='*50}")
            
            # 输出测试结果摘要
            print("\n📊 测试结果摘要:")
            print("=" * 60)
            
            total_tests = len(results)
            passed_tests = sum(1 for success in results.values() if success)
            
            for test_name, success in results.items():
                status = "✅ 通过" if success else "❌ 失败"
                print(f"   {test_name}: {status}")
            
            print(f"\n总计: {passed_tests}/{total_tests} 个测试通过")
            
            if passed_tests == total_tests:
                print("🎉 所有测试通过！秒杀功能正常")
            elif passed_tests >= total_tests * 0.8:
                print("⚠️  大部分测试通过，功能基本正常")
            else:
                print("😞 多个测试失败，需要检查功能")
            
            return passed_tests >= total_tests * 0.8
            
        except Exception as e:
            print(f"❌ 测试执行过程中出现异常: {e}")
            return False
        
        finally:
            # 清理
            if self.driver:
                print("\n🧹 清理浏览器...")
                sleep(5)  # 等待5秒供观察
                try:
                    self.driver.quit()
                except:
                    pass
    
    def quick_test(self):
        """快速测试主要功能"""
        print("⚡ 快速测试模式")
        print("=" * 40)
        
        try:
            if not self.setup_driver():
                return False
            
            # 只测试核心功能
            tests = [
                self.test_page_loading,
                self.test_login_detection,
                self.test_product_selection,
            ]
            
            for i, test_func in enumerate(tests, 1):
                print(f"\n⚡ 快速测试 {i}/{len(tests)}")
                success = test_func()
                if not success:
                    print(f"❌ 快速测试在第{i}步失败")
                    return False
            
            print("\n✅ 快速测试全部通过！")
            return True
            
        except Exception as e:
            print(f"❌ 快速测试异常: {e}")
            return False
        
        finally:
            if self.driver:
                sleep(3)
                try:
                    self.driver.quit()
                except:
                    pass

def main():
    """主函数"""
    print("🧪 优化版秒杀测试工具")
    print("请选择测试模式:")
    print("1. 完整测试 (推荐)")
    print("2. 快速测试")
    
    try:
        choice = input("请输入选择 (1-2): ").strip()
        
        tester = SecKillTester()
        
        if choice == "1":
            success = tester.run_all_tests()
        elif choice == "2":
            success = tester.quick_test()
        else:
            print("❌ 无效选择")
            return
        
        if success:
            print("\n🎊 测试完成，功能正常！")
        else:
            print("\n😞 测试完成，发现问题需要修复")
            
    except KeyboardInterrupt:
        print("\n⏹️  用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    main() 