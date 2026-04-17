# 安消大脑 Agent (基于 Hermes-Agent) 实施计划

## 摘要 (Summary)
本项目旨在基于开源的 [hermes-agent](https://github.com/NousResearch/hermes-agent) 构建“安消大脑 Agent”，作为安消综合管理平台的核心智能化引擎。平台将采用 **控制面 (Control Plane)** 架构，通过 FastAPI 后端和 React 前端，对底层的多个 `hermes-agent` 实例进行统一管理。每个“岗位数字员工”将映射为 Hermes-Agent 的一个独立 Profile（实例配置），支持独立的员工定义（Persona/SOUL.md）、功能授权（工具集/技能开启）、综合调度（内置 Cron 任务集）以及个人微信渠道的绑定互动（通过 HermesClaw 等社区桥接方案）。

## 当前状态分析 (Current State Analysis)
经过对 `hermes-agent` 核心架构的探索分析（参考 `AGENTS.md`）：
1. **多实例支持**：Hermes 提供了强大的 Profile 机制（多实例隔离），完美契合“构建岗位数字员工”的需求，每个 Profile 拥有独立的 `HERMES_HOME`、`SOUL.md`、`config.yaml` 和运行状态。
2. **工具与技能授权**：Hermes 支持通过 `tools/` 和 `skills/` 进行能力扩展，可以通过动态修改每个 Profile 的 `config.yaml` 实现对数字员工的“功能授权”。
3. **任务调度**：内置了 `cron` 调度器模块（`cron/`），支持数字员工执行定时任务（如自动巡检、数据定期上报）。
4. **渠道互动**：网关（Gateway）架构支持多种平台接入，支持与个人微信（通过 HermesClaw 等社区桥接方案）的绑定互动。

## 提议的变更 (Proposed Changes)

### 1. 核心底座扩展 (Hermes-Agent 增强)
- **安消专用工具集开发**：在 `tools/` 目录下开发安消垂直领域的定制工具（如 `fire_alarm_tool.py` 消防报警查询、`cctv_tool.py` 视频监控分析、`device_control_tool.py` 消防设备联动控制），并注册为独立的安消 Toolset。
- **自定义网关接入**：配置并集成个人微信网关（基于 OpenClaw / HermesClaw 方案），使其支持安消平台各数字员工的消息收发与事件推送。

### 2. 控制面后端开发 (FastAPI Backend)
提供一套 RESTful API 用于管理和调度底层的 Hermes-Agent 实例群：
- **数字员工管理 API**：
  - 创建、删除、查询数字员工（封装 `hermes profile` 命令行或 API 操作）。
  - **员工定义**：读取/更新对应 Profile 目录下的 `SOUL.md`，定义其岗位角色属性（如“安保队长”、“消防巡查员”）。
  - **功能授权**：修改 `config.yaml` 中启用的 `toolsets` 和 `skills`，精确控制不同岗位的可用能力。
- **综合调度 API**：
  - 任务下发：向指定数字员工的 Agent 注入临时指令或事件（例如突发火情告警）。
  - 定时任务配置：读写 `cron` 任务配置文件，实现数字员工的自动化排班与巡检调度。
- **进程管理 API**：
  - 启动/停止特定数字员工的微信交互网关 (`hermes -p <name> gateway start`)。
  - 监控各数字员工的运行状态和日志流。

### 3. 可视化面板开发 (React Frontend)
开发安消综合管理平台的 Web 前端，提供现代化的可视化操作界面：
- **Dashboard (全局概览)**：展示当前活跃的数字员工数量、处理的报警事件总数、各交互渠道活跃度等核心指标。
- **数字员工定义中心**：表单化创建数字员工，包括输入岗位职责（自动生成 SOUL.md 提示词）、勾选所需功能权限（如监控查看、报警复核、设备控制）。
- **调度指挥中心**：可视化配置数字员工的定时任务和值班表，查看任务执行结果与历史轨迹记录。
- **渠道管理面板**：为每个数字员工生成绑定个人微信的二维码或展示连接状态，实现交互渠道的可视化管理。

## 假设与决策 (Assumptions & Decisions)
1. **架构解耦**：采用 FastAPI + React 的 Control Plane 模式，不直接魔改 Hermes-Agent 的核心大循环代码，而是通过文件配置管理、进程控制和定制 Tools 的方式进行驱动，以便于未来跟随上游开源项目升级。
2. **微信接入方案**：使用 Personal WeChat 方案（基于 HermesClaw 社区实现），由于微信生态限制，后端需统一管理登录 Session 与二维码状态。
3. **技术栈**：后端 Python (FastAPI) 确保与 Hermes-Agent 的 Python 生态无缝对接并可直接引入内部模块；前端 React 确保良好的可交互性和组件生态支持。

## 验证步骤 (Verification Steps)
1. 启动 FastAPI 后端服务与 React 前端面板。
2. 在前端“定义中心”创建一个名为“消防巡检员”的数字员工，并赋予“视频监控查看”工具权限。
3. 验证后端是否成功在 `~/.hermes/profiles/` 目录下创建了对应的配置目录，并正确写入了 `SOUL.md` 和 `config.yaml`。
4. 为该数字员工绑定个人微信渠道，验证在微信端发送测试指令（如“查看当前最新的报警记录”）后，Agent 能否正确调用安消工具集并回复微信。
5. 在调度中心配置一个“每小时汇总消防报警”的 Cron 定时任务，验证任务能否按时触发、执行汇总并通过微信渠道成功推送报告。
