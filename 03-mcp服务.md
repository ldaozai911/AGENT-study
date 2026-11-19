

# MCP 服务应用

## 1. 什么是 MCP？

MCP（Model Context Protocol）是由 **Anthropic** 公司推出的一种开放协议。它的核心目标是让大型语言模型能够与外部工具、数据源和服务进行**安全、可控、标准化**的交互。

你可以把它想象成 LLM 的“**应用商店**”或“**插件系统**”。在 MCP 出现之前，每个 AI 应用或平台（如 ChatGPT、[Claude.ai](https://claude.ai/)）都需要自己单独为每个工具或数据源开发集成，这非常低效且不统一。MCP 旨在解决这个问题。



“MCP 服务”（**Model Context Protocol 服务**）是随着 **OpenAI 在 2024 年下半年推出 MCP 标准**（Model Context Protocol）后，才逐渐开始在国内被了解和采用的

**1 2025 年国内发展现状**

到了 **2025 年**：

- **MCP 服务在国内正式兴起**，主要体现在以下几个方向：
  1. **企业内部知识问答系统**（知识库、私有化 RAG）开始使用 MCP 作为数据层接口；
  2. **LangChain 代理系统**（AgentExecutor、Tool Calling）逐步迁移到 MCP 统一协议；
  3. **FastMCP 框架** 在国内 GitHub、Gitee 上出现大量 Fork；
  4. **高校、培训课程** 开始讲授 MCP 体系（如「LangChain 智能体 + MCP 工程实战」）



 **二、MCP 的核心目标：统一协议层，打通模型上下文与外部世界**

MCP 的全称是 **Model Context Protocol**，直译是“模型上下文协议”。

它的核心理念是：

> 让任何大模型（LLM）都能**安全、统一、标准化**地访问外部数据与工具。

 **三 跨平台兼容（真正的通用标准）**

MCP 目前被：

- OpenAI（GPT 系列）
- Anthropic（Claude）
- LangChain 
- LlamaIndex
  等主流框架共同采用。

这让它成为了**AI Agent 的通用底层协议**。


## 2. 核心概念与工作原理

MCP 的架构主要包含三个核心组成部分：

1. **MCP 客户端**
   - **角色**：**使用工具**的一方。通常是指大型语言模型本身或承载模型的应用程序（如 Claude 桌面端、Cursor IDE 等）。
   - **功能**：向 MCP 服务器发送请求，例如“请查询一下北京的天气”或“请从我的数据库中获取用户列表”。
   - **举例**：Claude 桌面应用程序就是一个 MCP 客户端。
2. **MCP 服务器**
   - **角色**：**提供工具和数据**的一方。它是一个独立的进程，负责封装特定的功能或数据访问能力。
   - **功能**：暴露一系列“工具”和“资源”给客户端调用。当客户端调用一个工具时，服务器负责执行具体的逻辑（如调用 API、查询数据库、执行计算）并返回结果。
   - **举例**：一个提供天气查询 API 的服务器、一个连接到你公司数据库的服务器、一个能够执行代码的服务器。
3. **传输层**
   - **角色**：**连接客户端和服务器**的通信桥梁。
   - **实现方式**：MCP 协议本身与传输方式无关。最常见的是 **Stdio**和 **SSE**。
     - **Stdio**：客户端直接启动服务器进程，通过**标准输入和标准输出**进行通信。简单、高效，适合本地工具。
     - **SSE ,http**：客户端通过 HTTP 连接到远程的服务器。适合需要远程访问或由第三方提供的服务



##  3  环境安装

**1 安装fastmcp**

```
pip install fastmcp -i   https://mirrors.aliyun.com/pypi/simple
```

## 4  FastMCP介绍

创建 MCP（Model Context Protocol）服务主要有以下几种方式，从易到难、从快速到灵活，各有侧重。

**核心方式概览**

| 方式                 | 核心工具                        | 优点                       | 缺点                     | 适合场景                          |
| ------------------ | --------------------------- | ------------------------ | ---------------------- | ----------------------------- |
| **1. 使用官方 SDK**    | `@modelcontextprotocol/sdk` | **官方推荐、最稳定、最便捷**，封装了底层细节 | 灵活性相对较低                | **绝大多数情况**，快速开发标准服务           |
| **2. 手动实现 STDIO**  | 任意语言 + 标准输入/输出              | **灵活性最高**，可用任何语言实现       | 需要手动处理协议、JSON RPC、生命周期 | 使用非 Node.js/Python 语言，或需要深度定制 |
| **3. 使用社区 SDK/模板** | 社区维护的 Python/Go/Rust 等 SDK  | 比手动实现方便，比官方支持更多语言        |                        |                               |

**fastMCP 属于第一种方式：使用官方 SDK 的增强版和简化版**。

更准确地说，fastMCP 是**基于官方 @modelcontextprotocol/sdk 构建的高层封装和工具集**，属于 "官方 SDK 生态" 的一部分。

**fastMCP 的定位**

**核心特点：**

- **底层依赖**：仍然使用官方的 `@modelcontextprotocol/sdk`
- **设计目标**：简化开发流程，减少样板代码，提供更友好的 API
- **额外功能**：内置了常用的工具、资源类型、服务器管理等开箱即用的功能

**fastMCP 的优势**

1. **开发效率**：用装饰器、依赖注入等模式大幅减少代码量
2. **内置功能**：提供了常用工具的快速实现（如 HTTP 客户端、文件操作等）
3. **配置简化**：简化了服务器配置和客户端连接
4. **生态整合**：更容易集成到现有的 Python/Node.js 项目中

## 5 基于SSE 协议创建MCP服务



### **5.1 创建mcp服务器**

基于 `FastMCP` 库创建一个简单的服务，包含两个功能：一个是问候功能，另一个是计算加法功能。

步骤如下：

1. **导入库**

```python
from fastmcp import FastMCP
import warnings
```

- `FastMCP`：是一个可以创建和运行微服务的库，可以很容易地添加工具和功能。
- `warnings`：用于控制警告的显示，这里用于忽略弃用警告。

2. **忽略警告**

```python
warnings.filterwarnings("ignore", category=DeprecationWarning)
```

- 这行代码告诉 Python 忽略所有 `DeprecationWarning` 类型的警告，这些警告通常用于提醒某个功能将在将来的版本中被弃用。通过此行代码，我们避免了控制台输出的过多警告信息，保持日志清洁。

3. **创建 FastMCP 实例**

```python
mcp = FastMCP("HelloWorld Server")
```

- `FastMCP("HelloWorld Server")`：创建一个名为 `"HelloWorld Server"` 的 FastMCP 服务器实例。这个实例将用于启动和运行服务。

4. **添加 say_hello 工具**

```python
@mcp.tool()
def say_hello(name: str = "World") -> str:
    """向指定的人问好"""
    return f"Hello, {name}! "

```

- `@mcp.tool()`：这是一个装饰器，用来将函数注册为 FastMCP 的一个工具。`say_hello` 就是我们添加的一个工具，功能是向指定的人问好。
- `name: str = "World"`：函数接受一个名为 `name` 的参数，默认值是 `"World"`，即如果没有传入参数时，默认向 `"World"` 问好。
- `return f"Hello, {name}! "`：返回一个问候信息，例如 `"Hello, Alice!"` 或 `"Hello, World!"`。

5. **添加 add_numbers 工具**

```python
@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """两个数字相加"""
    return a + b

```

- 这个工具的功能是两个数字相加。
- `a: float, b: float`：接受两个数字参数。
- `return a + b`：返回这两个数字的和。

6. **启动 HTTP 服务器**

```python
if __name__ == "__main__":
    try:
        mcp.run(
            transport="sse", #使用 SSE
            port=8000,       #端口号
            host="0.0.0.0",  # 允许外部访问
        )
    except Exception as e:
        print(f"服务器错误: {e}")

```

- `mcp.run()`：启动 FastMCP 服务器。

  - `transport="sse"`：指定使用 **Server-Sent Events (SSE)** 作为传输方式。SSE 是一种基于 HTTP 的协议，允许服务器将实时数据推送到客户端，适用于需要实时更新的应用。
  - `port=8000`：指定服务器监听的端口号为 `8000`。
  - `host="0.0.0.0"`：表示服务器将接受来自所有 IP 地址的请求（即对外开放）。

  ​

**完整案例如下**

```python

from fastmcp import FastMCP
import warnings
# 忽略警告
warnings.filterwarnings("ignore", category=DeprecationWarning)
# 创建 FastMCP 服务器实例
mcp = FastMCP("HelloWorld Server")

# 添加一个简单的 hello 工具
@mcp.tool()
def say_hello(name: str = "World") -> str:
    """向指定的人问好"""
    return f"Hello, {name}! "

# 添加一个计算工具
@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """两个数字相加"""
    return a + b

if __name__ == "__main__":
    # 启动 HTTP 服务器
    try:
        mcp.run(
            transport="sse",#使用 SSE
            port=8000,#端口号
            host="0.0.0.0",  # 允许外部访问

        )
    except Exception as e:
        print(f"服务器错误: {e}")
```

运行成功后，代码如下：

```
                               FastMCP  2.0                                │
│                                                                            │
│                                                                            │
│                🖥️  Server name:     HelloWorld Server                       │
│                📦 Transport:       SSE                                     │
│                🔗 Server URL:      http://0.0.0.0:8000/sse                 │
│                                                                            │
│                🏎️  FastMCP version: 2.12.4                                  │
│                🤝 MCP SDK version: 1.15.0                                  │
│                                                                            │
│                📚 Docs:            https://gofastmcp.com                   │
│                🚀 Deploy:          https://fastmcp.cloud  
```



### 5.2 创建mcp客户端

   如何使用 **FastMCP** 客户端与之前创建的 **FastMCP 服务器** 进行交互。主要流程是列出服务器提供的工具、测试这些工具的功能，并展示如何异步调用这些工具。步骤如下

1. **导入库**

```python
import asyncio
from fastmcp import Client
```

- `asyncio`：这是 Python 内建的库，用于管理异步 I/O 操作。
- `Client`：来自 `fastmcp` 库，用于与 `FastMCP` 服务器进行通信和交互。

2. **定义 main 异步函数**

```python
async def main():
    """使用 FastMCP 客户端进行测试（正确版本）"""
    print("使用 FastMCP 客户端测试...")

```

- `main` 是一个异步函数，它将会执行整个客户端的逻辑。
- `async` 用于定义 **异步函数**（也称为协程函数）。它是一个标志，表示函数内的操作是异步的，需要被调度和执行。
  - 当你在一个函数前面加上 `async` 关键字时，这个函数变成了一个 **协程函数**，它会返回一个 `coroutine` 对象，而不是立即执行返回值

3. **客户端连接**

```python
	async with Client("http://localhost:8000/sse") as client:
```

- `async with` 用来确保客户端在用完后正确关闭连接。
- `Client("http://localhost:8000/sse")`：这行代码创建一个客户端对象，连接到运行在 `localhost:8000` 上的 FastMCP 服务器，并使用 **Server-Sent Events (SSE)** 协议。
  - `localhost:8000/sse` 是服务器的地址，假设服务器在本地机器上运行并监听 8000 端口。

4. **列出可用工具**

```python
print(" 获取工具列表...")
tools = await client.list_tools()
print("可用工具:", tools)
print(f"找到 {len(tools)} 个工具:")
for tool in tools:
    print(f" - {tool.name}: {tool.description}")

```

- `await` 用来 **挂起**（暂停）协程的执行，等待另一个协程完成。它只能在异步函数（用 `async` 定义的函数）中使用。
  - `await` 表示当前协程暂停执行，等待另一个异步任务完成，并返回其结果。这样做可以让你同时运行多个任务，提高程序的效率。
  - 你通常会 `await` 一个异步函数调用（通常是一个 **协程**）或者一个 **异步对象**，比如 `asyncio` 库提供的 `Future` 对象。
- `await client.list_tools()`：调用 `client` 的 `list_tools` 方法，这是异步操作，获取当前服务器上可用的工具。
- `tools` 存储了一个包含所有工具信息的列表。
- 使用 `for` 循环遍历工具列表，输出每个工具的 `name` 和 `description`。

5. **测试 say_hello 工具**

```python
print("\n测试 say_hello...")
result1 = await client.call_tool("say_hello", {"name": "世界"})
print("结果:", result1)
print("数据结果", result1.data)

```

- `await client.call_tool("say_hello", {"name": "世界"})`：调用 `say_hello` 工具，并传递一个参数 `{"name": "世界"}`，表示向 `"世界"` 问好。
- `result1` 存储调用 `say_hello` 工具的结果。
- `result1.data` 用来输出工具返回的实际数据。

6. **测试 add_numbers 工具**

```python
print("\n 测试 add_numbers...")
result2 = await client.call_tool("add_numbers", {"a": 10, "b": 20})
print("结果:", result2)
print("结果", result2.data)

```

- 同样的方式，测试 `add_numbers` 工具，传入两个数字参数：`a=10` 和 `b=20`。
- `result2.data` 输出加法计算的结果。

7. **运行主函数**

```python
if __name__ == "__main__":
    asyncio.run(main())

```

- `asyncio.run(main())`：运行 `main()` 异步函数。
  - `asyncio.run()` 是一个用于启动异步任务的函数，它会创建事件循环并执行 `main` 函数。



**完整代码如下**

```python
# 05_simple_client_test.py
import asyncio
from fastmcp import Client

async def main():
    """使用 FastMCP 客户端进行测试（正确版本）"""
    print("🚀 使用 FastMCP 客户端测试...")

    try:
        # 使用 async with 来管理客户端连接
        async with Client("http://localhost:8000/sse") as client:
            # 列出可用工具
            print(" 获取工具列表...")
            tools = await client.list_tools()
            print("可用工具:", tools)
            print(f"找到 {len(tools)} 个工具:")
            for tool in tools:
                print(f" - {tool.name}: {tool.description}")

            # 测试各个工具
            print("\n测试 say_hello...")
            result1 = await client.call_tool("say_hello", {"name": "世界"})
            print("结果:", result1)
            print("数据结果",result1.data)

            print("\n 测试 add_numbers...")
            result2 = await client.call_tool("add_numbers", {"a": 10, "b": 20})
            print("结果:", result2)
            print("结果", result2.data)
            print("\n所有测试完成！")

    except Exception as e:
        print(f"测试失败: {e}")

# 运行异步主函数
if __name__ == "__main__":
    asyncio.run(main())
```

## 6 基于Stdio协议创建MCP服务

### 6.1 创建MCP服务器

```python
from fastmcp import FastMCP
import warnings

# 忽略警告
warnings.filterwarnings("ignore", category=DeprecationWarning)

# 创建 FastMCP 服务器实例
mcp = FastMCP("HelloWorld Server")

# 添加一个简单的 hello 工具
@mcp.tool()
def say_hello(name: str = "World") -> str:
    """向指定的人问好"""
    return f"Hello, {name}!"

# 添加一个计算工具
@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """两个数字相加"""
    return a + b

if __name__ == "__main__":
    # 启动 Stdio 服务器
    try:
        mcp.run(
            transport="stdio",  # 使用 Stdio 协议
        )
    except Exception as e:
        print(f"服务器错误: {e}")

```

### 6.2 创建MCP客户端



```python
#!/usr/bin/env python3
import sys

import asyncio

from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

async def test_mcp_server():
    """简单的 MCP 客户端测试"""
    file ="E:\\人工智能学习\\案例\my_mcp\\sever\\fast_mcp_stdio_server.py"
    # 创建 StdioServerParameters 对象
    server_params = StdioServerParameters(
        command="python",
        args=[file]
    )

    print("正在连接 MCP 服务器...")

    try:
        # 创建 stdio_client
        async with stdio_client(server_params) as (read, write):
            # 创建 ClientSession
            async with ClientSession(read, write) as session:
                # 初始化
                await session.initialize()
                print("✓ 服务器连接成功")

                # 获取工具列表
                tools = await session.list_tools()
                print(f"✓ 发现 {len(tools.tools)} 个工具:")

                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")

                print("\n测试工具功能:")

                # 测试 say_hello
                result1 = await session.call_tool("say_hello", {"name": "测试用户"})
                print(f"  say_hello: {result1.content}")
                print(f"  say_hello: {result1.content[0].text}")

                # 测试 add_numbers
                result2 = await session.call_tool("add_numbers", {"a": 7, "b": 8})
                print(f"  add_numbers: {result2.content}")
                print(f"  add_numbers: {result2.content[0].text}")

                print("\n✓ 所有测试完成!")

    except Exception as e:
        print(f"✗ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
```

## 7 langchain1.0版本调用MCP

​    模型上下文协议(MCP)是一项开放协议，它标准化了应用程序如何向LLM提供工具和上下文。LangChain代理可通过`langchain-mcp-adapters`库使用MCP服务器上定义的工具。

### 基于SSE协议调用

```
pip install langchain-mcp-adapters -i https://mirrors.aliyun.com/pypi/simple/

```

**MCP服务端代码**

```python
from fastmcp import FastMCP
import warnings
# 忽略警告
warnings.filterwarnings("ignore", category=DeprecationWarning)
# 创建 FastMCP 服务器实例
mcp = FastMCP("HelloWorld Server")

# 添加一个简单的 hello 工具
@mcp.tool()
def say_hello(name: str = "World") -> str:
    """向指定的人问好"""
    return f"Hello, {name}! "

@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """
    加法计算器
    :param a 第一个数据
    :param b 第二个数据
    """
    print(f"正在计算 {a} + {b}...")
    return a + b

if __name__ == "__main__":
    # 启动 HTTP 服务器
    try:
        mcp.run(
            transport="sse",#使用 SSE
            port=8000,#端口号
            host="0.0.0.0",  # 允许外部访问

        )
    except Exception as e:
        print(f"服务器错误: {e}")
```

**mcp 客户端**

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
from langchain.agents import create_agent

from app.model.my_model import MyModel    
    client = MultiServerMCPClient(
        {
            "mytool": {
                "transport": "sse",
                "url": "http://localhost:8000/sse",
            }
        }
    )

async def read():
    #1 获取工具
    tools = await client.get_tools()
    #2 创建大模型
    model = MyModel()
    llm = model.get_line_model()

    prompt = """
     如果用户问数学计算，请调用 add_numbers工具
    """
    # 3 创建智能体
    agent = create_agent(
        model=llm,
        system_prompt=prompt,
        tools= tools
    )
    info = "2+2="
    rs = await agent.ainvoke(
        {"messages": [{"role": "user", "content": info}]}
    )
    print(rs["messages"][-1].content)

if __name__ =="__main__":
    asyncio.run(read())
```

 `agent.ainvoke`

- **异步调用**。
- 返回一个 `awaitable` 对象，需要在 **异步函数 async def 中用 await** 才能得到结果。
- 典型用法：

```python
async def ask_agent():
    result = await agent.ainvoke({
        "messages": [{"role": "user", "content": "你好"}]
    })
    print(result["messages"][-1].content)

import asyncio
asyncio.run(ask_agent())

```

- 适合在 **异步环境** 或需要 **并发调用多个 Agent** 时使用。

**⚠️ 注意**

- **ainvoke 只能在异步上下文中调用**，否则会报错。
- **返回结果完全一样**，只是调用方式不同。
- 如果你用 `asyncio.run()` 启动异步函数，就必须用 `ainvoke`。
- 如果不想处理异步，可以直接用 `invoke`，更简单。




### 基于stdio协议调用

1 关键代码

```python
client = MultiServerMCPClient({
    "math": {
        "transport": "stdio",
        "command": "python",  # 要执行的命令
        "args": ["./math_server.py"],  # 命令参数
        # 可选：设置工作目录
        "cwd": "/path/to/working/directory"
    }
})
```

## **8  调用阿里的MCP广场服务**

**12306 MCP广场服务**

**1 采用官方给的 MCP SDK 调用**,  **12306 MCP服务地址**

```
https://bailian.console.aliyun.com/cn-beijing?tab=app#/mcp-market/detail/china-railway
```

**2 运行 get-current-date 服务，你才有工具**

**3 采用 官方给的 cursor版本，如图所示**

![3](E:\人工智能学习\文档\教学课程\大模型应用开发课程\langchain课程\langchain-1.0版本\images\3.bmp)**注意：官方给的是cursor版本，langchain 用的是MCPSDK调用，需要修改type为transport，修改后如下**

```
  {
            "mcp-server": {  
                "transport": "sse",
                "url": "https://dashscope.aliyuncs.com/api/v1/mcps/china-railway/sse",
                "headers": {
                    "Authorization": f"Bearer {DASHSCOPE_API_KEY}"
                }
            }

    }
```

**4  源码测试**

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
from langchain.agents import create_agent

from app.model.my_model import MyModel    # 你自己的模型封装
import time
from dotenv import  load_dotenv
import os
load_dotenv()

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

client = MultiServerMCPClient(
    {
            "mcp-server": {
                "transport": "sse",
                "url": "https://dashscope.aliyuncs.com/api/v1/mcps/china-railway/sse",
                "headers": {
                    "Authorization": f"Bearer {DASHSCOPE_API_KEY}"
                }
            }

    }
)

async def read():
    #1 获取工具
    tools = await client.get_tools()

    #2 创建大模型
    model = MyModel()
    llm = model.get_line_model()

    prompt = """
      火车票查询助手
    """
    # 3 创建智能体
    agent = create_agent(
        model=llm,
        system_prompt=prompt,
        tools= tools,
        debug= True
    )
    info = "成都到绵阳的火车票有多少了"
    # ainvoke 异步调用函数
    rs = await agent.ainvoke(
        {"messages": [{"role": "user", "content": info}]}
    )
    print(rs["messages"][-1].content)

if __name__ =="__main__":
    asyncio.run(read())


```

## 9 调用魔塔社区的MCP服务

地址：

```
https://modelscope.cn/my/overview
```

**网页抓取MCP服务**

1 打开MCP广场下的  Fetch网页内容抓取

```
https://modelscope.cn/mcp/servers/@modelcontextprotocol/fetch
```

2 配置MCP服务

![4](E:\人工智能学习\文档\教学课程\大模型应用开发课程\langchain课程\langchain-1.0版本\images\4.bmp)

**3 获取提供的服务地址如下**

```
{
  "mcpServers": {
    "fetch": {
      "type": "streamable_http",
      "url": "https://mcp.api-inference.modelscope.net/6c9530a75b6d4a/mcp"
    }
  }
}
```

4  langchain下修改为地址如下

```

    {
            "mcp-server01": {   
                "transport": "streamable_http",
                "url": "https://mcp.api-inference.modelscope.net/6c9530a75b6d4a/mcp",

            }

    }
```

5 测试代码

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
from langchain.agents import create_agent
from app.model.my_model import MyModel    # 你自己的模型封装

client = MultiServerMCPClient(
    {
            "mcp-server": {   #
                "transport": "streamable_http",
                "url": "https://mcp.api-inference.modelscope.net/6c9530a75b6d4a/mcp",

            }

    }
)

async def read():
    #1 获取工具
    tools = await client.get_tools()

    #2 创建大模型
    model = MyModel()
    llm = model.get_line_model()

    prompt = """
      网页抓取
    """
    # 3 创建智能体
    agent = create_agent(
        model=llm,
        system_prompt=prompt,
        tools= tools,
        debug= True
    )
    info = "百度新闻"
    # ainvoke 异步调用函数
    rs = await agent.ainvoke(
        {"messages": [{"role": "user", "content": info}]}
    )
    print(rs["messages"][-1].content)

if __name__ =="__main__":
    asyncio.run(read())


```

## 10  FastMCP服务添加密钥验证

我们在调用阿里的mcp服务，可以发现它添加了密钥验证，它是如何实现的呢

1 自定义  API Key 验证器

- 创建一个新的验证器类，继承自 `TokenVerifier`。必须实现 `verify_token` 方法。

```python
from fastmcp.server.auth import TokenVerifier, AccessToken
"""
 自定义 API Key 验证器
 """
class CustomApiKeyVerifier(TokenVerifier):

    async def verify_token(self, token: str) -> AccessToken | None:
        print(f"verify: {token}")
        if token == "123456":
            return AccessToken(
                  token=token,
                  client_id="44444",# 自定义服务端id
                  scopes=[]
            )
        else:
            return None

```

 **核心方法：`verify_token`**

```
async def verify_token(self, token: str) -> AccessToken | None:
```

**方法说明：**

- **async**：异步方法，因为验证可能涉及数据库查询或网络请求
- **token: str**：从客户端请求头 `Authorization: Bearer <token>` 中提取的 token 字符串
- **返回类型**：验证成功返回 `AccessToken` 对象，失败返回 `None`



 **AccessToken 参数说明**

```
AccessToken(
    token=token,        # 必需：原始 token 字符串
    client_id="44444",  # 可选：标识哪个客户端在访问
    scopes=[]           # 必需（当前版本）：权限范围列表
)
```

| 参数          | 作用                             | 示例值                 |
| ----------- | ------------------------------ | ------------------- |
| `token`     | 原始凭证，用于记录或后续验证                 | `"123456"`          |
| `client_id` | 标识客户端身份，用于审计或区分不同客户端           | `"44444"`（可以是任意字符串） |
| `scopes`    | 权限范围，控制客户端能做什么（当前为空列表，表示无特殊限制） |                     |

2 在创建FastMCP服务时候，引入

```python
mcp = FastMCP("HelloWorld Server",auth=CustomApiKeyVerifier())
#其它代码省略
```

3 测试，没有设置头部密钥

```python
client = MultiServerMCPClient(
    {
            "mcp-server": {   #
                "transport": "sse",
                "url": "http://localhost:8000/sse",
      
            }

    }
)
```

运行会报错

```
    | Traceback (most recent call last):
    |   File "E:\Anaconda\envs\langchain_demo_10\Lib\site-packages\mcp\client\sse.py", line 66, in sse_client
    |     event_source.response.raise_for_status()
    |   File "E:\Anaconda\envs\langchain_demo_10\Lib\site-packages\httpx\_models.py", line 829, in raise_for_status
    |     raise HTTPStatusError(message, request=request, response=self)
    | httpx.HTTPStatusError: Client error '401 Unauthorized' for url 'http://localhost:8000/sse'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401
```

4  添加了头部密钥后，就正常

```python
client = MultiServerMCPClient(
    {
            "mcp-server": {   #
                "transport": "sse",
                "url": "http://localhost:8000/sse",
                "headers": {
                    "Authorization": "Bearer 123456"
                }

            }

    }
)
```



**说明**

这段代码实现了一个**简单但完整的 API 密钥验证机制**：

1. **接收**：从请求中提取 token
2. **验证**：检查是否等于 `"123456"`
3. **返回**：成功返回 `AccessToken` 对象，失败返回 `None`
4. **效果**：只有携带正确密钥的客户端才能访问你的 MCP 服务

这是保护 MCP 服务最基础、最常用的方式，适合内部工具或测试环境。**生产环境建议使用更安全的 JWT 或 数据库查询 方案**