# -*- coding: utf-8 -*-"""
数据源配置与schema映射模块
"""

from typing import Dict, List, Any

class SchemaMapper:
    """
    数据源结构解析与schema映射类
    """
    
    def __init__(self):
        self.schema_mappings = []
    
    def parse_csv_schema(self, csv_path: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        解析CSV文件结构
        :param csv_path: CSV文件路径
        :param encoding: 文件编码
        :return: schema结构
        """
        import csv
        
        with open(csv_path, 'r', encoding=encoding) as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            # 简单的类型推断
            sample_rows = [row for row in reader][:10]
            field_types = {}
            
            for header in headers:
                field_types[header] = 'string'
                
                # 尝试推断数字类型
                has_number = True
                for row in sample_rows:
                    value = row[header]
                    if not value:
                        continue
                    try:
                        float(value)
                    except ValueError:
                        has_number = False
                        break
                
                if has_number:
                    field_types[header] = 'number'
            
            return {
                'type': 'csv',
                'headers': headers,
                'field_types': field_types,
                'sample_rows': sample_rows
            }
    
    def parse_json_schema(self, json_path: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        解析JSON文件结构
        :param json_path: JSON文件路径
        :param encoding: 文件编码
        :return: schema结构
        """
        import json
        
        with open(json_path, 'r', encoding=encoding) as f:
            data = json.load(f)
        
        if isinstance(data, list) and data:
            first_item = data[0]
            headers = list(first_item.keys())
            return {
                'type': 'json',
                'headers': headers,
                'field_types': {h: 'string' for h in headers},
                'sample_rows': data[:10]
            }
        
        return {
            'type': 'json',
            'headers': [],
            'field_types': {},
            'sample_rows': []
        }
    
    def generate_schema_mapping(self, source_schema: Dict[str, Any], target_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成schema映射关系
        :param source_schema: 源schema
        :param target_schema: 目标schema
        :return: 映射关系
        """
        mappings = []
        
        source_headers = source_schema.get('headers', [])
        target_headers = target_schema.get('headers', [])
        
        # 自动匹配字段名
        for source_field in source_headers:
            for target_field in target_headers:
                if source_field.lower() == target_field.lower():
                    mappings.append({
                        'source_field': source_field,
                        'target_field': target_field,
                        'type_conversion': None,
                        'default_value': None
                    })
                    break
        
        return {
            'source_type': source_schema.get('type', ''),
            'target_type': target_schema.get('type', ''),
            'mappings': mappings
        }
    
    def apply_mapping(self, row: Dict[str, str], mapping: Dict[str, Any]) -> Dict[str, str]:
        """
        应用schema映射
        :param row: 原始行数据
        :param mapping: 映射关系
        :return: 映射后的行数据
        """
        mapped_row = {}
        
        for field_mapping in mapping.get('mappings', []):
            source_field = field_mapping.get('source_field', '')
            target_field = field_mapping.get('target_field', '')
            type_conversion = field_mapping.get('type_conversion', None)
            default_value = field_mapping.get('default_value', None)
            
            value = row.get(source_field, default_value)
            
            # 类型转换
            if type_conversion == 'number' and value:
                try:
                    value = str(float(value))
                except ValueError:
                    value = default_value
            
            mapped_row[target_field] = value
        
        return mapped_row