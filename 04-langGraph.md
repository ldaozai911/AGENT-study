# 一 LangGraph

## **1 LangGraph 是什么？**

**LangGraph** 是 LangChain 生态中专门用于**构建有状态、多角色、复杂工作流的智能体框架**。它的核心特点是基于**图结构（Graph）**来编排 AI 应用，而不是传统的链式结构。

可以这样理解：

- **LangChain**：线性流程，像流水线一样顺序执行
- **LangGraph**：图状流程，可以有顺序，循环、分支、状态回溯，更像程序流程图

**LangGraph 是专为构建多智能体（Multi-Agent）系统而设计的架构框架**。它将复杂的协作流程定义为一张**有向状态图（StateGraph）**，每个智能体或功能模块都是图中的一个节点，通过“边”来定义它们之间的流转和交互逻辑

## **2 LangGraph vs LangChain 核心差异**

| 维度        | LangChain      | LangGraph         |
| --------- | -------------- | ----------------- |
| **工作流结构** | 线性链（Chain）     | 图结构（Graph）        |
| **循环支持**  | 不支持            | 原生支持循环            |
| **状态管理**  | 依赖外部           | 内置状态图（StateGraph） |
| **控制粒度**  | 高层抽象，较简单       | 精细控制每个节点和边        |
| **适用场景**  | 问答、RAG、摘要，单智能体 | 复杂 Agent、多智能体协作   |

**1 既然有了 LangGraph，还需要 LangChain 吗？**

**需要，而且它们是互补的，不是替代关系。**

- **LangChain 是"基础"**：它为 LangGraph 提供了所有基础组件。比如，你在 LangGraph 的节点（Node）里调用的 `ChatModel`、`Tool`，以及记忆模块，几乎都来自 LangChain。可以理解为，LangGraph 运行在 LangChain 提供的"物料"之上。
- **LangGraph 是"进阶"**：当你的应用逻辑超出简单的链式调用，需要一个更强大、更可控的"骨架"来承载复杂流程时，LangGraph 就是最佳选择。

**2 控制 Token 消耗**

**相比直接使用 LangChain Agent，LangGraph 确实更容易控制 Token 消耗**，但并不是 LangGraph 本身能减少 Token，而是因为它提供了更精细的流程控制能力。

为什么 LangGraph 更容易控制 Token

1. 节点级控制，避免无意义的大模型调用
2. 条件路由代替 LLM 决策
3. 缓存节点结果
4. 中断机制减少重复推理
5. 多智能体拆分

**LangGraph 作为多智能体架构的设计原理**

它的核心模型可以概括为三个要素

1. **State（共享状态）**：这是多智能体协作的“共享白板”，存储了任务信息、中间结果和对话历史等。所有智能体（节点）都能读取和修改这个状态，实现了信息的透明传递。
2. **Node（节点）**：每个节点代表一个独立的功能单元。它既可以是一个拥有特定工具的专业智能体（如“研究员”或“程序员”），也可以是一个简单的函数或一次大模型调用
3. **Edge（边）**：定义了节点之间的流转路径。LangGraph 支持**条件边（Conditional Edge）**，这意味着系统可以根据当前状态（State）的结果，动态决定“下一步该执行哪个智能体”，这是实现复杂决策和路由的关键

## 3 环境安装

```
pip install -U langgraph
```



##  4 LangGraph 核心组件

### 4.1 总体介绍

 总体先建立一个“脑图”

```
用户输入
   ↓
State（数据）
   ↓
Node（处理）
   ↓
Edge（决策）
   ↓
下一Node or 结束

```

一句话：

> LangGraph = **数据在节点之间流动 + 流程被你控制**



### 4.2 State（状态）

系统的“血液”

**1. 本质（一定要理解）**

> State = 在整个流程中流动的“数据容器”



 **2. 通俗理解**

你可以这样记：

State 就像：

- ：**全局变量（但更安全）**

 **3. 真实案例（发邮件系统）**

用户说：

```
给张三发邮件，说今晚开会

```

**State 设计：**

```python
from typing_extensions import TypedDict,Annotated
from langchain.messages import AnyMessage
import operator
"""
节点
"""
class State(TypedDict):
    # 消息
    messages: Annotated[list[AnyMessage], operator.add]
    # 用户名
    name: str
    # 用户邮箱
    user_email: str
    # 邮件标题
    title: str
    # 邮件内容
    content: str
    #执行结果
    result: str
```

**关键机制**

```
messages: Annotated[list[AnyMessage], operator.add]
```

每个节点返回的 messages 都会“自动追加”

**案例解释**

实际数据变化

**初始：**

```
messages = [
    HumanMessage("给张三发邮件")
]

```

**LLM判断后：**

```
messages = [
    HumanMessage("给张三发邮件"),
    AIMessage("我要调用数据库查邮箱")
]


```

**工具执行后：**

```
messages = [
    HumanMessage(...),
    AIMessage(...),
    ToolMessage("zhangsan@qq.com")
]

```

### 4.3 Node（节点）

什么是节点？

可以是普通函数，可以调用LLM的函数，可以执行调用工具的函数，也可以是一个agent

- 节点 = 工作流中的一个执行单元；智能体、工具调用、普通函数都可以被封装成节点
- 把复杂 Agent 系统拆成一个个 Node，然后用 Edge 把它们组织成工作流



```python
from langchain_core.messages import HumanMessage

from model.my_model import MyModel
from tool.send_email_tool import send_email_tool
from langchain.agents import create_agent
from pydantic import BaseModel,Field

class EmailParams(BaseModel):
    name:str =Field(...,description="收件人姓名")
    title:str =Field(...,description="邮件标题")
    content:str =Field(...,description="邮件内容")


def parse_node(state:State):
    #1 创建大语言模型
    model = MyModel.get_local_model()
    #2 创建工具
    tools = []
    #3 创建提示词
    prompt ="""
      一 你是一个信息提取助手
      二 任务：
            1 从用户输入中提取收件人姓名，邮件标题，邮件内容
      三 规则：
             - 收件人姓名,邮件标题和内容不能为空
      四 输出:
            1 提取收件人姓名，邮件标题，邮件内容
      五 示例:
            输入：给张三发送邮件，标题是测试，内容是这是一封测试邮件
            输出：张三 测试 测试邮件
    """
    #4 创建智能体或者创建代理
    agent = create_agent(
        model=model,#模型
        tools =tools,#工具
        system_prompt=prompt,#提示词
        response_format=EmailParams,#输出格式

    )
    #5 提问
    rs = agent.invoke(
        {"messages":[
            {
                "role":"user",
                "content":state["messages"]
            }
        ]}
    )
    data = rs["structured_response"].model_dump()

    return {
           "result": f"给用户：{data.get("name")}发邮件，邮件标题是:{data.get("title")},邮件内容是:	{data.get("content")}",
        "name": data.get("name"),
        "title": data.get("title"),
        "content": data.get("content"),
        "messages": [AIMessage(content=f"给用户：{data.get("name")}发邮件，邮件标题是:{data.get("title")},邮件内容是:	{data.get("content")}")]
    }


```

**state只返回“变化的部分”**



**🔹 2）数据库节点**

```python
from langchain_core.messages.tool import tool_call

from tools.mysql_tool import mysql_tool
from demo02.state.state import State
from langchain.messages import HumanMessage,AIMessage
def query_node(state:State):
    #获取用户名
    name = state["name"]
    #定义sql
    sql =f"select * from user_info where user_name='{name}'"
    #查询用户邮箱
    rs = mysql_tool.invoke({"sql":sql})
    if len(rs) ==1:
      email = rs[0][2]
      return {
            "result": "查询到用户邮箱",
          "user_email": email,
          "messages": [AIMessage(content=f"查询用户{name}的邮箱是{email}",tool_call_id="query_node")]
      }
    else:
      email = None
      return {
           "result": "没有查询到邮箱",
          "user_email": email,
          "messages": [AIMessage(content="没有查询到邮箱",tool_call_id="query_node")]
      }

```

🔹 3）**邮件**节点

```python
from langchain.messages import AIMessage
from tools.send_email_tool import send_mail_tool
from demo02.state.state import State
"""
发送邮件 智能体节点
"""
def email_node(state:State):
   email = state["user_email"]
   #标题
   title = state["title"]
   #邮件内容
   content = state["content"]
   #发送邮件
   rs = send_mail_tool.invoke({"email":email,"subject":title,"content":content})
   return {
      "result": f"发送邮件成功，收件人为：{email}",
      "messages": [AIMessage(content=f"发送邮件成功，收件人为：{email}",tool_call_id="email_node")]
   }


```



 **核心认知（非常重要）**

```
LLM负责“想”
Node负责“执行”
```



### 4.4 Edge（边）

Edge 负责定义：

> **Node 执行完之后，下一步去哪？**

**——流程控制器**

    1. 本质

> Edge = 控制流程怎么走

 **2. 通俗理解**

 Edge 就像：

- if / else
- 路由
- 流程图箭头

**3. 两种类型**

🔹 普通边（顺序执行）

```
    #定义边
    builder.add_edge("parse", "query")
    builder.add_edge("query", "mail")
    builder.add_edge("mail", END)

```



 **关键理解**

> Edge 决定系统“是不是可控”



### 4.5 Conditional Edge（条件边）

**——智能决策核心，通俗说法-路由**

**1. 本质**

> 根据 State 决定下一步

    2. 通俗理解

就是：

```
if (条件):
    去A
else:
    去B

```

**3. 案例（真实企业逻辑）**

用户输入：

```
查一下用户数据

```

**路由函数：**

```
def route(state):
    text = state["messages"][-1].content

    if "查" in text:
        return "sql_node"
    elif "邮件" in text:
        return "email_node"
    else:
        return END

```

 **4. 对比 Agent（非常重要）**

```
Agent：模型自己决定流程 
LangGraph：你写逻辑控制流程 

```

**核心价值**

> 让AI系统“像后端程序一样稳定”

### 4.6 Graph（大脑）

**——系统大脑**

**1. 本质**

> Graph = 把所有节点 + 流程拼起来

 **2. 通俗理解**

 Graph 就像：

- 后端系统
- 工作流引擎
- 调度中心

**3  常见函数介绍**

**一、`StateGraph()` —— 创建状态图**

```
from langgraph.graph import StateGraph

graph = StateGraph(State)
```

作用：

> 创建一个基于 `State` 的 Graph。

**二、`add_node()` —— 添加节点** 

```
graph.add_node("model", model_node)
```

作用：

> **向 Graph 中添加一个执行单元。**

**三、`add_edge()` —— 添加普通边** 

```
graph.add_edge("node1", "node2")
```

作用：

> **规定 node1 执行完以后进入 node2。**

**四、`add_conditional_edges()` —— 添加条件**边 ⭐⭐⭐⭐⭐

这个是做 Agent 时非常重要的。

```
graph.add_conditional_edges(
    "router",
    router_function,
    {
        "chat": "chat_node",
        "sql": "sql_node"
    }
)
```

意思是：

```
                 ┌── chat_node
                 │
router ──────────┤
                 │
                 └── sql_node
```

**五、`set_entry_point()` —— 设置入口**

```
graph.set_entry_point("model")
```

意思：

```
START
  ↓
model
```

不过在现在的 LangGraph 学习中，更推荐你理解并使用：

```
graph.add_edge(START, "model")
```

也就是说：

```
graph.set_entry_point("model")
```

可以理解成一种更直观的“设置入口”方式，而：

```
graph.add_edge(START, "model")
```

更能体现 LangGraph 的图结构思想



**`六 END` —— 与 START 相对应**

虽然 `END` 不是起点，但是初学者最好和 `START` 一起理解。

```
from langgraph.graph import START, END
```

它们可以理解为：

```
START = 开始
END   = 结束
```

例如：

```
graph.add_edge(START, "model")
graph.add_edge("model", END)
```

就是：

```
START
  ↓
model
  ↓
```

**七、`compile()` —— 编译 Graph** 

Graph 定义完成以后：

```
app = graph.compile()
```

作用：

> **把我们定义好的 Graph 编译成真正可以执行的对象。**



 **4. 完整案例**

```python
from langgraph.graph import StateGraph, END
from demo02.state.state import State
from demo02.node.email_node import  email_node
from demo02.node.parse_node import parse_node
from demo02.node.query_node import query_node

def build_graph():
    builder = StateGraph(State)

    # 注册节点
    builder.add_node("parse", parse_node)
    builder.add_node("query", query_node)
    builder.add_node("mail", email_node)

    # 定义流程（强控制关键）
    builder.set_entry_point("parse")
    #定义边
    builder.add_edge("parse", "query")
    builder.add_edge("query", "mail")
    builder.add_edge("mail", END)

    graph = builder.compile(debug=True)
    return  graph
```



**5 总结**

`StateGraph` 负责创建工作流，

`add_node()` 添加任务，

`add_edge()` 连接任务，

`add_conditional_edges()` 做条件路由，

`START` 定义入口，

`END` 定义出口，

`compile()` 把工作流变成可执行程序。

### 4.7 总结

```
State（数据流）
   ↓
Node（处理数据）
   ↓
Edge（决定去哪）
   ↓
Conditional Edge（决策）
   ↓
Graph（整体调度）

```

**一句话总结**

 State

> 数据在系统里怎么流动

 Node

> 谁在干活

Edge

> 流程怎么走

Conditional Edge（决策）

   实现**路由、决策、Agent 工作流**的核心。决策核心

 Graph

> 整个系统怎么跑

 

思维转变：

```
写AI代码 
```

变成：

```
设计AI系统 
```



**State 管数据，Node 干事情，Edge 管流程，Conditional Edge 做决策，Graph组装节点和流程**

**LangGraph 核心公式**

```
LangGraph = State（状态） + Node（节点） + Edge（边） + Compile（编译）
```



## 5. 四种图模式详解

****

| 模式     | 特点                             | 核心方法                                | 典型场景                 |
| ------ | ------------------------------ | ----------------------------------- | -------------------- |
| 顺序图    | 直线流水线                          | `add_edge(A, B)`                    | 固定流程的处理链             |
| 条件图    | 动态分支                           | `add_conditional_edges()`           | 意图识别 + 多路由           |
| 循环图    | 自我修正                           | 条件边指回前序节点                           | 重试、验证、迭代优化           |
| 动态路由架构 | 主管节点动态决策，运行时选择下一个执行节点，支持多轮循环调度 | `Command(goto=next_node)` + 循环边回到主管 | 多智能体协作、任务自动规划、复杂决策系统 |



### 5.1 模式一：顺序图（Sequential Graph）

**场景**：固定的直线流水线，无分支、无循环。

**流程**：`START → internet（提取信息）→ query（查邮箱）→ send_email（发邮件）→ END`

```python
def builder_graph():
    graph = StateGraph(EmailState)
    graph.add_node("internet", intenet_node)
    graph.add_node("query", query_node)
    graph.add_node("send_email", send_email_node)

    # 设置入口（两种方式任选）
    graph.set_entry_point("internet")  # 旧版方式
    # graph.add_edge(START, "internet")  # 新版方式

    graph.add_edge("internet", "query")
    graph.add_edge("query", "send_email")
    graph.add_edge("send_email", END)

    return graph.compile()
```

**调用方式**：

```python
from langchain_core.messages import HumanMessage

agent = builder_graph()
result = agent.invoke({
    "messages": [HumanMessage(
        content="给李四发一封邮件，标题是：测试，内容是：这是一封测试邮件"
    )]
})
print(result["messages"][-1].content)
```



### 5.2 模式二：条件图（Conditional Graph）

**场景**：根据用户意图动态选择处理路径。

**流程**：

```
START → router（路由判断）
         ├── email_agent → internet → query → send_email → END
         └── chat_agent  → chat → END
```

核心是**条件函数**和**条件边**：

```python
def condition(state: EmailState):
    """根据状态中的 step 字段决定走向"""
    if state["step"] == "email_agent":
        return "c"   # 走邮件流程
    else:
        return "d"   # 走聊天流程

def condition_graph(memory):
    graph = StateGraph(EmailState)
    graph.add_node("router", router_node)
    graph.add_node("chat", chat_node)
    graph.add_node("internet", intenet_node)
    graph.add_node("query", query_node)
    graph.add_node("send_email", send_email_node)

    graph.set_entry_point("router")

    # 条件边：router 执行完后，调用 condition 函数
    # 根据返回值映射到下一个节点
    graph.add_conditional_edges(
        "router",
        condition,
        {
            "c": "internet",     # 返回 "c" → 进入 internet 节点
            "d": "chat"          # 返回 "d" → 进入 chat 节点
        }
    )

    graph.add_edge("internet", "query")
    graph.add_edge("query", "send_email")
    graph.add_edge("send_email", END)
    graph.add_edge("chat", END)

    return graph.compile(checkpointer=memory)
```

**条件边的工作原理**：

```
router_node 执行 → state["step"] = "email_agent"
                    ↓
condition(state) → 返回 "c"
                    ↓
mapping {"c": "internet"} → 进入 internet 节点
```



### 5.3 模式三：循环图（Loop Graph）

**场景**：需要自我修正或重复执行直到满足条件。

**流程**：

```
START → router（路由判断）
         ├── email_agent → internet → query → send_email
         │                                     ↓
         │                          loop_condition?
         │                           ├── Yes(继续) → internet（循环）
         │                           └── No(结束)  → END
         └── chat_agent  → chat → END
```

```python
def loop_condition(state: EmailState):
    """循环条件：最多循环 3 次"""
    print(f"进入循环条件函数，当前次数：{state['count']}")
    if state["count"] > 3:
        return "end"
    else:
        return "start"

def loop_graph():
    graph = StateGraph(EmailState)
    graph.add_node("router", router_node)
    graph.add_node("chat", chat_node)
    graph.add_node("internet", intenet_node)
    graph.add_node("query", query_node)
    graph.add_node("send_email", send_email_node)

    graph.set_entry_point("router")

    # 路由条件边
    graph.add_conditional_edges("router", condition,
        {"c": "internet", "d": "chat"})

    graph.add_edge("internet", "query")
    graph.add_edge("query", "send_email")

    # 循环条件边：send_email 执行完后判断是否重新执行
    graph.add_conditional_edges("send_email", loop_condition, {
        "start": "internet",   # 继续循环 → 回到 internet
        "end": END             # 满足条件 → 结束
    })

    graph.add_edge("chat", END)
    return graph.compile()
```

**循环的关键**：在 `send_email_node` 中递增 `count`：

```python
def send_email_node(state: EmailState):
    count = state["count"] + 1   # 每次执行时计数 +1
    # ...发邮件逻辑...
    return {
        "count": count,           # 将更新后的 count 写回状态
        "messages": [AIMessage(content=msg)]
    }
```

### 5.4 模式四：动态路由（Supervisor-Worker 模式）

EmailState 状态定义

```
step:str#步骤名称
```

**主管节点**

```python
from demo.state.email_state import EmailState
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
def manager_node(state: EmailState):
    """主管：根据当前状态决定下一步"""

    current_step = state.get("step", "start")
    print(f"当前状态是：{current_step}")

    # 决策逻辑
    if current_step == "start":
        next_node = "internet"
    elif current_step == "internet_done":
        next_node = "query"
    elif current_step == "query_done":
        next_node = "send_email"
    elif current_step == "send_email_done":
        next_node = END
    elif current_step == "chat_done":
        next_node = END
    else:
        next_node = END

    # 使用 Command 动态跳转
    return Command(goto=next_node)
```

**核心功能**

`manager_node` 是一个决策节点，根据当前状态决定下一步应该执行哪个节点。

**代码解析**

1. **函数定义**

```python
def manager_node(state: EmailState):
```
- 接收 `EmailState` 类型的状态对象
- 这是LangGraph工作流中的一个节点函数

**2. 获取当前状态**

```python
current_step = state.get("step", "start")
```
- 从状态中读取 `step` 字段
- 如果不存在，默认值为 `"start"`

**3. 决策逻辑（路由表）**

这是一个**状态机**式的路由：

| 当前步骤                | 下一步            | 说明        |
| ------------------- | -------------- | --------- |
| `"start"`           | `"internet"`   | 开始→意图识别   |
| `"internet_done"`   | `"query"`      | 意图识别→查询处理 |
| `"query_done"`      | `"send_email"` | 查询完成→发送邮件 |
| `"send_email_done"` | `END`          | 邮件发送完成→结束 |
| `"chat_done"`       | `END`          | 聊天完成→结束   |
| 其他                  | `END`          | 默认结束      |

**4. 动态跳转**

```python
return Command(goto=next_node)
```
- 使用 `Command` 对象实现动态路由
- `goto` 参数指定要跳转到的下一个节点名称
- 这比静态边（`.add_edge()`）更灵活，允许运行时决策



**graph定义**

```python
def builder_graph():
    graph = StateGraph(EmailState)

    # 添加工人节点
    graph.add_node("internet", intenet_node)
    graph.add_node("query", query_node)
    graph.add_node("send_email", send_email_node)

    graph.add_node("manager_", manager_node)

    # 设置入口为主管
    graph.add_edge(START, "manager_")

    # 所有工人执行完后回到主管
    graph.add_edge("internet", "manager_")
    graph.add_edge("query", "manager_")
    graph.add_edge("send_email", "manager_")

    # 主管可以结束（goto=END）
    # 不需要 add_edge("supervisor", END)，因为 supervisor 内部可以直接 goto=END

    agent = graph.compile()
    return agent

```



## 6. 记忆管理



### 6.1 基于Postgres记忆处理

**“LangChain Agent 和 LangGraph 使用的是同一套Checkpointer 机制**

1 在流程控制中心 引入检测点

```python

def build_graph(memory):
 	#以上代码省略
    # 添加记忆
    return builder.compile(checkpointer= memory)
```

2 在对话引入PostgresSaver 完成记忆存储

```python
from graph.main_graph import build_graph
from langchain.messages import HumanMessage
from langgraph.checkpoint.postgres import PostgresSaver
import os
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":

        DB_URI = os.getenv("POSTGRES_URL")
        with PostgresSaver.from_conn_string(DB_URI) as memory:
            app = build_graph(memory)
            thread_id = "user_001"
            while True:
                user_input = input("请输入：")
                config = {
                    "configurable": {
                        "thread_id": thread_id
                    }
                }
                result = app.invoke(
                    {"messages": [HumanMessage(content=user_input)]},
                    config=config
                )
                print(result["messages"][-1].content)
```

### 



## 7 画流程图



langGraph 老版本需要安装 ：pip install grandalf  才能显示

```python
def test():
    graph = build_graph()

    png_data = graph.get_graph().draw_mermaid_png()

    with open("workflow.png", "wb") as f:
        f.write(png_data)

    print("流程图生成成功")

```



## 8.流式输出

**yield 关键字解释**

> **yield 是 Python 中的生成器关键字，用于返回一个值并暂停函数执行。下次继续迭代时，函数会从上次暂停的位置继续执行，而不是重新开始。**

**yield 与 return 的区别**

| 关键字    | 功能        |
| ------ | --------- |
| return | 返回结果并结束函数 |
| yield  | 返回结果并暂停函数 |

**yield 的特点**

- 函数中出现 `yield` 后，该函数会变成**生成器（Generator）**。
- 数据按需生成，不会一次性全部返回。
- 适用于流式输出、大数据处理、异步任务等场景。
- LangGraph 的 `astream()` 等流式接口底层就是通过生成器机制逐步返回数据。

**一句话理解**

> **return 是“返回并结束”，yield 是“返回并暂停”**

### 8.1 astream 接口

`astream()` 是 LangGraph 中最重要的异步流式接口之一，它允许你**边执行图（Graph），边获取执行结果**。



| 模式       | 本质         |
| -------- | ---------- |
| messages | LLM Token流 |
| updates  | State状态流   |

**1 messages 模式**

```python
async def test04():
    graph = build_graph()
    input = {
        "messages": [
            HumanMessage(content="给张三你发个邮件，说今晚开会")
        ]
    }
    async for chunk, metadata in graph.astream(input, stream_mode="messages",):
            yield chunk.content
```

**测试代码**

```python
    import asyncio
    async def run():
        async for text in test05():
            print(text, end="")  # 输出流式生成的文本
    asyncio.run(run())
```

**为什么前面所有的content都是空，后期才有数据？**

因为 LangChain / LangGraph 在兼容：

- OpenAI
- Anthropic
- Gemini
- Tool Call
- Function Call

这些协议时。

消息流会拆成：

| 阶段              | 内容         |
| --------------- | ---------- |
| 初始化chunk        | 空content   |
| role chunk      | assistant  |
| tool_call chunk | 工具调用信息     |
| thinking chunk  | 推理信息       |
| 真正token chunk   | 开始有content |

所以：

```
content=''不代表没工作。而是：“消息流已经开始，但 token 还没出来”。
```

**正确做法**

你应该过滤空 content：

```python
async for chunk, metadata in graph.astream(
        input,
        stream_mode="messages"
):
    if hasattr(chunk, "content") and chunk.content:
        yield chunk.content
```

适合：

- ChatGPT 打字机效果
- token 流输出

**2 updates 模式**

```python
async def test05():
    graph = build_graph()
    input = {
        "messages": [
            HumanMessage(content="给张三你发个邮件，说今晚开会")
        ]
    }
    async for chunk in graph.astream(input, stream_mode="updates"):
            yield chunk.content
```

updates 返回：节点状态更新。

例如：

```
{
   "parse": {
       "result": ...
   }
}
```

适合：

- 工作流监控
- 前端显示节点状态



**真正动态显示节点状态的写法**

```python
    async for chunk in graph.astream(input, stream_mode="updates"):

            if "parse" in chunk:
                yield chunk["parse"]["result"]
            if "query" in chunk:
                yield chunk["query"]["result"]
            if "mail" in chunk:
                yield chunk["mail"]["result"]
```



### 8.2 astream_events 接口

获取的就是 **Graph运行过程中产生的所有底层事件（Event）**。

**1 astream_events是什么**

官方定义：

```
流式获取Runnable执行过程中的所有事件
```

包括：

```
Graph开始
↓
Node开始
↓
LLM开始
↓
Token输出
↓
Tool开始
↓
Tool结束
↓
Node结束
↓
Graph结束
```

全部都能监听。

**2 基本语法**

```
async for event in graph.astream_events(
    input,
    version="v2"
):
    yield event
```

**返回数据结构**

例如：

```
{
    "event":"on_chain_start",
    "name":"chatbot",
    "run_id":"xxx",
    "data":{}
}
```

字段说明：

| 字段         | 作用    |
| ---------- | ----- |
| event      | 事件名称  |
| name       | 节点名称  |
| run_id     | 运行ID  |
| parent_ids | 父节点ID |
| tags       | 标签    |
| metadata   | 元数据   |
| data       | 具体数据  |

**3 最重要的事件**

**1 on_chain_start**

节点开始执行

```
{
    "event":"on_chain_start",
    "name":"chatbot"
}
```

说明：

```
chatbot节点开始
```

**2 on_chain_end**

节点结束

```
{
    "event":"on_chain_end",
    "name":"chatbot"
}
```

说明：

```
chatbot节点完成
```

**3 on_chat_model_start**

LLM开始

```
{
    "event":"on_chat_model_start"
}
```

说明：

```
正在调用DeepSeek
```

或者：

```
正在调用GPT
```



**4 on_chat_model_stream**

Token流

这是最常用的。

```
{
    "event":"on_chat_model_stream",
    "data":{
        "chunk":"你"
    }
}
```

然后：

```
{
    "event":"on_chat_model_stream",
    "data":{
        "chunk":"好"
    }
}
```

然后：

```
{
    "event":"on_chat_model_stream",
    "data":{
        "chunk":"呀"
    }
}
```

拼接：

```
你好呀
```

------

**5 on_chat_model_end**

模型结束

```
{
    "event":"on_chat_model_end"
}
```

说明：

```
LLM推理结束
```

------

**6 on_tool_start**

工具开始

例如：

```
@tool
def query_db():
    pass
```

执行时：

```
{
    "event":"on_tool_start",
    "name":"query_db"
}
```

**7 on_tool_end**

工具结束

```
{
    "event":"on_tool_end",
    "name":"query_db"
}
```



**过滤指定事件**

一般不会全部打印。

例如：

```
async for event in graph.astream_events(
    input,
    version="v2"
):

    if event["event"]=="on_chat_model_stream":
        print(event)
```

只监听：

```
Token流
```

或者：

```
if event["event"]=="on_tool_start":
```

监听：

```
工具调用
```

### 8.3 astream 与 astream_events 区别

很多人容易混淆。

**astream**

关注：

```
状态(State)
```

例如：

```
{
   "manager":{
      "approve":"同意"
   }
}
```

你拿到的是：

```
节点返回值
State变化
```

**astream_events**

关注：

```
执行事件(Event)
```

例如：

```
{
    "event":"on_chain_start"
}
```

它比 `astream()` 更底层。

## 9  HITL（人工审核机制）

LangGraph 的人工审核机制（Human-in-the-Loop，简称 HITL）本质上是一种**工作流暂停（Interrupt）+ 人工确认 + 继续执行（Resume）**的机制。它允许智能体在执行关键操作前暂停，等待人工审核后再继续执行。

对于企业级智能体来说，这是非常重要的能力，例如：

- 请假审批系统
- 邮件发送系统
- 财务报销系统
- 数据删除系统
- SQL执行系统
- AI生成内容审核系统

**流程图**

```
┌──────────────────────────────────────────┐
│ Agent生成邮件草稿                       │
│ 收件人: boss@company.com                  │
│ 内容: 项目延期通知                          │
└────────────────┬─────────────────────────┘
                 ▼
┌──────────────────────────────────────────┐
│ 调用 interrupt()                          │
│ 请求人工审核                               │
└────────────────┬─────────────────────────┘
                 ▼
┌──────────────────────────────────────────┐
│ 工作流暂停                                 │
│ 等待人类决策                               │
└────────────────┬─────────────────────────┘
                 ▼
┌──────────────────────────────────────────┐
│ 📨 发送审核通知给人类                       │
│ 展示邮件草稿内容                            │
└────────────────┬─────────────────────────┘
                 ▼
          ┌─────────────┐
          │ 👤 人工操作  │
          └──────┬──────┘
      ┌──────────┼──────────┐
      ▼          ▼          ▼
  ┌──────┐  ┌──────┐  ┌──────┐
  │批准   │  │修改  │   │拒绝  │
  └──┬───┘  └──┬───┘  └──┬───┘
     ▼         ▼         ▼
  ┌──────┐  ┌──────┐  ┌──────┐
  │发送邮件│ │修改内容│ │直接结束│
  └──┬───┘  └──┬───┘  └──────┘
     ▼         ▼
  ┌──────┐  ┌──────┐
  │完成   │  │发送邮件│
  └──────┘  └──┬───┘
               ▼
            ┌──────┐
            │完成   │
            └──────┘
```

### 9.1 基于LangGraph的人机协同邮件审批智能体

   使用LangGraph构建企业级邮件发送工作流，实现用户意图解析、用户信息查询、人工审核、状态持久化和邮件发送等功能。通过Interrupt实现人工审批中断，通过Command(resume)实现断点恢复，演示LangGraph在人机协同(Human-in-the-Loop)场景下的完整开发流程。

```
+=====================================================+
|              人工审批工作流 (LangGraph)               |
+=====================================================+

                    ┌─────────────┐
                    │   开始执行   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  解析节点    │
                    │ parse_node  │
                    │  解析输入   │
                    │  提取信息   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  查询节点    │
                    │ query_node  │
                    │  查询数据   │
                    └──────┬──────┘
                           │
                           ▼
              ╔═════════════════════════╗
              ║    人工审批节点         ║
              ║    approval_node        ║
              ║   触发中断，等待审批    ║
              ║   用户输入 yes/no       ║
              ╚═════════════════════════╝
                           │
                           ▼
              ┌─────────────────────────┐
              │   条件路由判断           │
              │ route_after_approval    │
              │                         │
              │  检查 state["approved"]  │
              └────────────┬────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               │               ▼
    ┌─────────────┐        │        ┌─────────────┐
    │  approved   │        │        │  approved   │
    │   = True    │        │        │   = False   │
    └──────┬──────┘        │        └──────┬──────┘
           │               │               │
           ▼               │               ▼
    ┌─────────────┐        │        ┌─────────────┐
    │  邮件节点    │        │        │  结束节点   │
    │ email_node  │        │        │    END      │
    │  发送邮件   │        │        │  流程终止   │
    └──────┬──────┘        │        └─────────────┘
           │               │
           ▼               │
    ┌─────────────┐        │
    │  结束节点   │        │
    │    END      │◄───────┘
    │  流程终止   │
    └─────────────┘


+=============================================================+
|  状态管理 & 中断恢复                                          |
+=============================================================+
|                                                             |
|  1. InMemorySaver  ──► 保存检查点 (checkpoint)              |
|                                                             |
|  2. thread_id = "1" ──► 线程标识，用于恢复状态              |
|                                                             |
|  3. interrupt 检测  ──► if state.interrupts:               |
|         └── 输出审批内容                                      |
|         └── 等待用户输入 yes/no                              |
|         └── Command(resume={"approved": approve}) 恢复执行   |
|                                                             |
|  4. astream_events ──► 流式输出事件                          |
|                                                             |
+=============================================================+


+=============================================================+
|  执行流程时序图                                              |
+=============================================================+
|                                                             |
|  用户输入 ──► 解析 ──► 查询 ──► 审批中断                   |
|                                    │                        |
|                                    ▼                        |
|                              [等待人工输入]                  |
|                                    │                        |
|                                    ▼                        |
|                              输入 yes/no                    |
|                                    │                        |
|                    ┌───────────────┴───────────────┐       |
|                    │                               │       |
|                    ▼                               ▼       |
|                 yes (通过)                      no (拒绝)   |
|                    │                               │       |
|                    ▼                               ▼       |
|                 发送邮件                        流程结束     |
|                    │                                       |
|                    ▼                                       |
|               流程结束                                     |
|                                                             |
+=============================================================+


+=============================================================+
|  节点功能说明                                                |
+=============================================================+
|                                                             |
|  1. parse_node    : 解析 HumanMessage，提取关键信息          |
|  2. query_node    : 根据解析结果查询必要数据                  |
|  3. approval_node : 触发人工审批，状态中断等待输入            |
|  4. email_node    : 发送邮件（审批通过后执行）                |
|                                                             |
+=============================================================+

```

**实现两种方式**

**第一种**

1 启动记忆，添加拦截节点之前

interrupt_before  节点之前暂停

```python
agent = graph.compile(checkpointer=memory,interrupt_before=["send_email"])
```

2 定义智能体

```python
agent = loop_graph(InMemorySaver())
config = {"configurable": {"thread_id": 1}}
async def stream_messages(question):
    q ={"messages":[HumanMessage(content=question)]}
    async for c,m in agent.astream(q,config,stream_mode="messages"):
         if c.content:
             yield c.content
```

3  人工审核-修改邮件内容

```python
#人工审核-修改邮件内容
def test01():
    q1= "给李四发一样封邮件，邮件标题是：测试邮件，邮件内容是：这是一封测试邮件"

    async  def test():
        async for chunk in stream_messages(q1):
            print(chunk, end="", flush=True)
    asyncio.run(test())
    # 查看当前状态
    state = agent.get_state(config)
    print(f"当前节点状态：{state.values}")
    info = input("请输入修改后的邮件内容：")
    # 修改邮件内容
    agent.update_state(config, {"content": info})
    #继续执行
    result = agent.invoke(None, config)  # 传 None 表示从断点继续
    print(f"继续执行结果：{result['messages'][-1].content}"
```

4 人工审核-批准和拒绝

一 ：定义一个取消节点

```python
from demo.state.email_state import EmailState

def cancel_node(state: EmailState):
    print("邮件发送已取消")
    return {}
```

二  添加取消节点，设置取消节点为 结束

```python
  graph.add_node("cancel", cancel_node)
    graph.add_edge("cancel", END)
```

三  如果批准，执行   result = agent.invoke(None, config) ，拒绝 跳转到取消节点

```python
#人工审核-批准执行
def test02():
    q1= "给李四发一样封邮件，邮件标题是：测试邮件，邮件内容是：这是一封测试邮件"

    async  def test():
        async for chunk in stream_messages(q1):
            print(chunk, end="", flush=True)
    asyncio.run(test())
    # 查看当前状态
    state = agent.get_state(config)
    print(f"当前节点状态：{state.values}")
    info = input("请输入批准执行的命令：y/n")
    if info == "y":
        result = agent.invoke(None, config)  # 传 None 表示从断点继续
        print(f"执行结果：{result['messages'][-1].content}")
    else:
        # 跳转到结束节点
        agent.invoke(Command(goto="cancel"),  config)
        print("已取消执行")
```



**第二种**

1 在状态中添加  批准实行，设置为布尔值

```python
 #是否批准
approve: bool
```

2  添加人工审核节点

```python
from langchain_core.messages import AIMessage
from langgraph.types import interrupt
from demo02.state.state import State
"""
人工审核节点
"""
def approval_node(state: State):

    approved = interrupt(
        "是否批准该申请？"
    )

    return {
        "approved": approved,
        "messages": [
            AIMessage(
                content=f"审批结果：{'通过' if approved['approved'] else '拒绝'}"
            )
        ]
    }y
```

3 引入记忆，创建一个记忆对象实例，在build_graph函数外面创建

```python
from langgraph.checkpoint.memory import InMemorySaver
memory = InMemorySaver()
def build_graph():
  #代码
```

4  定义人工审批路由，根据返回人工审核结果，调整流程走向

```python
"""
人工审批路由，根据返回人工审核结果，调整流程走向
"""
def route_after_approval(state):
    print("审批结果：", state["approved"]["approved"])
    if state["approved"]["approved"]:
        return "mail"
    print("审批拒绝")
    return "end"
```

5 定义条件边，添加记忆

```python
 def build_graph():
   #省略其它代码
  # 关键代码 ：定义条件边
    builder.add_conditional_edges(
        "approval",
        route_after_approval,
        {
            "mail": "mail",
            "end": END
        }
    )
    #添加记忆
     graph = builder.compile(checkpointer=memory)
    return  graph
```

6 定义测试函数，在问答结束后，获取当前状态，判断是否被中断，如果中断开始人工审批

- interrupt_info = state.interrupts[0] 获取审核节点定义的内容

- ```
    rs = graph.invoke(
              Command(
                  resume={
                      "approved": approve
                  }
              ),
              config=config
          )  
       #approve 接收用户返回的布尔值
       #rs 返回最终结果
    ```
  ```python

graph = build_graph()
async def test06():
    config = {
        "configurable": {
            "thread_id": "1"
        }
    }
    input_data = {
        "messages": [
            HumanMessage(content="给张三发个邮件，说今晚开会")
        ]
    }

    print("========开始执行工作流========")
    
    async for event in graph.astream_events(
            input_data,
            config=config,
            version="v2"
    ):
        yield event
    # 获取当前状态
    state = graph.get_state(config)
    
    print("\n========当前状态========")
    print(state)
    
    # 判断是否被中断
    if state.interrupts:
        print("\n========人工审批========")
        interrupt_info = state.interrupts[0]
        print("审批内容：")
        print(interrupt_info.value)
        # 人工输入
        result = input("请输入审批结果(yes/no): ")
        approve = result.lower() == "yes"
        print("审批结果：", approve)
        print("\n========继续执行========")
        rs = graph.invoke(
            Command(
                resume={
                    "approved": approve
                }
            ),
            config=config
        )
        print("\n========最终结果========")
        print(rs)
    else:
        print("流程未发生中断")

  ```

7 测试

```python
#测试流式输出
async def run():
        async for text in test06():
            print(text, end="")  # 输出流式生成的文本
if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
  ```

