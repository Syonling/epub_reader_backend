"""
单词解析服务
使用内置的字典和规则解析单个词汇
"""
from typing import Dict
from app.utils.language_detector import detect_language


class WordParser:
    """单词解析器 - 用于解析单个词汇"""
    
    def __init__(self):
        # 这里可以加载词典数据
        # 例如：self.dictionary = load_dictionary()
        pass
    
    def parse(self, word: str) -> Dict:
        """
        解析单个词汇
        
        Args:
            word: 单个词汇
        
        Returns:
            解析结果字典
        """
        language = detect_language(word)
        
        if language == '日文':
            return self._parse_japanese(word)
        elif language == '中文':
            return self._parse_chinese(word)
        elif language == '英文':
            return self._parse_english(word)
        else:
            return self._parse_unknown(word)
    
    def _parse_japanese(self, word: str) -> Dict:
        """
        解析日文单词
        
        TODO: 未来可以集成：
        - MeCab 日语分词
        - JMdict 词典
        - 假名标注
        """
        return {
            'word': word,
            'language': '日文',
            'type': 'japanese_word',
            'readings': self._get_japanese_readings(word),
            'meanings': self._get_japanese_meanings(word),
            'kanji_info': self._get_kanji_info(word),
            'example_sentences': [],
            'note': '💡 提示: 集成 MeCab 可获得更详细的解析'
        }
    
    def _parse_chinese(self, word: str) -> Dict:
        """
        解析中文词汇
        
        TODO: 未来可以集成：
        - jieba 分词
        - CC-CEDICT 词典
        - 拼音标注
        """
        return {
            'word': word,
            'language': '中文',
            'type': 'chinese_word',
            'pinyin': self._get_pinyin(word),
            'meanings': self._get_chinese_meanings(word),
            'components': self._get_character_components(word),
            'example_sentences': [],
            'note': '💡 提示: 集成 jieba 可获得更详细的解析'
        }
    
    def _parse_english(self, word: str) -> Dict:
        """
        解析英文单词
        
        TODO: 未来可以集成：
        - NLTK
        - WordNet
        - 词形变化
        """
        return {
            'word': word,
            'language': '英文',
            'type': 'english_word',
            'phonetic': self._get_phonetic(word),
            'meanings': self._get_english_meanings(word),
            'word_forms': self._get_word_forms(word),
            'example_sentences': [],
            'note': '💡 提示: 集成 NLTK 可获得更详细的解析'
        }
    
    def _parse_unknown(self, word: str) -> Dict:
        """解析未知语言"""
        return {
            'word': word,
            'language': '未知',
            'type': 'unknown',
            'note': '无法识别语言类型'
        }
    
    # ========================================
    # 辅助方法 - 目前返回模拟数据
    # 未来可以替换为真实的词典查询
    # ========================================
    
    def _get_japanese_readings(self, word: str) -> list:
        """获取日文读音（假名）"""
        # TODO: 使用 MeCab 或其他工具获取真实读音
        return [
            {'type': '训读', 'reading': '[待实现]'},
            {'type': '音读', 'reading': '[待实现]'}
        ]
    
    def _get_japanese_meanings(self, word: str) -> list:
        """获取日文词义"""
        # TODO: 查询 JMdict 词典
        return [
            {'definition': '词义1（待实现真实词典查询）', 'pos': '名词'},
            {'definition': '词义2', 'pos': '动词'}
        ]
    
    def _get_kanji_info(self, word: str) -> list:
        """获取汉字信息"""
        # TODO: 解析汉字的部首、笔画等
        kanji_chars = [c for c in word if '\u4e00' <= c <= '\u9fff']
        return [
            {
                'character': char,
                'stroke_count': '[待实现]',
                'radical': '[待实现]'
            }
            for char in kanji_chars
        ]
    
    def _get_pinyin(self, word: str) -> str:
        """获取拼音"""
        # TODO: 使用 pypinyin 库
        return '[待实现拼音标注]'
    
    def _get_chinese_meanings(self, word: str) -> list:
        """获取中文词义"""
        # TODO: 查询 CC-CEDICT 词典
        return [
            {'definition': '词义1（待实现真实词典查询）'},
            {'definition': '词义2'}
        ]
    
    def _get_character_components(self, word: str) -> list:
        """获取汉字部件"""
        # TODO: 解析汉字结构
        return [
            {
                'character': char,
                'radical': '[待实现]',
                'components': []
            }
            for char in word
        ]
    
    def _get_phonetic(self, word: str) -> str:
        """获取英文音标"""
        # TODO: 使用词典或 API
        return '[待实现音标]'
    
    def _get_english_meanings(self, word: str) -> list:
        """获取英文词义"""
        # TODO: 查询 WordNet 或其他词典
        return [
            {
                'definition': '词义1（待实现真实词典查询）',
                'pos': 'noun',
                'example': 'Example sentence...'
            }
        ]
    
    def _get_word_forms(self, word: str) -> Dict:
        """获取词形变化"""
        # TODO: 使用 NLTK
        return {
            'plural': '[待实现]',
            'past_tense': '[待实现]',
            'present_participle': '[待实现]'
        }


# 单例模式
_word_parser_instance = None

def get_word_parser() -> WordParser:
    """获取单词解析器实例"""
    global _word_parser_instance
    if _word_parser_instance is None:
        _word_parser_instance = WordParser()
    return _word_parser_instance