# -*- coding: utf-8 -*-"""
隐私处理模块
"""

import re
import hashlib
import random
from typing import Dict, List, Any, Callable

class PrivacyProcessor:
    """
    隐私处理器
    """
    
    def __init__(self):
        # 脱敏规则
        self.desensitization_rules = {
            'phone': self._desensitize_phone,
            'email': self._desensitize_email,
            'id_card': self._desensitize_id_card,
            'bank_card': self._desensitize_bank_card,
            'name': self._desensitize_name,
            'address': self._desensitize_address
        }
    
    def desensitize(self, data: str, sensitive_type: str) -> str:
        """
        脱敏处理
        :param data: 原始数据
        :param sensitive_type: 敏感类型
        :return: 脱敏后的数据
        """
        if sensitive_type in self.desensitization_rules:
            return self.desensitization_rules[sensitive_type](data)
        return data
    
    def _desensitize_phone(self, phone: str) -> str:
        """
        手机号脱敏：中间4位替换为*
        :param phone: 手机号
        :return: 脱敏后的手机号
        """
        if len(phone) == 11:
            return phone[:3] + '****' + phone[7:]
        return phone
    
    def _desensitize_email(self, email: str) -> str:
        """
        邮箱脱敏：@前的字符保留前3位，其余替换为*
        :param email: 邮箱
        :return: 脱敏后的邮箱
        """
        if '@' in email:
            username, domain = email.split('@', 1)
            if len(username) <= 3:
                return username + '@' + domain
            return username[:3] + '*' * (len(username) - 3) + '@' + domain
        return email
    
    def _desensitize_id_card(self, id_card: str) -> str:
        """
        身份证号脱敏：保留前6位和后4位，中间替换为*
        :param id_card: 身份证号
        :return: 脱敏后的身份证号
        """
        if len(id_card) == 18:
            return id_card[:6] + '**********' + id_card[14:]
        return id_card
    
    def _desensitize_bank_card(self, bank_card: str) -> str:
        """
        银行卡号脱敏：保留前4位和后4位，中间替换为*
        :param bank_card: 银行卡号
        :return: 脱敏后的银行卡号
        """
        if len(bank_card) >= 8:
            return bank_card[:4] + '*' * (len(bank_card) - 8) + bank_card[-4:]
        return bank_card
    
    def _desensitize_name(self, name: str) -> str:
        """
        姓名脱敏：保留姓，名替换为*
        :param name: 姓名
        :return: 脱敏后的姓名
        """
        if len(name) == 1:
            return name
        return name[0] + '*' * (len(name) - 1)
    
    def _desensitize_address(self, address: str) -> str:
        """
        地址脱敏：保留到城市级，详细地址替换为*
        :param address: 地址
        :return: 脱敏后的地址
        """
        # 简单实现：保留前两个逗号之前的内容
        parts = address.split('，') if '，' in address else address.split(',')
        if len(parts) >= 2:
            return '，'.join(parts[:2]) + '，***'
        return address
    
    def anonymize(self, rows: List[Dict[str, str]], quasi_identifiers: List[str], k: int = 5) -> List[Dict[str, str]]:
        """
        k-匿名化处理
        :param rows: 数据行
        :param quasi_identifiers: 准标识符
        :param k: k值
        :return: 匿名化后的数据行
        """
        # 简化实现：对每个准标识符进行泛化
        anonymized_rows = []
        
        for row in rows:
            anonymized_row = row.copy()
            
            for field in quasi_identifiers:
                if field in anonymized_row:
                    value = anonymized_row[field]
                    
                    # 简单泛化处理
                    if field in ['age', '年龄']:
                        # 年龄泛化为区间
                        try:
                            age = int(value)
                            if age < 18:
                                anonymized_row[field] = '0-17'
                            elif age < 30:
                                anonymized_row[field] = '18-29'
                            elif age < 40:
                                anonymized_row[field] = '30-39'
                            elif age < 50:
                                anonymized_row[field] = '40-49'
                            elif age < 60:
                                anonymized_row[field] = '50-59'
                            else:
                                anonymized_row[field] = '60+'
                        except ValueError:
                            pass
                    
                    elif field in ['zip', '邮编', 'postcode']:
                        # 邮编泛化为前三位
                        if len(value) >= 3:
                            anonymized_row[field] = value[:3] + '**'
                    
                    elif field in ['city', '城市']:
                        # 城市保留不变
                        pass
            
            anonymized_rows.append(anonymized_row)
        
        return anonymized_rows
    
    def differential_privacy(self, value: float, epsilon: float = 1.0) -> float:
        """
        差分隐私处理：添加拉普拉斯噪声
        :param value: 原始值
        :param epsilon: 隐私预算
        :return: 添加噪声后的值
        """
        # 拉普拉斯噪声
        noise = random.laplace(0, 1/epsilon)
        return value + noise
    
    def hash_anonymize(self, data: str, salt: str = '') -> str:
        """
        哈希匿名化
        :param data: 原始数据
        :param salt: 盐值
        :return: 哈希后的值
        """
        hash_obj = hashlib.sha256((data + salt).encode('utf-8'))
        return hash_obj.hexdigest()
    
    def add_desensitization_rule(self, sensitive_type: str, rule_func: Callable) -> None:
        """
        添加自定义脱敏规则
        :param sensitive_type: 敏感类型
        :param rule_func: 脱敏函数
        """
        self.desensitization_rules[sensitive_type] = rule_func
    
    def process_batch(self, rows: List[Dict[str, str]], sensitive_fields: Dict[str, str]) -> List[Dict[str, str]]:
        """
        批量处理隐私数据
        :param rows: 数据行
        :param sensitive_fields: 敏感字段字典
        :return: 处理后的数据行
        """
        processed_rows = []
        
        for row in rows:
            processed_row = row.copy()
            
            for field, sensitive_type in sensitive_fields.items():
                if field in processed_row:
                    processed_row[field] = self.desensitize(processed_row[field], sensitive_type)
            
            processed_rows.append(processed_row)
        
        return processed_rows