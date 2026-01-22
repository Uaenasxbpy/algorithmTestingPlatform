#!/usr/bin/env python3
"""
测试报告生成功能
"""
import requests
import json

def test_report_generation():
    base_url = "http://localhost:8000/api/v1"
    
    try:
        # 1. 获取任务列表
        print("1. 获取任务列表...")
        response = requests.get(f"{base_url}/tasks")
        if response.status_code == 200:
            tasks = response.json()
            print(f"找到 {len(tasks)} 个任务")
            
            # 找到已完成的任务
            completed_tasks = [task for task in tasks if task['status'] == 'COMPLETED']
            if completed_tasks:
                task = completed_tasks[0]
                task_id = task['id']
                print(f"使用任务 ID: {task_id}, 名称: {task['task_name']}")
                
                # 2. 生成PDF报告
                print("2. 生成PDF报告...")
                response = requests.post(f"{base_url}/reports/task/{task_id}/generate", 
                                       params={"report_type": "pdf"})
                if response.status_code == 200:
                    report = response.json()
                    report_id = report['id']
                    print(f"报告生成成功! 报告ID: {report_id}")
                    
                    # 3. 测试预览功能
                    print("3. 测试预览功能...")
                    preview_response = requests.get(f"{base_url}/reports/{report_id}/preview")
                    print(f"预览响应状态: {preview_response.status_code}")
                    print(f"预览响应头: {dict(preview_response.headers)}")
                    
                    # 4. 测试下载功能
                    print("4. 测试下载功能...")
                    download_response = requests.get(f"{base_url}/reports/{report_id}/download")
                    print(f"下载响应状态: {download_response.status_code}")
                    print(f"下载响应头: {dict(download_response.headers)}")
                    
                else:
                    print(f"报告生成失败: {response.status_code} - {response.text}")
            else:
                print("没有找到已完成的任务，请先运行一个测试任务")
        else:
            print(f"获取任务列表失败: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
    except Exception as e:
        print(f"其他错误: {e}")

if __name__ == "__main__":
    test_report_generation()