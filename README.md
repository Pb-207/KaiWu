# KaiWu | 开物

针对本地部署优化的开源 LLM 本地学术论文对话框架

An LLM PDF chat framework optimized for research articles and local deployment.

## 项目特点

✅ 可在 LLM 有最大`token`限制的情况下，实现基于文本量远大于`token`限制的多篇论文对话；

✅ 将 LLM 对单个文本块的回答拼接组合，重新分块后再次发给 LLM 生成回答，保证回答质量及内容完整性的同时避免因`token`限制或显存不足产生截断；

✅ 基于 langchain 和 gradio 构建的简单易用的 webui 界面；

✅ 生成的回答提供参考来源链接，通过点击链接一键定位到论文对应页面；

✅ 针对本地部署优化，原生支持使用 OpenAI API 格式的 text-generation-webui、fastchat 等开源 LLM 部署框架；

✅ 检测回答是否被截断并自动重新生成回答；

![Gradio - Google Chrome 2023_7_2 0_54_43](https://github.com/Pb-207/KaiWu/assets/51241613/e807658e-15e5-4b2e-b8b5-f304d1d98aa1)

![Gradio - Google Chrome 2023_7_2 0_54_59](https://github.com/Pb-207/KaiWu/assets/51241613/62d1a137-ec8b-4b9c-81a2-16e32aa7820a)

## 部署指南

### 1. 部署环境

(1). 克隆此仓库

```shell
git clone https://github.com/Pb-207/KaiWu.git
```

(2). 安装依赖

```shell
cd KaiWu
pip install -r requirements.txt
```

(3). 将项目目录中`example.config.ini`重命名为`config.ini`

### 2. 部署后端 LLM 服务 API

- 使用 OpenAI API

(1). 修改`config.ini`中的`openai_api_key`为你自己的 API Key；

(2). 根据需要修改`config.ini`中其他配置参数，各参数意义详见`3. 配置参数`栏；

- 使用 oobabooga/text-generation-webui

[text-generation-webui](https://github.com/oobabooga/text-generation-webui) 是一个功能全面且易于使用的开源 LLM 部署框架，支持几乎所有开源 LLM，本项目推荐配合 [text-generation-webui](https://github.com/oobabooga/text-generation-webui) 使用；

(1). 克隆 text-generation-webui 仓库并安装依赖

```shell
git clone https://github.com/oobabooga/text-generation-webui.git
cd text-generation-webui
pip install -r requirements.txt
```

(2). 运行 text-generation-webui 

运行时须添加 flag: --extensions openai

```shell
python server.py --extensions openai
```

(3). 访问 text-generation-webui 的 webui 界面，根据需要加载模型并修改参数，需特别注意修改`max_new_tokens`, `Truncate the prompt up to this length`和`temperature`这三个参数，如果使用 exllama 还需注意修改`max_seq_len`和`compress_pos_emb`；

(4). 修改`config.ini`为 text-generation-webui 启用的 API Base 地址，如未专门配置默认为：`http://127.0.0.1:5001/v1`；

### 3. 配置参数

本项目的配置参数均在`config.ini`中修改，每个配置参数的具体作用如下：

- `openai_api_key`

OpenAI 的 API Key
 
- `openai_api_base`

OpenAI 的 API 服务地址， 使用本地部署时须修改为本地 LLM 的 API 地址，text-generation-webui 的默认 API Base 地址为：`http://127.0.0.1:5001/v1`

**注意: 此处地址不是代理地址**，如使用 OpenAI 官方 API 此处请留空，代理地址在下面的`proxy_http`和`proxy_https`中配置；

- `enable_proxy`

是否开启代理，使用代理访问 OpenAI 请将该项设为`True`；

- `proxy_http`

http 代理地址；

- `proxy_https`

https 代理地址；

- `gpt_model`

使用的 OpenAI 的模型代号，详见 [OpenAI 官方文档](https://platform.openai.com/docs/models/continuous-model-upgrades)

- `chunk_size`

分割PDF文档时单个文本块的`token`数，设置为`trunction_size`的 1/2 有较好的效果(如：使用`llama`系列模型时可设置为`1024`)， 设置的`chunk_size`过高将会导致回答被截断；

- `chunk_overlap`

分割文档后相邻文本块的重叠部分`token`数；

- `embedding_model`

Embedding 时所使用的模型，默认模型效果较好，可使用`HuggingFace`上支持的模型；

- `embedding_gpu`

是否使用 GPU 进行 Embedding，使用 GPU 进行 Embedding 速度更快但需消耗较多显存从而导致留给推理使用的显存变少(测试300页PDF文档约消耗4GB显存用于Embedding)， 由于 Embedding 每次启动只需运行一次，故使用 CPU 进行 Embedding 可在不牺牲太多速度的情况下降低显存需求(使用一颗`AMD EPYC 9654`Embedding 300页PDF需要约1分钟)

- `faiss_threads`

Faiss 执行相似度搜索时使用的 CPU 线程数，设置为所使用 CPU 的物理核心数即可；

- `port`

Webui 运行的端口

- `top_k`

Faiss 执行相似度搜索时返回结果的个数，LLM 将会基于相似度最高的`top_k`个文本块进行回答；

- `search_all_chunks`

是否让 LLM 基于 PDF 中的所有文本进行回答。设为`True`时，在论文较短的情况下可能获得更高质量的回答；
 
- `llm_generate_keywords`

是否让 LLM 基于问题生成关键词用于相似度搜索。设为`True`时，在某些情况下会获得更高质量的回答；

- `fix_truncation`

是否自动处理被截断的回答并重新要求 LLM 生成回答， 当运行时控制台频繁出现生成内容被截断的警告且最终生成的回答不完整时，应优先降低`chunk_size`和`chunk_overlap`的值，如降低上述值仍不能解决生成内容被截断的问题时，可开启此项修复被截断内容，开启后将增加回答时间。如控制台出现生成内容被截断的警告，但生成的内容无明显缺失，则可忽略该警告；

- `temperature`

LLM 推理时使用的采样温度，介于 0 和 2 之间。较高的值（如 0.8）将使输出更加随机，而较低的值（如 0.2）将使其更加集中和确定；

- `[PROMPTS]`

LLM 推理时所使用的 prompt，一般情况下无需修改；

### 4. 运行`main.py`

```shell
python main.py
```

## 路线图

- [ ] 优化或更换语义搜索方法，更好地使用关键词进行语义搜索以提升回答质量
- [ ] 增加本地储存和加载向量数据库的功能
- [ ] 提供更多可供选择的`prompt`以支持更多类型的论文(如中文论文)
