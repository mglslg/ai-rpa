#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图表生成器示例 - 展示如何使用ChartGenerator类
"""

import pandas as pd
import os
from generator import ChartGenerator
import matplotlib.pyplot as plt
import matplotlib as mpl


def example_with_dataframe():
    """使用DataFrame创建图表示例"""
    print("示例1: 使用DataFrame创建图表")

    # 创建示例数据
    data = {
        "季度": ["Q1", "Q2", "Q3", "Q4"],
        "收入": [1200, 1800, 1600, 2100],
        "支出": [800, 1100, 900, 1300],
        "利润": [400, 700, 700, 800]
    }
    df = pd.DataFrame(data)

    # 初始化图表生成器
    chart_gen = ChartGenerator(df)

    # 输出目录
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    # 生成柱状图
    chart_gen.create_bar_chart(
        x_column="季度",
        y_column="收入",
        title="季度收入柱状图",
        save_path=f"{output_dir}/quarterly_revenue_bar.png"
    )
    print(f"- 已保存柱状图到 {output_dir}/quarterly_revenue_bar.png")

    # 生成折线图
    chart_gen.create_line_chart(
        x_column="季度",
        y_columns=["收入", "支出", "利润"],
        title="季度财务趋势",
        save_path=f"{output_dir}/quarterly_finances_line.png"
    )
    print(f"- 已保存折线图到 {output_dir}/quarterly_finances_line.png")

    # 生成饼图
    chart_gen.create_pie_chart(
        labels_column="季度",
        values_column="利润",
        title="季度利润分布",
        save_path=f"{output_dir}/quarterly_profit_pie.png"
    )
    print(f"- 已保存饼图到 {output_dir}/quarterly_profit_pie.png")

    # 生成热力图
    chart_gen.create_heatmap(
        title="财务数据相关性",
        save_path=f"{output_dir}/financial_correlation_heatmap.png"
    )
    print(f"- 已保存热力图到 {output_dir}/financial_correlation_heatmap.png")


def example_with_excel():
    """使用Excel文件创建图表示例"""
    print("\n示例2: 使用Excel文件创建图表")

    # 创建示例Excel文件
    data = {
        "产品": ["A产品", "B产品", "C产品", "D产品", "E产品"],
        "销量": [120, 85, 200, 150, 175],
        "评分": [4.5, 4.0, 4.8, 3.9, 4.2]
    }
    df = pd.DataFrame(data)

    # 输出目录
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    # 保存Excel文件
    excel_path = f"{output_dir}/product_data.xlsx"
    df.to_excel(excel_path, index=False)
    print(f"- 已创建示例Excel文件: {excel_path}")

    # 使用Excel文件初始化图表生成器
    chart_gen = ChartGenerator(excel_path)

    # 生成柱状图
    chart_gen.create_bar_chart(
        x_column="产品",
        y_column="销量",
        title="产品销量对比",
        save_path=f"{output_dir}/product_sales_bar.png"
    )
    print(f"- 已保存柱状图到 {output_dir}/product_sales_bar.png")

    # 生成折线图
    chart_gen.create_line_chart(
        x_column="产品",
        y_columns=["销量", "评分"],
        title="产品销量与评分",
        save_path=f"{output_dir}/product_metrics_line.png"
    )
    print(f"- 已保存折线图到 {output_dir}/product_metrics_line.png")


def example_credit_card_decline():
    """生成信用卡消费额下降比率柱状图示例"""
    print("\n示例3: 生成信用卡消费额下降比率柱状图")
    
    # 配置中文字体支持
    # 方法1: 使用系统自带的中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans', 'Bitstream Vera Sans', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号
    
    # 方法2: 如果方法1不起作用，可以尝试使用fonttools找到系统中的中文字体
    # 取消注释以下代码块:
    """
    from matplotlib.font_manager import FontManager
    import subprocess
    
    fm = FontManager()
    mat_fonts = set(f.name for f in fm.ttflist)
    print('可用的中文字体:')
    for f in sorted(mat_fonts):
        print(f)
    """

    # 创建银行信用卡消费额下降比率数据
    data = {
        "银行": ["工商银行", "建设银行", "中国银行", "交通银行", "平安银行"],
        "消费额下降比率(%)": [4.91, 4.44, 7.66, 12.00, 16.57]
    }
    df = pd.DataFrame(data)

    # 输出目录
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    # 初始化图表生成器
    chart_gen = ChartGenerator(df)

    # 由于ChartGenerator类没有提供在柱状图上直接添加数值标签的选项
    # 我们需要自定义创建图表并添加数值标签
    
    # 创建图表和轴
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 获取数据
    banks = df["银行"]
    decline_rates = df["消费额下降比例(%)"]
    
    # 绘制柱状图
    bars = ax.bar(banks, decline_rates)
    
    # 设置标题和轴标签
    ax.set_title("2024年各大银行信用卡消费额较上一年下降比例")
    ax.set_xlabel("银行")
    ax.set_ylabel("消费额下降比例(%)")
    
    # 在每个柱子上方添加百分比数值标签
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                f'{height:.2f}%',
                ha='center', va='bottom', fontsize=10)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图表
    save_path = f"{output_dir}/credit_card_decline_ratio1.png"
    plt.savefig(save_path)
    plt.close()
    
    print(f"- 已保存柱状图到 {save_path}")


if __name__ == "__main__":
    # example_with_dataframe()
    # example_with_excel()
    example_credit_card_decline()
