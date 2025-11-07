# -*- coding: utf-8 -*-"""
修复策略生成模块
"""

from typing import List, Dict, Any, Tuple

class RepairStrategyGenerator:
    """
    修复策略生成类
    """
    
    def __init__(self, knowledge_base=None):
        self.kb = knowledge_base
        self.confidence_threshold = 0.7
    
    def generate_repair_candidates(self, error: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        生成修复候选值
        :param error: 错误信息
        :return: 修复候选列表
        """
        candidates = []
        error_type = error.get('error_type', '')
        field = error.get('field', '')
        value = error.get('value', '')
        
        if error_type == 'semantic_mismatch':
            candidates.extend(self._fix_semantic_mismatch(field, value))
        elif error_type == 'type_mismatch':
            candidates.extend(self._fix_type_mismatch(field, value))
        elif error_type == 'invalid_format':
            candidates.extend(self._fix_invalid_format(field, value))
        elif error_type == 'logical_conflict':
            candidates.extend(self._fix_logical_conflict(error))
        
        return candidates
    
    def _fix_semantic_mismatch(self, field: str, value: str) -> List[Dict[str, Any]]:
        """
        修复语义不匹配
        :param field: 字段名
        :param value: 字段值
        :return: 修复候选列表
        """
        candidates = []
        
        if not self.kb:
            return candidates
        
        rules = self.kb.get_field_rules(field)
        enum_values = rules.get('enum', [])
        
        if not enum_values:
            return candidates
        
        # 性别字段特殊处理
        if '性别' in field or 'gender' in field.lower():
            gender_map = {
                '男': ['male', '1', 'M'],
                '女': ['female', '0', 'F']
            }
            
            for standard_val, variants in gender_map.items():
                if value in variants:
                    candidates.append({
                        'repair_value': standard_val,
                        'confidence': 0.95,
                        'method': 'gender_normalization'
                    })
        
        # 布尔值字段处理
        if 'bool' in field.lower() or 'boolean' in field.lower():
            bool_map = {
                '是': ['yes', '1', 'true', 'True'],
                '否': ['no', '0', 'false', 'False']
            }
            
            for standard_val, variants in bool_map.items():
                if value in variants:
                    candidates.append({
                        'repair_value': standard_val,
                        'confidence': 0.95,
                        'method': 'boolean_normalization'
                    })
        
        return candidates
    
    def _fix_type_mismatch(self, field: str, value: str) -> List[Dict[str, Any]]:
        """
        修复类型不匹配
        :param field: 字段名
        :param value: 字段值
        :return: 修复候选列表
        """
        candidates = []
        field_lower = field.lower()
        
        # 数字类型修复
        if '数字' in field_lower or 'number' in field_lower or 'age' in field_lower or 'price' in field_lower:
            # 提取数字部分
            import re
            digits = re.findall(r'\d+', value)
            if digits:
                candidates.append({
                    'repair_value': digits[0],
                    'confidence': 0.8,
                    'method': 'digit_extraction'
                })
        
        # 日期类型修复
        if '日期' in field_lower or 'date' in field_lower:
            # 简单的日期格式转换
            import re
            date_patterns = [
                (r'^(\d{4})(\d{2})(\d{2})$', r'\1-\2-\3'),  # 8位数字转YYYY-MM-DD
                (r'^(\d{2})/(\d{2})/(\d{4})$', r'\3-\1-\2'),  # MM/DD/YYYY转YYYY-MM-DD
                (r'^(\d{2})-(\d{2})-(\d{4})$', r'\3-\1-\2')   # MM-DD-YYYY转YYYY-MM-DD
            ]
            
            for pattern, replacement in date_patterns:
                match = re.match(pattern, value)
                if match:
                    repaired_date = re.sub(pattern, replacement, value)
                    candidates.append({
                        'repair_value': repaired_date,
                        'confidence': 0.85,
                        'method': 'date_format_conversion'
                    })
        
        return candidates
    
    def _fix_invalid_format(self, field: str, value: str) -> List[Dict[str, Any]]:
        """
        修复格式无效
        :param field: 字段名
        :param value: 字段值
        :return: 修复候选列表
        """
        candidates = []
        
        if '邮箱' in field.lower() or 'email' in field.lower():
            # 简单的邮箱修复
            if '@' not in value:
                # 尝试添加常见域名
                candidates.append({
                    'repair_value': f'{value}@example.com',
                    'confidence': 0.5,
                    'method': 'email_domain_guess'
                })
        
        return candidates
    
    def _fix_logical_conflict(self, error: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        修复逻辑冲突
        :param error: 错误信息
        :return: 修复候选列表
        """
        candidates = []
        # 简化实现：返回空列表，实际应根据具体逻辑冲突生成修复策略
        return candidates
    
    def generate_missing_field_value(self, field: str, row: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        生成缺失字段的填充值
        :param field: 缺失字段名
        :param row: 当前行数据
        :return: 修复候选列表
        """
        candidates = []
        
        if not self.kb:
            return candidates
        
        rules = self.kb.get_field_rules(field)
        if not rules:
            return candidates
        
        # 生成符合格式的填充值
        field_lower = field.lower()
        
        if 'id' in field_lower or '编号' in field_lower:
            # 生成唯一ID
            import uuid
            candidates.append({
                'repair_value': str(uuid.uuid4())[:10],
                'confidence': 0.9,
                'method': 'uuid_generation'
            })
        
        if '默认值' in rules:
            candidates.append({
                'repair_value': rules['默认值'],
                'confidence': 0.95,
                'method': 'default_value'
            })
        
        return candidates