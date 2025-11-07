# -*- coding: utf-8 -*-"""
语义修复引擎主模块
"""

import csv
from typing import List, Dict, Any, Tuple

from .knowledge_base import KnowledgeBase
from .error_detector import SemanticErrorDetector
from .repair_strategy import RepairStrategyGenerator
from .data_enhancer import DataEnhancer

class SemanticRepairEngine:
    """
    基于语义理解的CSV数据修复与增强引擎
    """
    
    def __init__(self):
        self.kb = KnowledgeBase()
        self.detector = SemanticErrorDetector(self.kb)
        self.repairer = RepairStrategyGenerator(self.kb)
        self.enhancer = DataEnhancer()
        self.repair_history = []
    
    def load_knowledge(self, file_path: str, knowledge_type: str = 'data_dict') -> bool:
        """
        加载领域知识
        :param file_path: 知识文件路径
        :param knowledge_type: 知识类型 (data_dict, terminology, owl)
        :return: 是否加载成功
        """
        if knowledge_type == 'data_dict':
            return self.kb.load_data_dictionary(file_path)
        elif knowledge_type == 'terminology':
            return self.kb.load_terminology(file_path)
        elif knowledge_type == 'owl':
            return self.kb.load_owl_ontology(file_path)
        return False
    
    def detect_errors(self, csv_path: str, encoding: str = 'utf-8') -> List[Dict[str, Any]]:
        """
        检测CSV文件中的语义错误
        :param csv_path: CSV文件路径
        :param encoding: 文件编码
        :return: 错误列表
        """
        errors = []
        
        with open(csv_path, 'r', encoding=encoding) as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            for row_index, row in enumerate(reader):
                row_errors = self.detector.detect_all_errors(row, row_index + 1)
                errors.extend(row_errors)
        
        return errors
    
    def generate_repair_report(self, errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成修复报告
        :param errors: 错误列表
        :return: 修复报告
        """
        report = {
            'total_errors': len(errors),
            'error_distribution': {},
            'repair_candidates': []
        }
        
        # 统计错误分布
        for error in errors:
            error_type = error.get('error_type', 'unknown')
            report['error_distribution'][error_type] = report['error_distribution'].get(error_type, 0) + 1
        
        # 生成修复候选
        for error in errors:
            candidates = self.repairer.generate_repair_candidates(error)
            if candidates:
                report['repair_candidates'].append({
                    'error': error,
                    'candidates': candidates
                })
        
        return report
    
    def repair_csv(self, input_path: str, output_path: str, encoding: str = 'utf-8', 
                  auto_apply: bool = True, confidence_threshold: float = 0.7) -> Dict[str, Any]:
        """
        修复CSV文件
        :param input_path: 输入CSV路径
        :param output_path: 输出CSV路径
        :param encoding: 文件编码
        :param auto_apply: 是否自动应用修复
        :param confidence_threshold: 修复置信度阈值
        :return: 修复结果统计
        """
        stats = {
            'total_rows': 0,
            'fixed_rows': 0,
            'total_errors': 0,
            'fixed_errors': 0,
            'enhanced_fields': 0
        }
        
        with open(input_path, 'r', encoding=encoding) as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames.copy()
            
            # 自动检测衍生字段
            sample_rows = [row for row in reader][:10]
            self.enhancer.auto_detect_derived_fields(sample_rows)
            
            # 添加衍生字段到表头
            for derived_field in self.enhancer.derived_fields:
                if derived_field['field_name'] not in headers:
                    headers.append(derived_field['field_name'])
                    stats['enhanced_fields'] += 1
        
        with open(input_path, 'r', encoding=encoding) as f_in:
            reader = csv.DictReader(f_in)
            
            with open(output_path, 'w', encoding=encoding, newline='') as f_out:
                writer = csv.DictWriter(f_out, fieldnames=headers)
                writer.writeheader()
                
                for row_index, row in enumerate(reader):
                    stats['total_rows'] += 1
                    
                    # 检测错误
                    errors = self.detector.detect_all_errors(row, row_index + 1)
                    stats['total_errors'] += len(errors)
                    
                    # 修复错误
                    fixed_row = row.copy()
                    fixed_errors = 0
                    
                    for error in errors:
                        candidates = self.repairer.generate_repair_candidates(error)
                        
                        # 选择置信度最高的修复
                        best_candidate = None
                        for candidate in candidates:
                            if candidate['confidence'] >= confidence_threshold:
                                if not best_candidate or candidate['confidence'] > best_candidate['confidence']:
                                    best_candidate = candidate
                        
                        if best_candidate and auto_apply:
                            field = error.get('field', '')
                            if isinstance(field, list):
                                # 逻辑冲突修复（简化处理）
                                continue
                            fixed_row[field] = best_candidate['repair_value']
                            fixed_errors += 1
                    
                    if fixed_errors > 0:
                        stats['fixed_rows'] += 1
                        stats['fixed_errors'] += fixed_errors
                    
                    # 数据增强
                    enhanced_row = self.enhancer.enhance_data(fixed_row)
                    
                    # 写入修复后的数据
                    writer.writerow(enhanced_row)
                    
                    # 记录修复历史
                    self.repair_history.append({
                        'row_index': row_index + 1,
                        'original_row': row,
                        'fixed_row': fixed_row,
                        'enhanced_row': enhanced_row,
                        'errors': errors
                    })
        
        return stats
    
    def get_repair_history(self) -> List[Dict[str, Any]]:
        """
        获取修复历史
        :return: 修复历史列表
        """
        return self.repair_history
    
    def save_repair_history(self, file_path: str) -> bool:
        """
        保存修复历史
        :param file_path: 保存路径
        :return: 是否保存成功
        """
        import json
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.repair_history, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存修复历史失败: {str(e)}")
            return False
    
    def add_custom_derived_field(self, field_name: str, formula: str, dependencies: List[str]):
        """
        添加自定义衍生字段
        :param field_name: 衍生字段名
        :param formula: 计算公式
        :param dependencies: 依赖字段列表
        """
        self.enhancer.add_derived_field(field_name, formula, dependencies)
    
    def add_custom_formula(self, formula_func):
        """
        添加自定义公式函数
        :param formula_func: 公式函数
        """
        self.enhancer.add_custom_formula(formula_func)