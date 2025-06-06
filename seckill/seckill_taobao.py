#!/usr/bin/env python3
# encoding=utf-8


import os
import json
import platform
from time import sleep
from random import choice
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

import seckill.settings as utils_settings
from utils.utils import get_useragent_data
from utils.utils import notify_user

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from optimized_sec_kill import OptimizedSecKill
# 直接使用最优版本，无需考虑其他选择



# 抢购失败最大次数
max_retry_count = 30


def default_chrome_path():

    driver_dir = getattr(utils_settings, "DRIVER_DIR", None)
    if platform.system() == "Windows":
        if driver_dir:
            return os.path.abspath(os.path.join(driver_dir, "chromedriver.exe"))

        raise Exception("The chromedriver drive path attribute is not found.")
    else:
        if driver_dir:
            return os.path.abspath(os.path.join(driver_dir, "chromedriver"))

        raise Exception("The chromedriver drive path attribute is not found.")


class ChromeDrive:

    def __init__(self, chrome_path=None, seckill_time=None, password=None):
        self.chrome_path = chrome_path or default_chrome_path()
        self.seckill_time = seckill_time
        self.seckill_time_obj = datetime.strptime(self.seckill_time, '%Y-%m-%d %H:%M:%S')
        self.password = password

    def start_driver(self):
        try:
            driver = self.find_chromedriver()
        except WebDriverException:
            print("Unable to find chromedriver, Please check the drive path.")
        else:
            return driver

    def find_chromedriver(self):
        try:
            # 首先尝试使用webdriver-manager自动管理的chromedriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self.build_chrome_options())

        except WebDriverException:
            try:
                # 如果失败，尝试使用系统PATH中的chromedriver
                driver = webdriver.Chrome(options=self.build_chrome_options())

            except WebDriverException:
                try:
                    # 最后尝试使用指定路径的chromedriver
                    service = Service(executable_path=self.chrome_path)
                    driver = webdriver.Chrome(service=service, options=self.build_chrome_options())

                except WebDriverException:
                    raise
        
        # 执行JavaScript隐藏自动化特征
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("delete navigator.__proto__.webdriver")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']})")
        driver.execute_script("window.chrome = { runtime: {} }")
        driver.execute_script("Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})})})")
        driver.execute_script("Object.defineProperty(window, 'outerHeight', {get: () => window.innerHeight})")
        driver.execute_script("Object.defineProperty(window, 'outerWidth', {get: () => window.innerWidth})")
        
        return driver

    def build_chrome_options(self):
        """配置启动项"""
        chrome_options = webdriver.ChromeOptions()
        
        # 基本配置
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        
        # 反检测配置
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 性能优化配置
        arguments = [
            '--no-sandbox', 
            '--disable-impl-side-painting', 
            '--disable-setuid-sandbox', 
            '--disable-seccomp-filter-sandbox',
            '--disable-breakpad', 
            '--disable-client-side-phishing-detection', 
            '--disable-cast',
            '--disable-cast-streaming-hw-encoding', 
            '--disable-cloud-import', 
            '--disable-popup-blocking',
            '--ignore-certificate-errors', 
            '--disable-session-crashed-bubble', 
            '--disable-ipv6',
            '--allow-http-screen-capture', 
            '--start-maximized',
            '--disable-dev-shm-usage',
            '--disable-extensions',
            '--disable-plugins',
            '--no-first-run',
            '--disable-default-apps'
        ]
        
        for arg in arguments:
            chrome_options.add_argument(arg)
            
        # 设置现代浏览器User-Agent
        user_agents = get_useragent_data()
        selected_ua = choice(user_agents)
        chrome_options.add_argument(f'--user-agent={selected_ua}')
        
        # 设置窗口大小
        chrome_options.add_argument('--window-size=1920,1080')
        
        return chrome_options

    def login(self, login_url: str="https://www.taobao.com"):
        """优化版登录方法，使用多选择器策略"""
        if login_url:
            self.driver = self.start_driver()
        else:
            print("Please input the login url.")
            raise Exception("Please input the login url.")

        print("🔐 开始智能登录流程...")
        max_login_attempts = 3
        
        for attempt in range(max_login_attempts):
            try:
                print(f"🔄 第{attempt + 1}次登录尝试...")
                self.driver.get(login_url)
                sleep(3)  # 等待页面加载
                
                # 检查是否已经登录
                if self._check_login_status():
                    print("✅ 检测到已登录状态")
                    return
                
                # 尝试找到登录按钮/链接
                login_element = self._find_login_element()
                
                if login_element:
                    print("🖱️ 找到登录按钮，准备点击...")
                    
                    # 滚动到元素位置并点击
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", login_element)
                    sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", login_element)
                    
                    print("⏳ 请在60秒内完成登录（扫码或输入账号密码）...")
                    
                    # 等待用户完成登录
                    login_success = self._wait_for_login_completion(60)
                    
                    if login_success:
                        print("🎉 登录成功！")
                        return
                    else:
                        print("⚠️ 登录超时或失败，准备重试...")
                        continue
                else:
                    print("❌ 未找到登录按钮，可能已经登录或页面结构变化")
                    # 检查是否实际上已经登录了
                    if self._check_login_status():
                        print("✅ 实际上已经登录")
                        return
                    else:
                        print("🔄 页面可能需要刷新...")
                        continue
                        
            except Exception as e:
                print(f"⚠️ 登录过程中出现错误: {str(e)}")
                if attempt == max_login_attempts - 1:
                    print("❌ 多次登录尝试失败，请检查网络连接或手动登录")
                    raise
                continue
    
    def _find_login_element(self):
        """查找登录按钮/链接，使用多选择器策略"""
        # 2024年淘宝登录按钮的多种可能选择器
        login_selectors = [
            # 常见的登录文本
            (By.LINK_TEXT, "亲，请登录", "经典登录链接"),
            (By.LINK_TEXT, "请登录", "简化登录链接"),
            (By.LINK_TEXT, "登录", "登录链接"),
            (By.PARTIAL_LINK_TEXT, "登录", "包含登录的链接"),
            
            # 基于XPATH的选择器
            (By.XPATH, "//a[contains(text(), '登录')]", "包含登录文本的链接"),
            (By.XPATH, "//a[contains(text(), '请登录')]", "包含请登录文本的链接"),
            (By.XPATH, "//span[contains(text(), '登录')]", "包含登录文本的span"),
            (By.XPATH, "//div[contains(text(), '登录')]", "包含登录文本的div"),
            
            # 基于常见ID和类名
            (By.ID, "J_Quick2login", "快速登录按钮"),
            (By.CSS_SELECTOR, ".h-login-link", "登录链接CSS"),
            (By.CSS_SELECTOR, ".site-nav-login", "站点导航登录"),
            (By.CSS_SELECTOR, "[data-spm*='login']", "登录SPM选择器"),
            
            # 更通用的选择器
            (By.XPATH, "//*[contains(@class, 'login')]", "包含login类的元素"),
            (By.XPATH, "//a[contains(@href, 'login')]", "href包含login的链接"),
        ]
        
        for by_method, selector, description in login_selectors:
            try:
                element = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((by_method, selector))
                )
                print(f"✅ 找到登录元素: {description}")
                return element
            except:
                print(f"❌ 未找到: {description}")
                continue
        
        return None
    
    def _check_login_status(self):
        """检查当前登录状态"""
        try:
            # 多种方式检查登录状态
            login_indicators = [
                # 用户信息相关选择器
                (By.XPATH, '//*[@id="J_SiteNavMytaobao"]/div[1]/a/span', "经典用户名"),
                (By.XPATH, '//span[contains(@class, "site-nav-user")]', "用户导航"),
                (By.CSS_SELECTOR, '.site-nav-user', "用户导航CSS"),
                (By.XPATH, '//a[contains(@href, "mytaobao")]', "我的淘宝链接"),
                (By.XPATH, '//*[contains(text(), "我的淘宝")]', "我的淘宝文本"),
            ]
            
            for by_method, selector, description in login_indicators:
                try:
                    element = self.driver.find_element(by_method, selector)
                    if element and element.text.strip():
                        print(f"✅ 检测到登录状态: {description} - {element.text}")
                        return True
                except:
                    continue
            
            # 检查页面源码中的登录状态
            page_source = self.driver.page_source
            if any(keyword in page_source for keyword in ['我的淘宝', 'mytaobao', 'user-nick']):
                print("✅ 通过页面源码检测到登录状态")
                return True
                
            return False
            
        except Exception as e:
            print(f"⚠️ 登录状态检查失败: {e}")
            return False
    
    def _wait_for_login_completion(self, timeout=60):
        """等待用户完成登录"""
        for i in range(timeout):
            sleep(1)
            if self._check_login_status():
                return True
            
            # 每10秒提示一次
            if i % 10 == 0 and i > 0:
                remaining = timeout - i
                print(f"⏳ 等待登录中... ({remaining}秒剩余)")
        
        return False

    def keep_wait(self):
        self.login()
        print("等待到点抢购...")
        while True:
            current_time = datetime.now()
            time_diff = (self.seckill_time_obj - current_time).total_seconds()
            
            print(f"⏰ 当前时间: {current_time.strftime('%H:%M:%S')}")
            print(f"🎯 目标时间: {self.seckill_time_obj.strftime('%H:%M:%S')}")
            print(f"⏳ 剩余时间: {time_diff:.1f}秒")
            
            if time_diff > 180:  # 如果还有超过3分钟
                self.driver.get("https://cart.taobao.com/cart.htm")
                print("📱 每分钟刷新一次界面，防止登录超时...")
                sleep(60)
            elif time_diff > 0:  # 如果时间还没到但已经很接近
                print(f"🚀 抢购时间将近({time_diff:.1f}秒)，停止自动刷新，准备进入抢购阶段...")
                self.get_cookie()
                break
            else:  # 如果时间已经过了
                print("⚡ 抢购时间已到或已过，立即进入抢购阶段...")
                self.get_cookie()
                break


    def sec_kill(self):
        """使用优化版秒杀方法"""
        print("🔄 使用OptimizedSecKill优化版秒杀方法...")
        
        # 等待登录和时间
        self.keep_wait()
        
        # 创建优化版秒杀实例
        optimizer = OptimizedSecKill(
            driver=self.driver,
            seckill_time_obj=self.seckill_time_obj,
            password=self.password,
            max_retry_count=50  # 增加重试次数
        )
        
        # 执行优化版秒杀
        return optimizer.optimized_sec_kill()


    def pay(self):
        try:
            element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'sixDigitPassword')))
            element.send_keys(self.password)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'J_authSubmit'))).click()
            notify_user(msg="付款成功")
        except:
            notify_user(msg="付款失败")
        finally:
            sleep(60)
            self.driver.quit()


    def get_cookie(self):
        cookies = self.driver.get_cookies()
        cookie_json = json.dumps(cookies)
        with open('./cookies.txt', 'w', encoding = 'utf-8') as f:
            f.write(cookie_json)
