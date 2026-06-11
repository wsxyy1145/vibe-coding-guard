# 贡献指南

## 提 Issue

仓库有 3 个 issue 模板，挑对应的用：

- **Bug Report** — 行为异常 / 误报 / 漏报
- **Feature Request** — 加新功能
- **New Code Smell** — 给反模式目录加条目（最常见的贡献）

## 提 PR

1. Fork + 切分支
2. 改完跑一遍 `references/code-smell-catalog.md` 自检（**用 dogfooding**）
3. 提 PR 时填好模板里的"改动类型"和"自检清单"
4. CI（`.github/workflows/validate-skill.yml`）会校验 frontmatter 和 references/

## 文件分工

| 想加什么 | 改哪里 |
|---|---|
| 主流程规则 | `SKILL.md` |
| 反模式条目 | `references/code-smell-catalog.md` |
| 重构手法 | `references/refactor-playbook.md` |
| 一句话吐槽 | `SKILL.md` 里的"万能吐槽模板"表 |
| README / 文档 | `README.md` |
| CI / 模板 | `.github/` |

## 版本号规则

走 [SemVer](https://semver.org/)：

- **Patch**（0.1.x）：吐槽模板新增、文档调整
- **Minor**（0.x.0）：新维度 / 新级别响应 / 新 P0 规则
- **Major**（x.0.0）：破坏性重构（重写 SKILL.md 主流程）

每次改动同步更新 `CHANGELOG.md`。

## Style

沿用 SKILL.md 主流程的"幽默吐槽"调调，**不要写"这是一个很好的开始"这种废话**。直接说"这函数 200 行了，重写"。
