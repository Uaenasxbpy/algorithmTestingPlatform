from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models import schemas
from app.services.report_service import ReportService
import os

router = APIRouter()

@router.get("/task/{task_id}", response_model=List[schemas.Report])
async def get_task_reports(
    task_id: int,
    db: Session = Depends(get_db)
):
    """获取任务的所有报告"""
    service = ReportService(db)
    reports = service.get_task_reports(task_id)
    return reports

@router.post("/task/{task_id}/generate", response_model=schemas.Report)
async def generate_report(
    task_id: int,
    report_type: str = "pdf",  # pdf 或 csv
    db: Session = Depends(get_db)
):
    """生成任务报告"""
    if report_type not in ["pdf", "csv"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="报告类型只能是 pdf 或 csv"
        )
    
    service = ReportService(db)
    try:
        report = service.generate_report(task_id, report_type)
        return report
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成报告失败: {str(e)}"
        )

@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """下载报告文件"""
    service = ReportService(db)
    report = service.get_report(report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在"
        )
    
    if not os.path.exists(report.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告文件不存在"
        )
    
    return FileResponse(
        path=report.file_path,
        filename=report.report_name,
        media_type='application/octet-stream'
    )

@router.get("/{report_id}/preview")
async def preview_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """预览报告文件（在浏览器中打开）"""
    service = ReportService(db)
    report = service.get_report(report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在"
        )
    
    if not os.path.exists(report.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告文件不存在"
        )
    
    # 根据文件类型返回不同MIME类型
    if report.file_type.upper() == 'PDF':
        media_type = 'application/pdf'
    elif report.file_type.upper() == 'CSV':
        media_type = 'text/csv'
    else:
        media_type = 'application/octet-stream'
    
    # 为PDF预览设置正确的响应头
    headers = {
        "Content-Disposition": f"inline; filename={report.report_name}",
        "Cache-Control": "no-cache",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Headers": "*"
    }
    
    return FileResponse(
        path=report.file_path,
        media_type=media_type,
        headers=headers
    )

@router.delete("/{report_id}", response_model=schemas.MessageResponse)
async def delete_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """删除报告"""
    service = ReportService(db)
    success = service.delete_report(report_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在"
        )
    return schemas.MessageResponse(message="报告删除成功")

@router.post("/batch-generate", response_model=List[schemas.Report])
async def batch_generate_reports(
    task_ids: List[int],
    report_type: str = "pdf",
    db: Session = Depends(get_db)
):
    """批量生成报告"""
    if report_type not in ["pdf", "csv"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="报告类型只能是 pdf 或 csv"
        )
    
    service = ReportService(db)
    reports = []
    errors = []
    
    for task_id in task_ids:
        try:
            report = service.generate_report(task_id, report_type)
            reports.append(report)
        except Exception as e:
            errors.append(f"任务 {task_id}: {str(e)}")
    
    if errors and not reports:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"所有报告生成失败: {'; '.join(errors)}"
        )
    
    return reports

@router.get("/", response_model=List[schemas.Report])
async def get_all_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取所有报告列表"""
    service = ReportService(db)
    reports = service.get_all_reports(skip, limit)
    return reports