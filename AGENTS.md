# AGENTS.md

# Project: Video Creator Tool

## 1. 项目定位

这是一个 AI 短视频生产辅助工作台。

目标：

帮助用户完成：

剧本 → 分镜 → 生产方式判断 → AI生产方案 → 视频生成 → 审核

的半自动生产流程。

本项目不是商业决策系统。

不负责：

- 产品选品
- 市场趋势预测
- 爆款预测
- 用户需求挖掘

这些属于未来商业内容决策系统。

---

# 2. 开发依据

开发必须严格遵守以下文档：

```
docs/

├── Master Design
├── 00_业务流程与状态流转设计.md
├── 01_数据结构设计.md
├── 02_页面设计.md
├── 03_技术架构设计.md
├── 04_API接口设计.md
└── 05_开发计划与Codex任务拆解.md
```

以上文档是项目唯一设计依据。

如果代码需求与文档冲突：

停止开发。

记录问题。

等待人工确认。

禁止自行修改业务设计。

---

# 3. Codex工作模式

Codex作为项目开发执行者。

执行顺序：

1. 阅读所有设计文档
2. 判断当前Phase和Task
3. 检查前置Task是否完成
4. 执行当前Task
5. 编写代码
6. 编写测试
7. 运行测试
8. 输出Task完成报告
9. 进入下一Task

禁止跳跃开发。

---

# 4. Task执行规则

每次开发必须绑定一个Task。

Task格式：

```
Task编号：

目标：

实现内容：

修改文件：

测试方式：

验收标准：
```

完成后输出：

```
Task完成报告：

完成内容：

修改文件：

测试结果：

当前状态：

下一Task：
```

---

# 5. 架构约束

## 5.1 后端

技术方向：

- Python
- FastAPI

负责：

- API
- 状态流转
- 数据管理
- AI调用编排

业务层禁止直接调用数据库。

必须通过Service层。

---

## 5.2 数据层

核心对象：

- Project
- Script
- Storyboard
- Shot
- ShotReview
- ProductionTask
- Asset
- GenerationResult

禁止随意增加核心业务对象。

---

## 5.3 AI调用

禁止业务代码直接调用模型API。

统一通过Provider层：

```
VideoProvider

├── SeedanceProvider
├── KlingProvider
└── JimengProvider
```

---

# 6. 状态管理规则

所有状态变化必须由Backend控制。

禁止前端直接修改状态。

核心状态：

- Project State
- Script State
- Shot State
- Production Task State
- Asset State
- Generation Result State

---

# 7. 视频生成规则

视频生成属于耗时任务。

必须采用异步任务模式：

```
Create Task

↓

Queue

↓

Worker

↓

Provider API

↓

Update Status

↓

Result
```

禁止同步等待视频生成完成。

---

# 8. 代码质量要求

所有新增功能必须包含：

- 单元测试
- API测试
- 错误处理

禁止：

- 临时代码进入主分支
- 删除已有功能
- 绕过测试

---

# 9. 开发边界

当前MVP优先实现：

Phase 0:

项目初始化

Phase 1:

数据模型和后端基础

Phase 2:

剧本→分镜

Phase 3:

人工审核流程

Phase 4:

AI生产方案

Phase 5:

素材和任务系统

Phase 6:

前端工作台

Phase 7:

视频API接入

不要提前开发未来功能。

---

# 10. 环境问题处理

以下情况允许请求人工协助：

- 软件安装失败
- 环境变量缺失
- API Key缺失
- 第三方账号权限问题
- 网络限制

除此之外：

优先自行分析和解决。

---

# 11. 最终目标

完成一个稳定的 AI 视频生产工作台：

用户输入剧本。

系统生成分镜。

人工审核。

AI镜头生成生产方案。

上传素材。

调用视频模型。

输出可审核视频结果。

形成完整生产闭环。
