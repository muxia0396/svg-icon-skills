# SVG Icon Skills

[![Validate skills](https://github.com/muxia0396/svg-icon-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/muxia0396/svg-icon-skills/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一套严格分层的 SVG 图标工作流，包含两个可独立触发、也可串联使用的 Agent Skill。

支持 Windows、macOS 与 Linux；提供自动依赖检查、跨平台 CI、PNG 切图回归测试和 SVG 安全审计。

## Skills

### `png-to-svg`

将 PNG、JPG、WebP 或截图中的扁平图形重建为透明、可编辑的真实 SVG。它要求先分离背景，再以简洁几何重建，并通过脚本阻止位图嵌入、外部引用和不安全元素。

### `create-svg-icon`

创作新的线性或面性 SVG 图标。流程不可跳过：先依据内置图标设计指南制定规范，使用 ImageGen 生成 PNG 设计稿，检查并切图，然后调用 `png-to-svg` 逐个重建与验收最终 SVG。

## 安装

克隆仓库：

```bash
git clone https://github.com/muxia0396/svg-icon-skills.git
cd svg-icon-skills
```

将两个 skill 目录分别复制到 Agent 的 skill 发现目录：

```text
skills/png-to-svg
skills/create-svg-icon
```

例如 Codex 的个人目录通常是：

```text
~/.codex/skills/png-to-svg
~/.codex/skills/create-svg-icon
```

两个目录应同时安装，才能让 `create-svg-icon` 调用相邻的转换流程。重新启动 Agent 或新建任务，使 skill 元数据被重新发现。

## 项目结构

```text
skills/
├── create-svg-icon/   # ImageGen PNG → SVG 创作流程
└── png-to-svg/        # 位图分析、矢量重建与 SVG 审计
scripts/
├── doctor.py          # 环境与依赖诊断
└── validate_all.py    # 可移植的仓库验证入口
```

## 示例

```text
Use $png-to-svg to turn this PNG logo into a transparent editable SVG.
```

```text
Use $create-svg-icon to create five cohesive filled SVG navigation icons for my reading app.
```

## 环境初始化

项目支持 Windows、macOS 和 Linux。建议先创建独立虚拟环境：

```bash
python -m venv .venv
```

激活环境并安装运行依赖：

```bash
# Windows PowerShell
.\.venv\Scripts\python -m pip install -r requirements.txt

# macOS / Linux
./.venv/bin/python -m pip install -r requirements.txt
```

维护、测试或准备发布时，再安装开发依赖：

```bash
python -m pip install -r requirements-dev.txt
```

运行环境自检：

```bash
python scripts/doctor.py
```

其中：

- `png-to-svg` 的 SVG 结构审计只依赖 Python 标准库。
- `create-svg-icon` 的 4×4 图标切图依赖 Pillow，已写入 `requirements.txt`。
- skill 元数据校验依赖 PyYAML，只在维护项目时需要，已写入 `requirements-dev.txt`。
- 创作流程还需要宿主提供可调用的 ImageGen / image-generation 工具；这属于宿主能力，`doctor.py` 会明确提示，skill 不会绕过 PNG 阶段。

## 发布前验证

```bash
python scripts/doctor.py --strict
python scripts/validate_all.py
```

`validate_all.py` 会校验两个 skill 的 frontmatter、UI 元数据、Python 语法和 SVG 审计器的正反样例。它不依赖 Codex 安装目录中的内部脚本，因此克隆仓库后即可运行。

如果还要运行 Agent Skill SDK 自带的 `quick_validate.py`，Windows 中文环境请启用 Python UTF-8 模式，避免系统 GBK 误读 Markdown：

```powershell
$env:PYTHONUTF8 = "1"
python <skill-creator-dir>\scripts\quick_validate.py .\skills\png-to-svg
python <skill-creator-dir>\scripts\quick_validate.py .\skills\create-svg-icon
```

## 贡献与安全

- 提交修改前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 并运行完整验证。
- 安全问题请遵循 [SECURITY.md](SECURITY.md)，不要在公开 Issue 中披露未修复漏洞。
- 项目使用 [MIT License](LICENSE) 开源。
