

# 05_开发计划与Codex任务拆解

# 1. 文档目的

本文档用于指导 Codex 按照固定顺序完成 Video Creator Tool 的开发。

开发原则：

- 严格按照 Task 顺序执行
- 前置任务未完成，不进入后续任务
- 每个 Task 必须完成代码、测试、验收
- 除环境安装、账号配置、外部服务权限问题外，不需要人工干预

项目开发依据：

- 业务流程定义剧本 → 分镜 → 生产决策 → AI生成完整流程。 
- 数据结构定义 Project、Script、Storyboard、Shot、Production Task、Asset、Generation Result 核心对象。
- 页面设计定义工作台、审核页面、生产页面。
- 技术架构定义前端、后端、AI服务、任务系统分层。
- API设计定义模块通信接口。

# 2. Codex执行规则

## 2.1 执行模式

Codex作为主要开发执行者。

执行方式：

读取当前Master文档

↓

读取当前Task

↓

检查前置条件

↓

实现代码

↓

运行测试

↓

生成Task完成报告

↓

进入下一Task

## 2.2 禁止行为

禁止：

- 修改业务流程设计
- 自行扩大功能范围
- 增加未定义模块
- 跳过测试
- 直接进入后续Task

如果发现设计问题：

记录问题

停止当前Task

等待人工确认。

# 3. 开发阶段总览

## Phase 0：项目初始化

目标：建立工程基础。

## Phase 1：核心数据和后端框架

目标：跑通业务数据流。

## Phase 2：AI分镜生成流程

目标：实现剧本 → 分镜。

## Phase 3：人工审核工作流

目标：实现状态驱动生产流程。

## Phase 4：AI生产方案生成

目标：实现Shot → Seedance Prompt。

## Phase 5：素材管理和任务系统

目标：实现AI视频生产准备。

## Phase 6：前端工作台

目标：完整用户操作流程。

## Phase 7：视频API接入

目标：调用真实模型生成视频。

# 4. Task详细拆解

# Phase 0 项目初始化

## TASK-001 创建项目基础结构

目标：

建立标准项目目录。

目录：

```text
video_creator_tool

├── backend
├── frontend
├── docs
├── tests
├── storage
└── README.md
```

执行：

- 创建目录
- 创建配置文件
- 创建开发文档入口
- 初始化Git

验收：

- 项目可以正常启动
- README存在

完成后进入TASK-002。

---

## TASK-002 后端基础环境

目标：

建立FastAPI后端。

实现：

- FastAPI项目
- 配置管理
- 健康检查接口

接口：

GET /health

返回：

```json
{
 "status":"ok"
}
```

测试：

pytest验证接口。

验收：

后端服务启动成功。

---

# Phase 1 数据层开发

## TASK-003 数据库模型实现

目标：

根据01_数据结构设计实现数据库模型。

实现：

- Project
- Script
- Storyboard
- Shot
- ShotReview
- ProductionTask
- Asset

技术：

SQLAlchemy + PostgreSQL/SQLite。

验收：

- 所有模型创建成功
- 数据迁移成功
- 单元测试通过

---

## TASK-004 数据访问层

目标：

建立Repository。

实现：

ProjectRepository

ScriptRepository

ShotRepository

AssetRepository

ProductionRepository

要求：

业务层禁止直接操作数据库。

验收：

CRUD测试通过。

---

# Phase 2 剧本和分镜系统

## TASK-005 Script服务

目标：

实现剧本管理。

接口：

POST /projects/{id}/scripts

GET /scripts/{id}

实现：

- 创建剧本
- 保存版本
- 查询剧本

验收：

API测试通过。

---

## TASK-006 Storyboard生成服务

目标：

实现剧本 → 分镜。

输入：

Script

输出：

Storyboard + Shot列表。

第一版：

调用OpenAI API。

要求：

输出必须符合Shot Schema。

验收：

输入测试剧本，可以生成结构化Shot。

---

# Phase 3 审核工作流

## TASK-007 Shot审核状态系统

目标：

实现人工审核流程。

实现：

POST /shots/{id}/review

支持：

approved
revision_required
rejected

实现状态迁移。

验收：

非法状态转换被拒绝。

---

## TASK-008 Production Type选择

目标：

实现：

真人拍摄 / AI生成

接口：

POST /shots/{id}/production-type

验收：

状态正确保存。

---

# Phase 4 AI生产方案

## TASK-009 AI Director Service

目标：

实现Shot → AI生产方案。

输入：

Shot

输出：

- generation_mode
- prompt
- negative_prompt
- camera
- motion
- lighting
- asset_requirement

验收：

生成结果符合Production Task结构。

---

# Phase 5 素材系统

## TASK-010 Asset管理

目标：

实现素材上传和管理。

实现：

- 上传接口
- 素材关联Shot
- 状态管理

验收：

素材可以上传、查询。

---

## TASK-011 Generation Task系统

目标：

建立异步任务框架。

实现：

Redis Queue

Worker

任务状态：

pending
running
completed
failed

验收：

任务可以创建和执行。

---

# Phase 6 前端工作台

## TASK-012 前端项目初始化

实现：

React
TypeScript
Tailwind

页面：

- Dashboard
- Project
- Script
- Storyboard

验收：

页面可以访问。

---

## TASK-013 Storyboard审核页面

实现：

Shot卡片展示。

按钮：

- 通过
- 修改
- 驳回

调用后端审核API。

验收：

完整审核流程可操作。

---

## TASK-014 AI生产页面

实现：

展示：

- Prompt
- Camera
- Motion
- Lighting
- Asset需求

支持上传素材。

验收：

用户可以准备AI生成任务。

---

# Phase 7 视频生成接入

## TASK-015 Seedance Provider

目标：

接入真实视频API。

实现：

VideoProvider接口。

方法：

create_task()

get_status()

get_result()

验收：

测试任务可以提交。

---

## TASK-016 视频结果审核

实现：

视频播放

审核按钮：

- 通过
- 重新生成
- 修改Prompt

验收：

完成完整闭环。

# 5. Codex每个Task完成标准

每个Task必须输出：

```text
Task编号：

完成内容：

修改文件：

测试结果：

存在问题：

下一步Task：
```

# 6. 最终MVP验收标准

用户可以：

1. 创建项目

2. 输入剧本

3. 自动生成分镜

4. 审核分镜

5. 选择实拍/AI

6. 获取AI生产方案

7. 上传素材

8. 创建视频生成任务

9. 查看生成结果

10. 审核视频

形成完整生产闭环。

# 7. 后续扩展方向

MVP完成后再增加：

- 爆款视频分析
- TikTok数据接入
- 商业决策系统
- 多模型自动选择
- 视频效果反馈学习