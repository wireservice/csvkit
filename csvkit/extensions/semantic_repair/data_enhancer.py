# -*- coding: utf-8 -*-"""
数据增强模块
"""

from typing import Dict, Any, List

class DataEnhancer:
    """
    数据增强类
    基于现有字段关联关系自动计算并补充衍生字段
    """
    
    def __init__(self):
        self.derived_fields = []
        self.custom_formulas = []
    
    def add_derived_field(self, field_name: str, formula: str, dependencies: List[str]):
        """
        添加衍生字段
        :param field_name: 衍生字段名
        :param formula: 计算公式（字符串形式）
        :param dependencies: 依赖字段列表
        """
        self.derived_fields.append({
            'field_name': field_name,
            'formula': formula,
            'dependencies': dependencies
        })
    
    def add_custom_formula(self, formula_func):
        """
        添加自定义公式函数
        :param formula_func: 公式函数，接收行数据返回计算结果
        """
        self.custom_formulas.append(formula_func)
    
    def enhance_data(self, row: Dict[str, str]) -> Dict[str, str]:
        """
        增强行数据
        :param row: 原始行数据
        :return: 增强后的行数据
        """
        enhanced_row = row.copy()
        
        # 计算衍生字段
        for derived_field in self.derived_fields:
            field_name = derived_field['field_name']
            formula = derived_field['formula']
            dependencies = derived_field['dependencies']
            
            # 检查所有依赖字段是否存在
            has_all_deps = all(dep in row for dep in dependencies)
            if not has_all_deps:
                continue
            
            try:
                # 安全执行公式
                local_vars = {dep: row[dep] for dep in dependencies}
                # 转换为数字类型
                for dep in dependencies:
                    try:
                        local_vars[dep] = float(local_vars[dep])
                    except ValueError:
                        local_vars[dep] = 0.0
                
                result = eval(formula, {}, local_vars)
                enhanced_row[field_name] = str(result)
            except Exception as e:
                continue
        
        # 执行自定义公式
        for formula_func in self.custom_formulas:
            try:
                result = formula_func(row)
                if isinstance(result, dict):
                    enhanced_row.update(result)
            except Exception as e:
                continue
        
        return enhanced_row
    
    def auto_detect_derived_fields(self, sample_rows: List[Dict[str, str]]):
        """
        自动检测衍生字段
        :param sample_rows: 样本行数据
        """
        if not sample_rows:
            return
        
        fields = list(sample_rows[0].keys())
        
        # 自动检测常见的衍生字段关系
        for row in sample_rows:
            # 检测订单金额=数量×单价
            if '数量' in fields and '单价' in fields and '订单金额' not in fields:
                self.add_derived_field(
                    '订单金额',
                    '数量 * 单价',
                    ['数量', '单价']
                )
            
            # 检测总价=单价×数量
            if '单价' in fields and '数量' in fields and '总价' not in fields:
                self.add_derived_field(
                    '总价',
                    '单价 * 数量',
                    ['单价', '数量']
                )
            
            # 检测年龄=当前年份-出生年份
            if '出生年份' in fields and '年龄' not in fields:
                self.add_derived_field(
                    '年龄',
                    '2024 - 出生年份',
                    ['出生年份']
                )
            
            break  # 只检测一次即可