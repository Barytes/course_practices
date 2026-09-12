# 上下文消融实验 1-1：独立 benchmark 数据

从 [ai-agent-book 的实验 1-1](https://bojieli.github.io/ai-agent-book/chapter1/context/) 提取的单题数据包。任务是将四个季度的多币种收入统一换算为美元，计算全年总额和季度均值。这里仅收录正式运行脚本的 canonical guarded task，不包含示例任务集或额外变体。

## 文件

- `task.txt`：上游英文任务原文，可直接作为用户任务输入。
- `tools.json`：正式运行完整上下文组暴露的四个工具的原始接口定义，仅为 schema。包含 `parse_pdf`、`convert_currency`、`calculate`、`code_interpreter`；本题不需要 PDF 文件。
- `currency-fixtures.json`：三笔指定换汇请求的固定工具结果，来自上游正式运行证据，已去掉时间戳。
- `expected.json`：标准答案及上游数值匹配规则，供评测端使用。
- `sources.json`：下载地址、原文件 SHA-256、证据时间与提取说明。
- `LICENSE`：上游 Apache-2.0 许可证。

## 接入自己的 Agent

向 Agent 提供 `task.txt` 和工具 schema；由自己的工具适配器根据请求返回对应 fixture，并提供计算能力。标准答案和 fixtures 属于评测端数据，不应预先拼进 Agent 的任务提示词；换汇结果应在对应工具调用后才提供。

三条 fixtures 只定义本题三个准确参数组合的换汇结果，不定义任意金额、反向换汇或其他货币的行为。若要严格复现任意探索性工具调用，还需另行实现完整环境；本数据包不声称复现完整工具环境。

以 `converted_amount` 为准。原始工具结果中的 `exchange_rate` 已舍入，直接用它乘本金会与标准答案不同。这里冻结观测金额；使用实时汇率会改变正确答案。

上游判分会去掉最终答案中的逗号、美元符号和空格，再检查两个标准数字是否同时出现。这是较弱的字符串检查，并不自动证明计算过程正确或数字有观测依据。此规则记录在 `expected.json` 中，没有附带执行代码。

## 消融协议与边界

原实验对同一道题比较五组配置：完整上下文、移除历史消息、移除历史 reasoning、移除工具定义、移除工具结果。默认最多 5 次迭代。移除 reasoning 指不向后续轮次传递历史 reasoning，不代表禁止模型当轮思考；移除工具结果的正式设置保留协议要求的工具消息，但内容为空。

这些配置由接入方自己的运行系统控制。本目录不包含 Agent loop、provider/SDK 适配器、工具执行实现、API 请求响应记录、模型回答或运行脚本。工具 schema 属于接口数据，并非实现。

这是自建的单题教学消融任务，不是独立发布的大规模标准 benchmark。来源下载自上游 main；精确下载内容哈希及上游证据中工作区未提交的说明见 `sources.json`。
