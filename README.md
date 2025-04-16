<!--
 * @Author: YuwanZ
 * @Date: 2024-07-20 11:28:10
 * @LastEditors: YuwanZ
 * @LastEditTime: 2024-09-05 11:23:58
 * @Description: 
 * @FilePath: \Text2SQL\README.md
-->
## 课题名称
**基于大模型的智能溯源Text2DSL工具研究**

## 课题内容
本项目旨在调研Text2DSL的前沿研究工作，研究如何让LLM掌握DSL的语义和语法，并且确保LLM在:decoding阶段输出正确且符合DSL的语法。
网络入侵溯源技术通常分析多个维度的数据(网络层面/主机层面/应用层面/员工层面)等实时数据，来初步确定是否为一次攻击事件或者确定入侵者所在的网络位置。
溯源需要更具当前告警的碎片化信息准确查询特定时刻特定实体的日志信息，用于帮助安全人员判别一次网络入侵。
溯源领域智能化需要解决的一个问题将安全人员的自然语言描述转换成特定的格式日志查询语句。

## 方法
1、 RAG2SQL：[Vanna相关报道](https://mlnotes.substack.com/p/no-more-text2sql-its-now-rag2sql)

2、 提示词优化：[Prompt优化大模型](https://blog.csdn.net/m0_59596990/article/details/135514992)

3、 基于微调的方法：[Text2SQL 微调｜手把手教程 复现 78.9% 准确率](https://blog.csdn.net/weixin_44292902/article/details/138327196)

# 参考资料

[大模型助力Text2SQL应用实战，自然语言轻松生成SQL语句并执行](https://www.bilibili.com/video/BV191421Z7JR/?share_source=copy_web&vd_source=e57cc28b3263b569e9e8a23945cd01b5)

[利用SQL数据库建立大模型应用](https://python.langchain.com/v0.2/docs/tutorials/sql_qa/#convert-question-to-sql-query)