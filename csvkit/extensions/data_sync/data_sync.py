# -*- coding: utf-8 -*-"""
数据同步引擎主模块
"""

from typing import Dict, List, Any, Callable

from .schema_mapper import SchemaMapper
from .incremental_capture import IncrementalCapture
from .conflict_resolver import ConflictResolver
from .version_control import VersionControl

class DataSyncEngine:
    """
    跨格式的增量数据同步与版本控制引擎
    """
    
    def __init__(self, version_dir: str = './versions'):
        self.schema_mapper = SchemaMapper()
        self.incremental_capture = IncrementalCapture()
        self.conflict_resolver = ConflictResolver()
        self.version_control = VersionControl(version_dir)
        self.sync_history = []
    
    def sync_csv_to_csv(self, source_csv: str, target_csv: str, primary_keys: List[str] = None, 
                       encoding: str = 'utf-8', conflict_strategy: str = 'latest_wins') -> Dict[str, Any]:
        """
        CSV到CSV的增量同步
        :param source_csv: 源CSV路径
        :param target_csv: 目标CSV路径
        :param primary_keys: 主键字段列表
        :param encoding: 文件编码
        :param conflict_strategy: 冲突解决策略
        :return: 同步结果
        """
        if not primary_keys:
            primary_keys = []
        
        # 解析源和目标schema
        source_schema = self.schema_mapper.parse_csv_schema(source_csv, encoding)
        target_schema = self.schema_mapper.parse_csv_schema(target_csv, encoding)
        
        # 生成schema映射
        schema_mapping = self.schema_mapper.generate_schema_mapping(source_schema, target_schema)
        
        # 检测源数据变化
        changes = self.incremental_capture.detect_csv_changes(source_csv, primary_keys, encoding)
        
        # 读取目标数据
        import csv
        target_data = []
        if os.path.exists(target_csv):
            with open(target_csv, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    target_data.append(row)
        
        # 检测冲突
        conflicts = self.conflict_resolver.detect_conflicts(changes['added'], target_data, primary_keys)
        
        # 解决冲突
        resolved_conflicts = self.conflict_resolver.resolve_conflicts(conflicts, conflict_strategy)
        
        # 应用映射和解决后的冲突
        mapped_rows = []
        for row in changes['added']:
            mapped_row = self.schema_mapper.apply_mapping(row, schema_mapping)
            mapped_rows.append(mapped_row)
        
        # 合并数据
        merged_data = target_data.copy()
        
        # 应用新增和修改
        for row in mapped_rows:
            merged_data.append(row)
        
        # 写入目标文件
        with open(target_csv, 'w', encoding=encoding, newline='') as f:
            if merged_data:
                headers = list(merged_data[0].keys())
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for row in merged_data:
                    writer.writerow(row)
        
        # 创建版本
        version = self.version_control.create_version(merged_data, f"Sync from {source_csv} to {target_csv}")
        
        # 记录同步历史
        sync_result = {
            'timestamp': datetime.now().isoformat(),
            'source': source_csv,
            'target': target_csv,
            'changes': changes,
            'conflicts': conflicts,
            'resolved_conflicts': resolved_conflicts,
            'version': version,
            'status': 'success'
        }
        
        self.sync_history.append(sync_result)
        
        return sync_result
    
    def sync_json_to_csv(self, source_json: str, target_csv: str, primary_keys: List[str] = None, 
                        encoding: str = 'utf-8', conflict_strategy: str = 'latest_wins') -> Dict[str, Any]:
        """
        JSON到CSV的增量同步
        :param source_json: 源JSON路径
        :param target_csv: 目标CSV路径
        :param primary_keys: 主键字段列表
        :param encoding: 文件编码
        :param conflict_strategy: 冲突解决策略
        :return: 同步结果
        """
        # 简化实现：将JSON转换为CSV后进行同步
        import json
        import csv
        
        if not primary_keys:
            primary_keys = []
        
        # 读取JSON数据
        with open(source_json, 'r', encoding=encoding) as f:
            json_data = json.load(f)
        
        if not isinstance(json_data, list):
            json_data = [json_data]
        
        # 解析源和目标schema
        source_schema = self.schema_mapper.parse_json_schema(source_json, encoding)
        target_schema = self.schema_mapper.parse_csv_schema(target_csv, encoding)
        
        # 生成schema映射
        schema_mapping = self.schema_mapper.generate_schema_mapping(source_schema, target_schema)
        
        # 应用映射
        mapped_rows = []
        for row in json_data:
            mapped_row = self.schema_mapper.apply_mapping(row, schema_mapping)
            mapped_rows.append(mapped_row)
        
        # 读取目标数据
        target_data = []
        if os.path.exists(target_csv):
            with open(target_csv, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    target_data.append(row)
        
        # 检测冲突
        conflicts = self.conflict_resolver.detect_conflicts(mapped_rows, target_data, primary_keys)
        
        # 解决冲突
        resolved_conflicts = self.conflict_resolver.resolve_conflicts(conflicts, conflict_strategy)
        
        # 合并数据
        merged_data = target_data.copy()
        for row in mapped_rows:
            merged_data.append(row)
        
        # 写入目标文件
        with open(target_csv, 'w', encoding=encoding, newline='') as f:
            if merged_data:
                headers = list(merged_data[0].keys())
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for row in merged_data:
                    writer.writerow(row)
        
        # 创建版本
        version = self.version_control.create_version(merged_data, f"Sync from {source_json} to {target_csv}")
        
        # 记录同步历史
        sync_result = {
            'timestamp': datetime.now().isoformat(),
            'source': source_json,
            'target': target_csv,
            'changes': {'added': mapped_rows, 'modified': [], 'deleted': []},
            'conflicts': conflicts,
            'resolved_conflicts': resolved_conflicts,
            'version': version,
            'status': 'success'
        }
        
        self.sync_history.append(sync_result)
        
        return sync_result
    
    def get_sync_history(self) -> List[Dict[str, Any]]:
        """
        获取同步历史
        :return: 同步历史列表
        """
        return self.sync_history
    
    def save_sync_history(self, file_path: str) -> bool:
        """
        保存同步历史
        :param file_path: 保存路径
        :return: 是否保存成功
        """
        import json
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.sync_history, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存同步历史失败: {str(e)}")
            return False
    
    def rollback_sync(self, version: str, output_path: str, encoding: str = 'utf-8') -> bool:
        """
        回滚同步
        :param version: 版本号
        :param output_path: 输出路径
        :param encoding: 文件编码
        :return: 是否回滚成功
        """
        return self.version_control.rollback_to_version(version, output_path, encoding)
    
    def add_custom_conflict_strategy(self, name: str, strategy_func: Callable):
        """
        添加自定义冲突解决策略
        :param name: 策略名称
        :param strategy_func: 策略函数
        """
        self.conflict_resolver.add_custom_strategy(name, strategy_func)

# 导入需要的模块
import os
from datetime import datetime