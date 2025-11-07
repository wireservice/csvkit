# -*- coding: utf-8 -*-"""
敏感信息检测模块
"""

import re
from typing import Dict, List, Any, Tuple

class SensitiveDetector:
    """
    敏感信息检测器
    """
    
    def __init__(self):
        # 预定义的敏感信息正则表达式
        self.sensitive_patterns = {
            'id_card': r'\d{17}[\dXx]',  # 身份证号
            'phone': r'1[3-9]\d{9}',  # 手机号
            'email': r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',  # 邮箱
            'bank_card': r'\d{16}|\d{19}',  # 银行卡号
            'credit_card': r'\d{16}',  # 信用卡号
            'ip': r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # IP地址
            'mac': r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})',  # MAC地址
            'social_security': r'\d{18}|\d{15}',  # 社保卡号
            'passport': r'[EeKkGgDdSsPpHh]\d{8}|[Ee]\d{9}',  # 护照号
            'driver_license': r'[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[\dXx]'  # 驾驶证号
        }
        
        # 预定义的敏感字段名称
        self.sensitive_field_names = {
            'id', '身份证', '身份证号', 'id_card', 'identity_card',
            'phone', '手机号', '电话', 'telephone', 'mobile',
            'email', '邮箱', '电子邮件',
            'bank', '银行卡', '银行卡号', 'bank_card',
            'credit', '信用卡', '信用卡号', 'credit_card',
            'ssn', '社保', '社保卡', '社保卡号', 'social_security',
            'passport', '护照', '护照号',
            'driver', '驾照', '驾驶证', '驾驶证号', 'driver_license',
            'address', '地址', '家庭地址',
            'birthday', '生日', '出生日期',
            'name', '姓名', '用户名', 'user_name',
            'password', '密码', 'pwd'
        }
    
    def detect_sensitive_fields(self, headers: List[str]) -> Dict[str, str]:
        """
        检测敏感字段
        :param headers: CSV表头
        :return: 敏感字段字典，键为字段名，值为敏感类型
        """
        sensitive_fields = {}
        
        for header in headers:
            header_lower = header.lower().strip()
            
            # 检查字段名是否包含敏感关键词
            for field_name in self.sensitive_field_names:
                if field_name in header_lower:
                    # 确定敏感类型
                    if 'id' in field_name or '身份证' in field_name:
                        sensitive_fields[header] = 'id_card'
                    elif 'phone' in field_name or '手机' in field_name or '电话' in field_name:
                        sensitive_fields[header] = 'phone'
                    elif 'email' in field_name or '邮箱' in field_name:
                        sensitive_fields[header] = 'email'
                    elif 'bank' in field_name or '银行卡' in field_name:
                        sensitive_fields[header] = 'bank_card'
                    elif 'credit' in field_name or '信用卡' in field_name:
                        sensitive_fields[header] = 'credit_card'
                    elif 'ssn' in field_name or '社保' in field_name:
                        sensitive_fields[header] = 'social_security'
                    elif 'passport' in field_name or '护照' in field_name:
                        sensitive_fields[header] = 'passport'
                    elif 'driver' in field_name or '驾照' in field_name or '驾驶证' in field_name:
                        sensitive_fields[header] = 'driver_license'
                    elif 'address' in field_name or '地址' in field_name:
                        sensitive_fields[header] = 'address'
                    elif 'birthday' in field_name or '生日' in field_name:
                        sensitive_fields[header] = 'birthday'
                    elif 'name' in field_name or '姓名' in field_name:
                        sensitive_fields[header] = 'name'
                    elif 'password' in field_name or '密码' in field_name or 'pwd' in field_name:
                        sensitive_fields[header] = 'password'
                    break
        
        return sensitive_fields
    
    def detect_sensitive_data(self, data: str, field_type: str = None) -> List[Tuple[str, str]]:
        """
        检测敏感数据
        :param data: 数据字符串
        :param field_type: 字段类型（可选）
        :return: 敏感数据列表，每个元素为(敏感类型, 敏感值)
        """
        sensitive_data = []
        
        if field_type and field_type in self.sensitive_patterns:
            # 如果指定了字段类型，只检查该类型
            pattern = self.sensitive_patterns[field_type]
            matches = re.findall(pattern, data)
            for match in matches:
                sensitive_data.append((field_type, match))
        else:
            # 检查所有敏感类型
            for sensitive_type, pattern in self.sensitive_patterns.items():
                matches = re.findall(pattern, data)
                for match in matches:
                    sensitive_data.append((sensitive_type, match))
        
        return sensitive_data
    
    def add_sensitive_pattern(self, sensitive_type: str, pattern: str) -> None:
        """
        添加自定义敏感信息正则表达式
        :param sensitive_type: 敏感类型
        :param pattern: 正则表达式
        """
        self.sensitive_patterns[sensitive_type] = pattern
    
    def add_sensitive_field_name(self, field_name: str) -> None:
        """
        添加自定义敏感字段名称
        :param field_name: 字段名称
        """
        self.sensitive_field_names.add(field_name.lower())
    
    def detect_all_sensitive(self, headers: List[str], rows: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        检测所有敏感信息
        :param headers: CSV表头
        :param rows: CSV数据行
        :return: 敏感信息检测结果
        """
        result = {
            'sensitive_fields': self.detect_sensitive_fields(headers),
            'sensitive_data': []
        }
        
        # 检测每行中的敏感数据
        for i, row in enumerate(rows):
            row_sensitive = {
                'row_index': i,
                'data': []
            }
            
            for field, value in row.items():
                field_type = result['sensitive_fields'].get(field)
                if field_type:
                    # 该字段是敏感字段，检测具体数据
                    data_matches = self.detect_sensitive_data(value, field_type)
                    for match in data_matches:
                        row_sensitive['data'].append({
                            'field': field,
                            'type': match[0],
                            'value': match[1]
                        })
            
            if row_sensitive['data']:
                result['sensitive_data'].append(row_sensitive)
        
        return result