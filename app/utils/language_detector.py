"""
语言检测工具
"""

def detect_language(text: str) -> str:
    """
    检测文本的语言类型
    
    Args:
        text: 输入文本
    
    Returns:
        语言类型: '中文', '日文', '英文'
    """
    chinese_count = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    japanese_count = sum(1 for char in text if '\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff')
    
    total_chars = len(text)
    if total_chars == 0:
        return '未知'
    
    chinese_ratio = chinese_count / total_chars
    japanese_ratio = japanese_count / total_chars
    
    if chinese_ratio > 0.3:
        return '中文'
    elif japanese_ratio > 0.3:
        return '日文'
    else:
        return '英文'


def is_single_word(text: str) -> bool:
    """
    判断是否为单个词汇
    
    Args:
        text: 输入文本
    
    Returns:
        True: 单个词汇, False: 句子或短语
    """
    text = text.strip()
    
    # 规则1: 非常短（1-20个字符）
    if len(text) > 20:
        return False
    
    # 规则2: 不包含句子标点
    sentence_punctuation = '。！？.!?;；、，,\n'
    if any(p in text for p in sentence_punctuation):
        return False
    
    # 规则3: 英文单词（不包含空格）
    if detect_language(text) == '英文' and ' ' not in text.strip():
        return True
    
    # 规则4: 日文单词（1-10个字符，没有句子结构）
    if detect_language(text) == '日文' and len(text) <= 10:
        return True
    
    # 规则5: 中文词汇（1-6个字符）
    if detect_language(text) == '中文' and 1 <= len(text) <= 6:
        return True
    
    return False