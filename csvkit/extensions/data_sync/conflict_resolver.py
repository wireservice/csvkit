# -*- coding: utf-8 -*-"""
冲突检测与解决模块
"""

from typing import Dict, List, Any, Callable

class ConflictResolver:
    """
    冲突检测与解决类
    """
    
    def __init__(self):
        self.conflict_strategies = {
            'database_wins': self._database_wins_strategy,
            'latest_wins': self._latest_wins_strategy,
            'custom': None
        }
    
    def detect_conflicts(self, source_data: List[Dict[str, str]], target_data: List[Dict[str, str]], 
                        primary_keys: List[str]) -> List[Dict[str, Any]]:
        """
        检测冲突
        :param source_data: 源数据
        :param target_data: 目标数据
        :param primary_keys: 主键字段列表
        :return: 冲突列表
        """
        conflicts = []
        
        if not primary_keys:
            return conflicts
        
        # 构建目标数据索引
        target_index = {}
        for row in target_data:
            key = tuple(row.get(pk, '') for pk in primary_keys)
            target_index[key] = row
        
        # 检查源数据与目标数据的冲突
        for source_row in source_data:
            key = tuple(source_row.get(pk, '') for pk in primary_keys)
            if key in target_index:
                target_row = target_index[key]
                
                # 检查字段值冲突
                for field in source_row:
                    if field in target_row and source_row[field] != target_row[field]:
                        conflicts.append({
                            'type': 'field_conflict',
                            'primary_key': key,
                            'field': field,
                            'source_value': source_row[field],
                            'target_value': target_row[field]
                        })
                        break  # 只记录第一个冲突字段
        
        return conflicts
    
    def resolve_conflicts(self, conflicts: List[Dict[str, Any]], strategy: str = 'latest_wins', 
                         custom_func: Callable = None, **kwargs) -> List[Dict[str, Any]]:
        """
        解决冲突
        :param conflicts: 冲突列表
        :param strategy: 解决策略
        :param custom_func: 自定义解决函数
        :param kwargs: 额外参数
        :return: 解决后的结果
        """
        resolved_conflicts = []
        
        for conflict in conflicts:
            resolved_value = None
            
            if strategy == 'database_wins':
                resolved_value = self._database_wins_strategy(conflict, **kwargs)
            elif strategy == 'latest_wins':
                resolved_value = self._latest_wins_strategy(conflict, **kwargs)
            elif strategy == 'custom' and custom_func:
                resolved_value = custom_func(conflict, **kwargs)
            
            if resolved_value is not None:
                resolved_conflicts.append({
                    'conflict': conflict,
                    'resolved_value': resolved_value,
                    'strategy': strategy
                })
        
        return resolved_conflicts
    
    def _database_wins_strategy(self, conflict: Dict[str, Any], **kwargs) -> Any:
        """
        以数据库为准策略
        :param conflict: 冲突信息
        :return: 解决后的值
        """
        return conflict.get('target_value', None)
    
    def _latest_wins_strategy(self, conflict: Dict[str, Any], **kwargs) -> Any:
        """
        取最新修改策略
        :param conflict: 冲突信息
        :return: 解决后的值
        """
        # 简化实现：假设源数据是最新的
        return conflict.get('source_value', None)
    
    def add_custom_strategy(self, name: str, strategy_func: Callable):
        """
        添加自定义解决策略
        :param name: 策略名称
        :param strategy_func: 策略函数
        """
        self.conflict_strategies[name] = strategy_func