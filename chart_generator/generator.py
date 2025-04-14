#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图表生成器模块 - 用于从Excel或其他结构化数据生成各种图表
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Union, List, Dict, Any, Optional


class ChartGenerator:
    """
    图表生成器类，支持从结构化数据生成多种图表格式
    """
    
    def __init__(self, data_source: Union[str, pd.DataFrame] = None):
        """
        初始化图表生成器
        
        参数:
            data_source: 数据源，可以是DataFrame对象或Excel/CSV文件路径
        """
        self.data = None
        if data_source is not None:
            self.load_data(data_source)
            
    def load_data(self, data_source: Union[str, pd.DataFrame]) -> None:
        """
        加载数据
        
        参数:
            data_source: 数据源，可以是DataFrame对象或Excel/CSV文件路径
        """
        if isinstance(data_source, pd.DataFrame):
            self.data = data_source
        elif isinstance(data_source, str):
            file_path = Path(data_source)
            if file_path.exists():
                if file_path.suffix.lower() == '.csv':
                    self.data = pd.read_csv(file_path)
                elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                    self.data = pd.read_excel(file_path)
                else:
                    raise ValueError(f"不支持的文件类型: {file_path.suffix}")
            else:
                raise FileNotFoundError(f"找不到文件: {data_source}")
        else:
            raise TypeError("数据源必须是DataFrame对象或文件路径字符串")
    
    def create_bar_chart(self, x_column: str, y_column: str, title: str = "柱状图", 
                         save_path: Optional[str] = None, figsize: tuple = (10, 6)) -> None:
        """
        创建柱状图
        
        参数:
            x_column: X轴列名
            y_column: Y轴列名
            title: 图表标题
            save_path: 保存路径，如不提供则显示图表
            figsize: 图表尺寸
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        plt.figure(figsize=figsize)
        plt.bar(self.data[x_column], self.data[y_column])
        plt.title(title)
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()
    
    def create_line_chart(self, x_column: str, y_columns: Union[str, List[str]], 
                          title: str = "折线图", save_path: Optional[str] = None,
                          figsize: tuple = (10, 6)) -> None:
        """
        创建折线图
        
        参数:
            x_column: X轴列名
            y_columns: Y轴列名，可以是单个列名或列名列表（多条线）
            title: 图表标题
            save_path: 保存路径，如不提供则显示图表
            figsize: 图表尺寸
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        plt.figure(figsize=figsize)
        
        if isinstance(y_columns, str):
            y_columns = [y_columns]
            
        for column in y_columns:
            plt.plot(self.data[x_column], self.data[column], label=column)
            
        plt.title(title)
        plt.xlabel(x_column)
        plt.ylabel("值")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()
    
    def create_pie_chart(self, labels_column: str, values_column: str, title: str = "饼图",
                         save_path: Optional[str] = None, figsize: tuple = (10, 8)) -> None:
        """
        创建饼图
        
        参数:
            labels_column: 标签列名
            values_column: 值列名
            title: 图表标题
            save_path: 保存路径，如不提供则显示图表
            figsize: 图表尺寸
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        plt.figure(figsize=figsize)
        plt.pie(self.data[values_column], labels=self.data[labels_column], autopct='%1.1f%%')
        plt.title(title)
        plt.axis('equal')
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()
    
    def create_heatmap(self, title: str = "热力图", save_path: Optional[str] = None,
                       figsize: tuple = (12, 10), cmap: str = "viridis") -> None:
        """
        创建热力图 (需要数值型数据)
        
        参数:
            title: 图表标题
            save_path: 保存路径，如不提供则显示图表
            figsize: 图表尺寸
            cmap: 颜色映射
        """
        if self.data is None:
            raise ValueError("请先加载数据")
        
        # 只选择数值列
        numeric_data = self.data.select_dtypes(include=['number'])
        
        if numeric_data.empty:
            raise ValueError("数据中没有数值列，无法创建热力图")
            
        plt.figure(figsize=figsize)
        sns.heatmap(numeric_data.corr(), annot=True, cmap=cmap)
        plt.title(title)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()


# 示例用法
if __name__ == "__main__":
    # 创建示例数据
    data = {
        "月份": ["一月", "二月", "三月", "四月", "五月", "六月"],
        "销售量": [100, 150, 130, 200, 180, 250],
        "利润": [50, 80, 70, 110, 90, 130]
    }
    df = pd.DataFrame(data)
    
    # 初始化图表生成器
    chart_gen = ChartGenerator(df)
    
    # 生成柱状图
    chart_gen.create_bar_chart("月份", "销售量", "月度销售量柱状图")
    
    # 生成折线图
    chart_gen.create_line_chart("月份", ["销售量", "利润"], "月度销售与利润趋势")
    
    # 生成饼图
    chart_gen.create_pie_chart("月份", "销售量", "销售量占比")
