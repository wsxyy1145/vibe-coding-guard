# Refactor Playbook — 重构手法手册

> 本文件按需加载。SKILL.md 主流程提到"给具体拆分方案"时，从本手册取对应手法。**包含示例代码（Python + TS 双语示例）。**

## 1. Extract Function（提取函数）

**适用**：长函数 / 一段独立逻辑被注释 header 分隔。

### 模式

```
# Before
def process_order(order):
    # === validate ===
    if not order.id: raise ValueError(...)
    if order.amount <= 0: raise ValueError(...)
    # === total ===
    total = sum(item.price * item.qty for item in order.items)
    # === save ===
    db.save(order)
    return total

# After
def process_order(order):
    validate_order(order)
    total = calc_total(order)
    db.save(order)
    return total

def validate_order(order): ...
def calc_total(order): ...
```

### 步骤

1. 找一段有清晰意图的代码块（通常以注释 / 空行分隔）
2. 起一个名字——**这个步骤里最花时间的就是起名字**，别将就
3. 复制粘贴为独立函数，声明需要的参数和返回值
4. 把原代码替换为函数调用
5. 跑测试

### 命名原则

- 函数名是**动词** + **宾语**：`validate_order` `calc_total` `send_email`
- 避免 `process` `handle` `do_thing` 这种万能词
- 名字要能回答"做完这个调用，调用方能拿到什么"或"调用方要传什么进去"

---

## 2. Extract Constant（提取常量）

**适用**：magic number / magic string。

```
# Before
if retry_count > 3: ...
time.sleep(86400)
status_code = 200

# After
MAX_RETRY_COUNT = 3
SECONDS_PER_DAY = 86400
HTTP_OK = 200

if retry_count > MAX_RETRY_COUNT: ...
time.sleep(SECONDS_PER_DAY)
status_code = HTTP_OK
```

### 命名原则

- 全大写 + 下划线（Python 风格）/ UPPER_SNAKE（TS/JS 风格）
- **带上单位**：`TIMEOUT_MS = 5000` `MAX_SIZE_MB = 100`（**永远不要**让读者猜单位）
- **带上含义**：`RETRY_COUNT_FOR_NETWORK_ERROR = 3` > `RETRY = 3`

---

## 3. Introduce Parameter Object（引入参数对象）

**适用**：函数参数 ≥ 4 个 / 多处传递相同组合的参数。

```
# Before
def create_user(name, email, age, role, department, manager_id): ...

# After
@dataclass
class CreateUserParams:
    name: str
    email: str
    age: int
    role: str
    department: str
    manager_id: int

def create_user(params: CreateUserParams): ...

# 调用
create_user(CreateUserParams(name="...", email="...", ...))
```

### 收益

- 未来加字段不用改所有调用点
- 字段自带类型提示和默认值
- 调用方代码更可读（`create_user(CreateUserParams(...))` vs `create_user(name, email, age, ...)` 哪个好记？）

---

## 4. Replace Magic Conditional with Polymorphism（用多态替代条件分支）

**适用**：同一组 if/elif 在多处重复 / 类型分支散落。

⚠️ **慎用**——这是经典"过度工程"温床。**只在 if/elif 出现 ≥3 次时才考虑**。

```
# Before（如果只用一次，就别动）
def render(item):
    if item.type == "video": return render_video(item)
    if item.type == "audio": return render_audio(item)
    if item.type == "doc":   return render_doc(item)

# After（用 Registry / Strategy）
RENDERERS = {
    "video": render_video,
    "audio": render_audio,
    "doc":   render_doc,
}

def render(item):
    renderer = RENDERERS.get(item.type)
    if not renderer: raise ValueError(f"unknown type: {item.type}")
    return renderer(item)
```

**反例**：下面这种"if/elif 只出现 1 次，但有 5 个分支"——**别动**，if/elif 在这里最清楚。

---

## 5. Replace Error Code with Exception（用异常替代错误码）

**适用**：函数返回 -1 / null / enum error code 表示失败。

```
# Before
def divide(a, b):
    if b == 0: return -1, "division by zero"
    return a / b, None

# After
def divide(a, b):
    if b == 0: raise ValueError("division by zero")
    return a / b
```

### 收益

- 调用方不再忘记检查错误码
- 错误信息自带 stack trace
- 异常可被上层统一捕获处理

### 何时**不要**用异常

- 业务上的"预期失败"（如"用户输入密码错误"）——用 Result / Either
- 性能极敏感的热路径——异常构造 stack trace 有成本

---

## 6. Move Method / Move Field（搬方法 / 搬字段）

**适用**：Feature Envy / 上帝类。

```
# Before
class Order:
    def customer_name(self): return self.customer.name
    def customer_email(self): return self.customer.email
    def customer_phone(self): return self.customer.phone
    # ... 50 个方法都在问 customer 字段

# After
class Order:
    def customer_info(self): return self.customer.summary()

class Customer:
    def summary(self): return f"{self.name} <{self.email}>"
```

**判断方法**：数一数方法里 `self.customer.xxx` 出现几次。如果比 `self.xxx` 多——**搬**。

---

## 7. Decompose Conditional（分解条件表达式）

**适用**：复杂 if 条件 / 三元表达式 / 嵌套条件。

```
# Before
if date.before(SUMMER_START) or date.after(SUMMER_END):
    charge = quantity * winter_rate + winter_service_charge
else:
    charge = quantity * summer_rate

# After
if is_winter(date):
    charge = winter_charge(quantity)
else:
    charge = summer_charge(quantity)
```

**收益**：每个函数名告诉你"什么算冬天"，省得你解 `date.before(...) or date.after(...)` 的逻辑。

---

## 8. Replace Nested Conditional with Guard Clauses（卫语句替代嵌套）

**适用**：if/else 嵌套 / 早返回缺失。

```
# Before
def get_pay_amount(employee):
    result = 0
    if employee.is_separated:
        result = separated_amount(employee)
    else:
        if employee.is_retired:
            result = retired_amount(employee)
        else:
            if employee.on_vacation and employee.days_vacation > 5:
                result = vacation_amount(employee)
            else:
                result = normal_pay_amount(employee)
    return result

# After
def get_pay_amount(employee):
    if employee.is_separated: return separated_amount(employee)
    if employee.is_retired: return retired_amount(employee)
    if employee.on_vacation and employee.days_vacation > 5:
        return vacation_amount(employee)
    return normal_pay_amount(employee)
```

**原则**：每个 if 都是"如果 X 就不做 Y"，用早返回；不要堆 if/else 塔。

---

## 9. Introduce Assertion（引入断言）

**适用**：函数入口校验 / 中间状态校验。

```
def divide(a, b):
    assert b != 0, "divisor must be non-zero"  # 调用方责任的契约
    return a / b

def process(orders):
    assert orders, "orders must not be empty"  # 中间状态契约
    ...
```

**注意**：断言 ≠ 业务校验。业务校验用 `if ... raise`；断言用于"程序员的契约"，生产环境通常禁用。

---

## 10. Replace Constructor with Factory Function（用工厂函数替代构造函数）

**适用**：构造逻辑复杂 / 需要根据参数返回不同子类。

```
# Before
class Shape:
    def __init__(self, type, *args):
        if type == "circle": self.radius = args[0]
        elif type == "rect": self.width, self.height = args

# After
class Shape:
    @classmethod
    def circle(cls, radius): return Circle(radius)
    @classmethod
    def rect(cls, w, h): return Rect(w, h)
```

**注意**：这是少数**值得早做**的抽象之一——`Circle(r)` 比 `Shape("circle", r)` 自带防呆。

---

## 实战建议

### 一次只做一个改动

**不要**同时做 Extract Function + Rename + Introduce Param Object + ...——你会迷失。每个 commit 只做一个改动，跑一次测试，commit，再做下一个。

### TDD 是最好的重构保险

如果你有测试覆盖，重构是**安全**的（红了就回滚）；没测试覆盖，重构是**赌博**。先补测试，再重构。

### 警惕"重构成瘾"

有些 smell 看着不爽，但实际无害（如一个 90 行的函数如果纯线性、可读、命名清晰，**别动它**）。本手册的每条手法都有**适用场景**——不符合场景就别用。

### 保留 commit 历史

每次重构独立 commit，message 写清"为什么"：

```
refactor(orders): extract validate_order() to clarify contract
```

不要：

```
refactor: cleanup
```

——三个月后你自己都看不懂改了什么。
