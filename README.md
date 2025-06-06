# BabyAgent

一个基于 Python 的 Agent，支持代码执行、OS 交互、网络搜索和文件操作等功能。

设计逻辑1:1复刻 lemonai ，只是去掉了前端设计 和 繁琐的数据库设计(直接json写入简单明了)



## 功能特点

- 无对话：提出需求Agent直接解决需求，要的就是无对话
- 代码执行：可以执行 Python 代码，丰富自定义，让agent干什么就干什么
- OS 交互：支持基本的操作系统操作
- 网络搜索：支持网络搜索功能
- 文件操作：支持基本的文件读写操作


## 为什么有这个项目
Agent 说简单也简单  说繁琐也够繁琐 入门别的Agent项目可能会被繁琐的代码组织吓退，但是本项目足够Baby 同时足够到位

看完本项目 基本就知道 Agent 是个怎么个玩法了，简单来说


Agent = LLM + plan + think + act + reflection + MCP

提个prompt 就让Agent 自动给你在服务器上生成代码跑代码 全程不需要交互, 想不想是不是很有意思，大胆一点 以后baseline就交给Agent了 



## 致谢
https://github.com/hexdocom/lemonai
