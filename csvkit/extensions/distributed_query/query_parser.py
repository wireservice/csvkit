# -*- coding: utf-8 -*-"""
查询解析模块
"""

from typing import Dict, List, Any, Tuple

class QueryParser:
    """
    类SQL查询解析器
    """
    
    def __init__(self):
        self.keywords = {
            'SELECT', 'FROM', 'WHERE', 'GROUP', 'BY', 'HAVING', 'ORDER', 'JOIN', 'ON', 'LEFT', 'RIGHT', 'INNER', 'OUTER'
        }
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """
        解析类SQL查询
        :param query: 查询字符串
        :return: 解析后的查询结构
        """
        # 简化实现：仅支持基本的SELECT查询
        query = query.strip().upper()
        
        parsed = {
            'select_fields': [],
            'from_table': '',
            'where_conditions': [],
            'group_by': [],
            'order_by': [],
            'join_clauses': []
        }
        
        # 解析SELECT部分
        if 'SELECT' in query:
            select_part = query.split('SELECT')[1]
            if 'FROM' in select_part:
                select_part = select_part.split('FROM')[0]
            fields = [f.strip() for f in select_part.split(',')]
            parsed['select_fields'] = fields
        
        # 解析FROM部分
        if 'FROM' in query:
            from_part = query.split('FROM')[1]
            if any(keyword in from_part for keyword in ['WHERE', 'GROUP', 'ORDER', 'JOIN']):
                for keyword in ['WHERE', 'GROUP', 'ORDER', 'JOIN']:
                    if keyword in from_part:
                        from_part = from_part.split(keyword)[0]
                        break
            parsed['from_table'] = from_part.strip()
        
        # 解析WHERE部分
        if 'WHERE' in query:
            where_part = query.split('WHERE')[1]
            if any(keyword in where_part for keyword in ['GROUP', 'ORDER', 'JOIN']):
                for keyword in ['GROUP', 'ORDER', 'JOIN']:
                    if keyword in where_part:
                        where_part = where_part.split(keyword)[0]
                        break
            # 简单解析条件
            conditions = [cond.strip() for cond in where_part.split('AND')]
            parsed['where_conditions'] = conditions
        
        # 解析GROUP BY部分
        if 'GROUP BY' in query:
            group_part = query.split('GROUP BY')[1]
            if 'HAVING' in group_part:
                group_part = group_part.split('HAVING')[0]
            if 'ORDER' in group_part:
                group_part = group_part.split('ORDER')[0]
            group_fields = [f.strip() for f in group_part.split(',')]
            parsed['group_by'] = group_fields
        
        # 解析ORDER BY部分
        if 'ORDER BY' in query:
            order_part = query.split('ORDER BY')[1]
            order_fields = [f.strip() for f in order_part.split(',')]
            parsed['order_by'] = order_fields
        
        return parsed
    
    def validate_query(self, parsed_query: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        验证查询的合法性
        :param parsed_query: 解析后的查询
        :param schema: 数据schema
        :return: 是否合法
        """
        # 检查SELECT字段是否存在
        for field in parsed_query.get('select_fields', []):
            if field != '*' and field not in schema.get('headers', []):
                return False
        
        # 检查WHERE条件中的字段是否存在
        for condition in parsed_query.get('where_conditions', []):
            if '=' in condition or '>' in condition or '<' in condition:
                # 简单解析字段名
                if '=' in condition:
                    field = condition.split('=')[0].strip()
                elif '>' in condition:
                    field = condition.split('>')[0].strip()
                elif '<' in condition:
                    field = condition.split('<')[0].strip()
                else:
                    continue
                
                if field not in schema.get('headers', []):
                    return False
        
        return True