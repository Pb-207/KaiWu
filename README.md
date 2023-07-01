# KaiWu | 开物

针对本地部署优化的开源LLM本地学术论文对话框架

An LLM PDF chat framework optimized for research articles and local deployment.

## 项目特点

✅ 可在LLM有最大token限制的情况下，实现基于文本量远大于token限制的多篇论文对话；

✅ 将LLM对单个文本块的回答拼接组合，重新分块后再次发给LLM生成回答，保证回答质量及内容完整性的同时避免因token限制或显存不足产生截断；

✅ 基于langchain和gradio构建的简单易用的webui界面；

✅ 生成的回答提供参考来源链接，通过点击链接一键定位到论文对应页面；

✅ 针对本地部署优化，原生支持使用 OpenAI API 格式的 text-generation-webui、fastchat 等开源LLM部署框架；

✅ 检测回答是否被截断并自动重新生成回答；

![Gradio - Google Chrome 2023_7_2 0_54_43](https://github.com/Pb-207/KaiWu/assets/51241613/e807658e-15e5-4b2e-b8b5-f304d1d98aa1)

![Gradio - Google Chrome 2023_7_2 0_54_59](https://github.com/Pb-207/KaiWu/assets/51241613/62d1a137-ec8b-4b9c-81a2-16e32aa7820a)

## 部署指南

### 1、部署后端LLM服务API

- 使用OpenAI API




