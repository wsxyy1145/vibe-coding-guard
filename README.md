# vibe-coding-guard 🏔️

[![GitHub stars](https://img.shields.io/github/stars/wsxyy1145/vibe-coding-guard?style=social)](https://github.com/wsxyy1145/vibe-coding-guard/stargazers)
[![Latest Release](https://img.shields.io/github/v/release/wsxyy1145/vibe-coding-guard)](https://github.com/wsxyy1145/vibe-coding-guard/releases)
[![License: Apache 2.0](https://img.shields.io/github/license/wsxyy1145/vibe-coding-guard)](https://github.com/wsxyy1145/vibe-coding-guard/blob/main/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/wsxyy1145/vibe-coding-guard)](https://github.com/wsxyy1145/vibe-coding-guard/issues)

> 别再 vibe 出史山了。

[English](#) · [简体中文](./README.md)

**vibe-coding-guard** 是一个通用的 vibe coding 质量拦截 skill。
让 AI 在交付代码前强制做一次 pre-flight self-review，把"史山预警"以吐槽 + 整改清单的形式摆出来，**不允许假装没看见**。

适用于任意语言、任意框架。Agent 通用。

---

## 🏷️ GitHub Topics（建议在仓库 About 侧栏勾选）

复制这一行到 GitHub 仓库的 "Topics" 输入框（建议选 5-10 个）：

```
ai coding agent code-review code-quality vibe-coding code-smells refactoring developer-tools linter best-practices
```

| Topic | 搜索量 | 为什么选 |
|---|---|---|
| `ai-coding` | 🔥🔥🔥 | 2025-2026 暴涨的垂直领域，是核心场景 |
| `agent` | 🔥🔥🔥 | 跟 Claude Code / WorkBuddy / Cursor 撞关键词 |
| `code-review` | 🔥🔥🔥 | 开发者主动搜索的高频词 |
| `code-quality` | 🔥🔥 | 跟 lint / static-analysis 同区 |
| `vibe-coding` | 🔥🔥 | 2025 年 Karpathy 提的概念，正在成主流 |
| `code-smells` | 🔥 | 圈内人才搜，精准用户 |
| `refactoring` | 🔥🔥 | 经典长青词 |
| `developer-tools` | 🔥🔥🔥 | GitHub Explore 大类 |
| `linter` | 🔥🔥 | 跟静态分析归类，曝光加分 |
| `best-practices` | 🔥 | 模糊但搜索量大 |

**避坑**：不要勾 `machine-learning` / `ai` / `gpt` 这种通用大词——会跟百万级仓库竞争，**搜不到你**。

**GitHub 上限 20 个 topic**，但建议 ≤10：太多会被算法判为"keyword stuffing"，反而降权。

---

## 这是什么

"vibe coding" 是那种"让 AI 直接写吧，先跑起来再说"的工作流。
问题在于：**跑起来 ≠ 写好**。一周后回来看自己写的代码，恨不得把键盘扔了——这就是"史山"。

本 skill 强制在每次代码交付前过一遍 4 维检查：

| 维度 | 戳 | 看什么 |
|---|---|---|
| 函数 / 模块臃肿 | 🏔️ | > 80 行？嵌套 > 4 层？一个函数干多件事？ |
| 职责混乱 | 🌀 | 上帝类？文件超 600 行？import 顺序乱？ |
| 错误处理 / 边界 | 🕳️ | 裸 except？I/O 没 try/catch？None 没检查？ |
| 过度工程 | 🎈 | 第 1 次出现就抽象？3 层间接？配置驱动一切？ |

按严重度分级响应：**🔴 P0 必改 → 🟠 P1 给方案 → 🟡 P2 列清单 → 🟢 P3 吐槽不强求**。

---

## 安装

### WorkBuddy (推荐)

把整个目录放到 `~/.workbuddy/skills/vibe-coding-guard/`（user scope）或 `.workbuddy/skills/vibe-coding-guard/`（project scope）。

### Claude Code / 其他 Agent 平台

`SKILL.md` 是入口。Agent 加载后会自动按主流程运行。
`references/` 下的两个文件按需加载——SKILL.md 主体保持精简。

### 一行安装（解压到 user scope）

```bash
# macOS / Linux
mkdir -p ~/.workbuddy/skills && unzip vibe-coding-guard.zip -d ~/.workbuddy/skills/

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.workbuddy\skills"
Expand-Archive .\vibe-coding-guard.zip -DestinationPath "$env:USERPROFILE\.workbuddy\skills"
```

---

## 触发条件

满足以下任一条件时 **必须** 触发自检：

- AI 刚刚为用户写完一段 ≥30 行的代码
- 用户说 "写个 XX 吧 / 帮我实现 XX / 搭一个 XX"
- 用户在 vibe coding 流程中（前缀词："vibe"、"快速搞个"、"先跑起来"）
- 一次性大段生成（≥100 行）的代码

**不属于本 skill 范围**：
- 纯文档 / 纯配置（单字段改动）
- 一次性 throwaway 脚本（用户明确说"用完就扔"）
- 用户明确说"别管质量，先跑起来"

---

## 使用示例

### 真实案例：199 行的"史山"注册 API

完整反面教材 → [`examples/bad_v0_register.py`](./examples/bad_v0_register.py)（199 行，单文件一把梭）。

vibe 出来那一刻**没拦**，结果 AI 在交付前自动插入了这段：

> 🏔️ **史山预警**
>
> 刚 vibe 完 `bad_v0_register.py`（199 行），强制自检了一遍，**4 个维度全中招**：
>
> 🔴 **P0：硬伤（必改）**
> - `register()` 第 92 行 `except Exception as e: return jsonify({"error": str(e)})` —— 直接把异常原文甩给用户，安全漏洞
> - `send_welcome_email()` 第 67 行 `except: pass` —— 吞错本尊，SMTP 挂了你都不知道
> - 密码用 `sha256(password + salt)` —— 无迭代无慢哈希，GPU 一秒跑几十亿次
> - 登录接口没有速率限制 —— 撞库分分钟
>
> 🟠 **P1：结构问题**
> - `register()` 单函数 65 行，从校验、查重、落库、发邮件、写审计日志全干了
> - 整个文件 5 个职责混在一起
>
> 🟡 **P2：可读性**
> - `salt = hashlib.sha256(str(hash(email)).encode())` —— 拿 email 哈希当 salt？彩虹表一打一个准
>
> **要现场整改 P0+P1 吗？P2/P3 你自己看着办。**

风格：**幽默吐槽 + 具体行号 + 可执行拆法**。不油腻、不说教、不爹味。

### 整改后（节选）

把上面那个 199 行的史山按 P0+P1 拆完，应该长这样（节选）：

```
register-api/
├── app.py                  # Flask 入口，仅 30 行
├── api/
│   └── auth.py            # HTTP 层：参数解析 + 响应
├── services/
│   ├── user_service.py    # 业务：注册 / 登录
│   ├── email_service.py   # 发邮件，吞错日志
│   └── audit_service.py   # 审计日志写文件
├── db/
│   ├── user_repo.py       # DAO：所有 SQL 在这
│   └── schema.sql
├── security/
│   ├── password.py        # argon2 哈希
│   └── rate_limit.py      # 登录限流
└── tests/
    └── test_register.py   # 关键路径测试
```

—— 同样的功能，5 个文件，每个文件单一职责，错误能被定位、能被测试、能在生产告警。

---

## 仓库结构

```
vibe-coding-guard/
├── SKILL.md                       # 主流程：4 维检查 + 4 级响应 + 预警卡片
├── references/
│   ├── code-smell-catalog.md     # 反模式目录（按需加载）
│   └── refactor-playbook.md      # 重构手法手册（按需加载）
├── examples/
│   └── bad_v0_register.py        # 史山反面教材（199 行）
├── .github/
│   ├── ISSUE_TEMPLATE/           # bug / feature / new_smell 三选
│   ├── workflows/validate-skill.yml  # CI：frontmatter + refs 校验
│   └── pull_request_template.md
├── LICENSE                        # Apache 2.0
├── CHANGELOG.md
├── CONTRIBUTING.md                # 贡献指南（文件分工 + SemVer）
└── README.md                      # 本文件
```

---

## 设计原则

1. **强制介入不跳过** —— 哪怕"很短的代码"也得过一遍
2. **渐进加载** —— SKILL.md 保持精简，反模式目录 / 重构手册放 references
3. **Rule of Three** —— 反对为了"将来可能用"过早抽象
4. **错误处理是 P0** —— vibe coding 最高频的失分点，单独列一维

---

## 风格（人设）

DO ✅
- 用"史山" "屎山" "答辩"等用户已经在用的词
- 给具体行号 / 函数名 / 改动方向
- 一句话定性 + 可执行拆法

DON'T ❌
- "这是一个很好的开始" "整体结构清晰" 这种废话
- "建议您可以考虑……或许可以……" —— 直接说"拆"
- 为了显得专业堆术语（"您当前实现存在 SRP 违反"）—— 说人话

---

## 贡献

Issue / PR 都欢迎。
- 加反模式 → 改 `references/code-smell-catalog.md`
- 加吐槽模板 → 改 `SKILL.md` 的"万能吐槽模板"表
- 加新语言示例 → 在 `references/` 下加 `<lang>-examples.md`

---

## License

Apache 2.0 — 详见 [LICENSE](./LICENSE)。
