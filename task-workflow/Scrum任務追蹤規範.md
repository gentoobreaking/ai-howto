# Scrum 任務追蹤規範

## 快速開始

### 1. 建立新專案

```bash
mkdir -p /Users/claw/Tasks/{project-name}/tasks
touch /Users/claw/Tasks/{project-name}/README.md
```

### 2. 拆分任務

使用 TEMPLATE.md 格式建立 T001.md, T002.md...

### 3. 指派執行

- 碼農1號: 後端開發
- 碼農2號: ML/交易系統
- 安安: 前端/文檔
- 樂樂: 驗證/測試

### 4. 產出報告

任務完成後自動產出報告到 `docs/reports/`：
- `execution/` - 執行報告
- `validation/` - 驗證報告
- `incidents/` - 問題報告
- `decisions/` - 決策記錄

### 5. 同步 GitHub

```bash
git add docs/reports/
git commit -m "docs(reports): 新增 XXX 報告"
git push origin main
```

## 目錄結構

```
Tasks/
├── PROJECTS.md          # 專案總覽
├── _inbox/              # 待分類
├── _verification/       # 驗證任務
├── {project}/
│   ├── README.md
│   └── tasks/
│       ├── T001.md
│       └── ...

Projects/{project}/
└── docs/reports/        # 統一報告中心
    ├── execution/
    ├── validation/
    ├── incidents/
    └── decisions/
```

## 相關連結

- [Skill 文件](../../.qclaw/workspace/skills/scrum-task-tracker/SKILL.md)
- [任務模板](../../.qclaw/workspace/skills/scrum-task-tracker/TEMPLATE.md)
