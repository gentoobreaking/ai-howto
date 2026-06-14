#!/usr/bin/env python3
"""
import_tasks_to_github_projects.py
掃描 /Users/claw/Tasks/ 下所有 T*.md，匯入到 GitHub Projects

用法：
  python3 import_tasks_to_github_projects.py [--dry-run] [--export <file>]

選項：
  --dry-run    預覽模式，不實際匯入
  --export     匯出 JSON 供手動匯入
"""

import re
import json
import argparse
from pathlib import Path
from datetime import datetime

TASKS_DIR = Path("/Users/claw/Tasks")

def parse_task_file(filepath: Path) -> dict:
    """解析 T*.md 檔案，提取 front matter"""
    content = filepath.read_text(encoding="utf-8")
    
    task = {
        "file": str(filepath),
        "project": filepath.parent.parent.name,  # e.g., gold-analysis
        "id": filepath.stem,  # e.g., T001
    }
    
    # 解析標題 (## T001 - Title)
    title_match = re.search(r'^#+\s*(T\d+)\s*[-—]\s*(.+)$', content, re.MULTILINE)
    if title_match:
        task["task_id"] = title_match.group(1)
        task["title"] = title_match.group(2).strip()
    else:
        task["task_id"] = filepath.stem
        task["title"] = "(無標題)"
    
    # 解析 Status
    status_match = re.search(r'(?:^|\n)-?\s*Status\s*:\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
    if status_match:
        status = status_match.group(1).strip().lower()
        # 正規化
        if status in ["done", "completed", "finished", "closed"]:
            task["status"] = "Done"
        elif status in ["in-progress", "in_progress", "doing", "active"]:
            task["status"] = "In Progress"
        elif status in ["skip", "skipped"]:
            task["status"] = "Skipped"
        else:
            task["status"] = "Pending"
    else:
        task["status"] = "Pending"
    
    # 解析 Assignee
    assignee_match = re.search(r'(?:^|\n)-?\s*Assignee\s*:\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
    if assignee_match:
        task["assignee"] = assignee_match.group(1).strip()
    else:
        task["assignee"] = ""
    
    # 解析 Due Date
    due_match = re.search(r'(?:^|\n)-?\s*Due\s*:\s*(\d{4}-\d{2}-\d{2})', content, re.IGNORECASE)
    if due_match:
        task["due_date"] = due_match.group(1)
    else:
        task["due_date"] = ""
    
    # 解析 Priority
    priority_match = re.search(r'(?:^|\n)-?\s*Priority\s*:\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
    if priority_match:
        task["priority"] = priority_match.group(1).strip()
    else:
        task["priority"] = ""
    
    return task

def scan_all_tasks() -> list:
    """掃描所有 T*.md 檔案"""
    tasks = []
    for task_file in TASKS_DIR.rglob("T*.md"):
        # 排除 _done 和 _inbox
        if "_done" in str(task_file) or "_inbox" in str(task_file):
            continue
        try:
            task = parse_task_file(task_file)
            tasks.append(task)
        except Exception as e:
            print(f"⚠️  解析失敗 {task_file}: {e}")
    
    # 按 project 和 id 排序
    tasks.sort(key=lambda t: (t["project"], t["id"]))
    return tasks

def print_summary(tasks: list):
    """印出摘要"""
    print(f"\n📊 共掃描到 {len(tasks)} 個任務\n")
    
    # 按專案分組
    by_project = {}
    by_status = {"Pending": 0, "In Progress": 0, "Done": 0, "Skipped": 0}
    
    for task in tasks:
        proj = task["project"]
        if proj not in by_project:
            by_project[proj] = []
        by_project[proj].append(task)
        by_status[task["status"]] = by_status.get(task["status"], 0) + 1
    
    print("按專案分類：")
    for proj, proj_tasks in sorted(by_project.items()):
        print(f"  {proj}: {len(proj_tasks)} 個任務")
    
    print("\n按狀態分類：")
    for status, count in by_status.items():
        if count > 0:
            print(f"  {status}: {count}")
    
    print("\n" + "="*60)

def print_tasks(tasks: list, limit: int = 20):
    """印出任務列表"""
    print(f"\n前 {min(limit, len(tasks))} 個任務預覽：\n")
    for task in tasks[:limit]:
        assignee = f" [{task['assignee']}]" if task['assignee'] else ""
        due = f" (Due: {task['due_date']})" if task['due_date'] else ""
        print(f"  {task['id']} | {task['status']:12} | {task['project']:20} | {task['title'][:40]}{assignee}{due}")
    
    if len(tasks) > limit:
        print(f"\n... 還有 {len(tasks) - limit} 個任務")

def export_json(tasks: list, filepath: str):
    """匯出 JSON"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 已匯出到 {filepath}")

def main():
    parser = argparse.ArgumentParser(description="匯入任務到 GitHub Projects")
    parser.add_argument("--dry-run", action="store_true", help="預覽模式")
    parser.add_argument("--export", metavar="FILE", help="匯出 JSON 檔案")
    parser.add_argument("--project", help="只匯入指定專案的任務")
    args = parser.parse_args()
    
    print("🔍 掃描任務檔案...")
    tasks = scan_all_tasks()
    
    if args.project:
        tasks = [t for t in tasks if t["project"] == args.project]
        print(f"篩選後: {len(tasks)} 個任務 (專案: {args.project})")
    
    print_summary(tasks)
    print_tasks(tasks)
    
    if args.export:
        export_json(tasks, args.export)
        return
    
    if args.dry_run:
        print("\n🏃 預覽模式完成（未實際匯入）")
        print("\n下一步：")
        print("  1. 確認 GitHub Projects 已建立")
        print("  2. 執行: gh auth refresh -s read:project,project")
        print("  3. 執行: python3 import_tasks_to_github_projects.py")
        return
    
    # 實際匯入（需要 gh CLI 權限）
    print("\n🚀 開始匯入到 GitHub Projects...")
    print("注意：需要 gh CLI 的 project 權限")
    print("請先執行: gh auth refresh -s read:project,project")
    
    # TODO: 實作 gh project item-create
    # 目前 GitHub CLI 對 Projects v2 的支援有限，可能需要 GraphQL API
    
    print("\n💡 替代方案：")
    print("  1. 使用 --export 匯出 JSON")
    print("  2. 手動在 GitHub Projects 匯入")
    print("  3. 或使用 GitHub Projects 的 CSV 匯入功能")

if __name__ == "__main__":
    main()
