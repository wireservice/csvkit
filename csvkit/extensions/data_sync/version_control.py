# -*- coding: utf-8 -*-"""
版本控制与回溯模块
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any

class VersionControl:
    """
    版本控制类
    """
    
    def __init__(self, version_dir: str = './versions'):
        self.version_dir = version_dir
        self.versions = []
        
        # 创建版本目录
        if not os.path.exists(self.version_dir):
            os.makedirs(self.version_dir)
        
        # 加载现有版本
        self._load_versions()
    
    def _load_versions(self):
        """
        加载现有版本
        """
        if not os.path.exists(self.version_dir):
            return
        
        for filename in os.listdir(self.version_dir):
            if filename.endswith('.json'):
                version_path = os.path.join(self.version_dir, filename)
                try:
                    with open(version_path, 'r', encoding='utf-8') as f:
                        version_info = json.load(f)
                        self.versions.append(version_info)
                except Exception as e:
                    print(f"加载版本信息失败: {str(e)}")
        
        # 按版本号排序
        self.versions.sort(key=lambda x: x.get('version', ''), reverse=True)
    
    def create_version(self, data: List[Dict[str, str]], description: str = '') -> str:
        """
        创建新版本
        :param data: 版本数据
        :param description: 版本描述
        :return: 版本号
        """
        # 生成版本号 (时间戳 + 随机字符串)
        version = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4()[:8]}"
        
        version_info = {
            'version': version,
            'timestamp': datetime.now().isoformat(),
            'description': description,
            'data_count': len(data),
            'data': data
        }
        
        # 保存版本信息
        version_path = os.path.join(self.version_dir, f"version_{version}.json")
        try:
            with open(version_path, 'w', encoding='utf-8') as f:
                json.dump(version_info, f, ensure_ascii=False, indent=2)
            
            # 添加到版本列表
            self.versions.insert(0, version_info)
            return version
        except Exception as e:
            print(f"创建版本失败: {str(e)}")
            return None
    
    def get_version(self, version: str) -> Dict[str, Any]:
        """
        获取指定版本
        :param version: 版本号
        :return: 版本信息
        """
        for v in self.versions:
            if v.get('version') == version:
                return v
        return None
    
    def get_latest_version(self) -> Dict[str, Any]:
        """
        获取最新版本
        :return: 最新版本信息
        """
        if self.versions:
            return self.versions[0]
        return None
    
    def rollback_to_version(self, version: str, output_path: str, encoding: str = 'utf-8') -> bool:
        """
        回滚到指定版本
        :param version: 版本号
        :param output_path: 输出路径
        :param encoding: 文件编码
        :return: 是否回滚成功
        """
        version_info = self.get_version(version)
        if not version_info:
            return False
        
        data = version_info.get('data', [])
        if not data:
            return False
        
        import csv
        
        try:
            with open(output_path, 'w', encoding=encoding, newline='') as f:
                if data:
                    headers = list(data[0].keys())
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    for row in data:
                        writer.writerow(row)
            return True
        except Exception as e:
            print(f"回滚版本失败: {str(e)}")
            return False
    
    def list_versions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        列出版本
        :param limit: 限制数量
        :return: 版本列表
        """
        return self.versions[:limit]
    
    def delete_version(self, version: str) -> bool:
        """
        删除版本
        :param version: 版本号
        :return: 是否删除成功
        """
        version_info = self.get_version(version)
        if not version_info:
            return False
        
        version_path = os.path.join(self.version_dir, f"version_{version}.json")
        try:
            os.remove(version_path)
            self.versions = [v for v in self.versions if v.get('version') != version]
            return True
        except Exception as e:
            print(f"删除版本失败: {str(e)}")
            return False