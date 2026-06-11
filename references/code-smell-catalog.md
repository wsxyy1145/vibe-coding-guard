# Code Smell Catalog — 史山反模式目录

> 本文件按需加载。当你遇到不确定"这算不算史山"的代码时，对照本目录的判定标准 + 修复方向。**不要在 SKILL.md 主流程里逐条引用本文件**——SKILL.md 保持精简。

## 1. 函数层（Bloaters）

### 1.1 Long Function（长函数）

- **判定**：单函数 > 80 行（不含纯数据 / 注释 / docstring）；或单函数嵌套层级 > 4。
- **症状**：滚动条狂拉，函数头部和尾部的变量名毫无关联。
- **修复**：Extract Function（提取函数）。规则：**一个函数做一件事，能用一句话说清它在做什么**。如果一句话说不清，就拆。
- **进阶**：先用 Comment Header 法——给函数加 `# === Input validation ===` `# === Transform ===` `# === Side effect ===` 这样的注释，每个 header 下面就是一个待提取函数。

### 1.2 Long Parameter List（长参数列表）

- **判定**：函数参数 > 4 个。
- **症状**：调用方记不住参数顺序，写出来一片 keyword arg。
- **修复**：Introduce Parameter Object（引入参数对象）。把相关参数打包成一个 struct / dataclass / TypedDict / options 对象。
- **反模式**：直接补到 8 个参数——这是拖延，不是解决。

### 1.3 Duplicated Code（重复代码）

- **判定**：相同 / 高度相似的代码块出现 ≥3 次（Rule of Three）。
- **症状**：改了一处忘了改另外两处，行为不一致。
- **修复**：Extract Function + Extract Superclass / Module。**注意：出现 1-2 次不要急着抽**——第 3 次出现再抽，详见"过度工程"章节。

## 2. 模块 / 架构层

### 2.1 God Object / God Module（上帝对象 / 上帝模块）

- **判定**：单个类 / 文件被 ≥5 个不相关模块依赖；或单个类字段 > 15 个、方法 > 20 个。
- **症状**：import 这个文件就引入了一坨不想引入的东西。
- **修复**：按职责拆。如果类名是 `Manager` `Helper` `Utils` 三个词都在里面，**几乎一定是上帝类**。

### 2.2 Feature Envy（功能依恋）

- **判定**：一个方法 80% 都在访问另一个类的字段，自己类的字段几乎不用。
- **症状**：调试时跳来跳去都跳到别人家。
- **修复**：Move Method（搬方法）。把这个方法挪到它最依恋的那个类里。

### 2.3 Inappropriate Intimacy（过度亲密）

- **判定**：两个类相互直接访问对方的 private 字段；或两个模块循环 import。
- **症状**：动一个全盘崩溃。
- **修复**：Move Method / Extract Class 把共有逻辑抽到第三方；或重新审视模块边界。

### 2.4 Shotgun Surgery（散弹枪修改）

- **判定**：改一个需求，要改 ≥5 个文件。
- **症状**：每次加 feature 都像做考古。
- **修复**：Move Method / Move Field 把相关逻辑聚合到同一个类 / 模块。

## 3. 错误处理层（vibe coding 最高频漏点）

### 3.1 Swallowed Exception（吞错）

- **判定**：
  - Python: `except: pass` / `except Exception: pass`
  - JS/TS: `catch (e) {}` / `.catch(() => {})`
  - Java: `catch (Exception e) { }`
- **症状**：线上出问题查不到日志。
- **修复**：**至少要 log**。更进一步：把异常转换 / 包装成有意义的领域错误向上抛。

### 3.2 Bare Rescues（裸救）

- **判定**：`except: ...` 而不是 `except SpecificError: ...`
- **症状**：`KeyboardInterrupt` `SystemExit` 也被吞了，Ctrl+C 都按不掉。
- **修复**：明确写 `except SpecificError`，别用裸 `except:`。

### 3.3 Return Null / Return None Hell（返回 null 之渊）

- **判定**：函数返回 `None` / `null` / `undefined` 但调用方直接 `.method()`。
- **症状**：经典的 `Cannot read property 'x' of undefined`。
- **修复**：
  - 用 Result 类型（Rust 风格 / Python `Result` / TS `never` 模式）
  - 用 Null Object Pattern（返回空对象）
  - 在边界处显式校验并抛错
  - **不要**：在 20 个调用点都加 `if (x == null) return null`——这只是把问题传染给下游。

### 3.4 Happy Path Programming（只写顺利路径）

- **判定**：函数里只处理了"输入对、依赖在、网络通"的情况。
- **症状**：本地跑得好好的，线上分分钟挂。
- **修复**：对每个 I/O / 外部依赖 / 用户输入**显式列出失败模式**，每种都给处理或显式抛出。

### 3.5 Unhelpful Error Message（无用的错误信息）

- **判定**：抛错 / 返回的信息是 `e.toString()` / `str(e)` / `print(e)` 直接给用户。
- **症状**：用户看到 `JSONDecodeError: Expecting value: line 1 column 1 (char 0)` 不知道是哪儿挂了。
- **修复**：错误信息三要素——**发生了什么、在哪儿发生、用户该做什么**。例：
  - 不好：`Error: timeout`
  - 好：`获取用户头像超时（5s），请检查用户 ID 12345 是否存在，或稍后重试`

## 4. 命名与可读性

### 4.1 Magic Numbers / Strings

- **判定**：代码里出现裸数字 / 字符串，且无法从上下文直接看出含义。
- **症状**：3 个月后回来看，**0 知道**那个 `86400` 是一天还是一秒。
- **修复**：Extract Constant（提取常量）。命名时说明单位：`SECONDS_PER_DAY = 86400` `MAX_RETRY_COUNT = 3`。

### 4.2 Cryptic Names（神秘命名）

- **判定**：
  - 单字母变量（除循环索引 / 极短 lambda 参数）
  - `tmp` `data` `result` `obj` `x` `a` `b` 等无意义名字
  - 缩写不一致（`usr` vs `user` vs `u` 混用）
- **修复**：让名字说出意图。如果实在想不出好名字，**说明这块逻辑本身没想清楚**——先理清逻辑再命名。

### 4.3 Comments Lie（注释撒谎）

- **判定**：注释和代码不一致；或注释解释"做了什么"而不是"为什么"。
- **症状**：注释比代码更不可信。
- **修复**：
  - 解释"为什么"（`// 必须是先减后加，因为……`）——保留
  - 解释"做了什么"（`// 循环遍历用户`）——删，代码自己会说话

## 5. 抽象层（vibe coding 第二高频坑）

### 5.1 Premature Abstraction（过早抽象）

- **判定**：为一个只出现 1-2 次的 pattern 抽出基类 / 策略 / 工厂。
- **症状**：半年后回头看，所谓的"通用框架"只支撑了 1 个用例。
- **修复**：Rule of Three——**同一个 pattern 出现第 3 次再抽象**。在第 1、2 次时，允许重复。

### 5.2 Speculative Generality（投机式泛化）

- **判定**：方法 / 参数 / 配置项根本没被用到，但被加上了"以防万一"。
- **症状**：抽象的迷宫，真正用到的东西埋在最里面。
- **修复**：YAGNI（You Aren't Gonna Need It）。删。**真需要时再加**。

### 5.3 Configuration-Driven Everything（配置驱动一切）

- **判定**：业务逻辑塞进 config 文件（YAML / JSON / TOML），通过读 config 决定行为。
- **症状**：半年后你自己都搞不清 config 配错会发生什么。
- **修复**：config 只放**值**（端口、超时、开关），不放**逻辑**。如果一段行为需要读 config 才搞得清，**那是代码问题，不是配置问题**。

### 5.4 Indirect Layers（多层间接）

- **判定**：调用链 `A → B → C → D`，其中 B 和 C 啥都不干只传话。
- **症状**：调试时像在迷宫里走。
- **修复**：Inline Class（内联） / Remove Middle Man（搬掉中间人）。如果中间层不增加价值，删。

## 6. 测试与可观测性

### 6.1 No Tests At All（完全没测试）

- **判定**：交付的代码无任何测试，且不是一次性脚本。
- **修复**：至少写 1-2 个 happy path + 1 个核心边界 case。**不要追求覆盖率，追求关键路径**。

### 6.2 Tests That Don't Test（假测试）

- **判定**：测试只 mock 了所有依赖，断言全是 `expect(true).toBe(true)`。
- **修复**：测试要测"在某种输入下，产生某种输出"。如果测不出行为，删掉这个测试。

### 6.3 Print Debugging Left In（残留 print）

- **判定**：代码里残留 `print()` `console.log()` `System.out.println()` 在生产路径上。
- **修复**：用 logger；或者删。**不要让 print 上线**。

---

## 使用建议

1. **不要死记硬背**：本目录是"参考书"，不是"题库"。先看症状，匹配到反模式，再看修复。
2. **不要一次整改完**：发现 10 个 smell 时，先整 P0 / P1，剩下的让用户决定。
3. **保留历史**：如果某个 smell 在团队里被反复"赦免"（如"我们就是用单字母变量"），记到团队风格文档里，不要每次都拦。
