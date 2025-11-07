# -*- coding: utf-8 -*-"""
分布式执行模块
"""

import csv
import multiprocessing
from typing import Dict, List, Any, Callable

class DistributedExecutor:
    """
    分布式执行器
    """
    
    def __init__(self, num_workers: int = None):
        """
        初始化分布式执行器
        :param num_workers: 工作进程数量
        """
        self.num_workers = num_workers or multiprocessing.cpu_count()
    
    def execute_query(self, query: Dict[str, Any], metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        执行分布式查询
        :param query: 查询计划
        :param metadata: 分片元数据
        :return: 查询结果
        """
        # 获取所有分片文件
        shard_files = [shard['file_path'] for shard in metadata['shards']]
        
        # 并行执行每个分片的查询
        with multiprocessing.Pool(processes=self.num_workers) as pool:
            results = pool.starmap(self._execute_shard_query, [(query, shard_file) for shard_file in shard_files])
        
        # 合并结果
        merged_results = self._merge_results(results, query)
        
        return merged_results
    
    def _execute_shard_query(self, query: Dict[str, Any], shard_file: str) -> List[Dict[str, Any]]:
        """
        在单个分片上执行查询
        :param query: 查询计划
        :param shard_file: 分片文件路径
        :return: 分片查询结果
        """
        results = []
        
        with open(shard_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            for row in reader:
                # 应用WHERE条件
                if self._apply_where_conditions(row, query.get('where_conditions', [])):
                    results.append(row.copy())
        
        return results
    
    def _apply_where_conditions(self, row: Dict[str, str], conditions: List[str]) -> bool:
        """
        应用WHERE条件
        :param row: 数据行
        :param conditions: WHERE条件列表
        :return: 是否满足条件
        """
        if not conditions:
            return True
        
        for condition in conditions:
            condition = condition.strip()
            
            # 简单解析条件
            if '=' in condition:
                field, value = condition.split('=', 1)
                field = field.strip()
                value = value.strip().strip("'").strip('"')
                
                if field not in row or row[field] != value:
                    return False
            
            elif '>' in condition:
                field, value = condition.split('>', 1)
                field = field.strip()
                value = value.strip()
                
                if field not in row:
                    return False
                
                try:
                    if float(row[field]) <= float(value):
                        return False
                except ValueError:
                    return False
            
            elif '<' in condition:
                field, value = condition.split('<', 1)
                field = field.strip()
                value = value.strip()
                
                if field not in row:
                    return False
                
                try:
                    if float(row[field]) >= float(value):
                        return False
                except ValueError:
                    return False
        
        return True
    
    def _merge_results(self, results: List[List[Dict[str, Any]]], query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        合并分片查询结果
        :param results: 分片查询结果列表
        :param query: 查询计划
        :return: 合并后的结果
        """
        merged = []
        
        # 合并所有结果
        for shard_results in results:
            merged.extend(shard_results)
        
        # 应用GROUP BY
        if query.get('group_by'):
            merged = self._apply_group_by(merged, query)
        
        # 应用ORDER BY
        if query.get('order_by'):
            merged = self._apply_order_by(merged, query)
        
        return merged
    
    def _apply_group_by(self, results: List[Dict[str, Any]], query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        应用GROUP BY
        :param results: 查询结果
        :param query: 查询计划
        :return: 分组后的结果
        """
        group_fields = query.get('group_by', [])
        if not group_fields:
            return results
        
        groups = {}
        
        for row in results:
            # 创建分组键
            group_key = tuple(row[field] for field in group_fields)
            
            if group_key not in groups:
                groups[group_key] = []
            
            groups[group_key].append(row)
        
        # 简单实现：返回分组后的第一行
        merged_groups = []
        for group_key, group_rows in groups.items():
            merged_groups.append(group_rows[0])
        
        return merged_groups
    
    def _apply_order_by(self, results: List[Dict[str, Any]], query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        应用ORDER BY
        :param results: 查询结果
        :param query: 查询计划
        :return: 排序后的结果
        """
        order_fields = query.get('order_by', [])
        if not order_fields:
            return results
        
        def key_func(row):
            return tuple(row[field] for field in order_fields)
        
        return sorted(results, key=key_func)
    
    def execute_aggregate_query(self, query: Dict[str, Any], metadata: Dict[str, Any], aggregate_func: Callable) -> Any:
        """
        执行聚合查询
        :param query: 查询计划
        :param metadata: 分片元数据
        :param aggregate_func: 聚合函数
        :return: 聚合结果
        """
        # 获取所有分片文件
        shard_files = [shard['file_path'] for shard in metadata['shards']]
        
        # 并行执行每个分片的聚合
        with multiprocessing.Pool(processes=self.num_workers) as pool:
            shard_aggregates = pool.starmap(self._execute_shard_aggregate, [(query, shard_file, aggregate_func) for shard_file in shard_files])
        
        # 合并聚合结果
        final_result = aggregate_func(shard_aggregates)
        
        return final_result
    
    def _execute_shard_aggregate(self, query: Dict[str, Any], shard_file: str, aggregate_func: Callable) -> Any:
        """
        在单个分片上执行聚合查询
        :param query: 查询计划
        :param shard_file: 分片文件路径
        :param aggregate_func: 聚合函数
        :return: 分片聚合结果
        """
        results = self._execute_shard_query(query, shard_file)
        return aggregate_func(results)