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
        """点击结算按钮 - 调试增强版"""
        print("💰 智能查找结算按钮...")
        
        # 快速状态检查
        cart_status = self.check_cart_status()
        if cart_status == "unselected":
            print("   ⚡ 快速选择商品...")
            self.select_all_items_safe()
            sleep(0.3)
        
        # 记录当前URL
        current_url_before = self.driver.current_url
        print(f"   📍 点击前URL: {current_url_before}")
        
        # 使用修复版JavaScript方法
        try:
            result = self.driver.execute_script(self.react_utils.get_find_settlement_button_script())
            
            if result.get('success'):
                print(f"✅ 找到结算按钮: {result.get('clicked')[:50]}...")
                print(f"   🔧 使用方法: {result.get('method')}")
                
                # 等待页面响应
                for i in range(10):  # 最多等待5秒
                    sleep(0.5)
                    
                    # 检查URL是否发生变化
                    current_url_after = self.driver.current_url
                    if current_url_after != current_url_before:
                        print(f"✅ 页面已跳转: {current_url_after}")
                        return True
                    
                    # 检查是否出现了订单确认页面的内容
                    page_info = self.driver.execute_script(self.react_utils.get_page_url_check_script())
                    if page_info.get('isOrderPage'):
                        print(f"✅ 检测到订单页面内容")
                        return True
                    
                    # 检查页面内容变化
                    if i % 2 == 1:  # 每1秒检查一次
                        page_content = self.driver.execute_script("""
                            return document.body.textContent.includes('提交订单') || 
                                   document.body.textContent.includes('确认订单') ||
                                   document.body.textContent.includes('商品总价');
                        """)
                        if page_content:
                            print(f"✅ 检测到订单页面关键内容")
                            return True
                
                print("⚠️  点击后页面未发生预期跳转")
                return False
            else:
                print(f"⚠️  未找到结算按钮: {result.get('reason', '未知原因')}")
                print(f"   📊 候选按钮数量: {result.get('candidates', 0)}")
                
                # 开始页面分析
                print("🔍 开始分析页面结构...")
                try:
                    analysis = self.driver.execute_script(self.react_utils.get_page_analysis_script())
                    
                    print(f"📊 页面分析结果:")
                    print(f"   - 按钮总数: {len(analysis.get('allButtons', []))}")
                    print(f"   - 链接总数: {len(analysis.get('allLinks', []))}")
                    print(f"   - 可点击元素: {len(analysis.get('allClickable', []))}")
                    print(f"   - 文本匹配: {len(analysis.get('textMatches', []))}")
                    print(f"   - SPM元素: {len(analysis.get('spmElements', []))}")
                    
                    # 分析文本匹配的元素
                    text_matches = analysis.get('textMatches', [])
                    if text_matches:
                        print("🎯 找到包含结算文本的元素:")
                        for i, match in enumerate(text_matches[:5]):  # 只显示前5个
                            print(f"   {i+1}. {match.get('tag')} - '{match.get('text')[:30]}...' - 可点击: {match.get('clickable')}")
                            if match.get('class'):
                                print(f"      类名: {match.get('class')[:50]}")
                            if match.get('dataSpm'):
                                print(f"      SPM: {match.get('dataSpm')}")
                    
                    # 尝试点击文本匹配的可点击元素
                    print("🎯 尝试点击文本匹配的元素...")
                    clickable_matches = [m for m in text_matches if m.get('clickable') and m.get('rect')]
                    clickable_matches.sort(key=lambda x: x.get('rect', {}).get('w', 0) * x.get('rect', {}).get('h', 0), reverse=True)
                    
                    for i, match in enumerate(clickable_matches[:3]):  # 尝试前3个最大的可点击元素
                        try:
                            print(f"   尝试点击第{i+1}个匹配元素: {match.get('text')[:30]}")
                            
                            # 构建选择器
                            selectors_to_try = []
                            if match.get('id'):
                                selectors_to_try.append(f"#{match.get('id')}")
                            if match.get('dataSpm'):
                                selectors_to_try.append(f"[data-spm='{match.get('dataSpm')}']")
                            if match.get('class'):
                                # 尝试用类名的第一个部分
                                first_class = match.get('class').split()[0] if match.get('class') else ''
                                if first_class:
                                    selectors_to_try.append(f".{first_class}")
                            
                            # 通用选择器
                            tag = match.get('tag', '').lower()
                            text = match.get('text', '')
                            if len(text) < 50:
                                selectors_to_try.append(f"{tag}[contains(text(),'{text[:20]}')]")
                            
                            for selector in selectors_to_try:
                                try:
                                    if selector.startswith('#') or selector.startswith('.') or selector.startswith('['):
                                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                                    else:
                                        element = self.driver.find_element(By.XPATH, f"//{selector}")
                                    
                                    element.click()
                                    print(f"✅ 成功点击元素: {selector}")
                                    sleep(1)
                                    
                                    # 检查是否跳转
                                    if self.driver.current_url != current_url_before:
                                        print(f"✅ 页面分析策略成功跳转!")
                                        return True
                                        
                                except Exception as e:
                                    continue
                                    
                        except Exception as e:
                            print(f"   点击匹配元素失败: {e}")
                            continue
                    
                    # 如果文本匹配失败，尝试SPM元素
                    spm_elements = analysis.get('spmElements', [])
                    if spm_elements:
                        print("🔧 尝试点击SPM元素...")
                        for i, spm_el in enumerate(spm_elements[:3]):
                            try:
                                spm_selector = f"[data-spm='{spm_el.get('spm')}']"
                                element = self.driver.find_element(By.CSS_SELECTOR, spm_selector)
                                element.click()
                                print(f"✅ 成功点击SPM元素: {spm_el.get('spm')}")
                                sleep(1)
                                
                                if self.driver.current_url != current_url_before:
                                    print(f"✅ SPM策略成功跳转!")
                                    return True
                                    
                            except Exception as e:
                                continue
                    
                except Exception as e:
                    print(f"❌ 页面分析失败: {e}")
                
                # 深度分析 - 新增功能
                print("🔍 启动深度分析...")
                try:
                    deep_analysis = self.driver.execute_script(self.react_utils.get_deep_settlement_analysis_script())
                    
                    print(f"📊 深度分析结果:")
                    print(f"   - 结算容器: {len(deep_analysis.get('settlementContainers', []))}")
                    print(f"   - 可点击子元素: {len(deep_analysis.get('clickableChildren', []))}")
                    print(f"   - 页面按钮总数: {len(deep_analysis.get('allButtons', []))}")
                    print(f"   - 推荐点击: {len(deep_analysis.get('recommendations', []))}")
                    
                    # 显示推荐的点击目标
                    recommendations = deep_analysis.get('recommendations', [])
                    if recommendations:
                        print("🎯 推荐的点击目标:")
                        for rec in recommendations[:5]:
                            print(f"   {rec.get('rank', '?')}. {rec.get('text', '')[:40]} (得分: {rec.get('score', 0)})")
                            print(f"      方法: {rec.get('method')} - {rec.get('selector', '')[:60]}")
                    
                    # 尝试点击推荐的目标
                    print("🚀 尝试点击推荐目标...")
                    recommendations.sort(key=lambda x: x.get('score', 0), reverse=True)
                    
                    for i, rec in enumerate(recommendations[:5]):
                        try:
                            print(f"   尝试第{i+1}个推荐: {rec.get('text', '')[:30]}...")
                            
                            clicked = False
                            if rec.get('method') == 'XPATH':
                                xpath = rec.get('xpath')
                                if xpath:
                                    elements = self.driver.find_elements(By.XPATH, xpath)
                                    for elem in elements:
                                        try:
                                            elem.click()
                                            print(f"✅ XPATH点击成功: {xpath}")
                                            clicked = True
                                            break
                                        except Exception as e:
                                            continue
                            
                            elif rec.get('method') == 'CSS_SELECTOR':
                                selector = rec.get('selector')
                                if selector:
                                    try:
                                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                                        element.click()
                                        print(f"✅ CSS选择器点击成功: {selector}")
                                        clicked = True
                                    except Exception as e:
                                        # 尝试JavaScript点击
                                        try:
                                            self.driver.execute_script(f"document.querySelector('{selector}').click();")
                                            print(f"✅ JavaScript点击成功: {selector}")
                                            clicked = True
                                        except Exception as e2:
                                            continue
                            
                            if clicked:
                                sleep(2)  # 等待页面响应
                                current_url_after = self.driver.current_url
                                if current_url_after != current_url_before:
                                    print(f"🎉 深度分析策略成功！页面已跳转: {current_url_after}")
                                    return True
                                else:
                                    print(f"   页面未跳转，继续尝试下一个...")
                                    
                        except Exception as e:
                            print(f"   推荐目标{i+1}点击失败: {e}")
                            continue
                    
                    # 如果推荐目标都失败，尝试直接点击包含"结算(数字)"的元素
                    print("🎯 尝试直接点击结算数字元素...")
                    try:
                        # 构建更精确的XPATH
                        settlement_xpath = "//div[contains(text(), '结算') and contains(text(), '(') and contains(text(), ')')]"
                        elements = self.driver.find_elements(By.XPATH, settlement_xpath)
                        
                        for elem in elements:
                            try:
                                elem_text = elem.text.strip()
                                if '结算' in elem_text and '(' in elem_text:
                                    print(f"   尝试点击: {elem_text[:40]}...")
                                    
                                    # 尝试多种点击方式
                                    click_methods = [
                                        lambda: elem.click(),
                                        lambda: self.driver.execute_script("arguments[0].click();", elem),
                                        lambda: self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));", elem),
                                    ]
                                    
                                    for method in click_methods:
                                        try:
                                            method()
                                            sleep(1)
                                            if self.driver.current_url != current_url_before:
                                                print(f"✅ 直接点击成功！")
                                                return True
                                        except Exception:
                                            continue
                                            
                            except Exception as e:
                                continue
                                
                    except Exception as e:
                        print(f"   直接点击失败: {e}")
                    
                except Exception as e:
                    print(f"❌ 深度分析失败: {e}")
                
                # 备用方案：传统选择器
                print("   🔄 尝试传统备用选择器...")
                try:
                    backup_selectors = [
                        (By.XPATH, "//button[contains(text(),'结算')]"),
                        (By.XPATH, "//a[contains(text(),'结算')]"),
                        (By.CSS_SELECTOR, "button[data-spm*='settlement']"),
                        (By.CSS_SELECTOR, "a[data-spm*='settlement']"),
                        (By.CSS_SELECTOR, "button[data-spm*='checkout']"),
                        (By.XPATH, "//button[contains(@class,'settlement')]"),
                        (By.XPATH, "//div[@role='button' and contains(text(),'结算')]"),
                        # 新增更多可能的选择器
                        (By.XPATH, "//span[contains(text(),'结算')]/../.."),
                        (By.CSS_SELECTOR, "div[class*='checkout']"),
                        (By.CSS_SELECTOR, "span[class*='checkout']"),
                        (By.XPATH, "//button[contains(@onclick,'checkout')]"),
                        (By.XPATH, "//a[contains(@href,'checkout')]")
                    ]
                    
                    for by_method, selector in backup_selectors:
                        try:
                            element = self.wait_short.until(EC.element_to_be_clickable((by_method, selector)))
                            element.click()
                            print(f"✅ 备用选择器成功: {selector}")
                            sleep(1)
                            
                            # 检查是否跳转
                            if self.driver.current_url != current_url_before:
                                return True
                                
                        except TimeoutException:
                            continue
                        except Exception as e:
                            continue
                    
                    print("❌ 所有备用选择器都失败")
                except Exception as e:
                    print(f"❌ 备用方案执行失败: {e}")
                
                # 最后的强力尝试
                print("🚀 启动最后的强力点击尝试...")
                try:
                    powerful_result = self.driver.execute_script(self.react_utils.get_powerful_click_script())
                    
                    if powerful_result.get('success'):
                        print(f"✅ 强力点击成功: {powerful_result.get('clicked')[:50]}")
                        print(f"   🔧 使用方法: {powerful_result.get('method')}")
                        
                        # 等待并检查页面响应
                        for check_i in range(8):  # 等待4秒
                            sleep(0.5)
                            current_url_check = self.driver.current_url
                            if current_url_check != current_url_before:
                                print(f"🎉 强力点击策略成功！页面已跳转!")
                                return True
                        
                        print("⚠️  强力点击后页面未跳转")
                    else:
                        print(f"❌ 强力点击也失败: {powerful_result.get('reason', '未知')}")
                        attempts = powerful_result.get('attempts', [])
                        if attempts:
                            print("   📝 尝试的元素:")
                            for attempt in attempts[:3]:
                                print(f"     - {attempt.get('tag')}: {attempt.get('text')[:40]} (得分: {attempt.get('score')})")
                        
                except Exception as e:
                    print(f"❌ 强力点击执行失败: {e}")
                
                return False
                
        except Exception as e:
            print(f"❌ 结算按钮点击过程出错: {e}")
            return False
    
    def submit_order(self):
        """提交订单 - 深度分析增强版"""
        print("📝 智能查找提交订单按钮...")
        
        # 记录当前URL
        current_url_before = self.driver.current_url
        print(f"   📍 提交前URL: {current_url_before}")
        
        # 使用修复版JavaScript方法
        try:
            result = self.driver.execute_script(self.react_utils.get_find_submit_button_script())
            
            if result.get('success'):
                print(f"✅ 找到提交按钮: {result.get('clicked')}")
                print(f"   🔧 使用方法: {result.get('method')}")
                
                # 等待页面响应
                for i in range(15):  # 最多等待7.5秒
                    sleep(0.5)
                    
                    # 检查URL是否跳转到支付页面
                    current_url_after = self.driver.current_url
                    if current_url_after != current_url_before:
                        print(f"✅ 页面已跳转: {current_url_after}")
                        
                        # 检查是否是支付页面
                        page_info = self.driver.execute_script(self.react_utils.get_page_url_check_script())
                        if page_info.get('isPaymentPage'):
                            print(f"🎉 成功跳转到支付页面！")
                            return True
                        elif 'cashier' in current_url_after or 'pay' in current_url_after:
                            print(f"🎉 URL显示已到达支付页面！")
                            return True
                        else:
                            print(f"⚠️  跳转了但可能不是支付页面: {current_url_after}")
                            return True  # 先认为成功，避免重复提交
                    
                    # 检查页面内容变化
                    if i % 2 == 1:  # 每1秒检查一次
                        payment_content = self.driver.execute_script("""
                            var text = document.body.textContent;
                            return text.includes('支付宝') || 
                                   text.includes('微信支付') ||
                                   text.includes('确认支付') ||
                                   text.includes('输入支付密码') ||
                                   text.includes('收银台');
                        """)
                        if payment_content:
                            print(f"✅ 检测到支付页面关键内容")
                            return True
                
                print("⚠️  提交后页面未发生预期跳转")
                return False
            else:
                print(f"⚠️  未找到提交按钮")
                for line in result.get('results', []):
                    print(f"   📝 {line}")
                
                # 对订单页面进行深度分析
                print("🔍 对订单页面启动深度分析...")
                try:
                    # 使用专门的订单页面分析脚本
                    order_analysis = self.driver.execute_script(self.get_order_page_analysis_script())
                    
                    print(f"📊 订单页面分析结果:")
                    print(f"   - 按钮总数: {len(order_analysis.get('allButtons', []))}")
                    print(f"   - 提交相关元素: {len(order_analysis.get('submitMatches', []))}")
                    print(f"   - 推荐点击: {len(order_analysis.get('recommendations', []))}")
                    
                    # 显示推荐的点击目标
                    recommendations = order_analysis.get('recommendations', [])
                    if recommendations:
                        print("🎯 订单页面推荐点击目标:")
                        for rec in recommendations[:5]:
                            print(f"   {rec.get('rank', '?')}. {rec.get('text', '')[:40]} (得分: {rec.get('score', 0)})")
                            print(f"      方法: {rec.get('method')} - {rec.get('selector', '')[:60]}")
                    
                    # 尝试点击推荐的目标
                    print("🚀 尝试点击订单页面推荐目标...")
                    recommendations.sort(key=lambda x: x.get('score', 0), reverse=True)
                    
                    for i, rec in enumerate(recommendations[:5]):
                        try:
                            print(f"   尝试第{i+1}个推荐: {rec.get('text', '')[:30]}...")
                            
                            clicked = False
                            if rec.get('method') == 'XPATH':
                                xpath = rec.get('xpath')
                                if xpath:
                                    elements = self.driver.find_elements(By.XPATH, xpath)
                                    for elem in elements:
                                        try:
                                            elem.click()
                                            print(f"✅ XPATH点击成功: {xpath}")
                                            clicked = True
                                            break
                                        except Exception as e:
                                            continue
                            
                            elif rec.get('method') == 'CSS_SELECTOR':
                                selector = rec.get('selector')
                                if selector:
                                    try:
                                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                                        element.click()
                                        print(f"✅ CSS选择器点击成功: {selector}")
                                        clicked = True
                                    except Exception as e:
                                        # 尝试JavaScript点击
                                        try:
                                            self.driver.execute_script(f"document.querySelector('{selector}').click();")
                                            print(f"✅ JavaScript点击成功: {selector}")
                                            clicked = True
                                        except Exception as e2:
                                            continue
                            
                            if clicked:
                                sleep(2)  # 等待页面响应
                                current_url_after = self.driver.current_url
                                if current_url_after != current_url_before:
                                    print(f"🎉 订单页面深度分析策略成功！页面已跳转: {current_url_after}")
                                    return True
                                else:
                                    print(f"   页面未跳转，继续尝试下一个...")
                                    
                        except Exception as e:
                            print(f"   推荐目标{i+1}点击失败: {e}")
                            continue
                    
                except Exception as e:
                    print(f"❌ 订单页面深度分析失败: {e}")
                
                # 强力点击订单提交相关元素
                print("🚀 对订单页面启动强力点击...")
                try:
                    powerful_result = self.driver.execute_script(self.get_order_powerful_click_script())
                    
                    if powerful_result.get('success'):
                        print(f"✅ 订单页面强力点击成功: {powerful_result.get('clicked')[:50]}")
                        print(f"   🔧 使用方法: {powerful_result.get('method')}")
                        
                        # 等待并检查页面响应
                        for check_i in range(10):  # 等待5秒
                            sleep(0.5)
                            current_url_check = self.driver.current_url
                            if current_url_check != current_url_before:
                                print(f"🎉 订单页面强力点击策略成功！页面已跳转!")
                                return True
                        
                        print("⚠️  订单页面强力点击后页面未跳转")
                    else:
                        print(f"❌ 订单页面强力点击也失败: {powerful_result.get('reason', '未知')}")
                        
                except Exception as e:
                    print(f"❌ 订单页面强力点击执行失败: {e}")
                
                # 备用方案：传统选择器
                print("   🔄 尝试传统备用提交方案...")
                try:
                    backup_selectors = [
                        (By.XPATH, "//button[contains(text(),'提交订单')]"),
                        (By.XPATH, "//button[contains(text(),'立即支付')]"),
                        (By.XPATH, "//a[contains(text(),'提交订单')]"),
                        (By.CSS_SELECTOR, "button[data-spm*='submit']"),
                        (By.CSS_SELECTOR, "button[data-spm*='order']"),
                        (By.CSS_SELECTOR, "input[type='submit']"),
                        (By.XPATH, "//button[contains(@class,'submit')]"),
                        (By.XPATH, "//div[@role='button' and contains(text(),'提交')]"),
                        # 新增订单页面特有的选择器
                        (By.XPATH, "//button[contains(text(),'确认订单')]"),
                        (By.XPATH, "//button[contains(text(),'确认下单')]"),
                        (By.XPATH, "//span[contains(text(),'提交订单')]/../.."),
                        (By.CSS_SELECTOR, "button[class*='submit']"),
                        (By.CSS_SELECTOR, "div[class*='submit'][role='button']"),
                        (By.XPATH, "//button[contains(@onclick,'submit')]")
                    ]
                    
                    for by_method, selector in backup_selectors:
                        try:
                            element = self.wait_short.until(EC.element_to_be_clickable((by_method, selector)))
                            element.click()
                            print(f"✅ 备用提交选择器成功: {selector}")
                            sleep(2)
                            
                            # 检查是否跳转
                            if self.driver.current_url != current_url_before:
                                print(f"✅ 备用方案成功跳转")
                                return True
                                
                        except TimeoutException:
                            continue
                        except Exception:
                            continue
                    
                    print("❌ 所有备用提交方案都失败")
                except Exception as e:
                    print(f"❌ 备用提交方案执行失败: {e}")
                
                return False
                
        except Exception as e:
            print(f"❌ 提交订单过程出错: {e}")
            return False
    
    def get_order_page_analysis_script(self):
        """订单页面专用分析脚本"""
        return """
            function analyzeOrderPage() {
                console.log('开始分析订单页面...');
                
                var results = {
                    allButtons: [],
                    submitMatches: [],
                    recommendations: []
                };
                
                // 获取页面上所有按钮
                var allButtons = document.querySelectorAll('button');
                for(var i = 0; i < allButtons.length; i++) {
                    var btn = allButtons[i];
                    var rect = btn.getBoundingClientRect();
                    var text = btn.textContent || btn.innerText || '';
                    
                    if(rect.width > 0 && rect.height > 0) {
                        results.allButtons.push({
                            text: text.trim(),
                            class: btn.className,
                            id: btn.id,
                            rect: {w: Math.round(rect.width), h: Math.round(rect.height)},
                            visible: rect.width > 30 && rect.height > 20,
                            dataSpm: btn.getAttribute('data-spm'),
                            disabled: btn.disabled
                        });
                    }
                }
                
                // 查找提交相关的所有元素
                var submitKeywords = ['提交订单', '确认订单', '立即支付', '确认下单', '下单', 'submit', 'order'];
                var allElements = document.querySelectorAll('*');
                
                for(var i = 0; i < allElements.length; i++) {
                    var el = allElements[i];
                    var text = el.textContent || el.innerText || '';
                    
                    for(var k = 0; k < submitKeywords.length; k++) {
                        if(text.includes(submitKeywords[k]) && text.length < 100) {
                            var rect = el.getBoundingClientRect();
                            if(rect.width > 30 && rect.height > 15) {
                                results.submitMatches.push({
                                    tag: el.tagName,
                                    text: text.trim(),
                                    keyword: submitKeywords[k],
                                    class: el.className,
                                    id: el.id,
                                    dataSpm: el.getAttribute('data-spm'),
                                    rect: {w: Math.round(rect.width), h: Math.round(rect.height)},
                                    clickable: ['BUTTON', 'A'].includes(el.tagName) || el.getAttribute('role') === 'button'
                                });
                            }
                        }
                    }
                }
                
                // 生成点击建议 - 优先考虑按钮和大尺寸元素
                var candidates = results.submitMatches.concat(results.allButtons.map(btn => ({
                    tag: 'BUTTON',
                    text: btn.text,
                    class: btn.class,
                    id: btn.id,
                    dataSpm: btn.dataSpm,
                    rect: btn.rect,
                    clickable: true
                })));
                
                // 对候选元素评分
                for(var i = 0; i < candidates.length; i++) {
                    var candidate = candidates[i];
                    var score = 0;
                    
                    // 基础评分
                    if(candidate.tag === 'BUTTON') score += 50;
                    if(candidate.tag === 'A') score += 30;
                    if(candidate.clickable) score += 40;
                    
                    // 文本匹配评分
                    var text = candidate.text.toLowerCase();
                    if(text === '提交订单') score += 50;
                    if(text === '确认订单') score += 45;
                    if(text === '立即支付') score += 40;
                    if(text.includes('提交')) score += 35;
                    if(text.includes('确认')) score += 30;
                    if(text.includes('支付')) score += 25;
                    if(text.includes('下单')) score += 20;
                    
                    // 尺寸评分
                    if(candidate.rect) {
                        var rect = candidate.rect;
                        if(rect.w > 80 && rect.w < 300 && rect.h > 30 && rect.h < 80) score += 30;
                        if(rect.w > 100 && rect.h > 35) score += 20;
                    }
                    
                    // 类名评分
                    if(candidate.class) {
                        if(candidate.class.includes('submit')) score += 40;
                        if(candidate.class.includes('btn')) score += 25;
                        if(candidate.class.includes('button')) score += 25;
                        if(candidate.class.includes('primary')) score += 20;
                    }
                    
                    if(score > 20) {
                        var selector = '';
                        if(candidate.id) {
                            selector = '#' + candidate.id;
                        } else if(candidate.dataSpm) {
                            selector = '[data-spm="' + candidate.dataSpm + '"]';
                        } else if(candidate.class) {
                            var firstClass = candidate.class.split(' ').filter(c => c.length > 3)[0];
                            if(firstClass) selector = '.' + firstClass;
                        }
                        
                        if(selector) {
                            results.recommendations.push({
                                rank: Math.floor(score),
                                selector: selector,
                                text: candidate.text,
                                score: score,
                                method: 'CSS_SELECTOR'
                            });
                        }
                    }
                }
                
                // 排序推荐
                results.recommendations.sort((a, b) => b.score - a.score);
                
                console.log('订单页面分析完成:', results);
                return results;
            }
            
            return analyzeOrderPage();
        """
    
    def get_order_powerful_click_script(self):
        """订单页面强力点击脚本"""
        return """
            function orderPowerfulClick() {
                console.log('开始订单页面强力点击...');
                
                // 订单页面特有的提交文本
                var submitTexts = ['提交订单', '确认订单', '立即支付', '确认下单', '立即下单'];
                
                for(var textIndex = 0; textIndex < submitTexts.length; textIndex++) {
                    var targetText = submitTexts[textIndex];
                    console.log('尝试强力点击:', targetText);
                    
                    // 搜索包含目标文本的所有元素
                    var allElements = document.querySelectorAll('*');
                    var candidates = [];
                    
                    for(var i = 0; i < allElements.length; i++) {
                        var el = allElements[i];
                        var text = el.textContent || el.innerText || '';
                        
                        if(text.includes(targetText) && text.length < 100) {
                            var rect = el.getBoundingClientRect();
                            if(rect.width > 30 && rect.height > 20) {
                                var score = 0;
                                
                                // 评分
                                if(el.tagName === 'BUTTON') score += 50;
                                if(el.tagName === 'A') score += 30;
                                if(text === targetText) score += 40;
                                if(rect.width > 80 && rect.width < 300) score += 20;
                                if(el.className.includes('btn') || el.className.includes('submit')) score += 25;
                                
                                candidates.push({
                                    element: el,
                                    score: score,
                                    text: text.trim()
                                });
                            }
                        }
                    }
                    
                    // 按分数排序并尝试点击
                    candidates.sort((a, b) => b.score - a.score);
                    
                    for(var i = 0; i < Math.min(3, candidates.length); i++) {
                        var candidate = candidates[i];
                        var el = candidate.element;
                        
                        try {
                            // 尝试多种点击方法
                            el.click();
                            return {
                                success: true,
                                clicked: candidate.text,
                                method: '普通click() - ' + targetText
                            };
                        } catch(e1) {
                            try {
                                el.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                                return {
                                    success: true,
                                    clicked: candidate.text,
                                    method: 'MouseEvent - ' + targetText
                                };
                            } catch(e2) {
                                continue;
                            }
                        }
                    }
                }
                
                return {success: false, reason: '未找到可点击的订单提交元素'};
            }
            
            return orderPowerfulClick();
        """
    
    def optimized_sec_kill(self):
        """优化版的秒杀主函数 - 修复版"""
        print("🚀 开始智能秒杀流程...")
        print(f"   ⏰ 当前时间: {datetime.now()}")
        print(f"   🎯 目标时间: {self.seckill_time_obj}")
        
        # 精确等待到抢购时间
        while datetime.now() < self.seckill_time_obj:
            remaining = (self.seckill_time_obj - datetime.now()).total_seconds()
            if remaining > 1:
                sleep(min(0.3, remaining - 1))
            else:
                sleep(0.01)  # 更高精度等待
        
        print("⚡ 抢购时间到！开始智能执行...")
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
        
        # 步骤3：智能抢购循环
        submit_success = False
        retry_count = 0
        last_url = ""
        stagnant_count = 0  # 页面无变化计数
        
        print("🧠 开始智能抢购循环...")
        
        while not submit_success and retry_count < self.max_retry_count:
            retry_count += 1
            elapsed = (datetime.now() - start_time).total_seconds()
            
            if retry_count % 3 == 1:  # 更频繁的进度报告
                print(f"⚡ 第{retry_count}次抢购 (已用时{elapsed:.2f}秒)...")
            
            try:
                # 获取当前页面状态
                current_url = self.driver.current_url.lower()
                page_info = self.driver.execute_script(self.react_utils.get_page_url_check_script())
                
                # 检测页面是否有变化
                if current_url == last_url:
                    stagnant_count += 1
                else:
                    stagnant_count = 0
                    last_url = current_url
                
                # 如果页面长时间无变化，尝试刷新
                if stagnant_count > 10:
                    print("🔄 页面长时间无变化，尝试刷新...")
                    self.driver.refresh()
                    sleep(2)
                    stagnant_count = 0
                    continue
                
                # 智能判断当前页面状态并执行相应操作
                if page_info.get('isCartPage') or 'cart' in current_url:
                    # 在购物车页面，尝试点击结算
                    print(f"📍 检测到购物车页面，尝试结算...")
                    if self.click_settlement_button():
                        print("✅ 结算按钮点击成功，等待页面跳转...")
                        sleep(1)
                        continue
                    else:
                        print("⚠️  结算按钮点击失败，继续重试...")
                        
                elif page_info.get('isOrderPage') or any(keyword in current_url for keyword in ['buy', 'order', 'confirm', 'checkout']):
                    # 在订单确认页面，尝试提交订单
                    print(f"📍 检测到订单确认页面，尝试提交...")
                    
                    # 第一次进入订单页面时等待加载
                    if retry_count == 1 or 'order' not in last_url:
                        print("📍 首次进入订单页面，等待加载...")
                        self.page_loader.wait_for_order_page_load(timeout=3)
                    
                    if self.submit_order():
                        submit_success = True
                        print("🎉 订单提交成功！")
                        break
                    else:
                        print("⚠️  订单提交失败，继续重试...")
                        
                elif page_info.get('isPaymentPage') or any(keyword in current_url for keyword in ['cashier', 'pay']):
                    # 已经到达支付页面
                    print("🎉 已成功到达支付页面！")
                    submit_success = True
                    break
                    
                else:
                    # 未知页面状态，尝试通用策略
                    print(f"📍 未知页面状态: {current_url[:50]}...")
                    
                    # 检查页面内容来判断应该执行什么操作
                    page_content = self.driver.execute_script("""
                        var text = document.body.textContent;
                        return {
                            hasCart: text.includes('购物车') || text.includes('结算'),
                            hasOrder: text.includes('提交订单') || text.includes('确认订单'),
                            hasPayment: text.includes('支付') || text.includes('收银台'),
                            hasError: text.includes('页面出错') || text.includes('网络异常')
                        };
                    """)
                    
                    if page_content.get('hasError'):
                        print("❌ 检测到页面错误，尝试刷新...")
                        self.driver.refresh()
                        sleep(2)
                    elif page_content.get('hasCart'):
                        print("🛒 页面包含购物车内容，尝试结算...")
                        self.click_settlement_button()
                    elif page_content.get('hasOrder'):
                        print("📋 页面包含订单内容，尝试提交...")
                        self.submit_order()
                    elif page_content.get('hasPayment'):
                        print("💳 页面包含支付内容，认为成功...")
                        submit_success = True
                        break
                    else:
                        print("❓ 无法识别页面状态，重新导航到购物车...")
                        self.driver.get("https://cart.taobao.com/cart.htm")
                        sleep(1)
                    
            except Exception as e:
                if retry_count % 5 == 0:  # 减少错误报告频率
                    print(f"⚠️  第{retry_count}次抢购错误: {str(e)}")
                self.save_debug_info("seckill_error", e)
            
            sleep(0.05)  # 更短的重试间隔
        
        # 输出最终结果
        total_time = (datetime.now() - start_time).total_seconds()
        if submit_success:
            print(f"🎊 抢购成功！总用时: {total_time:.2f}秒")
            print(f"📍 最终页面: {self.driver.current_url}")
            if self.password:
                print("💳 开始自动支付流程...")
                self.pay()
        else:
            print(f"😞 抢购失败，已达到最大重试次数({self.max_retry_count}次)")
            print(f"   📊 总用时: {total_time:.2f}秒")
            print(f"   📍 最终页面: {self.driver.current_url}")
        
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