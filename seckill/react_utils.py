#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
React页面处理工具模块 - 修复版
专门解决结算按钮点击和页面跳转问题
"""

class ReactPageUtils:
    """React页面处理工具类 - 修复版"""
    
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
        """获取查找结算按钮的脚本 - 修复版"""
        return """
            // 修复版结算按钮查找和点击策略
            function findAndClickSettlementButton() {
                console.log('开始查找结算按钮...');
                
                // 策略1: 查找具体的可点击结算按钮
                var buttonSelectors = [
                    'button[data-spm*="settlement"]',
                    'button[data-spm*="checkout"]', 
                    'a[data-spm*="settlement"]',
                    'a[data-spm*="checkout"]',
                    'div[data-spm*="settlement"][role="button"]',
                    'span[data-spm*="settlement"][role="button"]'
                ];
                
                for(var i = 0; i < buttonSelectors.length; i++) {
                    var elements = document.querySelectorAll(buttonSelectors[i]);
                    for(var j = 0; j < elements.length; j++) {
                        var btn = elements[j];
                        var rect = btn.getBoundingClientRect();
                        
                        if(rect.width > 30 && rect.height > 20) {
                            console.log('找到SPM结算按钮:', btn);
                            try {
                                btn.scrollIntoView({behavior: 'instant'});
                                btn.click();
                                return {success: true, clicked: '精确SPM按钮', method: 'spm-button'};
                            } catch(e) {
                                console.log('SPM按钮点击失败:', e);
                            }
                        }
                    }
                }
                
                // 策略2: 查找包含"结算"文本的具体按钮元素
                var allButtons = document.querySelectorAll('button, a, span[role="button"], div[role="button"]');
                var settlementCandidates = [];
                
                for(var i = 0; i < allButtons.length; i++) {
                    var btn = allButtons[i];
                    var text = btn.textContent || btn.innerText || '';
                    var rect = btn.getBoundingClientRect();
                    
                    // 查找精确的结算按钮
                    if(text.includes('结算') && !text.includes('明细') && text.length < 50) {
                        if(rect.width > 30 && rect.height > 20) {
                            var score = 0;
                            score += (text === '结算') ? 1000 : 0; // 精确匹配
                            score += text.match(/^结算\\s*\\(\\d+\\)$/) ? 800 : 0; // 结算(数字)格式
                            score += (btn.tagName === 'BUTTON') ? 500 : 0;
                            score += rect.right + rect.bottom; // 位置权重
                            
                            settlementCandidates.push({
                                element: btn,
                                text: text.trim(),
                                score: score,
                                rect: rect
                            });
                        }
                    }
                }
                
                // 按得分排序
                settlementCandidates.sort(function(a, b) { return b.score - a.score; });
                
                console.log('找到结算候选按钮数量:', settlementCandidates.length);
                
                // 尝试点击最佳候选
                for(var i = 0; i < Math.min(settlementCandidates.length, 3); i++) {
                    var candidate = settlementCandidates[i];
                    console.log('尝试点击候选按钮:', candidate.text, '得分:', candidate.score);
                    
                    try {
                        var btn = candidate.element;
                        
                        // 滚动到可见区域
                        btn.scrollIntoView({behavior: 'instant', block: 'center'});
                        
                        // 多种点击方式
                        var clicked = false;
                        
                        // 方式1: 原生点击
                        try {
                            btn.click();
                            clicked = true;
                            console.log('原生点击成功');
                        } catch(e) {
                            console.log('原生点击失败:', e);
                        }
                        
                        // 方式2: 触发鼠标事件
                        if(!clicked) {
                            try {
                                var clickEvent = new MouseEvent('click', {
                                    view: window,
                                    bubbles: true,
                                    cancelable: true
                                });
                                btn.dispatchEvent(clickEvent);
                                clicked = true;
                                console.log('鼠标事件触发成功');
                            } catch(e) {
                                console.log('鼠标事件触发失败:', e);
                            }
                        }
                        
                        // 方式3: 查找并点击子元素
                        if(!clicked) {
                            try {
                                var clickableChild = btn.querySelector('button, a, span');
                                if(clickableChild) {
                                    clickableChild.click();
                                    clicked = true;
                                    console.log('子元素点击成功');
                                }
                            } catch(e) {
                                console.log('子元素点击失败:', e);
                            }
                        }
                        
                        if(clicked) {
                            // 等待一下检查是否跳转
                            setTimeout(function() {
                                var currentUrl = window.location.href;
                                console.log('点击后URL:', currentUrl);
                            }, 100);
                            
                            return {
                                success: true, 
                                clicked: candidate.text,
                                method: 'precise-button-' + i,
                                score: candidate.score
                            };
                        }
                        
                    } catch(e) {
                        console.log('候选按钮点击异常:', e);
                    }
                }
                
                // 策略3: 最后尝试React事件模拟
                console.log('尝试React事件模拟...');
                try {
                    var reactButtons = document.querySelectorAll('[data-reactroot] button, [data-reactid] button');
                    for(var i = 0; i < reactButtons.length; i++) {
                        var btn = reactButtons[i];
                        var text = btn.textContent || '';
                        if(text.includes('结算') && text.length < 20) {
                            try {
                                // React合成事件
                                var syntheticEvent = new Event('click', {bubbles: true});
                                Object.defineProperty(syntheticEvent, 'target', {
                                    value: btn,
                                    enumerable: true
                                });
                                btn.dispatchEvent(syntheticEvent);
                                
                                return {success: true, clicked: text, method: 'react-synthetic'};
                            } catch(e) {
                                console.log('React事件失败:', e);
                            }
                        }
                    }
                } catch(e) {
                    console.log('React事件模拟异常:', e);
                }
                
                return {success: false, candidates: settlementCandidates.length, reason: '所有方法都失败'};
            }
            
            return findAndClickSettlementButton();
        """
    
    @staticmethod
    def get_find_submit_button_script():
        """获取查找提交订单按钮的脚本 - 修复版"""
        return """
            // 修复版提交订单按钮查找
            function findAndClickSubmitButton() {
                console.log('开始查找提交订单按钮...');
                var results = [];
                
                // 策略1: 精确查找提交按钮
                var submitSelectors = [
                    'button[data-spm*="submit"]',
                    'button[data-spm*="order"]',
                    'button[data-spm*="pay"]',
                    'a[data-spm*="submit"]',
                    'a[data-spm*="order"]'
                ];
                
                for(var i = 0; i < submitSelectors.length; i++) {
                    var elements = document.querySelectorAll(submitSelectors[i]);
                    for(var j = 0; j < elements.length; j++) {
                        var btn = elements[j];
                        var rect = btn.getBoundingClientRect();
                        
                        if(rect.width > 30 && rect.height > 20) {
                            console.log('找到SPM提交按钮:', btn);
                            try {
                                btn.scrollIntoView({behavior: 'instant'});
                                btn.click();
                                results.push('SPM按钮点击成功');
                                return {success: true, clicked: 'SPM提交按钮', method: 'spm-submit', results: results};
                            } catch(e) {
                                results.push('SPM按钮点击失败: ' + e.message);
                            }
                        }
                    }
                }
                
                // 策略2: 文本匹配查找
                var submitTexts = ['提交订单', '立即支付', '确认支付'];
                var allButtons = document.querySelectorAll('button, a, input[type="submit"]');
                var bestCandidate = null;
                var bestScore = 0;
                
                for(var i = 0; i < allButtons.length; i++) {
                    var btn = allButtons[i];
                    var text = btn.textContent || btn.innerText || btn.value || '';
                    var rect = btn.getBoundingClientRect();
                    
                    for(var j = 0; j < submitTexts.length; j++) {
                        if(text.includes(submitTexts[j])) {
                            if(rect.width > 30 && rect.height > 20) {
                                var score = 0;
                                score += (text === submitTexts[j]) ? 1000 : 500; // 精确匹配得分更高
                                score += (btn.tagName === 'BUTTON') ? 300 : 0;
                                score += rect.right + rect.bottom;
                                
                                if(score > bestScore) {
                                    bestScore = score;
                                    bestCandidate = {element: btn, text: text.trim(), score: score};
                                }
                            }
                            break;
                        }
                    }
                }
                
                if(bestCandidate) {
                    console.log('找到最佳提交按钮:', bestCandidate.text);
                    try {
                        var btn = bestCandidate.element;
                        btn.scrollIntoView({behavior: 'instant'});
                        
                        // 多种点击方式
                        try {
                            btn.click();
                        } catch(e) {
                            // 触发鼠标事件
                            var clickEvent = new MouseEvent('click', {
                                view: window,
                                bubbles: true,
                                cancelable: true
                            });
                            btn.dispatchEvent(clickEvent);
                        }
                        
                        results.push('文本匹配按钮点击成功');
                        return {
                            success: true,
                            clicked: bestCandidate.text,
                            method: 'text-match',
                            results: results
                        };
                    } catch(e) {
                        results.push('文本匹配按钮点击失败: ' + e.message);
                    }
                }
                
                results.push('未找到有效的提交按钮');
                return {success: false, results: results, candidates: bestCandidate ? 1 : 0};
            }
            
            return findAndClickSubmitButton();
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
    def get_page_url_check_script():
        """检查页面URL变化的脚本"""
        return """
            return {
                currentUrl: window.location.href,
                isCartPage: window.location.href.includes('cart'),
                isOrderPage: window.location.href.includes('buy') || 
                            window.location.href.includes('order') || 
                            window.location.href.includes('confirm'),
                isPaymentPage: window.location.href.includes('cashier') || 
                              window.location.href.includes('pay'),
                pageTitle: document.title
            };
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
    
    @staticmethod
    def get_page_analysis_script():
        """分析页面结构，找出所有可能的结算相关元素"""
        return """
            function analyzePage() {
                console.log('开始分析页面结构...');
                
                var analysis = {
                    allButtons: [],
                    allLinks: [],
                    allClickable: [],
                    textMatches: [],
                    spmElements: []
                };
                
                // 分析所有按钮
                var buttons = document.querySelectorAll('button');
                for(var i = 0; i < buttons.length; i++) {
                    var btn = buttons[i];
                    var rect = btn.getBoundingClientRect();
                    var text = btn.textContent || btn.innerText || '';
                    
                    if(rect.width > 0 && rect.height > 0) {
                        analysis.allButtons.push({
                            tag: btn.tagName,
                            text: text.trim(),
                            class: btn.className,
                            id: btn.id,
                            dataSpm: btn.getAttribute('data-spm'),
                            rect: {w: Math.round(rect.width), h: Math.round(rect.height)},
                            visible: rect.width > 10 && rect.height > 10
                        });
                    }
                }
                
                // 分析所有链接
                var links = document.querySelectorAll('a');
                for(var i = 0; i < links.length; i++) {
                    var link = links[i];
                    var rect = link.getBoundingClientRect();
                    var text = link.textContent || link.innerText || '';
                    
                    if(rect.width > 0 && rect.height > 0) {
                        analysis.allLinks.push({
                            tag: link.tagName,
                            text: text.trim(),
                            href: link.href,
                            class: link.className,
                            dataSpm: link.getAttribute('data-spm'),
                            rect: {w: Math.round(rect.width), h: Math.round(rect.height)}
                        });
                    }
                }
                
                // 分析所有可点击元素
                var clickableSelectors = [
                    '[role="button"]',
                    '[onclick]',
                    'div[class*="btn"]',
                    'span[class*="btn"]',
                    'div[class*="button"]',
                    'span[class*="button"]'
                ];
                
                for(var s = 0; s < clickableSelectors.length; s++) {
                    var elements = document.querySelectorAll(clickableSelectors[s]);
                    for(var i = 0; i < elements.length; i++) {
                        var el = elements[i];
                        var rect = el.getBoundingClientRect();
                        var text = el.textContent || el.innerText || '';
                        
                        if(rect.width > 0 && rect.height > 0) {
                            analysis.allClickable.push({
                                tag: el.tagName,
                                text: text.trim(),
                                class: el.className,
                                selector: clickableSelectors[s],
                                dataSpm: el.getAttribute('data-spm'),
                                rect: {w: Math.round(rect.width), h: Math.round(rect.height)}
                            });
                        }
                    }
                }
                
                // 查找包含"结算"相关文本的所有元素
                var allElements = document.querySelectorAll('*');
                var settlementKeywords = ['结算', '去结算', '立即结算', 'checkout', 'settlement'];
                
                for(var i = 0; i < allElements.length; i++) {
                    var el = allElements[i];
                    var text = el.textContent || el.innerText || '';
                    
                    for(var k = 0; k < settlementKeywords.length; k++) {
                        if(text.includes(settlementKeywords[k]) && text.length < 100) {
                            var rect = el.getBoundingClientRect();
                            analysis.textMatches.push({
                                tag: el.tagName,
                                text: text.trim(),
                                keyword: settlementKeywords[k],
                                class: el.className,
                                id: el.id,
                                dataSpm: el.getAttribute('data-spm'),
                                rect: rect.width > 0 ? {w: Math.round(rect.width), h: Math.round(rect.height)} : null,
                                clickable: ['BUTTON', 'A'].includes(el.tagName) || el.getAttribute('role') === 'button'
                            });
                        }
                    }
                }
                
                // 查找所有有data-spm属性的元素
                var spmElements = document.querySelectorAll('[data-spm]');
                for(var i = 0; i < spmElements.length; i++) {
                    var el = spmElements[i];
                    var spm = el.getAttribute('data-spm');
                    var text = el.textContent || el.innerText || '';
                    
                    if(spm && (spm.includes('settlement') || spm.includes('checkout') || text.includes('结算'))) {
                        var rect = el.getBoundingClientRect();
                        analysis.spmElements.push({
                            tag: el.tagName,
                            text: text.trim(),
                            spm: spm,
                            class: el.className,
                            rect: rect.width > 0 ? {w: Math.round(rect.width), h: Math.round(rect.height)} : null
                        });
                    }
                }
                
                console.log('页面分析完成:', analysis);
                return analysis;
            }
            
            return analyzePage();
        """
    
    @staticmethod
    def get_deep_settlement_analysis_script():
        """深度分析结算相关元素的子元素结构"""
        return """
            function deepAnalyzeSettlement() {
                console.log('开始深度分析结算区域...');
                
                var results = {
                    settlementContainers: [],
                    clickableChildren: [],
                    allButtons: [],
                    recommendations: []
                };
                
                // 找到所有包含"结算"的容器元素
                var allElements = document.querySelectorAll('*');
                var settlementContainers = [];
                
                for(var i = 0; i < allElements.length; i++) {
                    var el = allElements[i];
                    var text = el.textContent || el.innerText || '';
                    
                    if((text.includes('结算') || text.includes('checkout')) && text.length < 200) {
                        var rect = el.getBoundingClientRect();
                        if(rect.width > 50 && rect.height > 20) {
                            settlementContainers.push(el);
                            results.settlementContainers.push({
                                tag: el.tagName,
                                text: text.trim().substring(0, 100),
                                class: el.className,
                                id: el.id,
                                rect: {w: Math.round(rect.width), h: Math.round(rect.height)},
                                childrenCount: el.children.length
                            });
                        }
                    }
                }
                
                // 深度分析每个结算容器的子元素
                for(var c = 0; c < settlementContainers.length; c++) {
                    var container = settlementContainers[c];
                    var allChildren = container.querySelectorAll('*');
                    
                    for(var i = 0; i < allChildren.length; i++) {
                        var child = allChildren[i];
                        var rect = child.getBoundingClientRect();
                        var text = child.textContent || child.innerText || '';
                        
                        // 寻找可能的按钮子元素
                        var isPotentialButton = false;
                        var buttonScore = 0;
                        
                        // 评分系统
                        if(child.tagName === 'BUTTON') buttonScore += 50;
                        if(child.tagName === 'A') buttonScore += 40;
                        if(child.getAttribute('role') === 'button') buttonScore += 45;
                        if(child.style.cursor === 'pointer') buttonScore += 30;
                        if(child.onclick) buttonScore += 35;
                        if(text.includes('结算') && text.length < 20) buttonScore += 40;
                        if(text.includes('(') && text.includes(')')) buttonScore += 25; // 结算(1)
                        if(child.className.includes('btn')) buttonScore += 30;
                        if(child.className.includes('button')) buttonScore += 30;
                        if(rect.width > 60 && rect.width < 200 && rect.height > 25 && rect.height < 60) buttonScore += 20;
                        
                        if(buttonScore > 20 && rect.width > 0 && rect.height > 0) {
                            results.clickableChildren.push({
                                containerIndex: c,
                                tag: child.tagName,
                                text: text.trim(),
                                class: child.className,
                                id: child.id,
                                score: buttonScore,
                                rect: {w: Math.round(rect.width), h: Math.round(rect.height)},
                                hasClick: !!child.onclick,
                                cursor: child.style.cursor,
                                dataSpm: child.getAttribute('data-spm')
                            });
                        }
                    }
                }
                
                // 获取页面上所有真正的button元素（不限于结算区域）
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
                            visible: rect.width > 10 && rect.height > 10,
                            dataSpm: btn.getAttribute('data-spm'),
                            disabled: btn.disabled
                        });
                    }
                }
                
                // 生成点击建议
                var clickableChildren = results.clickableChildren;
                clickableChildren.sort((a, b) => b.score - a.score);
                
                for(var i = 0; i < Math.min(3, clickableChildren.length); i++) {
                    var child = clickableChildren[i];
                    var selector = '';
                    
                    if(child.id) {
                        selector = '#' + child.id;
                    } else if(child.dataSpm) {
                        selector = '[data-spm="' + child.dataSpm + '"]';
                    } else if(child.class) {
                        var firstClass = child.class.split(' ').filter(c => c.length > 3)[0];
                        if(firstClass) selector = '.' + firstClass;
                    }
                    
                    if(selector) {
                        results.recommendations.push({
                            rank: i + 1,
                            selector: selector,
                            text: child.text,
                            score: child.score,
                            method: 'CSS_SELECTOR'
                        });
                    }
                }
                
                // 特殊策略：寻找包含数字的结算文本（如"结算(1)"）
                var settlementWithNumber = document.querySelectorAll('*');
                for(var i = 0; i < settlementWithNumber.length; i++) {
                    var el = settlementWithNumber[i];
                    var text = el.textContent || el.innerText || '';
                    
                    if(/结算\\s*\\(\\d+\\)/.test(text) && text.length < 50) {
                        var rect = el.getBoundingClientRect();
                        if(rect.width > 40 && rect.height > 20) {
                            results.recommendations.push({
                                rank: 0, // 最高优先级
                                selector: 'XPATH_TEXT_MATCH',
                                text: text.trim(),
                                score: 100,
                                method: 'XPATH',
                                xpath: '//*[contains(text(), "结算") and contains(text(), "(' + text.match(/\\((\\d+)\\)/)[1] + ')")]'
                            });
                        }
                    }
                }
                
                console.log('深度分析完成:', results);
                return results;
            }
            
            return deepAnalyzeSettlement();
        """
    
    @staticmethod
    def get_powerful_click_script():
        """强力点击脚本 - 处理各种复杂情况"""
        return """
            function powerfulClick(targetText) {
                console.log('开始强力点击搜索:', targetText);
                
                var results = {
                    success: false,
                    clicked: '',
                    method: '',
                    attempts: []
                };
                
                // 搜索包含目标文本的所有元素
                var allElements = document.querySelectorAll('*');
                var candidates = [];
                
                for(var i = 0; i < allElements.length; i++) {
                    var el = allElements[i];
                    var text = el.textContent || el.innerText || '';
                    
                    if(text.includes(targetText) && text.length < 200) {
                        var rect = el.getBoundingClientRect();
                        if(rect.width > 20 && rect.height > 15) {
                            candidates.push({
                                element: el,
                                text: text.trim(),
                                rect: rect,
                                score: 0
                            });
                        }
                    }
                }
                
                // 对候选元素评分
                for(var i = 0; i < candidates.length; i++) {
                    var candidate = candidates[i];
                    var el = candidate.element;
                    var score = 0;
                    
                    // 基础评分
                    if(el.tagName === 'BUTTON') score += 50;
                    if(el.tagName === 'A') score += 40;
                    if(el.getAttribute('role') === 'button') score += 45;
                    if(el.style.cursor === 'pointer') score += 30;
                    if(el.onclick) score += 35;
                    
                    // 文本匹配度评分
                    var text = candidate.text.toLowerCase();
                    if(text === targetText.toLowerCase()) score += 40;
                    if(text.includes('(' + targetText + ')')) score += 35;
                    if(text.startsWith(targetText)) score += 30;
                    
                    // 尺寸合理性评分
                    var rect = candidate.rect;
                    if(rect.width > 60 && rect.width < 300 && rect.height > 25 && rect.height < 80) score += 25;
                    
                    // 类名评分
                    if(el.className.includes('btn') || el.className.includes('button')) score += 20;
                    if(el.className.includes('clickable')) score += 15;
                    
                    candidate.score = score;
                }
                
                // 按得分排序
                candidates.sort((a, b) => b.score - a.score);
                
                // 尝试点击高分候选元素
                for(var i = 0; i < Math.min(5, candidates.length); i++) {
                    var candidate = candidates[i];
                    var el = candidate.element;
                    
                    results.attempts.push({
                        text: candidate.text,
                        score: candidate.score,
                        tag: el.tagName
                    });
                    
                    // 尝试多种点击方法
                    var clickMethods = [
                        // 方法1：普通点击
                        function() {
                            el.click();
                            return '普通click()';
                        },
                        
                        // 方法2：JavaScript点击
                        function() {
                            var event = document.createEvent('MouseEvents');
                            event.initEvent('click', true, true);
                            el.dispatchEvent(event);
                            return 'dispatchEvent(click)';
                        },
                        
                        // 方法3：鼠标事件模拟
                        function() {
                            var rect = el.getBoundingClientRect();
                            var x = rect.left + rect.width / 2;
                            var y = rect.top + rect.height / 2;
                            
                            ['mousedown', 'mouseup', 'click'].forEach(function(eventType) {
                                var event = new MouseEvent(eventType, {
                                    bubbles: true,
                                    cancelable: true,
                                    clientX: x,
                                    clientY: y,
                                    button: 0
                                });
                                el.dispatchEvent(event);
                            });
                            return 'MouseEvent模拟';
                        },
                        
                        // 方法4：React事件模拟
                        function() {
                            var event = new Event('click', { bubbles: true });
                            Object.defineProperty(event, 'target', {value: el, enumerable: true});
                            Object.defineProperty(event, 'currentTarget', {value: el, enumerable: true});
                            el.dispatchEvent(event);
                            return 'React事件模拟';
                        },
                        
                        // 方法5：强制触发所有事件监听器
                        function() {
                            // 触发父元素的点击事件
                            var parent = el.parentElement;
                            while(parent && parent !== document.body) {
                                try {
                                    parent.click();
                                    return '父元素点击';
                                } catch(e) {
                                    parent = parent.parentElement;
                                }
                            }
                            return '父元素点击失败';
                        }
                    ];
                    
                    for(var m = 0; m < clickMethods.length; m++) {
                        try {
                            var method = clickMethods[m]();
                            console.log('尝试方法:', method, '元素:', candidate.text);
                            
                            // 简单检查是否有效果（这里无法检查页面跳转，留给外部检查）
                            results.success = true;
                            results.clicked = candidate.text;
                            results.method = method;
                            return results;
                            
                        } catch(e) {
                            console.log('点击方法失败:', method, e.message);
                            continue;
                        }
                    }
                }
                
                results.success = false;
                return results;
            }
            
            // 寻找包含"结算"和数字的文本
            var settlementTexts = ['结算(1)', '结算(2)', '结算(3)', '结算', '去结算'];
            for(var i = 0; i < settlementTexts.length; i++) {
                var result = powerfulClick(settlementTexts[i]);
                if(result.success) {
                    return result;
                }
            }
            
            return {success: false, reason: '未找到任何可点击的结算相关元素'};
        """ 