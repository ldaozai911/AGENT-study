from tool.amap_driver_tool import driver_tool

from model.my_model import MyModel
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
#演示智能体创建
def create_email_agent(q):
    # 1 创建一个大模型
    model = MyModel.get_model()
    #2 创建一个工具
    tools=[driver_tool]
    #3 创建提示词,系统提示词
    prompt = """
       一 角色:  你是一个路径规划助手
       二 任务： 请根据用户输入问题，完成汽车路线规则
       三 规则：
              - 根据工具返回的结果，生成详细的汽车路线
    """
    #4 创建智能体
    agent =create_agent(
        model =model,
        tools =tools,
        system_prompt=prompt,
        debug=True #可选参数，一般用于调试，生成环境必须设置未false
    )

    human_msg = {"messages": [HumanMessage(content=q)]}
    rs = agent.invoke(human_msg)
    print(rs["messages"][-1].content)

if __name__ =="__main__":
    q="请给1553911731@qq.com 发送一封邮件，通知他来上课"
    q1="开车从成都到绵阳怎么走"
    create_email_agent(q1)