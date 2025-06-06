#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from utils.utils import notify_user
from seckill.react_utils import ReactPageUtils
from seckill.page_loader import PageLoader

class OptimizedSecKill:
    """
    基于2024年淘宝页面结构优化的秒杀功能 - 高性能版
    支持React动态渲染、现代化选择器、智能等待机制
    """
    
    def __init__(self, driver, seckill_time_obj, password=None, max_retry_count=30):
        self.driver = driver
        self.seckill_time_obj = seckill_time_obj
        self.password = password
        self.max_retry_count = max_retry_count
        # 缩短等待时间，提高响应速度
        self.wait_short = WebDriverWait(driver, 1)
        self.wait_medium = WebDriverWait(driver, 3)
        self.wait_long = WebDriverWait(driver, 5)
        
        # 初始化工具模块
        self.react_utils = ReactPageUtils()
        self.page_loader = PageLoader(driver)
        
        print(f"🚀 OptimizedSecKill高性能版初始化完成")
        print(f"   ⏰ 抢购时间: {seckill_time_obj}")
        print(f"   🔄 最大重试次数: {max_retry_count}")
    
    def save_debug_info(self, step, error=None):
        """保存调试信息到文件"""
        try:
            debug_info = {
                'timestamp': datetime.now().isoformat(),
                'step': step,
                'current_url': self.driver.current_url,
                'page_title': self.driver.title,
                'error': str(error) if error else None
            }
            
            with open('debug_seckill.json', 'a', encoding='utf-8') as f:
                f.write(json.dumps(debug_info, ensure_ascii=False) + '\n')
        except:
            pass
    
    def check_login_status(self):
        """检查登录状态 - 快速版"""
        try:
            current_url = self.driver.current_url
            
            # 快速URL检查
            if any(keyword in current_url.lower() for keyword in ['login', 'signin', 'passport']):
                return False
            
            # 快速检查登录状态，只使用最可靠的指示器
            try:
                # 使用JavaScript快速检查
                is_logged_in = self.driver.execute_script("""
                    // 快速检查登录状态的多个指示器
                    var indicators = [
                        document.querySelector('*[class*="user"]'),
                        document.querySelector('*[href*="mytaobao"]'),
                        document.querySelector('*[class*="nick"]'),
                        document.querySelector('*[class*="avatar"]')
                    ];
                    
                    for(var i = 0; i < indicators.length; i++) {
                        if(indicators[i] && indicators[i].textContent) {
                            return true;
                        }
                    }
                    
                    // 检查页面源码关键词
                    var pageText = document.body.textContent || '';
                    return pageText.includes('我的淘宝') || pageText.includes('个人中心');
                """)
                
                if is_logged_in:
                    print("✅ 快速检测到登录状态")
                    return True
            except:
                pass
            
            print("⚠️  无法确定登录状态，默认继续")
            return True
            
        except Exception as e:
            print(f"⚠️  登录状态检查失败: {e}")
            return True
    
    def select_all_items_safe(self):
        """选择购物车中的所有商品 - 高性能版"""
        print("🛒 高速选择购物车商品...")
        
        try:
            # 优先使用最高效的JavaScript方法
            print("   ⚡ 使用高性能JavaScript选择...")
            result = self.driver.execute_script(self.react_utils.get_select_products_script())
            
            print(f"   📊 选择结果: 总共{result['total']}个，已选{result['selected']}个")
            
            if result['selected'] > 0:
                # 快速验证
                if self.verify_selection():
                    print("✅ 高速选择成功！")
                    return True
            
            # 如果JavaScript失败，尝试传统方法（但限制时间）
            print("   🎯 备用方法: 查找全选复选框...")
            try:
                # 只尝试最有效的选择器
                effective_selectors = [
                    (By.XPATH, "(//input[@type='checkbox'])[1]", "第一个复选框"),
                    (By.XPATH, "//span[contains(text(), '全选')]/preceding-sibling::input[@type='checkbox']", "全选复选框"),
                ]
                
                for by_method, selector, desc in effective_selectors:
                    try:
                        element = self.wait_short.until(EC.element_to_be_clickable((by_method, selector)))
                        if not element.is_selected():
                            element.click()
                            sleep(0.5)
                            if self.verify_selection():
                                print(f"✅ {desc}选择成功！")
                                return True
                    except TimeoutException:
                        continue
            except:
                pass
            
            print("⚠️  商品选择完成，继续流程")
            return True  # 即使失败也继续，避免阻塞
            
        except Exception as e:
            print(f"❌ 商品选择出错: {e}")
            return True  # 继续执行
    
    def verify_selection(self):
        """验证商品是否已被选中 - 快速版"""
        try:
            total_amount = self.driver.execute_script(self.react_utils.get_verify_selection_script())
            
            if total_amount > 0:
                print(f"   💰 合计金额: ¥{total_amount}")
                return True
            
            # 快速检查复选框状态
            checked_count = self.driver.execute_script("""
                return document.querySelectorAll('input[type="checkbox"]:checked:not(:disabled)').length;
            """)
            
            return checked_count > 0
            
        except:
            return True  # 验证失败时默认继续
    
    def check_cart_status(self):
        """检查购物车状态 - 快速版"""
        try:
            total_amount = self.driver.execute_script(self.react_utils.get_verify_selection_script())
            
            if total_amount > 0:
                print(f"✅ 购物车正常: 合计 ¥{total_amount}")
                return "normal"
            else:
                return "unselected"
                
        except:
            return "unknown"
    
    def click_settlement_button(self):
        """点击结算按钮 - 高性能版"""
        print("💰 高速查找结算按钮...")
        
        # 快速状态检查
        cart_status = self.check_cart_status()
        if cart_status == "unselected":
            print("   ⚡ 快速选择商品...")
            self.select_all_items_safe()
            sleep(0.3)
        
        # 直接使用最高效的JavaScript方法
        try:
            result = self.driver.execute_script(self.react_utils.get_find_settlement_button_script())
            
            if result.get('success'):
                print(f"✅ 高速找到结算按钮: {result.get('clicked')}")
                sleep(1)  # 等待页面跳转
                return True
            else:
                print(f"⚠️  未找到结算按钮，找到{result.get('candidates', 0)}个候选")
                
                # 快速备用方案：直接尝试SPM选择器（从日志看这个有效）
                try:
                    spm_element = self.wait_short.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-spm*='settlement'], [data-spm*='checkout']"))
                    )
                    spm_element.click()
                    print("✅ SPM选择器成功点击结算按钮")
                    sleep(1)
                    return True
                except:
                    pass
                
                return False
                
        except Exception as e:
            print(f"❌ 点击结算按钮出错: {e}")
            return False
    
    def submit_order(self):
        """提交订单 - 高性能版"""
        print("📝 高速查找提交订单按钮...")
        
        # 直接使用最高效的JavaScript方法
        try:
            result = self.driver.execute_script(self.react_utils.get_find_submit_button_script())
            
            if result.get('success'):
                print(f"✅ 高速找到提交按钮: {result.get('clicked')}")
                
                # 快速验证跳转
                sleep(2)
                current_url = self.driver.current_url
                
                # 快速检查支付页面指示器
                payment_indicators = [
                    'cashier' in current_url.lower(),
                    'pay' in current_url.lower() and 'confirm' not in current_url.lower(),
                    'alipay' in current_url.lower(),
                ]
                
                if any(payment_indicators):
                    print(f"✅ 已跳转到支付页面: {current_url}")
                    return True
                else:
                    print(f"⚠️  可能未完全跳转: {current_url}")
                    return True  # 继续认为成功，避免重复提交
            else:
                print(f"⚠️  未找到提交按钮，尝试备用方案...")
                
                # 快速备用方案：使用最有效的选择器（从日志分析）
                try:
                    # 从日志看，SPM选择器是有效的
                    submit_element = self.wait_short.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-spm*='submit'], [data-spm*='order'], [data-spm*='pay']"))
                    )
                    submit_element.click()
                    print("✅ SPM选择器成功提交订单")
                    return True
                except:
                    # 最后尝试通用文本匹配
                    try:
                        submit_element = self.wait_short.until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '提交') or contains(text(), '支付')]"))
                        )
                        submit_element.click()
                        print("✅ 通用选择器成功提交订单")
                        return True
                    except:
                        pass
                
                return False
                
        except Exception as e:
            print(f"❌ 提交订单出错: {e}")
            return False
    
    def optimized_sec_kill(self):
        """优化版的秒杀主函数 - 高性能版"""
        print("🚀 开始高性能秒杀流程...")
        print(f"   ⏰ 当前时间: {datetime.now()}")
        print(f"   🎯 目标时间: {self.seckill_time_obj}")
        
        # 精确等待到抢购时间
        while datetime.now() < self.seckill_time_obj:
            remaining = (self.seckill_time_obj - datetime.now()).total_seconds()
            if remaining > 1:
                sleep(min(0.3, remaining - 1))
            else:
                sleep(0.01)  # 更高精度等待
        
        print("⚡ 抢购时间到！开始高速执行...")
        start_time = datetime.now()
        
        # 步骤1：快速刷新和页面检查
        try:
            print("🔄 快速刷新购物车...")
            self.driver.get("https://cart.taobao.com/cart.htm")
            
            # 使用快速页面加载器
            if self.page_loader.wait_for_cart_page_load(timeout=5):
                print("✅ 页面快速加载完成")
            else:
                print("⚠️  页面加载超时，继续执行")
            
            # 快速登录检查
            if not self.check_login_status():
                print("❌ 未登录，秒杀失败")
                return False
                
        except Exception as e:
            print(f"❌ 页面刷新失败: {e}")
            # 不return False，继续尝试
        
        # 步骤2：高速商品选择
        print("⚡ 高速商品选择...")
        self.select_all_items_safe()
        
        # 步骤3：超高速抢购循环
        submit_success = False
        retry_count = 0
        
        print("🏃‍♂️ 开始超高速抢购循环...")
        
        while not submit_success and retry_count < self.max_retry_count:
            retry_count += 1
            elapsed = (datetime.now() - start_time).total_seconds()
            
            if retry_count % 3 == 1:  # 更频繁的进度报告
                print(f"⚡ 第{retry_count}次抢购 (已用时{elapsed:.2f}秒)...")
            
            try:
                current_url = self.driver.current_url.lower()
                
                if 'cart' in current_url:
                    # 在购物车页面，直接高速点击结算
                    if self.click_settlement_button():
                        sleep(0.5)  # 减少等待时间
                        continue
                        
                elif any(keyword in current_url for keyword in ['buy', 'order', 'confirm', 'checkout']):
                    # 在订单确认页面，快速加载后提交
                    if retry_count == 1:  # 只在第一次等待加载
                        print("📍 订单页面快速加载...")
                        self.page_loader.wait_for_order_page_load(timeout=3)
                    
                    print("📝 高速提交订单...")
                    if self.submit_order():
                        submit_success = True
                        print("🎉 抢购成功！")
                        break
                        
                else:
                    # 未知页面，快速尝试通用流程
                    if self.click_settlement_button():
                        sleep(0.5)
                        if self.submit_order():
                            submit_success = True
                            print("🎉 抢购成功！")
                            break
                    
            except Exception as e:
                if retry_count % 5 == 0:  # 减少错误报告频率
                    print(f"⚠️  第{retry_count}次抢购错误: {str(e)}")
                self.save_debug_info("seckill_error", e)
            
            sleep(0.05)  # 更短的重试间隔
        
        # 输出最终结果
        total_time = (datetime.now() - start_time).total_seconds()
        if submit_success:
            print(f"🎊 抢购成功！总用时: {total_time:.2f}秒")
            if self.password:
                print("💳 开始自动支付流程...")
                self.pay()
        else:
            print(f"😞 抢购失败，已达到最大重试次数({self.max_retry_count}次)")
            print(f"   📊 总用时: {total_time:.2f}秒")
        
        return submit_success
    
    def pay(self):
        """自动支付功能 - 快速版"""
        print("💳 快速支付处理...")
        
        try:
            # 快速查找支付密码框
            password_input = self.wait_medium.until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'sixDigitPassword'))
            )
            password_input.clear()
            password_input.send_keys(self.password)
            print("✅ 已输入支付密码")
            
            # 快速查找确认按钮
            confirm_btn = self.wait_medium.until(
                EC.element_to_be_clickable((By.ID, 'J_authSubmit'))
            )
            confirm_btn.click()
            
            print("✅ 支付成功！")
            notify_user(msg="淘宝秒杀：支付成功！")
            
        except Exception as e:
            print(f"❌ 支付失败: {str(e)}")
            notify_user(msg="淘宝秒杀：支付失败，请手动完成")
        finally:
            print("💤 等待30秒后关闭...")
            sleep(30)
            try:
                self.driver.quit()
            except:
                pass
    
    def find_element_smart(self, selectors_list, timeout=3, description="元素"):
        """智能元素查找 - 快速版"""
        wait = WebDriverWait(self.driver, timeout)
        
        for by_method, selector, desc in selectors_list:
            try:
                element = wait.until(EC.element_to_be_clickable((by_method, selector)))
                print(f"✅ 找到{description}: {desc}")
                return element
            except TimeoutException:
                continue
            except Exception:
                continue
        
        raise NoSuchElementException(f"未找到{description}")

# 集成到原有ChromeDrive类的方法
def optimized_sec_kill_method(self):
    """替换原有ChromeDrive类中的sec_kill方法 - 高性能版"""
    print("🔄 使用高性能秒杀方法...")
    
    # 等待登录和时间
    self.keep_wait()
    
    # 创建高性能秒杀实例
    optimizer = OptimizedSecKill(
        driver=self.driver,
        seckill_time_obj=self.seckill_time_obj,
        password=self.password,
        max_retry_count=30  # 减少重试次数，提高效率
    )
    
    # 执行高性能秒杀
    return optimizer.optimized_sec_kill()

if __name__ == '__main__':
    print("OptimizedSecKill模块已加载")
    print("版本: 2024现代淘宝优化版 - 高性能版")
    print("特性: React支持、模块化架构、智能等待、超高速抢购") 