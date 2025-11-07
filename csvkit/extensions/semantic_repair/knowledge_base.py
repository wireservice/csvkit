# -*- coding: utf-8 -*-"""
领域知识加载与知识图谱构建模块
"""

import os
import json
from typing import Dict, List, Any

class KnowledgeBase:
    """
    领域知识图谱管理类
    支持导入行业特定的术语表、数据字典或本体文件
    """
    
    def __init__(self):
        self.term_dict: Dict[str, Dict[str, Any]] = {}
        self.field_rules: Dict[str, Dict[str, Any]] = {}
        self.ontology: Dict[str, Any] = {}
        self.relation_rules: List[Dict[str, Any]] = []
    
    def load_terminology(self, file_path: str) -> bool:
        """
        加载术语表文件
        :param file_path: 术语表文件路径（JSON格式）
        :return: 是否加载成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                terminology = json.load(f)
                self.term_dict.update(terminology.get('terms', {}))
            return True
        except Exception as e:
            print(f"加载术语表失败: {str(e)}")
            return False
    
    def load_data_dictionary(self, file_path: str) -> bool:
        """
        加载数据字典文件
        :param file_path: 数据字典文件路径（JSON格式）
        :return: 是否加载成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data_dict = json.load(f)
                self.field_rules.update(data_dict.get('fields', {}))
                self.relation_rules.extend(data_dict.get('relations', []))
            return True
        except Exception as e:
            print(f"加载数据字典失败: {str(e)}")
            return False
    
    def load_owl_ontology(self, file_path: str) -> bool:
        """
        加载OWL本体文件
        :param file_path: OWL文件路径
        :return: 是否加载成功
        """
        # 简化实现：仅支持解析JSON-LD格式的OWL文件
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                owl_data = json.load(f)
                self.ontology.update(owl_data)
            return True
        except Exception as e:
            print(f"加载OWL本体失败: {str(e)}")
            return False
    
    def get_field_rules(self, field_name: str) -> Dict[str, Any]:
        """
        获取字段规则
        :param field_name: 字段名
        :return: 字段规则字典
        """
        return self.field_rules.get(field_name, {})
    
    def get_relation_rules(self) -> List[Dict[str, Any]]:
        """
        获取关联字段规则
        :return: 关联规则列表
        """
        return self.relation_rules
    
    def is_valid_value(self, field_name: str, value: str) -> bool:
        """
        验证字段值是否符合领域规则
        :param field_name: 字段名
        :param value: 字段值
        :return: 是否有效
        """
        rules = self.get_field_rules(field_name)
        if not rules:
            return True
        
        # 检查枚举值
        enum_values = rules.get('enum', [])
        if enum_values and value not in enum_values:
            return False
        
        # 检查格式正则
        import re
        pattern = rules.get('pattern', None)
        if pattern and not re.match(pattern, value):
            return False
        
        return True
    
    def save_knowledge_base(self, file_path: str) -> bool:
        """
        保存知识图谱到文件
        :param file_path: 保存路径
        :return: 是否保存成功
        """
        try:
            kb_data = {
                'terms': self.term_dict,
                'fields': self.field_rules,
                'relations': self.relation_rules,
                'ontology': self.ontology
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(kb_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存知识图谱失败: {str(e)}")
            return False