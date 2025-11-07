# -*- coding: utf-8 -*-"""
语义错误检测模块
"""

import re
from typing import List, Dict, Any, Tuple

class SemanticErrorDetector:
    """
    语义错误检测类
    利用语义相似度、NER和交叉验证检测错误
    """
    
    def __init__(self, knowledge_base=None):
        self.kb = knowledge_base
        self.error_types = {
            'semantic_mismatch': '语义不匹配',
            'type_mismatch': '类型不匹配',
            'invalid_format': '格式无效',
            'logical_conflict': '逻辑冲突',
            'out_of_range': '超出范围'
        }
    
    def detect_semantic_mismatch(self, field_name: str, value: str) -> bool:
        """
        检测语义不匹配（简化实现：基于规则匹配）
        :param field_name: 字段名
        :param value: 字段值
        :return: 是否存在语义不匹配
        """
        if not self.kb:
            return False
        
        rules = self.kb.get_field_rules(field_name)
        if not rules:
            return False
        
        # 检查枚举值
        enum_values = rules.get('enum', [])
        if enum_values and value not in enum_values:
            return True
        
        return False
    
    def detect_type_mismatch(self, field_name: str, value: str) -> bool:
        """
        检测类型不匹配
        :param field_name: 字段名
        :param value: 字段值
        :return: 是否存在类型不匹配
        """
        if not value:
            return False
        
        # 简单的类型检测
        field_lower = field_name.lower()
        
        if '日期' in field_lower or 'date' in field_lower:
            # 检查日期格式
            date_patterns = [
                r'^\d{4}-\d{2}-\d{2}$',
                r'^\d{4}/\d{2}/\d{2}$',
                r'^\d{8}$'
            ]
            for pattern in date_patterns:
                if re.match(pattern, value):
                    return False
            return True
        
        if '数字' in field_lower or 'number' in field_lower or 'age' in field_lower or 'price' in field_lower:
            # 检查数字格式
            try:
                float(value)
                return False
            except ValueError:
                return True
        
        if '邮箱' in field_lower or 'email' in field_lower:
            # 检查邮箱格式
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return not bool(re.match(email_pattern, value))
        
        if '手机' in field_lower or 'phone' in field_lower:
            # 检查手机号格式
            phone_pattern = r'^1[3-9]\d{9}$'
            return not bool(re.match(phone_pattern, value))
        
        return False
    
    def detect_logical_conflict(self, row: Dict[str, str], relation_rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        检测关联字段逻辑冲突
        :param row: 行数据
        :param relation_rules: 关联规则
        :return: 冲突列表
        """
        conflicts = []
        
        for rule in relation_rules:
            fields = rule.get('fields', [])
            condition = rule.get('condition', None)
            
            if not condition or len(fields) < 2:
                continue
            
            # 简化实现：检查字段是否都存在
            has_all_fields = all(field in row for field in fields)
            if not has_all_fields:
                continue
            
            # 尝试执行简单的逻辑检查
            try:
                if '=' in condition:
                    left, right = condition.split('=')
                    left_val = row.get(left.strip(), '')
                    right_val = row.get(right.strip(), '')
                    if left_val != right_val:
                        conflicts.append({
                            'type': 'logical_conflict',
                            'fields': fields,
                            'message': f'字段 {left} 和 {right} 不满足关系 {condition}'
                        })
            except Exception as e:
                continue
        
        return conflicts
    
    def detect_invalid_email_domain(self, email: str) -> bool:
        """
        检测邮箱域名是否有效
        :param email: 邮箱地址
        :return: 域名是否无效
        """
        if '@' not in email:
            return True
        
        domain = email.split('@')[1]
        
        # 简单的域名有效性检查（实际应使用DNS查询）
        invalid_domains = ['example.com', 'test.com', 'invalid.com']
        if domain in invalid_domains:
            return True
        
        # 检查域名格式
        domain_pattern = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return not bool(re.match(domain_pattern, domain))
    
    def detect_all_errors(self, row: Dict[str, str], row_index: int = -1) -> List[Dict[str, Any]]:
        """
        检测行中的所有语义错误
        :param row: 行数据
        :param row_index: 行索引
        :return: 错误列表
        """
        errors = []
        
        for field_name, value in row.items():
            # 检测语义不匹配
            if self.detect_semantic_mismatch(field_name, value):
                errors.append({
                    'row_index': row_index,
                    'field': field_name,
                    'value': value,
                    'error_type': 'semantic_mismatch',
                    'message': f'字段值与字段名语义不匹配'
                })
            
            # 检测类型不匹配
            if self.detect_type_mismatch(field_name, value):
                errors.append({
                    'row_index': row_index,
                    'field': field_name,
                    'value': value,
                    'error_type': 'type_mismatch',
                    'message': f'字段值类型与字段名不匹配'
                })
            
            # 检测邮箱域名有效性
            if '邮箱' in field_name.lower() or 'email' in field_name.lower():
                if self.detect_invalid_email_domain(value):
                    errors.append({
                        'row_index': row_index,
                        'field': field_name,
                        'value': value,
                        'error_type': 'invalid_format',
                        'message': f'邮箱域名无效'
                    })
        
        # 检测逻辑冲突
        if self.kb:
            relation_rules = self.kb.get_relation_rules()
            logical_conflicts = self.detect_logical_conflict(row, relation_rules)
            for conflict in logical_conflicts:
                errors.append({
                    'row_index': row_index,
                    'field': conflict['fields'],
                    'value': [row[field] for field in conflict['fields']],
                    'error_type': conflict['type'],
                    'message': conflict['message']
                })
        
        return errors