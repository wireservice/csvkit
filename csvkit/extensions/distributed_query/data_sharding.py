# -*- coding: utf-8 -*-"""
数据分片模块
"""

import os
import json
import hashlib
import csv
from typing import Dict, List, Any

class DataSharder:
    """
    数据分片器
    """
    
    def __init__(self, chunk_size: int = 10000, num_shards: int = 10):
        """
        初始化数据分片器
        :param chunk_size: 每个分片的行数（基于大小分片时使用）
        :param num_shards: 分片数量（基于键分片时使用）
        """
        self.chunk_size = chunk_size
        self.num_shards = num_shards
    
    def shard_data(self, input_file: str, output_dir: str, shard_key: str = None) -> Dict[str, Any]:
        """
        对CSV文件进行分片
        :param input_file: 输入CSV文件路径
        :param output_dir: 输出分片目录
        :param shard_key: 分片键（可选）
        :return: 分片元数据
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        metadata = {
            'input_file': input_file,
            'shard_key': shard_key,
            'num_shards': 0,
            'shards': []
        }
        
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            if shard_key and shard_key not in headers:
                raise ValueError(f"Shard key '{shard_key}' not found in headers")
            
            # 根据分片方式选择不同的分片策略
            if shard_key:
                # 基于键分片
                shard_files = {}
                shard_writers = {}
                
                # 初始化所有分片文件
                for i in range(self.num_shards):
                    shard_file = os.path.join(output_dir, f'shard_{i}.csv')
                    shard_files[i] = shard_file
                    f_shard = open(shard_file, 'w', encoding='utf-8', newline='')
                    writer = csv.DictWriter(f_shard, fieldnames=headers)
                    writer.writeheader()
                    shard_writers[i] = (f_shard, writer)
                
                # 分配行到不同分片
                for row in reader:
                    key_value = row[shard_key]
                    shard_id = self._get_shard_id(key_value)
                    shard_writers[shard_id][1].writerow(row)
                
                # 关闭所有分片文件
                for i in range(self.num_shards):
                    shard_writers[i][0].close()
                    shard_size = os.path.getsize(shard_files[i])
                    metadata['shards'].append({
                        'shard_id': i,
                        'file_path': shard_files[i],
                        'size': shard_size,
                        'row_count': 0  # 简化实现，实际应统计行数
                    })
                
                metadata['num_shards'] = self.num_shards
            else:
                # 基于大小分片
                shard_id = 0
                row_count = 0
                current_shard_file = None
                current_writer = None
                
                for row in reader:
                    if row_count % self.chunk_size == 0:
                        # 关闭当前分片文件
                        if current_shard_file:
                            current_writer.close()
                            shard_size = os.path.getsize(current_shard_file)
                            metadata['shards'].append({
                                'shard_id': shard_id,
                                'file_path': current_shard_file,
                                'size': shard_size,
                                'row_count': self.chunk_size
                            })
                            shard_id += 1
                        
                        # 打开新的分片文件
                        current_shard_file = os.path.join(output_dir, f'shard_{shard_id}.csv')
                        f_shard = open(current_shard_file, 'w', encoding='utf-8', newline='')
                        current_writer = csv.DictWriter(f_shard, fieldnames=headers)
                        current_writer.writeheader()
                    
                    current_writer.writerow(row)
                    row_count += 1
                
                # 关闭最后一个分片文件
                if current_shard_file:
                    current_writer.close()
                    shard_size = os.path.getsize(current_shard_file)
                    metadata['shards'].append({
                        'shard_id': shard_id,
                        'file_path': current_shard_file,
                        'size': shard_size,
                        'row_count': row_count % self.chunk_size or self.chunk_size
                    })
                    shard_id += 1
                
                metadata['num_shards'] = shard_id
        
        # 保存元数据
        metadata_file = os.path.join(output_dir, 'metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return metadata
    
    def _get_shard_id(self, key_value: str) -> int:
        """
        根据键值计算分片ID
        :param key_value: 键值
        :return: 分片ID
        """
        # 使用哈希函数计算分片ID
        hash_obj = hashlib.md5(key_value.encode('utf-8'))
        hash_int = int(hash_obj.hexdigest(), 16)
        return hash_int % self.num_shards
    
    def load_metadata(self, metadata_file: str) -> Dict[str, Any]:
        """
        加载分片元数据
        :param metadata_file: 元数据文件路径
        :return: 分片元数据
        """
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)