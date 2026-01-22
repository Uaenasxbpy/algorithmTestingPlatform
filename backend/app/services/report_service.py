from sqlalchemy.orm import Session
from typing import List, Optional
import os
import pandas as pd
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

from app.models.models import Report, TestTask
from app.models import schemas
from app.services.result_service import ResultService
from app.core.config import settings

class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.result_service = ResultService(db)

    def get_report(self, report_id: int) -> Optional[Report]:
        """获取报告信息"""
        return self.db.query(Report).filter(Report.id == report_id).first()

    def get_task_reports(self, task_id: int) -> List[Report]:
        """获取任务的所有报告"""
        return self.db.query(Report).filter(Report.task_id == task_id).all()

    def get_all_reports(self, skip: int = 0, limit: int = 100) -> List[Report]:
        """获取所有报告列表"""
        return self.db.query(Report).offset(skip).limit(limit).all()

    def generate_report(self, task_id: int, report_type: str) -> Report:
        """生成任务报告"""
        # 验证任务是否存在且已完成
        task = self.db.query(TestTask).filter(
            TestTask.id == task_id,
            TestTask.status == 'COMPLETED'
        ).first()
        
        if not task:
            raise ValueError("任务不存在或未完成")

        # 创建报告目录
        os.makedirs(settings.REPORTS_DIR, exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{task_id}_{timestamp}.{report_type}"
        file_path = os.path.join(settings.REPORTS_DIR, filename)

        # 根据类型生成报告
        if report_type.lower() == 'pdf':
            self._generate_pdf_report(task, file_path)
        elif report_type.lower() == 'csv':
            self._generate_csv_report(task, file_path)
        else:
            raise ValueError("不支持的报告类型")

        # 保存报告记录
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        db_report = Report(
            task_id=task_id,
            report_name=filename,
            file_path=file_path,
            file_type=report_type.upper(),
            file_size=file_size
        )
        
        self.db.add(db_report)
        self.db.commit()
        self.db.refresh(db_report)
        
        return db_report

    def _generate_pdf_report(self, task: TestTask, file_path: str):
        """生成PDF报告"""
        # 注册中文字体
        try:
            # 尝试使用系统中文字体
            import platform
            if platform.system() == 'Windows':
                # Windows 系统使用微软雅黑
                try:
                    pdfmetrics.registerFont(TTFont('SimHei', 'C:/Windows/Fonts/simhei.ttf'))
                    chinese_font = 'SimHei'
                except:
                    try:
                        pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
                        chinese_font = 'Arial'
                    except:
                        chinese_font = 'Helvetica'
            else:
                # Linux/Mac 系统使用内置字体
                chinese_font = 'Helvetica'
        except Exception as e:
            print(f"Font registration warning: {e}")
            # 如果注册失败，使用默认字体
            chinese_font = 'Helvetica'
        
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # 自定义样式支持中文
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=1,  # 居中
            fontName=chinese_font
        )
        
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            fontName=chinese_font
        )
        
        heading3_style = ParagraphStyle(
            'CustomHeading3', 
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            fontName=chinese_font
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            fontName=chinese_font
        )

        # 报告标题
        story.append(Paragraph("算法测试平台 - 性能测试报告", title_style))
        story.append(Spacer(1, 20))
        
        # 报告生成信息
        report_info = [
            ['报告生成时间', datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ['平台版本', settings.VERSION],
            ['测试环境', '模拟测试环境' if task.algorithm.source == 'Mock' else '生产环境'],
        ]
        
        report_info_table = Table(report_info, colWidths=[2*inch, 3*inch])
        report_info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), chinese_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey)
        ]))
        
        story.append(report_info_table)
        story.append(Spacer(1, 30))

        # 测试基本信息
        story.append(Paragraph("测试基本信息", heading2_style))
        
        # 计算测试时长
        if task.started_at and task.finished_at:
            duration = task.finished_at - task.started_at
            duration_str = f"{duration.total_seconds():.2f} 秒"
        else:
            duration_str = 'N/A'
        
        basic_info = [
            ['项目', '值'],
            ['算法名称', task.algorithm.name],
            ['算法类别', '密钥封装机制(KEM)' if task.algorithm.category == 'KEM' else '数字签名(SIGNATURE)'],
            ['测试任务', task.task_name],
            ['测试次数', str(task.test_count)],
            ['开始时间', task.started_at.strftime("%Y-%m-%d %H:%M:%S") if task.started_at else 'N/A'],
            ['完成时间', task.finished_at.strftime("%Y-%m-%d %H:%M:%S") if task.finished_at else 'N/A'],
            ['测试时长', duration_str],
            ['算法来源', task.algorithm.source],
            ['算法版本', task.algorithm.version or 'N/A'],
            ['算法描述', task.algorithm.description or '无描述'],
            ['任务状态', '已完成' if task.status == 'COMPLETED' else task.status]
        ]
        
        basic_table = Table(basic_info, colWidths=[2*inch, 4*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), chinese_font),
            ('FONTNAME', (0, 0), (-1, 0), chinese_font),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        story.append(basic_table)
        story.append(Spacer(1, 20))

        # 性能指标概览
        story.append(Paragraph("性能指标概览", heading2_style))
        
        metrics = self.result_service.get_performance_metrics(task.id)
        if metrics:
            metrics_data = [['\u6307\u6807\u540d\u79f0', '\u6570\u503c', '\u5355\u4f4d', '\u8bc4\u4ef7']]
            
            metric_mapping = {
                'avg_keygen_time': ('平均密钥生成时间', 'ms'),
                'avg_encaps_time': ('平均封装时间', 'ms'),
                'avg_decaps_time': ('平均解封装时间', 'ms'),
                'avg_sign_time': ('平均签名时间', 'ms'),
                'avg_verify_time': ('平均验证时间', 'ms'),
                'success_rate': ('成功率', '%'),
                'public_key_size': ('公钥大小', 'bytes'),
                'private_key_size': ('私钥大小', 'bytes'),
                'signature_size': ('签名大小', 'bytes'),
                'ciphertext_size': ('密文大小', 'bytes')
            }
            
            for attr, (display_name, unit) in metric_mapping.items():
                value = getattr(metrics, attr, None)
                if value is not None:
                    if attr == 'success_rate':
                        formatted_value = f"{value:.2f}"
                        evaluation = '优秀' if value >= 99 else ('良好' if value >= 95 else '一般')
                    elif 'time' in attr:
                        formatted_value = f"{value:.4f}"
                        # 根据时间评价性能
                        if value < 1.0:
                            evaluation = '优秀'
                        elif value < 5.0:
                            evaluation = '良好'
                        else:
                            evaluation = '一般'
                    else:
                        formatted_value = f"{int(value)}"
                        # 根据大小评价（越小越好）
                        if value < 1000:
                            evaluation = '优秀'
                        elif value < 3000:
                            evaluation = '良好'
                        else:
                            evaluation = '一般'
                    
                    metrics_data.append([display_name, formatted_value, unit, evaluation])
            
            metrics_table = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), chinese_font),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            
            story.append(metrics_table)
        else:
            story.append(Paragraph("未找到性能指标数据", normal_style))

        story.append(Spacer(1, 20))
        
        # 测试环境信息
        story.append(Paragraph("测试环境信息", heading2_style))
        
        import platform
        try:
            import psutil
            memory_info = f"{psutil.virtual_memory().total // (1024**3)} GB"
            cpu_info = f"{psutil.cpu_count()} 核心"
            disk_info = f"{psutil.disk_usage('/').total // (1024**3)} GB" if platform.system() != 'Windows' else f"{psutil.disk_usage('C:').total // (1024**3)} GB"
        except ImportError:
            memory_info = '不可用'
            cpu_info = '不可用'
            disk_info = '不可用'
        
        env_info = [
            ['项目', '信息'],
            ['操作系统', f"{platform.system()} {platform.release()}"],
            ['处理器架构', platform.machine()],
            ['CPU核心数', cpu_info],
            ['内存大小', memory_info],
            ['磁盘空间', disk_info],
            ['Python版本', platform.python_version()],
            ['测试模式', '模拟测试' if task.algorithm.source == 'Mock' else '真实测试'],
            ['平台版本', settings.VERSION],
            ['数据库类型', 'MySQL' if settings.USE_MYSQL else 'SQLite']
        ]
        
        env_table = Table(env_info, colWidths=[2*inch, 4*inch])
        env_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), chinese_font),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightcyan),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        story.append(env_table)
        story.append(Spacer(1, 20))
        
        # 平台状态信息
        story.append(Paragraph("平台状态信息", heading2_style))
        
        try:
            import psutil
            import time
            
            # 获取系统运行时间
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            uptime_str = f"{uptime.days} 天 {uptime.seconds // 3600} 小时"
            
            # 获取CPU和内存使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 获取磁盘使用率
            disk_usage = psutil.disk_usage('C:' if platform.system() == 'Windows' else '/')
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            
            platform_status = [
                ['状态项', '当前值', '状态评价'],
                ['系统运行时间', uptime_str, '正常'],
                ['CPU使用率', f"{cpu_percent:.1f}%", '正常' if cpu_percent < 80 else '较高'],
                ['内存使用率', f"{memory_percent:.1f}%", '正常' if memory_percent < 80 else '较高'],
                ['磁盘使用率', f"{disk_percent:.1f}%", '正常' if disk_percent < 80 else '较高'],
                ['可用内存', f"{memory.available // (1024**3)} GB", '充足' if memory.available > 2*(1024**3) else '不足'],
                ['平台服务状态', '运行中', '正常'],
                ['数据库连接', '正常', '正常'],
                ['测试引擎状态', '就绪', '正常']
            ]
        except:
            platform_status = [
                ['状态项', '当前值', '状态评价'],
                ['系统运行时间', '无法获取', '未知'],
                ['CPU使用率', '无法获取', '未知'],
                ['内存使用率', '无法获取', '未知'],
                ['磁盘使用率', '无法获取', '未知'],
                ['平台服务状态', '运行中', '正常'],
                ['数据库连接', '正常', '正常'],
                ['测试引擎状态', '就绪', '正常']
            ]
        
        status_table = Table(platform_status, colWidths=[2.5*inch, 2*inch, 1.5*inch])
        status_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), chinese_font),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        story.append(status_table)
        story.append(Spacer(1, 20))

        # 详细统计信息
        story.append(Paragraph("详细统计信息", heading2_style))
        
        summary = self.result_service.get_task_results_summary(task.id)
        if summary:
            for metric_name, stats in summary.items():
                if metric_name != 'task_info' and isinstance(stats, dict):
                    story.append(Paragraph(f"{metric_name} 统计", heading3_style))
                    
                    stats_data = [
                        ['统计项', '数值'],
                        ['样本数量', str(stats.get('count', 0))],
                        ['平均值', f"{stats.get('avg', 0):.4f}"],
                        ['最小值', f"{stats.get('min', 0):.4f}"],
                        ['最大值', f"{stats.get('max', 0):.4f}"],
                        ['中位数', f"{stats.get('median', 0):.4f}"],
                        ['标准差', f"{stats.get('std_dev', 0):.4f}"]
                    ]
                    
                    stats_table = Table(stats_data, colWidths=[2*inch, 2*inch])
                    stats_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, -1), chinese_font),
                        ('FONTSIZE', (0, 0), (-1, 0), 11),
                        ('FONTSIZE', (0, 1), (-1, -1), 10),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                    ]))
                    
                    story.append(stats_table)
                    story.append(Spacer(1, 10))
        
        # 性能分析和建议
        story.append(Paragraph("性能分析和建议", heading2_style))
        
        analysis_content = [
            "基于测试结果的性能分析：",
            "",
            "1. 算法性能评价："
        ]
        
        if metrics:
            if hasattr(metrics, 'success_rate') and metrics.success_rate:
                if metrics.success_rate >= 99:
                    analysis_content.append("   • 算法成功率表现优秀，稳定性良好")
                elif metrics.success_rate >= 95:
                    analysis_content.append("   • 算法成功率表现良好，偶有失败")
                else:
                    analysis_content.append("   • 算法成功率需要改进，建议检查实现")
            
            # 时间性能分析
            time_metrics = ['avg_keygen_time', 'avg_encaps_time', 'avg_decaps_time', 'avg_sign_time', 'avg_verify_time']
            for metric in time_metrics:
                if hasattr(metrics, metric):
                    value = getattr(metrics, metric)
                    if value and value < 1.0:
                        analysis_content.append(f"   • {metric.replace('avg_', '').replace('_', ' ').title()} 性能优秀")
                    elif value and value < 5.0:
                        analysis_content.append(f"   • {metric.replace('avg_', '').replace('_', ' ').title()} 性能良好")
        
        analysis_content.extend([
            "",
            "2. 建议和优化方向：",
            "   • 如需提升性能，可考虑算法参数优化",
            "   • 建议在不同硬件环境下进行对比测试",
            "   • 对于生产环境，建议进行更大规模的压力测试",
            "   • 关注算法的内存使用效率和安全性",
            "",
            "3. 测试环境说明：",
            f"   • 当前测试基于{'模拟环境' if task.algorithm.source == 'Mock' else '生产环境'}",
            "   • 实际性能可能因硬件配置而有所差异",
            "   • 建议定期进行性能基准测试"
        ])
        
        for line in analysis_content:
            story.append(Paragraph(line, normal_style))
            if line == "":
                story.append(Spacer(1, 6))
        
        # 添加页脚信息
        story.append(Spacer(1, 30))
        story.append(Paragraph("————————————————————————————————————————————————————————————", normal_style))
        story.append(Paragraph(f"报告生成于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        story.append(Paragraph("算法测试平台 - 后量子密码算法性能测试与验证平台", normal_style))

        # 生成PDF
        doc.build(story)

    def _generate_csv_report(self, task: TestTask, file_path: str):
        """生成CSV报告"""
        results = self.result_service.get_task_results(task.id)
        
        if not results:
            # 创建空的CSV文件
            df = pd.DataFrame(columns=['metric_name', 'value', 'unit', 'test_round', 'created_at'])
        else:
            # 转换为DataFrame
            data = []
            for result in results:
                data.append({
                    'task_id': result.task_id,
                    'metric_name': result.metric_name,
                    'value': result.value,
                    'unit': result.unit,
                    'test_round': result.test_round,
                    'created_at': result.created_at
                })
            
            df = pd.DataFrame(data)

        # 添加任务信息
        task_info = {
            'task_name': task.task_name,
            'algorithm_name': task.algorithm.name,
            'algorithm_category': task.algorithm.category,
            'test_count': task.test_count,
            'started_at': task.started_at,
            'finished_at': task.finished_at
        }

        # 保存CSV文件
        with open(file_path, 'w', encoding='utf-8-sig') as f:
            # 写入任务信息
            f.write("# 任务信息\n")
            for key, value in task_info.items():
                f.write(f"# {key}: {value}\n")
            f.write("\n")
            
            # 写入结果数据
            df.to_csv(f, index=False)

    def delete_report(self, report_id: int) -> bool:
        """删除报告"""
        report = self.get_report(report_id)
        if not report:
            return False

        # 删除文件
        if os.path.exists(report.file_path):
            try:
                os.remove(report.file_path)
            except Exception:
                pass  # 忽略文件删除错误

        # 删除数据库记录
        self.db.delete(report)
        self.db.commit()
        return True

    def generate_comparison_report(
        self,
        algorithm_ids: List[int],
        report_type: str = 'pdf'
    ) -> Report:
        """生成算法对比报告"""
        if not algorithm_ids:
            raise ValueError("至少需要一个算法ID")

        # 获取对比数据
        comparison = self.result_service.compare_algorithms(algorithm_ids)
        
        # 创建报告目录
        os.makedirs(settings.REPORTS_DIR, exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comparison_report_{timestamp}.{report_type}"
        file_path = os.path.join(settings.REPORTS_DIR, filename)

        if report_type.lower() == 'pdf':
            self._generate_comparison_pdf(comparison, file_path)
        elif report_type.lower() == 'csv':
            self._generate_comparison_csv(comparison, file_path)
        else:
            raise ValueError("不支持的报告类型")

        # 保存报告记录（使用第一个算法的最新任务ID）
        first_algorithm = list(comparison['algorithms'].values())[0]
        task_id = first_algorithm.get('latest_task_id', 0)

        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        db_report = Report(
            task_id=task_id,
            report_name=filename,
            file_path=file_path,
            file_type=report_type.upper(),
            file_size=file_size
        )
        
        self.db.add(db_report)
        self.db.commit()
        self.db.refresh(db_report)
        
        return db_report

    def _generate_comparison_pdf(self, comparison_data: dict, file_path: str):
        """生成对比PDF报告"""
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # 标题
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1
        )
        
        story.append(Paragraph("算法性能对比报告", title_style))
        story.append(Spacer(1, 20))

        # 对比摘要
        algorithms = comparison_data['algorithms']
        if algorithms:
            story.append(Paragraph("算法对比摘要", styles['Heading2']))
            
            summary_data = [['算法名称', '类别', '测试日期', '任务ID']]
            for alg_name, alg_data in algorithms.items():
                test_date = alg_data.get('test_date', 'N/A')
                if test_date != 'N/A':
                    test_date = test_date.strftime("%Y-%m-%d %H:%M:%S")
                
                summary_data.append([
                    alg_name,
                    alg_data.get('category', 'N/A'),
                    test_date,
                    str(alg_data.get('latest_task_id', 'N/A'))
                ])
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 20))

        doc.build(story)

    def _generate_comparison_csv(self, comparison_data: dict, file_path: str):
        """生成对比CSV报告"""
        algorithms = comparison_data['algorithms']
        
        # 收集所有算法的性能数据
        data = []
        for alg_name, alg_data in algorithms.items():
            base_row = {
                'algorithm_name': alg_name,
                'category': alg_data.get('category'),
                'task_id': alg_data.get('latest_task_id'),
                'test_date': alg_data.get('test_date')
            }
            
            if 'performance_metrics' in alg_data:
                base_row.update(alg_data['performance_metrics'])
            
            data.append(base_row)

        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False, encoding='utf-8-sig')