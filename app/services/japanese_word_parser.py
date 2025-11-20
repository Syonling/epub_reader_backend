"""
日语单词分析器 - 完整版
支持词典查询、动词变形分析
"""
import json
from typing import Dict, List, Optional
from sudachipy import tokenizer, dictionary



class JapaneseWordParser:
    """日语单词解析器"""
    
    def __init__(self):
        # 尝试导入依赖库
        self.jamdict = self._import_jamdict()
        self.sudachi = self._import_sudachi()
    
    def _import_jamdict(self):
        """导入 jamdict 词典库"""
        try:
            from jamdict import Jamdict
            return Jamdict()
        except ImportError:
            print("⚠️ jamdict 未安装，词典功能将受限")
            print("   安装: poetry add jamdict")
            return None
    
    def _import_sudachi(self):
        """导入 sudachi 形态分析库"""
        try:
            tokenizer_obj = dictionary.Dictionary().create()
            return tokenizer_obj
        except ImportError:
            print("⚠️ sudachipy 未安装，形态分析功能将受限")
            print("   安装: poetry add sudachipy sudachidict_core")
            return None
    
    def parse(self, word: str) -> Dict:
        """
        解析日语单词（返回统一格式）
        
        返回格式与 AI 分析一致：
        {
            "translation": "翻译",
            "grammar_points": [],
            "vocabulary": [],
            "special_notes": []
        }
        """
        # 使用 Sudachi 进行形态分析
        morphology = self._analyze_with_sudachi(word) if self.sudachi else None
        
        # 使用 Jamdict 查询词典
        dict_results = self._lookup_dict(word) if self.jamdict else None
        
        # 构建统一格式的结果
        result = self._build_unified_result(word, morphology, dict_results)
        
        return json.dumps(result, ensure_ascii=False)
    
    def _analyze_with_sudachi(self, word: str) -> Optional[Dict]:
        """使用 Sudachi 进行形态分析"""
        try:
            from sudachipy import tokenizer
            
            tokens = self.sudachi.tokenize(word, tokenizer.Tokenizer.SplitMode.C)
            
            if not tokens:
                return None
            
            token = tokens[0]  # 取第一个token
            
            # 获取词性
            pos_tags = token.part_of_speech()
            
            return {
                'surface': token.surface(),           # 表层形式
                'dictionary_form': token.dictionary_form(),  # 辞书形
                'reading': token.reading_form(),      # 读音
                'normalized_form': token.normalized_form(),  # 正规化形式
                'pos': pos_tags,                      # 词性标签
                'pos_type': self._classify_pos(pos_tags),  # 词性分类
                'verb_type': self._get_verb_type(pos_tags),  # 动词类型
                'verb_form': self._get_verb_form(pos_tags),  # 动词形式
            }
        except Exception as e:
            print(f"Sudachi 分析失败: {e}")
            return None
    
    def _classify_pos(self, pos_tags: List[str]) -> str:
        """分类词性"""
        if not pos_tags:
            return 'unknown'
        
        main_pos = pos_tags[0]
        
        if main_pos == '動詞':
            return 'verb'
        elif main_pos == '形容詞':
            return 'i_adjective'
        elif main_pos == '形状詞':
            return 'na_adjective'
        elif main_pos == '名詞':
            return 'noun'
        elif main_pos == '副詞':
            return 'adverb'
        else:
            return main_pos
    
    def _get_verb_type(self, pos_tags: List[str]) -> Optional[str]:
        """获取动词类型"""
        if len(pos_tags) < 2 or pos_tags[0] != '動詞':
            return None
        
        # 自他动词
        transitivity = pos_tags[1] if len(pos_tags) > 1 else ''
        
        # 活用类型
        conjugation = pos_tags[4] if len(pos_tags) > 4 else ''
        
        verb_info = {
            'transitivity': transitivity,  # 自立, 非自立 等
            'conjugation_type': conjugation  # 五段-ラ行, 一段-上, サ行変格 等
        }
        
        # 判断五段/一段/カ变/サ变
        if '五段' in conjugation:
            verb_info['class'] = '五段动词（一类动词）'
        elif '一段' in conjugation:
            verb_info['class'] = '一段动词（二类动词）'
        elif 'サ行変格' in conjugation:
            verb_info['class'] = 'サ变动词'
        elif 'カ行変格' in conjugation:
            verb_info['class'] = 'カ变动词'
        else:
            verb_info['class'] = conjugation
        
        return verb_info
    
    def _get_verb_form(self, pos_tags: List[str]) -> Optional[str]:
        """获取动词形式（原型、て形、た形等）"""
        if len(pos_tags) < 6 or pos_tags[0] != '動詞':
            return None
        
        return pos_tags[5] if len(pos_tags) > 5 else '終止形-一般'
    
    def _lookup_dict(self, word: str) -> Optional[List]:
        """查询 Jamdict 词典"""
        try:
            result = self.jamdict.lookup(word)
            
            entries = []
            
            # 查询词条
            for entry in result.entries:
                meanings = []
                
                # 提取中文释义
                for sense in entry.senses:
                    # Jamdict 包含多语言，需要过滤中文
                    gloss_list = []
                    for gloss in sense.gloss:
                        # 默认是英文，我们先用英文
                        gloss_list.append(str(gloss))
                    
                    meanings.append({
                        'pos': ', '.join([str(p) for p in sense.pos]),
                        'meanings': gloss_list
                    })
                
                # 获取读音
                readings = []
                for kana in entry.kana_forms:
                    readings.append(str(kana))
                
                entries.append({
                    'kanji': str(entry.kanji_forms[0]) if entry.kanji_forms else word,
                    'readings': readings,
                    'meanings': meanings
                })
            
            return entries if entries else None
            
        except Exception as e:
            print(f"词典查询失败: {e}")
            return None
    
    def _build_unified_result(self, word: str, morphology: Optional[Dict], dict_results: Optional[List]) -> Dict:
        """构建统一格式的结果"""
        
        # 基础信息
        translation = self._build_translation(dict_results)
        vocabulary = self._build_vocabulary(word, morphology, dict_results)
        grammar_points = self._build_grammar_points(morphology)
        special_notes = self._build_special_notes(morphology, dict_results)
        
        return {
            "translation": translation,
            "grammar_points": grammar_points,
            "vocabulary": vocabulary,
            "special_notes": special_notes
        }
    
    def _build_translation(self, dict_results: Optional[List]) -> str:
        """构建翻译"""
        if not dict_results:
            return "（词典中未找到该词）"
        
        # 取第一个词条的第一个释义
        first_entry = dict_results[0]
        if first_entry['meanings']:
            first_meanings = first_entry['meanings'][0]['meanings']
            return '、'.join(first_meanings[:3])  # 最多3个释义
        
        return "（无释义）"
    
    def _build_vocabulary(self, word: str, morphology: Optional[Dict], dict_results: Optional[List]) -> List[Dict]:
        """构建词汇列表"""
        vocab_list = []
        
        # 主词条
        main_vocab = {
            "word": word,
            "reading": "",
            "meaning": "",
            "level": "N2",  # 默认N2，实际可以根据词频判断
            "conjugation": {
                "has_conjugation": False
            }
        }
        
        # 从形态分析获取读音和词性
        if morphology:
            main_vocab["reading"] = morphology.get('reading', '')
            
            # 如果是动词，添加活用信息
            if morphology['pos_type'] == 'verb':
                main_vocab["conjugation"] = self._build_verb_conjugation(morphology)
        
        # 从词典获取释义
        if dict_results:
            first_entry = dict_results[0]
            
            # 读音（如果形态分析没有）
            if not main_vocab["reading"] and first_entry['readings']:
                main_vocab["reading"] = first_entry['readings'][0]
            
            # 释义
            if first_entry['meanings']:
                meanings_list = first_entry['meanings'][0]['meanings']
                main_vocab["meaning"] = '；'.join(meanings_list[:2])
        
        vocab_list.append(main_vocab)
        
        return vocab_list
    
    def _build_verb_conjugation(self, morphology: Dict) -> Dict:
        """构建动词活用信息"""
        verb_type_info = morphology.get('verb_type', {})
        
        if not verb_type_info or not isinstance(verb_type_info, dict):
            return {"has_conjugation": False}
        
        dictionary_form = morphology.get('dictionary_form', '')
        surface_form = morphology.get('surface', '')
        current_form = morphology.get('verb_form', '終止形-一般')
        
        conjugation = {
            "has_conjugation": True,
            "original_form": f"{dictionary_form}（{verb_type_info.get('class', '动词')}）",
            "current_form": surface_form,
            "conjugation_type": self._translate_verb_form(current_form),
            "reason": self._explain_verb_form(current_form),
            "verb_class": verb_type_info.get('class', ''),
            "transitivity": self._translate_transitivity(verb_type_info.get('transitivity', ''))
        }
        
        return conjugation
    
    def _translate_verb_form(self, form: str) -> str:
        """翻译动词形式名称"""
        form_map = {
            '終止形-一般': '原型（辞书形）',
            '連用形-一般': '连用形',
            '連用形-促音便': 'て形/た形',
            '仮定形-一般': '假定形（ば形）',
            '命令形': '命令形',
            '未然形-一般': '未然形',
            '連体形-一般': '连体形',
        }
        return form_map.get(form, form)
    
    def _explain_verb_form(self, form: str) -> str:
        """解释动词形式的用法"""
        explanations = {
            '終止形-一般': '原型，用于结句或作为辞书形',
            '連用形-一般': '用于连接其他动词或助词',
            '連用形-促音便': '用于构成て形或た形，表示动作的连接或完成',
            '仮定形-一般': '假定形，用于表达假设条件',
            '命令形': '命令形，用于表达命令或指示',
            '未然形-一般': '未然形，用于接续否定助词ない等',
            '連体形-一般': '连体形，用于修饰名词',
        }
        return explanations.get(form, '具体用法请参考语法书')
    
    def _translate_transitivity(self, transitivity: str) -> str:
        """翻译自他动词"""
        if '自立' in transitivity:
            return '自动词'
        elif transitivity == '':
            return ''
        return transitivity
    
    def _build_grammar_points(self, morphology: Optional[Dict]) -> List[Dict]:
        """构建语法点（如果是动词，显示常见变形）"""
        grammar_points = []
        
        if not morphology or morphology['pos_type'] != 'verb':
            return grammar_points
        
        verb_type_info = morphology.get('verb_type', {})
        dictionary_form = morphology.get('dictionary_form', '')
        
        if not dictionary_form:
            return grammar_points
        
        # 生成常见变形示例
        conjugations = self._generate_verb_conjugations(dictionary_form, verb_type_info)
        
        if conjugations:
            grammar_points.append({
                "pattern": "动词活用形式",
                "explanation": f"这是一个{verb_type_info.get('class', '动词')}，以下是常见的活用形式",
                "example_in_sentence": "",
                "level": "N2",
                "is_special": False
            })
        
        return grammar_points
    
    def _generate_verb_conjugations(self, verb: str, verb_type_info: Dict) -> Dict:
        """生成动词各种变形（简化版）"""
        # TODO: 实现完整的动词活用规则
        # 这里提供一个框架，实际需要根据动词类型生成正确的变形
        
        conjugations = {
            'dictionary_form': verb,
            'masu_form': '（需要完整实现）',
            'te_form': '（需要完整实现）',
            'ta_form': '（需要完整实现）',
            'nai_form': '（需要完整实现）',
            'passive_form': '（需要完整实现）',
            'causative_form': '（需要完整实现）',
            'potential_form': '（需要完整实现）',
            'volitional_form': '（需要完整实现）',
        }
        
        return conjugations
    
    def _build_special_notes(self, morphology: Optional[Dict], dict_results: Optional[List]) -> List[str]:
        """构建特殊说明"""
        notes = []
        
        # 词典状态说明
        if not self.jamdict:
            notes.append("⚠️ 未安装 jamdict 词典库，释义功能受限")
            notes.append("💡 安装: poetry add jamdict")
        
        if not self.sudachi:
            notes.append("⚠️ 未安装 sudachipy 形态分析库，分析功能受限")
            notes.append("💡 安装: poetry add sudachipy sudachidict_core")
        
        # 如果没有找到词条
        if not dict_results:
            notes.append("📝 词典中未找到该词，可能是：1) 生僻词 2) 变形后的形式 3) 非标准写法")
        
        # 动词类型说明
        if morphology and morphology['pos_type'] == 'verb':
            verb_type_info = morphology.get('verb_type', {})
            if isinstance(verb_type_info, dict):
                verb_class = verb_type_info.get('class', '')
                if verb_class:
                    notes.append(f"📚 这是一个{verb_class}")
        
        return notes


# 全局单例
_parser_instance = None


def get_japanese_parser():
    """获取日语解析器单例"""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = JapaneseWordParser()
    return _parser_instance


# ============= 简化版（备用方案）=============
# 如果 sudachipy 安装失败，可以只使用这个简化版

class JapaneseWordParserSimple:
    """日语单词解析器（简化版 - 只用 Jamdict）"""
    
    def __init__(self):
        self.jamdict = self._import_jamdict()
    
    def _import_jamdict(self):
        """导入 jamdict 词典库"""
        try:
            from jamdict import Jamdict
            return Jamdict()
        except ImportError:
            print("⚠️ jamdict 未安装")
            return None
    
    def parse(self, word: str) -> str:
        """解析日语单词（返回统一格式JSON）"""
        dict_results = self._lookup_dict(word) if self.jamdict else None
        result = self._build_result(word, dict_results)
        return json.dumps(result, ensure_ascii=False)
    
    def _lookup_dict(self, word: str):
        """查询词典（同上）"""
        try:
            result = self.jamdict.lookup(word)
            entries = []
            
            for entry in result.entries:
                meanings = []
                for sense in entry.senses:
                    gloss_list = [str(gloss) for gloss in sense.gloss]
                    pos_list = [str(p) for p in sense.pos]
                    meanings.append({
                        'pos': ', '.join(pos_list),
                        'meanings': gloss_list
                    })
                
                readings = [str(kana) for kana in entry.kana_forms]
                kanji = str(entry.kanji_forms[0]) if entry.kanji_forms else word
                
                entries.append({
                    'kanji': kanji,
                    'readings': readings,
                    'meanings': meanings
                })
            
            return entries if entries else None
        except Exception as e:
            print(f"词典查询失败: {e}")
            return None
    
    def _build_result(self, word: str, dict_results):
        """构建结果"""
        translation = self._build_translation(dict_results)
        vocabulary = self._build_vocabulary(word, dict_results)
        special_notes = ["💡 当前使用简化版（仅词典查询，无形态分析）"]
        
        return {
            "translation": translation,
            "grammar_points": [],
            "vocabulary": vocabulary,
            "special_notes": special_notes
        }
    
    def _build_translation(self, dict_results):
        """构建翻译"""
        if not dict_results:
            return "（词典中未找到该词）"
        
        first_entry = dict_results[0]
        if first_entry['meanings']:
            first_meanings = first_entry['meanings'][0]['meanings']
            return '、'.join(first_meanings[:3])
        return "（无释义）"
    
    def _build_vocabulary(self, word: str, dict_results):
        """构建词汇"""
        vocab = {
            "word": word,
            "reading": "",
            "meaning": "",
            "level": "N2",
            "conjugation": {"has_conjugation": False}
        }
        
        if dict_results:
            first_entry = dict_results[0]
            if first_entry['readings']:
                vocab["reading"] = first_entry['readings'][0]
            if first_entry['meanings']:
                meanings_list = []
                for mg in first_entry['meanings'][:2]:
                    meanings_list.extend(mg['meanings'][:2])
                vocab["meaning"] = '；'.join(meanings_list[:3])
        
        return [vocab]


def get_japanese_parser_simple():
    """获取简化版解析器（备用）"""
    return JapaneseWordParserSimple()