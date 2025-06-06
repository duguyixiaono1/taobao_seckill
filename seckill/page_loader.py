#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
页面加载工具模块 - 性能优化版
处理淘宝现代React页面的加载和等待逻辑
"""

from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from .react_utils import ReactPageUtils

class PageLoader:
    """页面加载工具类 - 性能优化版"""
    
    def __init__(self, driver):
        self.driver = driver
        self.react_utils = ReactPageUtils()
    
    def wait_for_cart_page_load(self, timeout=8):
        """等待购物车页面完全加载 - 快速版"""
        try:
            print("⚡ 快速等待购物车页面加载...")
            return self._wait_for_react_page_load_fast(timeout, 'cart')
        except Exception as e:
            print(f"⚠️  购物车页面加载失败: {e}")
            return False
    
    def wait_for_order_page_load(self, timeout=10):
        """等待订单确认页面完全加载 - 快速版"""
        try:
            print("⚡ 快速等待订单确认页面加载...")
            return self._wait_for_react_page_load_fast(timeout, 'order')
        except Exception as e:
            print(f"⚠️  订单页面加载失败: {e}")
            return False
    
    def _wait_for_react_page_load_fast(self, timeout, page_type):
        """高性能React页面加载等待"""
        # 1. 快速DOM检查
        try:
            WebDriverWait(self.driver, 3).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("   ✅ DOM就绪")
        except:
            print("   ⚠️  DOM加载超时，继续执行")
        
        # 2. 并行检查React容器和内容
        print("   ⚡ 检查React应用状态...")
        for i in range(timeout):
            try:
                # 一次性检查所有条件
                status = self.driver.execute_script("""
                    // 检查容器
                    var container = document.getElementById('ice-container');
                    if (!container) return {ready: false, reason: 'no_container'};
                    
                    // 检查内容
                    var textContent = container.textContent || container.innerText || '';
                    var elements = container.querySelectorAll('*');
                    
                    // 根据页面类型检查特定内容
                    var hasContent = false;
                    if (arguments[0] === 'cart') {
                        hasContent = textContent.includes('全选') || 
                                   textContent.includes('结算') || 
                                   textContent.includes('合计') ||
                                   elements.length > 50;
                    } else if (arguments[0] === 'order') {
                        hasContent = textContent.includes('提交订单') || 
                                   textContent.includes('商品总价') || 
                                   textContent.includes('实付款') ||
                                   elements.length > 30;
                    } else {
                        hasContent = elements.length > 20;
                    }
                    
                    // 强制隐藏加载动画
                    try {
                        if (window.$tradeHideDocLoading) {
                            window.$tradeHideDocLoading();
                        }
                    } catch(e) {}
                    
                    return {
                        ready: hasContent,
                        elements: elements.length,
                        textLength: textContent.length,
                        reason: hasContent ? 'success' : 'loading'
                    };
                """, page_type)
                
                if status['ready']:
                    print(f"   ✅ {page_type}页面就绪 (元素:{status['elements']}, 文本:{status['textLength']})")
                    # 最小等待确保稳定
                    sleep(0.5)
                    return True
                    
                if i % 2 == 1:  # 每2秒报告一次
                    print(f"   ⏳ 等待{page_type}内容... ({i+1}/{timeout}) - {status['reason']}")
                
            except Exception as e:
                if i > timeout * 0.7:  # 后期才报告错误
                    print(f"   ⚠️  检查异常: {e}")
            
            sleep(1)
        
        print(f"   ⚠️  {page_type}页面加载超时，但继续执行")
        return True  # 超时也返回True，避免阻塞
    
    def quick_content_check(self, page_type):
        """快速内容检查，不等待"""
        try:
            result = self.driver.execute_script("""
                var container = document.getElementById('ice-container');
                if (!container) return false;
                
                var textContent = container.textContent || container.innerText || '';
                
                if (arguments[0] === 'cart') {
                    return textContent.includes('结算') && textContent.includes('合计');
                } else if (arguments[0] === 'order') {
                    return textContent.includes('提交订单') || textContent.includes('立即支付');
                }
                
                return textContent.length > 100;
            """, page_type)
            
            return result
        except:
            return False 