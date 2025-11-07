# -*- coding: utf-8 -*-"""
增量捕获机制模块
"""

import os
import hashlib
from typing import Dict, List, Any, Tuple

class IncrementalCapture:
    """
    增量数据捕获类
    """
    
    def __init__(self):
        self.last_sync_info = {}
    
    def calculate_file_hash(self, file_path: str, encoding: str = 'utf-8') -> str:
        """
        计算文件哈希值
        :param file_path: 文件路径
        :param encoding: 文件编码
        :return: 哈希值
        """
        hasher = hashlib.md5()
        with open(file_path, 'r', encoding=encoding) as f:
            for line in f:
                hasher.update(line.encode(encoding))
        return hasher.hexdigest()
    
    def calculate_row_fingerprint(self, row: Dict[str, str], primary_keys: List[str]) -> str:
        """
        计算行指纹
        :param row: 行数据
        :param primary_keys: 主键字段列表
        :return: 指纹值
        """
        if not primary_keys:
            # 使用所有字段计算指纹
            sorted_fields = sorted(row.keys())
            row_str = '|'.join([row[field] for field in sorted_fields])
        else:
            # 使用主键字段计算指纹
            row_str = '|'.join([row.get(pk, '') for pk in primary_keys])
        
        return hashlib.md5(row_str.encode('utf-8')).hexdigest()
    
    def detect_csv_changes(self, csv_path: str, primary_keys: List[str] = None, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        检测CSV文件的变化
        :param csv_path: CSV文件路径
        :param primary_keys: 主键字段列表
        :param encoding: 文件编码
        :return: 变化信息
        """
        import csv
        
        if not primary_keys:
            primary_keys = []
        
        # 读取当前文件内容
        current_rows = []
        current_fingerprints = set()
        
        with open(csv_path, 'r', encoding=encoding) as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            for row in reader:
                fingerprint = self.calculate_row_fingerprint(row, primary_keys)
                current_fingerprints.add(fingerprint)
                current_rows.append((fingerprint, row))
        
        # 对比上次同步的指纹
        changes = {
            'added': [],
            'modified': [],
            'deleted': [],
            'unchanged': []
        }
        
        if csv_path in self.last_sync_info:
            last_fingerprints = self.last_sync_info[csv_path]['fingerprints']
            last_rows = {fp: row for fp, row in self.last_sync_info[csv_path]['rows']}
            
            # 检测新增和修改
            for fp, row in current_rows:
                if fp not in last_fingerprints:
                    changes['added'].append(row)
                elif last_rows[fp] != row:
                    changes['modified'].append({'old': last_rows[fp], 'new': row})
                else:
                    changes['unchanged'].append(row)
            
            # 检测删除
            for fp in last_fingerprints:
                if fp not in current_fingerprints:
                    changes['deleted'].append(last_rows[fp])
        else:
            # 首次同步，所有行都是新增
            changes['added'] = [row for fp, row in current_rows]
        
        # 更新上次同步信息
        self.last_sync_info[csv_path] = {
            'fingerprints': current_fingerprints,
            'rows': current_rows,
            'last_sync_time': os.path.getmtime(csv_path)
        }
        
        return changes
    
    def load_last_sync_info(self, file_path: str) -> bool:
        """
        加载上次同步信息
        :param file_path: 同步信息文件路径
        :return: 是否加载成功
        """
        import json
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.last_sync_info = json.load(f)
            return True
        except Exception as e:
            print(f"加载同步信息失败: {str(e)}")
            return False
    
    def save_last_sync_info(self, file_path: str) -> bool:
        """
        保存同步信息
        :param file_path: 同步信息文件路径
        :return: 是否保存成功
        """
        import json
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.last_sync_info, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存同步信息失败: {str(e)}")
            return False