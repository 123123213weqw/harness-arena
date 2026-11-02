# 对标其他 benchmark:harness-arena 当前差距分析

> 基于 main@68c8861(2026-10-31 R14 收官)盘点;对比对象为与我们生态位相关的七个评测:
> Terminal-Bench 2.0/Harbor、SWE-bench Verified/Live、LiveBench、τ-bench、WebDev Arena(LMArena)、HAL、Aider polyglot。
> 结论先行:**我们的"同题同模型纯 harness 对照 + 逐 run 记账"生态位是对的且稀缺,但防污染、沙箱隔离、统计功效三块地基与头部 benchmark 差距最大,且已有同名竞品上线了我们要做的盲投 Elo。**

## 0. TL;DR:十个缺点,按严重度排序

| # | 缺点 | 对标差距 | 严重度 |
|---|---|---|---|
| 1 | 防污染空窗:repo 公开,`secret/`+`mock/` 全部入库可见;M3 的私有化/参数化/滚动入库均未落地 | LiveBench 月度换题、SWE-bench Live 后 cutoff 滚动、TB2.0 canary | **P0** |
| 2 | 无沙箱:adapter 与 verifier 都在宿主机裸跑,容器化只是 compose 草案 | TB2.0/Harbor 全容器原生、SWE-bench 每题官方镜像 | **P0** |
| 3 | 统计功效不足:×2 重复、无置信区间,BATTLE 自认"<8pp 在分辨率之内",而终榜前四名只差 1-2 题 | τ-bench pass^k(k≥4)、HAL 统计检验 | **P0** |
| 4 | 题库小且合成题为主:49 题,真实仓库题仅 6 道,无 25 分钟以上长任务 | SWE-bench V 500 道真实 issue、TB2.0 真实终端任务 | P1 |
| 5 | 区分度塌缩:头部臂挤在 98-100%,名次实际由 1-2 道 hell 题决定 | 头部 benchmark 靠题量+难度分层维持区分 | P1 |
| 6 | 记账口径不统一:token 靠 harness 自报(缓存/推理口径各异),成本按统一牌价估算;M2 网关未做 | HAL 标准化成本口径、Aider 公开全量 transcript | P1 |
| 7 | 实验元数据缺失:store 无 harness 版本/题库 commit/温度/端点快照;DeepSeek 偷偷路由 chat→flash 靠人工发现;臂间未交错 | TB2.0 每次运行带完整环境元数据 | P1 |
| 8 | 人评/盲评缺失:`verifier: human` 仍是占位,盲投 Elo 排在 M3;同名竞品 Ondemand-OSS/harness-arena 已上线 LMSYS 式盲投 Elo | WebDev Arena/Code Arena 全链路盲投 | P1 |
| 9 | 可见性弱:无在线榜单/dashboard/paper,单机自托管,无社区贡献题通道 | TB2.0/SWE-bench/LiveBench/LMArena 均有公开网站+社区 | P2 |
| 10 | 指标体系单薄:无 pass^k/部分分/任务族/token-性能曲线;frontend 仅 1 题、computer-use 刚起步 | τ-bench pass^k、TB2.0 任务族+逐任务 telemetry | P2 |

## 1. 对标概览

| 维度 | Terminal-Bench 2.0 + Harbor | SWE-bench Verified / Live | LiveBench | τ-bench | WebDev Arena | HAL | **harness-arena(我们)** |
|---|---|---|---|---|---|---|---|
| 评测对象 | agent+harness(容器) | agent scaffold+模型 | 模型 | agent+模型 | 模型(前端) | agent(统一 scaffold) | **harness(同题同模型)** |
| 任务来源 | 真实终端任务 | 真实 GitHub issue | 持续新造题 | 领域工具模拟 | 真实前端需求 | 复用现有 bench | **自造合成题(49)** |
| 判定 | oracle 解+resolver | FAIL_TO_PASS 隐藏测试 | 自动判分 | 环境终态+用户模拟 | 人类盲投 | 各 bench 原判定 | **隐藏测试/answer/script/human(占位)** |
| 防污染 | canary+任务族+私有集 | Live 滚动+cutoff 后 issue | 月度换题 | 低敏感 | 天然免疫(每次新需求) | 继承 | **无(M3 未落地)** |
| 隔离 | Docker 容器原生 | 每题官方镜像 | 不适用 | 模拟环境 | 沙箱预览 | 统一 harness | **宿主机裸跑** |
| 统计口径 | 逐任务 telemetry | 官方固定子集+pass@1 | 公开榜单+分类 | **pass^k 可靠性** | 盲投 Elo+置信 | 成本+显著性检验 | ×2 重复+手写战报 |
| 成本记账 | 有 | 无强制 | 不适用 | 有 | 不适用 | **标准化强制** | 自报+牌价估算 |
| 形态 | 公开网站+社区贡献 | 公开网站+论文 | 公开网站 | 论文+开源 | 公开网站 | 公开榜单 | **私有 CLI+SQLite+md** |

引用:[TB2.0 发布公告](https://www.tbench.ai/news/announcement-2-0)、[VentureBeat:TB2.0 与 Harbor](https://venturebeat.com/technology/terminal-bench-2-0-launches-alongside-harbor-a-new-framework-for-testing-agents-in-containers)、[SWE-bench Live](https://arxiv.org/abs/2505.23419)、[LiveBench](https://arxiv.org/html/2406.19314v2)、[τ-bench](https://arxiv.org/abs/2406.12045)、[HAL](https://arxiv.org/abs/2510.11977)、[harness 差异的 TB 官方分析](https://tmustier.github.io/harness-benchmarks/)。

## 2. 逐项展开

### 2.1 防污染是当前最大的空窗(P0)

**现状**:README 把"完整题库不公开、参数化变体、滚动入库"列为 M3 目标——即尚未落地;而本 repo 是 public,49 道题的 `prompt.md`、`secret/`(隐藏测试、expected_answer)、`mock/`(参考解)全部公开可读。也没有 canary 字符串。

**别人怎么做**:LiveBench 用月度新题+公开题剔除保证"contamination-free";SWE-bench Live 只收模型 cutoff 之后的真实 issue 并周期滚动;TB2.0 在任务里嵌 canary 串检测训练污染,并用任务族控制过拟合;SWE-bench Verified 靠人工复核 500 题保证判定可信。

**后果**:(a) 未来模型训练数据可能吸入题库,横比逐渐失真;(b) 更现实的风险是**同组织 harness 的过拟合与利益冲突**——zcode、xharness 与题库同属一个 org,开发者可以看到全部判定标准做针对性优化,而 pi/claude-code/codex 是外部黑盒,这对"公平竞技场"的公信力是结构性伤害;(c) 别人复现我们的榜,只需把 mock/ 喂给任何 harness 即可"作弊满分"。

**建议**:secret/ 与 mock/ 移出公开 repo(私有子模块或运行时挂载);prompt 进库可以,判定材料必须私有;每题加 canary;参数化变体生成器(同模板不同参数/数据种子)优先级提到 M2 末;滚动入库规则("只统计新题成绩")先在 store 里落字段,别只写在 README。

### 2.2 无沙箱隔离(P0)

**现状**:`runner.run_one` 在宿主机目录直接调 adapter 子进程,verifier 也在宿主跑(`exec(expected_answer.py)`);docs/V100-DEPLOY.md 的 docker-compose(每题一容器 + dashboard)是草案。cu-01/cu-02 用了 pty/Xvfb/xdotool,但仍是宿主进程。

**别人怎么做**:TB2.0 与 Harbor 把"容器即环境"作为框架地基——同任务在任何机器上同环境复现;SWE-bench 每题提供官方镜像与安装脚本;WebDev Arena 预览也在沙箱里。

**后果**:(a) 宿主机装了什么( Node 版本、pip 包、locale)会进结果,跨轮次/跨机器不可复现——我们的 R8 曾把 xharness 60% 丢分归因到 max-output 配置,这类环境耦合每轮都在赌;(b) adapter 是任意代码执行器,密钥文件(~/.config 里放着的 credentials)裸露在工作区可及范围;(c) 多臂并行时互相污染 PATH/端口的风险(battle 报告里已有 PATH 教训)。

**建议**:先做最小版——每题一 Docker 容器(adapter 与 verifier 同容器跑完即弃),不要等完整 Harbor 级平台;V100 已有 Docker 28.5,成本主要是一次性镜像构建。顺手解决密钥隔离(密钥挂载给网关,不给 agent)。

### 2.3 统计功效与稳定性口径不足(P0)

**现状**:每题 ×2 重复;BATTLE 明确"12 题样本下差距 <8pp 不作强结论";R13 终榜 zcode 104/104、claude/codex/pi 102-103——**前四名差距 1-2 题,在 ×2 重复的噪声带以内,名次实际不可分辨**;"2/2 稳定"只是二点估计。

**别人怎么做**:τ-bench 提出 pass^k(全部 k 次通过才算),专门度量可靠性;k 取 4 起;HAL 对臂间差做显著性检验;TB2.0 上榜要跑全部任务并给出逐任务明细。

**后果:**我们的结论"zcode 夺冠"严格说只是"并列第一梯队";效率分又把解出数乘进成本比,进一步放大了本不显著的 1-2 题差异。对外讲故事可以,当工程决策依据会误导。

**建议**:repeats 提到 ≥5(52 题 ×5 ×6 臂 ≈ 1560 run,按历史 ¥/run 成本完全可承受);报表加 bootstrap 置信区间;主指标改成 pass^k 并保留 pass^1;对"每题最省赢家数"这类次级指标同样给区间。

### 2.4 题库规模与真实度(P1)

**现状**:49 题(domains:algo 16、coding 23、data 2、ops 2、math 3、cu 2、frontend 1),难度 3-6;真实仓库题 6 道(arrow/dateutil/more-itertools 等的 168KB 级裁剪);timeout 10-25 分钟。

**别人怎么做**:SWE-bench Verified 500 道人工复核真实 issue;TB2.0 面向真实终端工作流(装环境、改配置、跑通服务);SWE-bench Live 维持滚动新增。

**后果**:合成 algo/math 小题对"真实工程负载"的代表性有限——不涉及依赖地狱、跨文件大重构、git 工作流、长时程任务(METR 一派已把"任务时域"当核心维度);结论外推到"哪个 harness 更适合日常开发"的证据链偏弱。

**建议**:扩到 100 题时把真实 repo 题比例提到 30%+(用 SWE-bench Live 的思路收 cutoff 后的真实 issue);加 2-3 道 45-60 分钟长任务(现在 hell 上限 25 分钟,考察不了长时程恢复);algo/math 域可以保留作"模型智力对照",但别让它们主导 harness 结论。

### 2.5 区分度塌缩(P1)

**现状**:R14 六臂 98-100% 挤在顶部,唯一全灭题 hell-01 与个别单发题决定名次;已经靠退役 8 道"送分题"手动续命。

**别人怎么做**:LiveBench 靠持续加难题维持头部区分;TB2.0 2.0 版整体上调难度并引入任务族方差分析;WebDev Arena 靠人评连续量(而非 0/1)天然高分辨。

**建议**:判分从 0/1 points(现在全是 1.0)走向部分分(隐藏测试按用例计分);hell 层做成"任务族"(同型不同参),既防污染又把区分度参数化;盲投 Elo(连续量)落地后前端/开放题天然高区分。

### 2.6 记账口径不统一(P1)

**现状**:token 完全靠各 harness 自报,Claude/codex/pi/xharness 对缓存读、推理 token 是否计入口径不同;README 承认"只记录不横比",但 BATTLE 的效率分又直接用这些数横比成本——**口径矛盾**;成本按"统一牌价"估算,与真实计费(缓存折扣、推理 token 定价)有偏差;M2 的网关强制记账未做。

**别人怎么做**:HAL 把"统一 harness、强制成本口径"作为存在理由;Aider 榜把每个模型的完整 transcript 公开可审计;TB2.0 telemetry 逐任务采集。

**后果**:zcode"能力第一、效率垫底"这类结论对口径敏感——若 zcode 缓存利用率数据口径与 pi 不同,排名会翻转;效率分(解出×最低成本/本臂成本)还奖励"少做题省成本"的保守策略。

**建议**:M2 网关(OpenAI 兼容反代)优先做,自报数降级为交叉核对;效率分改为"每解出一题的边际成本"并标注口径;raw usage 原文(transcript.jsonl 已有)进 SQLite 外链,保证可审计。

### 2.7 实验元数据与可复现(P1)

**现状**:store 一行 run 只有 model 字符串;harness 版本、题库 commit、温度/种子、API base 都靠 BATTLE.md 手写;DeepSeek 把 deepseek-chat 路由到 flash 这种事靠人工发现;臂间未交错调度(服务端负载波动未消除)。

**建议**:runs 表加列 harness_version、taskbank_commit、api_base、params_json;每次 suite 记录随机交错后的执行序;对每臂首末 run 做一次模型身份抽查(问 self-knowledge 或比对 tokenizer 行为),防"静默换后端"。

### 2.8 人评/盲评缺失 + 同名竞品(P1)

**现状**:`verifier: human` 只返回 pending_human 占位;盲投 Elo 在 M3;frontend 域仅 1 题且用结构化 HTML 判定,不是真盲投。

**别人怎么做**:WebDev Arena/Code Arena 用成对盲投 + Elo + 大样本人类投票;**GitHub 上已有同名项目 [Ondemand-OSS/harness-arena](https://github.com/Ondemand-OSS/harness-arena):LMSYS 式 harness 盲评(Claude Code/Codex CLI/OpenClaw/Hermes/OnDemand),同题同模型、人盲评出 Elo,FastAPI+Mongo 全栈;PyPI 上也已存在同名 harness-arena 包**。

**后果**:我们要做的"盲投 harness 竞技场"已被别人先发,且名字相同——品牌占位和搜索可见性都会被分走;纯客观判定在"代码质量/可维护性"维度确实测不到,这块只能靠人评补。

**建议**:M3 盲评做"双轨"差异化:客观 pass^k 主榜 + 盲投 Elo 副榜(竞品只有主观投票,没有隐藏测试与成本账本——这正是我们的护城河);命名尽早处理(改包名或注册占位)。

### 2.9 可见性(P2)

无公开 dashboard(M2 计划)、无在线榜单、无 paper/tech report、无外部贡献题通道;对比 TB2.0/SWE-bench/LiveBench/LMArena 全部有公开网站+社区。**一个榜单的影响力 = 任务质量 × 可复现性 × 可见性**,我们目前只有第一项。建议:先把 SQLite→静态 HTML 榜单(gitHub pages 即可,零运维);R1-R14 的方法论写成 tech report(arXiv),"pi-rs 行为克隆 parity"这种结果有独立发表价值。

### 2.10 指标体系(P2)

无 pass^k、无部分分、无任务族分析、无 token-性能曲线;cu 域刚起步、frontend 1 题。τ-bench 的 pass^k、TB2.0 的任务族+逐任务 telemetry、HAL 的成本-得分散点都是成熟范式,抄作业即可,关键是先把 2.3/2.6 的地基补上。

## 3. 已经做对、要保住的差异化

1. **生态位稀缺**:同题同模型、只变 harness 的受控对照——TB2.0 的 harness 榜与 HAL 都在证明这个方向值钱,但都没有我们"逐 run 成本账本 + 同组织可控全栈"的纵深;
2. **mock 参考解全绿门禁**(49/49):与 TB2.0 oracle 解同思路,题目可解性有保证;
3. **SQLite 逐 run 账本**:多数公开榜只给汇总,我们能下钻到单题单次;
4. **效率意识**:效率分/¥/解出题在 harness 榜里独一份(Aider 只对模型做);
5. **工程细节**:退役送分题、isatty 反作弊、regression_diff 回归对拍、pi-rs parity 对拍。

## 4. 行动优先级(对齐路线图)

- **P0(公平性地基,先于一切扩容)**:secret/mock 私有化 + canary;每题一容器最小沙箱;网关强制记账;repeats≥5 + pass^k + 置信区间。
- **P1(区分度与真实度)**:参数化变体生成器;真实 repo 题占比 30%+;45-60 分钟长任务;任务族;盲投 Elo 双轨;runs 表元数据 v2。
- **P2(影响力)**:静态在线榜单;tech report;多模型矩阵(harness×model 交互本来就是我们的独家维度);命名与品牌处理。

一句话:**方向对、账本细,但"公开题库+裸跑宿主+两点重复"让现在的数字还撑不起它想讲的结论;先补防污染/沙箱/统计三块地基,再谈百题扩容与盲投 Elo。**
