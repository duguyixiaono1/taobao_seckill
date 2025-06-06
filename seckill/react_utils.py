#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
React页面处理工具模块 - 性能优化版
包含所有与React页面交互相关的JavaScript代码和工具函数
"""

class ReactPageUtils:
    """React页面处理工具类 - 性能优化版"""
    
    @staticmethod
    def get_hide_loading_script():
        """获取隐藏加载动画的脚本"""
        return """
            try {
                if (window.$tradeHideDocLoading) {
                    window.$tradeHideDocLoading();
                }
            } catch(e) {}
        """
    
    @staticmethod
    def get_select_products_script():
        """获取选择商品的脚本 - 优化版"""
        return """
            var result = {total: 0, selected: 0};
            
            // 快速查找并选择所有复选框
            var checkboxes = document.querySelectorAll('input[type="checkbox"]');
            
            for(var i = 0; i < checkboxes.length; i++) {
                var cb = checkboxes[i];
                if(cb.disabled || cb.style.display === 'none') continue;
                
                result.total++;
                
                if(!cb.checked) {
                    try {
                        cb.click();
                        result.selected++;
                    } catch(e) {
                        try {
                            cb.checked = true;
                            cb.dispatchEvent(new Event('change', {bubbles: true}));
                            result.selected++;
                        } catch(e2) {}
                    }
                } else {
                    result.selected++;
                }
            }
            
            return result;
        """
    
    @staticmethod
    def get_find_settlement_button_script():
        """获取查找结算按钮的脚本 - 高性能版"""
        return """
            // 高性能结算按钮查找策略
            function findSettlementButtonFast() {
                // 策略1: 直接查找最常见的结算按钮格式
                var patterns = [
                    'button:contains("结算")',
                    'div:contains("结算")',
                    '*[class*="settlement"]',
                    '*[class*="checkout"]'
                ];
                
                // 优先查找右下角的橙色按钮
                var buttons = document.querySelectorAll('button, div, span, a');
                var candidates = [];
                
                for(var i = 0; i < buttons.length; i++) {
                    var btn = buttons[i];
                    var text = btn.textContent || btn.innerText || '';
                    
                    // 快速匹配结算文本
                    if(!text.includes('结算')) continue;
                    
                    var rect = btn.getBoundingClientRect();
                    if(rect.width <= 0 || rect.height <= 0) continue;
                    
                    var styles = window.getComputedStyle(btn);
                    
                    // 计算优先级得分
                    var score = 0;
                    score += rect.right * 0.1;  // 右侧位置加分
                    score += rect.bottom * 0.1; // 底部位置加分
                    score += (styles.backgroundColor.includes('rgb(255') || 
                             styles.backgroundColor.includes('orange')) ? 1000 : 0; // 橙色加分
                    score += text.match(/结算\\s*\\(\\d+\\)/) ? 2000 : 0; // 精确格式加分
                    score += (btn.tagName === 'BUTTON') ? 500 : 0; // 按钮标签加分
                    
                    candidates.push({element: btn, text: text.trim(), score: score});
                }
                
                // 按得分排序，优先点击高分按钮
                candidates.sort(function(a, b) { return b.score - a.score; });
                
                // 尝试点击最佳候选
                for(var i = 0; i < Math.min(candidates.length, 3); i++) {
                    try {
                        var candidate = candidates[i];
                        candidate.element.scrollIntoView({behavior: 'instant'});
                        candidate.element.click();
                        return {success: true, clicked: candidate.text, method: 'fast-' + i};
                    } catch(e) {}
                }
                
                return {success: false, candidates: candidates.length};
            }
            
            return findSettlementButtonFast();
        """
    
    @staticmethod
    def get_find_submit_button_script():
        """获取查找提交订单按钮的脚本 - 高性能版"""
        return """
            // 高性能提交订单按钮查找
            function findSubmitButtonFast() {
                var results = [];
                
                // 快速查找策略：优先查找最可能的按钮
                var submitTexts = ['提交订单', '立即支付', '确认支付', '立即购买'];
                var bestCandidate = null;
                var bestScore = 0;
                
                var buttons = document.querySelectorAll('button, a, input[type="submit"]');
                
                for(var i = 0; i < buttons.length; i++) {
                    var btn = buttons[i];
                    var text = btn.textContent || btn.innerText || btn.value || '';
                    var rect = btn.getBoundingClientRect();
                    
                    // 检查是否包含提交相关文本
                    var hasSubmitText = false;
                    for(var j = 0; j < submitTexts.length; j++) {
                        if(text.includes(submitTexts[j])) {
                            hasSubmitText = true;
                            break;
                        }
                    }
                    
                    if(!hasSubmitText || rect.width <= 0 || rect.height <= 0) continue;
                    
                    var styles = window.getComputedStyle(btn);
                    
                    // 快速计算得分
                    var score = 0;
                    score += rect.right + rect.bottom; // 位置得分
                    score += (styles.backgroundColor.includes('rgb(255') || 
                             styles.backgroundColor.includes('orange')) ? 1000 : 0;
                    score += text.includes('提交订单') ? 2000 : 0; // 精确匹配加分
                    score += (btn.tagName === 'BUTTON') ? 500 : 0;
                    score += (rect.width > 80 && rect.height > 30) ? 300 : 0;
                    
                    if(score > bestScore) {
                        bestScore = score;
                        bestCandidate = {element: btn, text: text.trim(), score: score};
                    }
                }
                
                results.push('找到最佳候选按钮');
                
                // 尝试点击最佳按钮
                if(bestCandidate) {
                    try {
                        bestCandidate.element.scrollIntoView({behavior: 'instant'});
                        bestCandidate.element.click();
                        
                        return {
                            success: true,
                            clicked: bestCandidate.text,
                            method: 'fast-submit',
                            results: results
                        };
                    } catch(e) {
                        results.push('点击失败: ' + e.message);
                    }
                }
                
                return {success: false, results: results, candidates: bestCandidate ? 1 : 0};
            }
            
            return findSubmitButtonFast();
        """
    
    @staticmethod
    def get_page_content_check_script():
        """获取页面内容检查脚本"""
        return """
            var container = document.getElementById('ice-container') || document.getElementById('tbpc-trade-cart');
            if (!container) return {elements: 0, hasContent: false};
            
            var elements = container.querySelectorAll('*');
            var textContent = container.textContent || container.innerText || '';
            
            return {
                elements: elements.length,
                hasContent: textContent.length > 100,
                textSample: textContent.substring(0, 200)
            };
        """
    
    @staticmethod
    def get_verify_selection_script():
        """获取验证商品选择状态的脚本 - 优化版"""
        return """
            // 快速查找合计金额
            var elements = document.querySelectorAll('*');
            for(var i = 0; i < Math.min(elements.length, 200); i++) {
                var text = elements[i].textContent || elements[i].innerText || '';
                if(text.includes('合计') && text.includes('¥')) {
                    var match = text.match(/¥\\s*(\\d+(?:\\.\\d+)?)/);
                    if(match) {
                        return parseFloat(match[1]);
                    }
                }
            }
            return 0;
        """
    
    @staticmethod
    def get_smart_element_finder_script(element_type):
        """通用智能元素查找脚本"""
        return f"""
            // 通用高性能元素查找
            function smartFind(elementType) {{
                var patterns = {{
                    'settlement': ['结算', '去结算', '立即结算'],
                    'submit': ['提交订单', '立即支付', '确认支付', '立即购买'],
                    'login': ['登录', '登陆', '请登录']
                }};
                
                var texts = patterns[elementType] || [elementType];
                var selectors = ['button', 'a', 'span', 'div', 'input[type="submit"]'];
                
                for(var i = 0; i < selectors.length; i++) {{
                    var elements = document.querySelectorAll(selectors[i]);
                    
                    for(var j = 0; j < elements.length; j++) {{
                        var el = elements[j];
                        var text = el.textContent || el.innerText || el.value || '';
                        
                        for(var k = 0; k < texts.length; k++) {{
                            if(text.includes(texts[k])) {{
                                var rect = el.getBoundingClientRect();
                                if(rect.width > 0 && rect.height > 0) {{
                                    return {{element: el, text: text.trim(), found: true}};
                                }}
                            }}
                        }}
                    }}
                }}
                
                return {{found: false}};
            }}
            
            return smartFind('{element_type}');
        """ 