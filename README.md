# harness-arena

> 自托管 coding-agent **harness 竞技场**:同一套题,让多种 harness(ZCode / Claude Code / Codex / mini 裸基线…)同场跑分,实时统计 pass 率、token 消耗与成本。
> 动机:同一个模型换 harness,Terminal-Bench 2.0 上能差出 35 个百分点——比模型的差异还大,但认真比 harness 的榜几乎没有。

## 快速开始

```bash
pip install -e .                 # 或 uv pip install -e .
python3 -m arena --adapters mock # 零成本验证管线(mock 参考解应全绿)

# 接真实模型跑裸 agent 基线(任意 OpenAI 兼容 API)
export ARENA_API_KEY=sk-xxx      # 智谱 GLM / OpenAI / 本地 Ollama 均可
export ARENA_MODEL=glm-5.3       # 默认 glm-5.3
export ARENA_API_BASE=https://open.bigmodel.cn/api/paas/v4   # 指向 V100 本地推理时换成 http://localhost:11434/v1
python3 -m arena --adapters mini --repeats 3
```

结果落 `runs/arena.db`(SQLite,每次 run 一行,token/时长/错误全记),工作区留档在 `runs/workspaces/<task>/<adapter>/runN/`,含 `.arena/transcript.jsonl` 完整轨迹。

## 架构

```
python3 -m arena
   │  载入题库 tasks/*/
   ▼
runner:干净工作区(env/ 拷入) ──► adapter 干活 ──► verifier 判定(secret/ 此时才可见)
   │                                                   │
   ▼                                                   ▼
store(SQLite 记账:tokens/calls/秒) ◄──────────────► report(总榜 + 分域透视)
```

## 出题(schema)

每题一个目录:

```
tasks/<task-id>/
  task.yaml   # id/domain/difficulty(1-5)/points/verifier/timeout_minutes
  prompt.md   # 给 agent 看的题目
  env/        # 初始工作区(agent 可见)
  secret/     # 判定材料,跑完 agent 才拷入(agent 不可见!)
  mock/       # 参考解,只有 mock adapter 用,永不进真实工作区
```

domain:`coding | ops | algo | math | frontend | data | composite`
verifier:`pytest`(隐藏测试)| `answer`(answer.txt 精确比对,期望值写在 secret/expected_answer.py 里动态计算)| `script`(secret/verify.sh 退出码)| `human`(进盲投队列)

出题守则:

- 判定必须确定性、与宿主机环境隔离(runner 已注入 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`),期望值用代码算出来而不是手写;
- `secret/` 与 `mock/` 永不进 agent 工作区;
- 防污染三件套(M3 落地):完整题库不公开、参数化变体生成器、滚动入库只统计新题成绩。

## adapters

| 名字 | 是什么 | 记账来源 |
|---|---|---|
| `mock` | 把 mock/ 参考解拷进工作区,验证管线,零 token | - |
| `mini` | 自研裸 agent 基线(对标 mini-swe-agent):单命令 bash 循环 | API usage 字段 |
| `claude` | Claude Code headless(`claude -p --output-format json`) | CLI JSON usage |
| `codex` | Codex CLI headless(`codex exec --json`) | jsonl token_count 事件 |

新增 harness:实现 `arena/adapters/base.py` 的 `Adapter` 协议(`run(task, workdir) -> AgentRun`),在 `adapters/__init__.py` 注册一行即可。M2 计划:统一 token 强制记账走网关(harness 自报只作交叉核对)+ Docker 沙箱。

## 已完成:十三轮 harness 对比(2026-10-01 → 10-26,约 4000 次真实运行)

### 同模型五臂终榜(52 题 × 2,统一 deepseek-flash,思考全开)

| 臂 | 通过 | ¥/解出题 | 均耗时 | 效率分(解出×最低单价/本臂单价) |
|---|---|---|---|---|
| **zcode 0.17.0** | **104/104(100%)** | ¥0.44 | 82.0s | 9.5 |
| claude 2.1.310 | 103/104(99%) | 0.12 | 47.3s | 34 |
| pi 1.4.0 | 103/104(99%) | **0.04** | 19.6s | **103** |
| codex 0.164 | 102/104(98%) | 0.10 | 117.5s | 41 |
| xharness cf9b0fc | 99-101/104 | 0.10-0.12 | 59-62s | 34 |

- **zcode×DeepSeek 首秀即满分夺冠**(104/104 零失败;但每轮新鲜输入 16.5M、缓存利用率仅 ~1×,效率分垫底——能力第一、经济性倒数);
- **pi 效率分登顶**(满分能力 + 最低单价 + 最快);
- xharness #394 修复验证:persona 字节级复原(system 7,484→1,739)但**每调用新鲜 token 仍涨**(531→772→1,116),残留膨胀源已反馈 [issue #393](https://github.com/123123213weqw/x-harness-rs/issues/393);
- zcode 原生 GLM-5.3-Flash 对照:61%——同 harness 换模型档位差 39 个百分点。

### 历轮脉络

R1-2 基线与成本分水岭 → R3 超越智力题击穿 claude → R4 思考全开 → R5 泛化题 → R6 真实仓库修复题(arrow/dateutil/more-itertools,三方求证) → R7 地狱题 L6 → R8 max-output 修复实证(xharness 丢分 60% 系配置 bug) → R9 全上游 2026-10-25(pi 首满分) → R10 52 题新库(claude 翻盘) → R11-13 zcode 五臂上线、换 DeepSeek 满分、xharness 修复验证。

## 已完成:四 harness Tier-B 对比(前八轮)

**最终全量轮(2026-10-03,suite `20261003-201117`,46 题 × 4 臂 × 2 重复 = 368 run,模型统一 `deepseek-chat`)**,下表数字直接由 `sqlite3 runs/arena.db` 查询得出:

| 臂 | 解出(≥1次) | 2/2 稳定 | run 级通过率 | 平均耗时 | 输入 token | 缓存读 | 输出 token |
|---|---|---|---|---|---|---|---|
| codex 0.142.0 | 45/46 | **45/46** | 97.8%(90/92) | 53.6s | 208,533 | 10,776,448 | 291,634 |
| pi 0.74.2 | 45/46 | 43/46 | 95.7%(88/92) | 30.3s | 258,595 | 2,123,520 | 236,201 |
| xharness(74f378c) | 45/46 | 42/46 | 94.6%(87/92) | 81.6s | 510,677 | 14,753,536 | 331,551 |
| claude-code 2.1.212 | 44/46 | 37/46 | 88.0%(81/92) | 70.3s | 2,754,256 | 20,987,776 | 542,928 |

观察:头部三臂(97.8 / 95.7 / 94.6%)咬得很紧,claude-code 落后 ~10 个百分点,且其输入 token(含系统提示词地板)与缓存读比 codex 高一个数量级——**harness 的差异真实、可测、值钱**。

**竞技场累计账本(V100 `runs/arena.db`,截至 2026-10-03)**:共 **2,338 个 run**、29 个 suite、46 道题、6 个 adapter(mock / mini / claude-code / codex / pi / xharness),全量 token 与耗时逐 run 留档。完整分题矩阵与历轮战报见 [BATTLE.md](BATTLE.md)。

**第三轮(2026-10-02 深夜,28 题 = 22 + 6 道「超越智力」难题,4 臂 × 28 × 2 = 224 run,耗 ¥33.56)**:

| 臂 | 解出 | 稳定 2/2 | 估算成本 | ¥/解出题 | 平均耗时 |
|---|---|---|---|---|---|
| xharness(74f378c) | 28/28 | **28/28** | ¥2.83+ | 0.05 | 49.2s |
| codex 0.142.0 | 28/28 | 28/28 | ¥2.55+ | 0.05 | 40.7s |
| pi 0.74.2 | 28/28 | 28/28 | ¥0.94+ | 0.02 | 40.1s |
| claude-code 2.1.212 | 23/28 | — | ¥9.42 | 0.20 | 50.0s |

难题战报:6 道 hard 题(数位 DP/矩阵幂/组合数/Grundy 博弈/缺失子串/带权区间)只有 **claude-code 被击穿**(hard-02、hard-05 双挂,hard-03 磨 866 秒/¥0.66 才过,hard-04 磨 178 秒失败);其余三臂 12/12 全绿。xharness 在 hard-04 上磨 20 分钟最终解出(恢复力强);codex 数学洞察型最快(hard-03 36s、hard-04 51s);pi 最省最稳。

**推理强度审计**(用户关键提问):四臂名义设置不同——codex 默认中档 reasoning(Responses 端点真生效,每轮 3-6 千 reasoning token);pi 名义 thinking=high 但 deepseek-chat 的 chat 端点不认(纯摆设);xharness/claude 未开。**受控实验**(codex `model_reasoning_effort=none` 重跑 6 道难题):11/12 过、耗时持平,仅 hard-03 丢一次稳定——codex 的难题优势**不主要依赖推理加成**,排名成立但已加注。

另外实测:DeepSeek 把 deepseek-chat 路由到 `deepseek-flash` 实际服务;Claude Code 2.1.212 的系统提示词地板 27,462 token,最新 2.1.287 降到 22,935(旁路安装在 `~/claude-287/`)。

**第二轮(2026-10-02,22 题 = 12 基础 + 10 道 L4-L5)**:xharness/codex/pi 全 22/22(claude 20/22 稳定),成本 claude ¥6.71 vs pi ¥0.94;**第一轮(12 题,96 run,¥2.31)**:四臂全解,claude 唯一丢一次。完整数据与分题矩阵见 [BATTLE.md](BATTLE.md)。

四臂接法:xharness 走其 loopback JSON-RPC 控制面;claude 走 DeepSeek Anthropic 兼容端点;codex 走 DeepSeek 原生 Responses API;pi 走 `--provider deepseek`。key 在 V100 `~/.config/xharness-bench/credentials.env`。

## 路线图

- **M1(已完成)**:题库 schema + 样例题 + runner/verifier/SQLite 记账 + adapters + CLI 报表
- **M2(已完成)**:四臂 Tier-B 对比两轮(12 题 → 22 题含 L4-L5);Docker 沙箱、网关强制记账、实时 Dashboard 待做
- **M3**:前端设计题 + 匿名盲投 Elo(对标 WebDev Arena)、题库扩到 100 题、参数化变体生成器
- **M4**:滚动入库防污染、按月 harness 战报、成本效率榜(每 $ 买到的分数)

部署到 V100 见 [docs/V100-DEPLOY.md](docs/V100-DEPLOY.md)。
