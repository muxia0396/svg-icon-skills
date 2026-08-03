# Contributing

感谢你改进 SVG Icon Skills。提交变更前，请先确认修改属于以下范围之一：技能触发与工作流、图标设计规范、PNG 切图、SVG 审计、跨平台兼容或文档清晰度。

## 开发环境

```bash
python -m venv .venv
python -m pip install -r requirements-dev.txt
python scripts/doctor.py --strict
python scripts/validate_all.py
```

请在虚拟环境中运行命令。不要提交 `.venv`、`__pycache__`、测试切图、生成图片或个人工作目录。

## 修改规则

- 保持每个 skill 自包含；运行时所需文件必须位于对应 skill 目录内。
- `create-svg-icon` 必须保留“ImageGen PNG → PNG-to-SVG”的顺序门禁。
- `png-to-svg` 不得接受嵌入位图、外部引用或用背景色伪造透明孔洞。
- `SKILL.md` frontmatter 只能包含 `name` 与 `description`。
- 新增依赖时，说明用途并设置合理的版本范围；运行依赖与开发依赖分开。
- 修改切图或审计逻辑时，在 `scripts/validate_all.py` 中补充回归样例。
- 不要把测试产物、参考项目名称、私人路径、密钥或访问令牌写入仓库。

## Pull request

PR 应保持单一目的，并说明：

1. 解决的问题；
2. 对两个 skill 工作流的影响；
3. 执行过的验证命令；
4. 涉及视觉输出时的前后对比。

提交 PR 前必须保证 `python scripts/validate_all.py` 通过。GitHub Actions 会在 Windows 和 Linux、Python 3.10 与 3.12 上重复验证。
