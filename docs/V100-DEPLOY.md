# V100 部署方案

目标机:`ssh <v100>`(tailscale 内网),2× Tesla V100-PCIE-32GB(driver 580.178.04),Docker 28.5.2,Python 3.10,64 核 / 251G 内存,根分区余 ~529G。

## 角色分工

V100 同时承担两个角色:

1. **竞技场平台**:跑 `python3 -m arena` 调度(M2 起容器化 worker + dashboard 常驻)
2. **本地推理**:Ollama/llama.cpp 起 OpenAI 兼容端点,给 mini adapter(以及以后所有想省钱的回归跑)当 `ARENA_API_BASE`,零 API 成本跑分

## 本地推理选型(V100 = Volta,SM70,注意三个坑)

- **没有 BF16**(Ampere 才有)、**没有 FlashAttention-2**(SM80+):一切以 FP16 / GGUF 为准
- **AWQ/Marlin 量化 kernel 不支持 Volta**,GPTQ kernel 能跑但慢;结论:**首选 llama.cpp 系(Ollama)跑 GGUF**,FP16 直出也行
- 新版 **vLLM 已弃用/移除 Volta**;如必须用 vLLM,锁旧版(≤0.9.x)+ `VLLM_ATTENTION_BACKEND=XFORMERS`

推荐配置(2×32GB):

| 用途 | 模型 | 说明 |
|---|---|---|
| 回归跑分/调试 | `qwen3:14b` 或 `qwen3:32b`(Q4) | 单卡即可,32B Q4 ~20G 显存 |
| 认真跑分省钱档 | 70B 级 Q4 GGUF | llama.cpp 双卡 tensor split,或 Ollama 自动分布 |
| 正式跑分 | 云端 GLM/Claude 等走 API | 平台只管记账 |

```bash
# Ollama 安装(服务器无 ollama 时)
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl enable --now ollama
ollama pull qwen3:32b        # 模型盘位较大,注意 /home 空间
# 之后:ARENA_API_BASE=http://localhost:11434/v1 ARENA_MODEL=qwen3:32b
```

## 平台部署

```bash
rsync -az --exclude runs/ --exclude .venv --exclude __pycache__ \
  <本地仓库路径>/harness-arena/ <v100>:~/harness-arena/

ssh <v100>
cd ~/harness-arena && python3 -m venv .venv && .venv/bin/pip install -e .
.venv/bin/python -m arena --adapters mock   # 服务器上验证全绿
```

M2 常驻化(草案,每题一容器 + dashboard):

```yaml
# deploy/docker-compose.yml(规划)
services:
  api:        { build: ., command: uvicorn arena.api:app, ports: ["8950:8950"] }   # 调度 + WebSocket
  worker:     { build: ., volumes: ["/var/run/docker.sock:/var/run/docker.sock"] } # 沙箱执行
  dashboard:  { ports: ["8951:80"] }   # 实时榜单/单题详情/token 曲线
  ollama:     { image: ollama/ollama, devices: [nvidia], volumes: ["ollama:/root/.ollama"], ports: ["11434:11434"] }
```

## 端口与运维注意(来自这台机器的既有约定)

- 8902 / 8908 / 8912 已被本机其他服务占用,竞技场用 **8950(api)/ 8951(dashboard)**
- SSH 端口转发到 V100 不稳定(约 5.6s 响应),访问 dashboard 一律走 tailscale IP 直连 `http://<tailscale-ip>:8951`
- 远程命令里 `pkill -f` 会匹配自身命令行导致自杀,要写成 `pkill -f "[h]ttp.server"` 形式
- GPU 与 Dora 容器共享:大跑分前 `nvidia-smi` 看占用,必要时错峰
- 判定用独立 Python(`ARENA_TASK_PYTHON` 可指定),pytest 已禁插件自动加载,宿主机包环境影响不到判定

## 开销红线

正式跑分用云端 API 时注意:一轮「3 harness × 100 题 × 3 repeats」按业界均值 $1.8/题可达数千美元。先用 V100 本地模型回归测试,确认管线与题目无误,再用最小 repeats 上云端。
