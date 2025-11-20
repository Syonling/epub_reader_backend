"""
日语单词分析器 - 生产版（无调试信息）
支持词典查询、动词变形分析、自动还原变形词
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
            return None
    
    def _import_sudachi(self):
        """导入 sudachi 形态分析库"""
        try:
            tokenizer_obj = dictionary.Dictionary().create()
            return tokenizer_obj
        except ImportError:
            print("⚠️ sudachipy 未安装，形态分析功能将受限")
            return None
    
    def _katakana_to_hiragana(self, text: str) -> str:
        """将片假名转换为平假名"""
        result = []
        for char in text:
            code = ord(char)
            if 0x30A0 <= code <= 0x30FF:
                result.append(chr(code - 0x60))
            else:
                result.append(char)
        return ''.join(result)

    def _generate_reading_for_kanji_only(self, surface: str, dictionary_form: str, dictionary_reading: str) -> str:
        """
        为整个单词生成完整读音（汉字用词典读音，假名直接从surface取）
        
        算法：
        1. 找到 dictionary_form 中第一个假名的位置
        2. 提取该位置之前的读音（词干读音）
        3. 组合：词干读音 + surface中词干后的所有假名
        
        示例：
        - 驚かされた: おどろ(词干) + かされた(surface后缀) = おどろかされた
        - 頼まれた: たの(词干) + まれた(surface后缀) = たのまれた
        """
        # 如果相同，直接返回
        if surface == dictionary_form:
            return dictionary_reading
        
        # 找到 dictionary_form 中第一个假名的位置
        first_hira_idx = -1
        for i, char in enumerate(dictionary_form):
            if '\u3040' <= char <= '\u309f':  # 平假名
                first_hira_idx = i
                break
        
        if first_hira_idx == -1:
            # 没有假名，全是汉字（如：読）
            # 找 surface 中第一个假名的位置
            first_hira_in_surface = -1
            for i, char in enumerate(surface):
                if '\u3040' <= char <= '\u309f':
                    first_hira_in_surface = i
                    break
            
            if first_hira_in_surface == -1:
                # surface 也全是汉字
                return dictionary_reading
            else:
                # surface 中汉字后有假名（如：読んだ）
                return dictionary_reading + surface[first_hira_in_surface:]
        
        # dictionary_form 中有假名（大部分情况）
        # 找到该假名在 dictionary_reading 中的位置
        first_hira_char = dictionary_form[first_hira_idx]
        stem_reading_end = -1
        
        for i, char in enumerate(dictionary_reading):
            if char == first_hira_char:
                stem_reading_end = i
                break
        
        if stem_reading_end == -1:
            stem_reading_end = len(dictionary_reading)
        
        # 词干读音（汉字部分的读音）
        stem_reading = dictionary_reading[:stem_reading_end]
        
        # surface 中词干后的所有字符（包括假名变形）
        surface_suffix = surface[first_hira_idx:]
        
        # 组合
        return stem_reading + surface_suffix
        
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
        
        ⚠️ 注意：返回 Dict 对象，不是 JSON 字符串！
        """
        # 先尝试还原变形词到原型
        original_form = self._get_original_form(word)
        search_word = original_form if original_form else word
        
        # 使用 Sudachi 进行形态分析（分析原始输入）
        morphology = self._analyze_with_sudachi(word) if self.sudachi else None
        
        # 使用 Jamdict 查询词典（查询原型）
        dict_results = self._lookup_dict(search_word) if self.jamdict else None
        
        # 如果原型查不到，尝试查询原始输入
        if not dict_results and original_form:
            dict_results = self._lookup_dict(word) if self.jamdict else None
        
        # 构建统一格式的结果
        result = self._build_unified_result(word, morphology, dict_results)
        
        # 如果使用了原型查询，添加提示
        if original_form and original_form != word:
            result['special_notes'].insert(0, f"💡 已自动查询原型：{original_form}")
        
        # ✅ 返回 Dict 对象，不要转成 JSON 字符串！
        return result
    
    def _get_original_form(self, word: str) -> Optional[str]:
        """获取单词的原型（辞书形）"""
        if not self.sudachi:
            return None
        
        try:
            from sudachipy import tokenizer
            tokens = self.sudachi.tokenize(word, tokenizer.Tokenizer.SplitMode.C)
            
            if tokens:
                dictionary_form = tokens[0].dictionary_form()
                if dictionary_form != word:
                    return dictionary_form
            
            return None
        except Exception as e:
            return None
    
    def _analyze_with_sudachi(self, word: str) -> Optional[Dict]:
        """使用 Sudachi 进行形态分析"""
        try:
            from sudachipy import tokenizer
            
            tokens = self.sudachi.tokenize(word, tokenizer.Tokenizer.SplitMode.C)
            
            if not tokens:
                return None
            
            token = tokens[0]
            pos_tags = token.part_of_speech()
            
            # 获取原型读音（片假名）
            surface_reading = token.reading_form()
            # 转换为平假名
            surface_reading = self._katakana_to_hiragana(surface_reading)
            
            return {
                'surface': token.surface(),
                'dictionary_form': token.dictionary_form(),
                'reading': surface_reading,
                'normalized_form': token.normalized_form(),
                'pos': pos_tags,
                'pos_type': self._classify_pos(pos_tags),
                'verb_type': self._get_verb_type(pos_tags),
                'verb_form': self._get_verb_form(pos_tags),
            }
        except Exception as e:
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
    
    def _get_verb_type(self, pos_tags: List[str]) -> Optional[Dict]:
        """获取动词类型"""
        if len(pos_tags) < 2 or pos_tags[0] != '動詞':
            return None
        
        transitivity = pos_tags[1] if len(pos_tags) > 1 else ''
        conjugation = pos_tags[4] if len(pos_tags) > 4 else ''
        
        verb_info = {
            'transitivity': transitivity,
            'conjugation_type': conjugation
        }
        
        # 判断动词类型
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
        """获取动词形式"""
        if len(pos_tags) < 6 or pos_tags[0] != '動詞':
            return None
        
        return pos_tags[5] if len(pos_tags) > 5 else '終止形-一般'
    
    def _lookup_dict(self, word: str) -> Optional[List]:
        """查询 Jamdict 词典"""
        try:
            result = self.jamdict.lookup(word)
            entries = []
            
            for entry in result.entries:
                meanings = []
                
                for sense in entry.senses:
                    gloss_list = []
                    for gloss in sense.gloss:
                        gloss_list.append(str(gloss))
                    
                    meanings.append({
                        'pos': ', '.join([str(p) for p in sense.pos]),
                        'meanings': gloss_list
                    })
                
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
            return None
    
    def _build_unified_result(self, word: str, morphology: Optional[Dict], dict_results: Optional[List]) -> Dict:
        """构建统一格式的结果"""
        translation = self._build_translation(dict_results)
        vocabulary = self._build_vocabulary(word, morphology, dict_results)
        grammar_points = []
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
        
        first_entry = dict_results[0]
        if first_entry['meanings']:
            first_meanings = first_entry['meanings'][0]['meanings']
            return '、'.join(first_meanings[:3])
        
        return "（无释义）"
    
    def _build_vocabulary(self, word: str, morphology: Optional[Dict], dict_results: Optional[List]) -> List[Dict]:
        """构建词汇列表"""
        vocab_list = []
        
        main_vocab = {
            "word": word,
            "reading": "",
            "meaning": "",
            "level": "N2",
            "conjugation": {
                "has_conjugation": False
            }
        }
        
        # 从形态分析获取信息
        if morphology:
            surface = morphology.get('surface', '')
            dictionary_form = morphology.get('dictionary_form', '')
            dictionary_reading = morphology.get('reading', '')
            
            # ✅ 生成完整读音（汉字+假名）
            complete_reading = self._generate_reading_for_kanji_only(
                surface,
                dictionary_form, 
                dictionary_reading
            )
            main_vocab["reading"] = complete_reading
            
            # 检查是否是动词
            if morphology.get('pos_type') == 'verb':
                verb_type = morphology.get('verb_type')
                if verb_type and isinstance(verb_type, dict):
                    main_vocab["conjugation"] = self._build_verb_conjugation(morphology)
        
        # 从词典获取释义
        if dict_results:
            first_entry = dict_results[0]
            
            if not main_vocab["reading"] and first_entry['readings']:
                main_vocab["reading"] = first_entry['readings'][0]
            
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

        # ✅ 检测被动形和使役形（优先检测，因为 Sudachi 可能识别错误）
        if 'れる' in surface_form or 'られる' in surface_form:
            if surface_form.endswith('た'):
                current_form = '被动形-过去'
            elif surface_form.endswith('て'):
                current_form = '被动形-て形'
            else:
                current_form = '被动形'
        elif 'せる' in surface_form or 'させる' in surface_form:
            if surface_form.endswith('た'):
                current_form = '使役形-过去'
            elif surface_form.endswith('て'):
                current_form = '使役形-て形'
            else:
                current_form = '使役形'

        conjugation = {
            "has_conjugation": True,
            "original_form": f"{dictionary_form}（{verb_type_info.get('class', '动词')}）",
            "current_form": surface_form,
            "conjugation_type": self._translate_verb_form(current_form),
            "reason": self._explain_verb_form(current_form),
            "verb_class": verb_type_info.get('class', ''),
            "transitivity": self._translate_transitivity(verb_type_info.get('transitivity', ''))
        }

        # ✅ 生成所有活用形
        try:
            from app.services.verb_conjugator import get_verb_conjugator
            conjugator = get_verb_conjugator()
            all_forms = conjugator.conjugate(dictionary_form, verb_type_info.get('class', ''))
            conjugation['all_forms'] = all_forms
        except Exception as e:
            pass
        
        return conjugation
    
    def _translate_verb_form(self, form: str) -> str:
        """翻译动词形式名称"""
        form_map = {
            '終止形-一般': '原型（辞书形）',
            '連用形-一般': '连用形',
            '連用形-促音便': 'た形（过去形）',
            '仮定形-一般': '假定形（ば形）',
            '命令形': '命令形',
            '未然形-一般': '未然形',
            '連体形-一般': '连体形',
            '被动形': '被动形（受身形）',
            '被动形-过去': '被动形的过去式',
            '被动形-て形': '被动形的て形',
            '使役形': '使役形',
            '使役形-过去': '使役形的过去式',
            '使役形-て形': '使役形的て形',
        }
        return form_map.get(form, form)
    
    def _explain_verb_form(self, form: str) -> str:
        """解释动词形式的用法"""
        explanations = {
            '終止形-一般': '原型，用于结句或作为辞书形',
            '連用形-一般': '用于连接其他动词或助词',
            '連用形-促音便': '过去形（た形），表示动作已完成',
            '仮定形-一般': '假定形，用于表达假设条件',
            '命令形': '命令形，用于表达命令或指示',
            '未然形-一般': '未然形，用于接续否定助词ない等',
            '連体形-一般': '连体形，用于修饰名词',
            '被动形': '被动形，表示被动语态',
            '被动形-过去': '被动形的过去式（如：驚かされた）',
            '被动形-て形': '被动形的て形（如：驚かされて）',
            '使役形': '使役形，表示让/使某人做某事',
            '使役形-过去': '使役形的过去式',
            '使役形-て形': '使役形的て形',
        }
        return explanations.get(form, '具体用法请参考语法书')
    
    def _translate_transitivity(self, transitivity: str) -> str:
        """翻译自他动词"""
        if '自立' in transitivity:
            return '自动词'
        elif transitivity == '':
            return ''
        return transitivity
    
    def _build_special_notes(self, morphology: Optional[Dict], dict_results: Optional[List]) -> List[str]:
        """构建特殊说明"""
        notes = []
        
        if not dict_results:
            notes.append("⚠️ 词典中未找到该词")
            notes.append("💡 可能是：1) 变形词 2) 专有名词 3) 较新的词汇")
        
        return notes


# 全局单例
_parser_instance = None

def get_japanese_parser():
    """获取日语解析器单例"""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = JapaneseWordParser()
    return _parser_instance