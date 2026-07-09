


# 04_API接口设计

# 1. 文档目的

本文档定义 Video Creator Tool 后端 API 设计。

API设计依据：

- Master Design业务流程
- 00状态流转设计
- 01数据结构设计
- 02页面交互设计
- 03技术架构设计

API目标：

提供前端工作台、业务服务、AI服务之间的统一通信接口。

# 2. API设计原则

## 2.1 资源对象驱动

API围绕核心业务对象设计：

- Project
- Script
- Storyboard
- Shot
- Asset
- Production Task
- Generation Result

## 2.2 状态由后端控制

前端只能提交操作请求。

状态变化由Backend Service完成。

## 2.3 AI任务异步化

视频生成属于长耗时任务。

采用：

创建任务 → 查询状态 → 获取结果

模式。

# 3. API基础规范

Base URL:

```text
/api/v1
```

数据格式：

```json
{
  "code":0,
  "message":"success",
  "data":{}
}
```

# 4. Project API

## 创建项目

POST

```text
/projects
```

Request:

```json
{
  "name":"steam cleaner video",
  "product_name":"steam cleaner",
  "video_goal":"TikTok product video"
}
```

Response:

```json
{
  "project_id":"project_001",
  "status":"created"
}
```

---

## 获取项目详情

GET

```text
/projects/{project_id}
```

返回：

- 项目信息
- 当前状态
- 当前流程节点
- 关联剧本
- 分镜数量

---

## 获取项目列表

GET

```text
/projects
```

# 5. Script API

## 创建剧本

POST

```text
/projects/{project_id}/scripts
```

Request:

```json
{
  "content":"视频剧本文本"
}
```

---

## 提交剧本分析

POST

```text
/scripts/{script_id}/analyze
```

功能：

调用LLM生成分镜。

返回：

storyboard_id

---

## 获取剧本

GET

```text
/scripts/{script_id}
```

# 6. Storyboard API

## 获取分镜列表

GET

```text
/storyboards/{storyboard_id}/shots
```

返回：

Shot列表。

---

## 重新生成分镜

POST

```text
/storyboards/{storyboard_id}/regenerate
```

用于：

人工认为当前分镜不符合要求。

# 7. Shot API

## 获取镜头详情

GET

```text
/shots/{shot_id}
```

返回：

- 镜头描述
- Camera
- Action
- 当前状态
- 审核记录

---

## 分镜审核

POST

```text
/shots/{shot_id}/review
```

Request:

```json
{
  "result":"approved",
  "comment":"符合要求"
}
```

result:

```text
approved
revision_required
rejected
```

---

## 设置生产方式

POST

```text
/shots/{shot_id}/production-type
```

Request:

```json
{
  "production_type":"ai_generate"
}
```

可选：

```text
real_shoot
ai_generate
```

# 8. AI Director API

## 生成AI生产方案

POST

```text
/shots/{shot_id}/generate-production-plan
```

功能：

调用Seedance Skill逻辑。

输出：

- generation_mode
- prompt
- negative_prompt
- camera
- motion
- lighting
- asset_requirement

---

## 获取AI生产方案

GET

```text
/shots/{shot_id}/production-plan
```

# 9. Asset API

## 获取素材需求

GET

```text
/shots/{shot_id}/assets/requirements
```

返回：

```json
{
 "required_assets":[
  "product_image",
  "first_frame",
  "reference_video"
 ]
}
```

---

## 上传素材

POST

```text
/assets/upload
```

Request:

multipart/form-data

字段：

- shot_id
- asset_type
- file

---

## 获取素材列表

GET

```text
/shots/{shot_id}/assets
```

# 10. Video Generation API

## 创建生成任务

POST

```text
/generation/tasks
```

Request:

```json
{
  "shot_id":"shot_001",
  "provider":"seedance",
  "generation_mode":"i2v"
}
```

Response:

```json
{
  "task_id":"task_001",
  "status":"waiting_asset"
}
```

---

## 查询任务状态

GET

```text
/generation/tasks/{task_id}
```

状态：

```text
draft
waiting_asset
ready
generating
completed
failed
```

---

## 提交生成

POST

```text
/generation/tasks/{task_id}/start
```

功能：

进入任务队列并调用视频模型。

# 11. Generation Result API

## 获取生成结果

GET

```text
/generation/results/{result_id}
```

返回：

- 视频地址
- 使用Prompt
- 使用素材
- 生成参数

---

## 视频审核

POST

```text
/generation/results/{result_id}/review
```

Request:

```json
{
 "result":"approved",
 "comment":"视频符合预期"
}
```

result:

```text
approved
rejected
regenerate
```

# 12. AI Provider接口

业务层禁止直接调用模型。

统一接口：

```python
class VideoProvider:

    create_task()

    get_status()

    get_result()
```

实现：

```text
VideoProvider
 |
 ├── SeedanceProvider
 ├── KlingProvider
 └── JimengProvider
```

# 13. MVP接口范围

V0.1：

必须实现：

- Project API
- Script API
- Storyboard API
- Shot Review API
- Production Type API
- AI Production Plan API

V0.2：

增加：

- Asset API
- Generation Task API
- Video Result API

V0.3：

增加：

- 多模型Provider
- 成本统计API
- 用户权限API

# 14. API状态设计原则

所有异步任务必须返回task_id。

前端通过状态查询获取进度。

禁止长时间HTTP阻塞等待AI生成完成。