# -*- coding: utf-8 -*-"""
分布式查询引擎主模块
"""

import os
from typing import Dict, List, Any, Callable
from .query_parser import QueryParser
from .query_optimizer import QueryOptimizer
from .data_sharding import DataSharder
from .distributed_executor import DistributedExecutor

class DistributedQueryEngine:
    """
    分布式查询引擎
    """
    
    def __init__(self, chunk_size: int = 10000, num_shards: int = 10, num_workers: int = None):
        """
        初始化分布式查询引擎
        :param chunk_size: 每个分片的行数
        :param num_shards: 分片数量
        :param num_workers: 工作进程数量
        """
        self.chunk_size = chunk_size
        self.num_shards = num_shards
        self.num_workers = num_workers
        
        self.parser = QueryParser()
        self.optimizer = QueryOptimizer()
        self.sharder = DataSharder(chunk_size=chunk_size, num_shards=num_shards)
        self.executor = DistributedExecutor(num_workers=num_workers)
    
    def create_shards(self, input_file: str, output_dir: str, shard_key: str = None) -> Dict[str, Any]:
        """
        创建数据分片
        :param input_file: 输入CSV文件路径
        :param output_dir: 输出分片目录
        :param shard_key: 分片键（可选）
        :return: 分片元数据
        """
        return self.sharder.shard_data(input_file, output_dir, shard_key)
    
    def load_shards(self, metadata_file: str) -> Dict[str, Any]:
        """
        加载已有的数据分片
        :param metadata_file: 元数据文件路径
        :return: 分片元数据
        """
        return self.sharder.load_metadata(metadata_file)
    
    def execute_query(self, query: str, metadata: Dict[str, Any], schema: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        执行查询
        :param query: 查询字符串
        :param metadata: 分片元数据
        :param schema: 数据schema（可选）
        :return: 查询结果
        """
        # 解析查询
        parsed_query = self.parser.parse_query(query)
        
        # 验证查询
        if schema and not self.parser.validate_query(parsed_query, schema):
            raise ValueError("Invalid query")
        
        # 优化查询
        optimized_query = self.optimizer.optimize_query(parsed_query, schema or {})
        
        # 执行查询
        results = self.executor.execute_query(optimized_query, metadata)
        
        return results
    
    def execute_aggregate(self, query: str, metadata: Dict[str, Any], aggregate_func: Callable, schema: Dict[str, Any] = None) -> Any:
        """
        执行聚合查询
        :param query: 查询字符串
        :param metadata: 分片元数据
        :param aggregate_func: 聚合函数
        :param schema: 数据schema（可选）
        :return: 聚合结果
        """
        # 解析查询
        parsed_query = self.parser.parse_query(query)
        
        # 验证查询
        if schema and not self.parser.validate_query(parsed_query, schema):
            raise ValueError("Invalid query")
        
        # 优化查询
        optimized_query = self.optimizer.optimize_query(parsed_query, schema or {})
        
        # 执行聚合查询
        result = self.executor.execute_aggregate_query(optimized_query, metadata, aggregate_func)
        
        return result
    
    def estimate_query_cost(self, query: str, schema: Dict[str, Any]) -> float:
        """
        估算查询成本
        :param query: 查询字符串
        :param schema: 数据schema
        :return: 成本估算值
        """
        parsed_query = self.parser.parse_query(query)
        return self.optimizer.estimate_query_cost(parsed_query, schema)
    
    def get_query_plan(self, query: str, schema: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取查询计划
        :param query: 查询字符串
        :param schema: 数据schema（可选）
        :return: 查询计划
        """
        parsed_query = self.parser.parse_query(query)
        return self.optimizer.optimize_query(parsed_query, schema or {})
    
    def create_index(self, metadata: Dict[str, Any], field: str) -> None:
        """
        为字段创建索引
        :param metadata: 分片元数据
        :param field: 字段名
        """
        # 简化实现：创建字段索引
        for shard in metadata['shards']:
            shard_file = shard['file_path']
            index_file = shard_file + '.index.' + field
            
            with open(shard_file, 'r', encoding='utf-8') as f:
                reader = __import__('csv').DictReader(f)
                
                with open(index_file, 'w', encoding='utf-8') as idx_f:
                    for i, row in enumerate(reader):
                        if field in row:
                            idx_f.write(f"{row[field]},{i}\n")
    
    def drop_index(self, metadata: Dict[str, Any], field: str) -> None:
        """
        删除字段索引
        :param metadata: 分片元数据
        :param field: 字段名
        """
        for shard in metadata['shards']:
            shard_file = shard['file_path']
            index_file = shard_file + '.index.' + field
            
            if os.path.exists(index_file):
                os.remove(index_file)