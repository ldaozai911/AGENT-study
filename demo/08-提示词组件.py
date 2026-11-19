from tool.send_email_tool import send_email_tool
from model.my_model import MyModel
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from  prompt.builder_prompt_yaml import BuilderPromptYaml
#演示智能体创建
def create_email_agent(q):
    # 1 创建一个大模型
    model = MyModel.get_model()
    #2 创建一个工具
    tools=[send_email_tool]
    #3 创建提示词,系统提示词
    prompt = BuilderPromptYaml.get_prompt("send_email_agent.yaml")

    #4 创建智能体
    agent =create_agent(
        model =model,
        tools =tools,
        system_prompt=prompt,
        debug=True #可选参数，一般用于调试，生成环境必须设置未false
    )
    #5 提问
    #定义一个人类消息类型格式（第一种）
    #human_msg = {"messages":[{"role":"user","content":q}]}
    # 定义一个人类消息类型格式（第二种）
    human_msg = {"messages": [HumanMessage(content=q)]}
    rs = agent.invoke(human_msg)
    print(rs["messages"][-1].content)

if __name__ =="__main__":
    q="请给1553911731@qq.com 发送一封邮件，通知他来上课"
    q1="你是谁，你是干什么"
    q2="请解释一下什么是python"
    q3="请给1553911731@qq.com 发送一封邮件，通知他来上课"
    create_email_agent(q3)
