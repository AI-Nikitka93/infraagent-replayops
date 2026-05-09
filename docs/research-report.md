# InfraAgent deployment research: AMD MI300X vLLM + Hugging Face Spaces

Checked: 2026-05-09 02:20 Europe/Minsk  
Research slug: `qwen-rocm-hf-tunnel`  
Query type: New Build / Choice Under Uncertainty  
Depth: Standard  
Evidence quality: high for vLLM image, ROCm support, HF Spaces outbound networking, and Cloudflare Tunnel mechanics; medium for exact AMD Developer Cloud public-port behavior because AMD delegates the cloud substrate to third-party providers.

## Executive answer

Recommended topology:

```text
Browser
  -> Hugging Face Space public UI (Gradio/Streamlit, CPU Basic is enough)
  -> HTTPS request on port 443
  -> Cloudflare Tunnel public hostname
  -> cloudflared on AMD Developer Cloud VM
  -> LangGraph API on AMD VM, localhost:8010
  -> vLLM OpenAI-compatible API on the same AMD VM, localhost:8000
  -> Qwen/Qwen2.5-72B-Instruct on AMD MI300X via ROCm
```

Decision: run both `vLLM` and `LangGraph` on the AMD Developer Cloud instance. Keep Hugging Face Spaces as a thin public UI only.

Why:

- LangGraph will call the model repeatedly during agent loops. Keeping LangGraph next to vLLM avoids HF Space -> tunnel -> AMD round-trips for every tool/model call.
- HF Spaces free CPU hardware is enough for UI, but not for Qwen2.5-72B inference. Hugging Face docs list CPU Basic as 2 vCPU / 16 GB RAM / 50 GB ephemeral disk and allow upgrade, but the hackathon already provides MI300X credits.
- HF Spaces networking allows outbound HTTP/HTTPS requests on ports 80, 443, and 8080. Cloudflare Tunnel gives a public HTTPS endpoint on 443, so it fits the Spaces networking rule.
- Cloudflare Tunnel does not require an inbound port or public origin IP; `cloudflared` makes outbound connections to Cloudflare.

## Confirmed facts

### vLLM ROCm Docker image

Verified:

- vLLM official docs say the ROCm Docker images are `vllm/vllm-openai-rocm:latest` and `vllm/vllm-openai-rocm:nightly`.
- vLLM official docs say AMD's older `rocm/vllm` and `rocm/vllm-dev` images are deprecated in favor of `vllm/vllm-openai-rocm`.
- AMD ROCm docs now recommend upstream vLLM docs for latest inference/deployment guides and show `docker pull vllm/vllm-openai-rocm:latest`.
- Docker Hub currently shows `vllm/vllm-openai-rocm:v0.20.1`, `latest`, and `nightly`.
- Local live check with `docker manifest inspect` succeeded for:
  - `vllm/vllm-openai-rocm:latest`
  - `vllm/vllm-openai-rocm:v0.20.1`
  - `vllm/vllm-openai-rocm:nightly`

Chosen image for reproducibility:

```bash
vllm/vllm-openai-rocm:v0.20.1
```

Fallback:

```bash
vllm/vllm-openai-rocm:latest
```

Use `nightly` only if `v0.20.1` fails on the actual AMD image and the failure matches a known fixed upstream issue.

### Qwen2.5-72B model facts

Verified from the Hugging Face model card:

- Model: `Qwen/Qwen2.5-72B-Instruct`
- Size: 72.7B parameters
- Tensor type: BF16
- Current config context is set up to 32,768 tokens.
- Full long context up to 131,072 tokens requires YaRN/static rope scaling; Qwen recommends adding that only when long context is required because static YaRN can hurt shorter-text performance.
- Qwen model card includes a vLLM serve path: `vllm serve "Qwen/Qwen2.5-72B-Instruct"`.

Inference:

- On a single MI300X 192GB, default stable launch should start with BF16 and 32K max context, not 128K.
- Long context should be a separate validation profile, not the default hackathon demo path.

### Hugging Face Spaces networking

Verified:

- HF Spaces supports Gradio, Streamlit, Docker, and static HTML Spaces.
- HF Spaces default free hardware is 2 vCPU, 16 GB RAM, 50 GB ephemeral disk.
- HF Spaces allows outbound network requests through HTTP/HTTPS ports 80 and 443 plus port 8080. Requests to other ports are blocked.
- HF Spaces supports Secrets/Variables for storing backend URL and API tokens.

Implication:

- The Space should call `https://<public-hostname>/...` on port 443.
- Do not expose vLLM directly on `:8000` to the Space. Put Cloudflare/ngrok in front so the public URL is HTTPS/443.

### Cloudflare Tunnel

Verified:

- Cloudflare Tunnel is available on all plans.
- It creates outbound-only encrypted connections from `cloudflared` to Cloudflare.
- It does not require inbound firewall changes or a public origin IP.
- Named tunnels can map a public hostname to a local service such as `http://localhost:8000`.
- Quick Tunnels can expose local services with one command: `cloudflared tunnel --url http://localhost:8080`.
- Quick Tunnels are testing-only, have a 200 concurrent request limit, and do not support Server-Sent Events.
- Linux service mode is supported via `systemctl` / `cloudflared.service`.

Decision:

- Preferred for hackathon final: Cloudflare named tunnel with a stable hostname, if a Cloudflare-managed domain is available.
- Fallback for early demo: Quick Tunnel, but expect URL changes after restart and no SSE.

## Recommended topology

### Components

1. AMD Developer Cloud VM
   - `vLLM` container on localhost port `8000`.
   - LangGraph/FastAPI service on localhost port `8010`.
   - `cloudflared` service exposing only LangGraph, not raw vLLM.

2. Hugging Face Space
   - Thin UI only.
   - Stores:
     - `INFRAAGENT_API_BASE=https://infraagent.example.com`
     - `INFRAAGENT_API_KEY=<secret>`
   - Calls LangGraph API over HTTPS.

3. Cloudflare Tunnel
   - Public hostname routes to `http://localhost:8010`.
   - LangGraph internally calls `http://127.0.0.1:8000/v1/chat/completions`.

### Why expose LangGraph, not vLLM

Expose LangGraph because it can enforce:

- API auth;
- request validation;
- rate limits;
- agent-session state;
- logging and redaction;
- model call retries;
- clean public endpoints for the UI.

Do not expose raw vLLM unless you need a direct OpenAI-compatible endpoint for debugging.

## Exact vLLM Docker command

Default stable profile for one MI300X 192GB:

```bash
export HF_TOKEN="<hf_read_token_if_needed>"
export VLLM_API_KEY="$(openssl rand -hex 32)"
export HF_CACHE="/mnt/data/huggingface-cache"
mkdir -p "$HF_CACHE"

sudo docker run -d \
  --name infraagent-vllm-qwen25-72b \
  --restart unless-stopped \
  --device /dev/kfd \
  --device /dev/dri \
  --group-add video \
  --ipc=host \
  --cap-add SYS_PTRACE \
  --security-opt seccomp=unconfined \
  --shm-size 32g \
  -p 127.0.0.1:8000:8000 \
  -v "$HF_CACHE:/root/.cache/huggingface" \
  -e "HF_TOKEN=$HF_TOKEN" \
  vllm/vllm-openai-rocm:v0.20.1 \
  --model Qwen/Qwen2.5-72B-Instruct \
  --served-model-name qwen2.5-72b-instruct \
  --host 0.0.0.0 \
  --port 8000 \
  --dtype bfloat16 \
  --tensor-parallel-size 1 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.90 \
  --max-num-seqs 16 \
  --api-key "$VLLM_API_KEY"
```

Why these flags:

- `--device /dev/kfd` and `--device /dev/dri`: required ROCm device access pattern in official vLLM ROCm Docker docs.
- `--ipc=host` / `--shm-size 32g`: vLLM docs note shared memory matters for PyTorch/tensor parallel inference; AMD reference commands also use shared memory.
- `-p 127.0.0.1:8000:8000`: binds vLLM only to localhost on the VM. Cloudflare should expose LangGraph, not this raw port.
- `--dtype bfloat16`: model card says weights are BF16; vLLM `auto` would use BF16 for BF16 models, but explicit BF16 makes the choice visible.
- `--tensor-parallel-size 1`: one MI300X has 192GB VRAM, enough for a BF16 72B model plus a conservative 32K KV cache. Use higher TP only on multi-GPU instances.
- `--max-model-len 32768`: matches Qwen2.5 current config; avoids YaRN/128K risks during hackathon.
- `--gpu-memory-utilization 0.90`: below vLLM default 0.92 to leave more headroom for ROCm/PyTorch overhead.
- `--max-num-seqs 16`: conservative concurrency for a demo; raise only after memory profiling.
- `--api-key`: vLLM docs support requiring API keys in request headers.

Health check:

```bash
curl -s http://127.0.0.1:8000/v1/models \
  -H "Authorization: Bearer $VLLM_API_KEY" | jq
```

Smoke request:

```bash
curl -s http://127.0.0.1:8000/v1/chat/completions \
  -H "Authorization: Bearer $VLLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-72b-instruct",
    "messages": [{"role": "user", "content": "Reply with one sentence."}],
    "max_tokens": 64
  }' | jq
```

### Multi-GPU profile

If AMD Developer Cloud gives the 8x MI300X instance:

```bash
--tensor-parallel-size 8 \
--gpu-memory-utilization 0.90 \
--max-model-len 32768
```

Only after the 32K profile is stable, test:

```bash
--max-model-len 65536
```

Do not jump directly to 131072 unless the demo actually needs it. Qwen's model card says long context requires YaRN/static rope scaling, and static scaling can hurt shorter prompts.

## LangGraph placement

Recommended:

```text
AMD VM:
  vLLM:      http://127.0.0.1:8000
  LangGraph: http://127.0.0.1:8010

HF Space:
  UI -> https://infraagent.example.com
```

LangGraph environment:

```bash
export VLLM_BASE_URL="http://127.0.0.1:8000/v1"
export VLLM_API_KEY="$VLLM_API_KEY"
export PUBLIC_API_KEY="$(openssl rand -hex 32)"
```

Expose LangGraph through Cloudflare, not vLLM:

```text
Cloudflare public hostname -> http://localhost:8010
```

Reasoning:

- Frequent agent/tool/model calls stay on the VM.
- HF Space only waits on one higher-level API call per user action.
- If the tunnel drops, LangGraph/vLLM stay alive and can be re-exposed.

## Cloudflare Tunnel plan

### Preferred: named tunnel with stable hostname

Prerequisite: Cloudflare account and a domain in Cloudflare. Free plan is enough for Tunnel according to Cloudflare docs.

1. Install `cloudflared` on the AMD VM.

2. Authenticate:

```bash
cloudflared tunnel login
```

3. Create the tunnel:

```bash
cloudflared tunnel create infraagent-amd
```

4. Create `~/.cloudflared/config.yml`:

```yaml
tunnel: <Tunnel-UUID>
credentials-file: /root/.cloudflared/<Tunnel-UUID>.json

ingress:
  - hostname: infraagent.example.com
    service: http://localhost:8010
  - service: http_status:404
```

5. Route DNS:

```bash
cloudflared tunnel route dns infraagent-amd infraagent.example.com
```

6. Run as a service:

```bash
sudo cloudflared service install
sudo systemctl enable --now cloudflared
sudo systemctl status cloudflared --no-pager
```

7. Test from outside:

```bash
curl -s https://infraagent.example.com/health \
  -H "Authorization: Bearer $PUBLIC_API_KEY"
```

8. Set HF Space secrets:

```text
INFRAAGENT_API_BASE=https://infraagent.example.com
INFRAAGENT_API_KEY=<PUBLIC_API_KEY>
```

### Fast fallback: Cloudflare Quick Tunnel

Use only for development/demo when no domain is available:

```bash
cloudflared tunnel --url http://localhost:8010
```

It prints a public `https://*.trycloudflare.com` URL.

Constraints:

- URL is ephemeral.
- Testing-only path.
- 200 concurrent request limit.
- No Server-Sent Events support, so use non-streaming HTTP responses from HF Space.

### ngrok fallback

ngrok can also run as a Linux service and creates HTTPS endpoints over outbound TLS on port 443. Use only if Cloudflare Tunnel is blocked or unavailable.

Basic shape:

```bash
ngrok config add-authtoken "<token>"
ngrok http 8010
```

For a stable hackathon demo, confirm the current free-plan endpoint/domain behavior in your ngrok account before relying on it.

## Hugging Face Space plan

Space type:

- Gradio or Streamlit is enough.
- Docker Space is optional only if the UI needs custom system dependencies.
- Free CPU Basic should be enough for thin UI.

Networking:

- The UI must call `https://...` on port 443.
- Do not call `http://amd-ip:8000`; HF Spaces blocks arbitrary outbound ports and AMD public ingress may not be open.

Secrets:

```text
INFRAAGENT_API_BASE=https://infraagent.example.com
INFRAAGENT_API_KEY=<secret>
```

Request pattern:

```text
HF Space UI -> POST /runs or /chat on LangGraph API
LangGraph -> vLLM OpenAI-compatible API on localhost
LangGraph -> returns final answer/events to HF UI
```

For Cloudflare Quick Tunnel, prefer non-streaming responses because Quick Tunnels do not support SSE.

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---:|---|
| Wrong Docker image family | High | Use `vllm/vllm-openai-rocm:v0.20.1`; avoid deprecated `rocm/vllm` unless upstream image fails and AMD support says otherwise. |
| OOM on startup | High | Start with `--max-model-len 32768`, `--gpu-memory-utilization 0.90`, `--max-num-seqs 16`; lower utilization to 0.85 if needed. |
| Long context temptation | Medium | Do not enable 128K/YaRN unless product demo requires it. Validate 32K first, then 64K. |
| Tunnel URL instability | High for demos | Use named Cloudflare Tunnel with stable hostname. Quick Tunnel only for dev. |
| Quick Tunnel lacks SSE | Medium | Use non-streaming API responses or named tunnel; avoid Gradio streaming through Quick Tunnel. |
| Exposing raw vLLM | High | Bind vLLM to `127.0.0.1`; expose only LangGraph; require API keys. |
| HF Space outbound port block | High | Use HTTPS 443 tunnel URL only. |
| Cloud credits expire / VM destroyed | High | Keep setup script and cache path documented; destroy VM only after preserving required artifacts. |
| Model download time | Medium | Use persistent cache path on AMD scratch/data disk; pull model before demo. |
| Unverified exact AMD firewall behavior | Medium | Assume no public HTTP ingress and use outbound tunnel; this is robust even if public ingress exists. |

## Evidence map

### Sources used

1. vLLM ROCm installation docs  
   URL: https://docs.vllm.ai/en/latest/getting_started/installation/gpu/?device=rocm  
   Used for: official ROCm support, official image names, deprecation of AMD `rocm/vllm`.

2. vLLM Docker deployment docs  
   URL: https://docs.vllm.ai/en/latest/deployment/docker/  
   Used for: ROCm Docker `docker run` pattern and required device flags.

3. vLLM CLI reference  
   URL: https://docs.vllm.ai/en/latest/cli/serve/  
   Used for: `--api-key`, `--max-model-len`, `--dtype`, `--gpu-memory-utilization`, `--kv-cache-dtype`, related serve flags.

4. Docker Hub `vllm/vllm-openai-rocm` tags  
   URL: https://hub.docker.com/r/vllm/vllm-openai-rocm/tags  
   Used for: confirming `v0.20.1`, `latest`, `nightly` tags.

5. Local live Docker manifest checks  
   Commands:
   - `docker manifest inspect vllm/vllm-openai-rocm:latest`
   - `docker manifest inspect vllm/vllm-openai-rocm:v0.20.1`
   - `docker manifest inspect vllm/vllm-openai-rocm:nightly`
   Used for: practical existence confirmation.

6. AMD ROCm vLLM inference docs  
   URL: https://rocm.docs.amd.com/en/latest/how-to/rocm-for-ai/inference/benchmark-docker/vllm.html  
   Used for: AMD's current recommendation to use upstream vLLM docs and image.

7. AMD Developer Cloud page  
   URL: https://www.amd.com/en/developer/resources/cloud-access/amd-developer-cloud.html  
   Used for: MI300X small/large configuration, 192GB VRAM, Docker/Jupyter environment, cloud credit constraints.

8. AMD Developer Cloud getting-started article  
   URL: https://www.amd.com/es/developer/resources/technical-articles/2025/how-to-get-started-on-the-amd-developer-cloud-.html  
   Used for: SSH/Web Console/JupyterLab access model and preconfigured ROCm/Docker environment.

9. AMD vLLM Semantic Router article  
   URL: https://www.amd.com/en/developer/resources/technical-articles/2026/deploying-vllm-semantic-router-on-amd-developer-cloud.html  
   Used for: contemporary AMD example of vLLM on Developer Cloud, `/dev/kfd`, `/dev/dri`, Docker, local service composition.

10. Hugging Face Spaces overview  
    URL: https://huggingface.co/docs/hub/spaces-overview  
    Used for: Space hardware, networking allowed ports, secrets/variables.

11. Hugging Face Docker Spaces docs  
    URL: https://huggingface.co/docs/hub/main/spaces-sdks-docker  
    Used for: Docker Space capability and persistence caveat.

12. Qwen/Qwen2.5-72B-Instruct model card  
    URL: https://huggingface.co/Qwen/Qwen2.5-72B-Instruct  
    Used for: model size, BF16, vLLM command, 32K current config, YaRN long-context caveat.

13. Cloudflare Tunnel docs  
    URL: https://developers.cloudflare.com/tunnel/  
    Used for: outbound-only tunnel, no public IP/inbound firewall requirement, all-plan availability.

14. Cloudflare Tunnel setup docs  
    URL: https://developers.cloudflare.com/tunnel/setup/  
    Used for: Quick Tunnel command and Quick Tunnel limitations.

15. Cloudflare locally-managed tunnel docs  
    URL: https://developers.cloudflare.com/tunnel/advanced/local-management/create-local-tunnel/  
    Used for: stable named tunnel config and DNS routing.

16. Cloudflare run-parameters docs  
    URL: https://developers.cloudflare.com/tunnel/advanced/run-parameters/  
    Used for: Linux service/systemd behavior and log caveats.

17. ngrok agent docs  
    URL: https://ngrok.com/docs/agent  
    Used for: Linux service support and outbound TLS behavior.

18. ngrok Linux download docs  
    URL: https://ngrok.com/download/linux  
    Used for: Linux install and authtoken setup.

### Sources rejected or downgraded

- Old vLLM docs that recommend building ROCm Docker images from source: stale for this task because current vLLM docs now publish official ROCm Docker images.
- Old AMD `rocm/vllm` image examples: useful historical evidence only; current vLLM docs mark them deprecated.
- Reddit/community posts about ROCm/vLLM: not used for the final command because the task requires official docs.
- Unofficial mirrors of vLLM docs: not used.

## Main contradictions resolved

1. Contradiction: older docs and blogs use `rocm/vllm` or build-from-source; latest vLLM docs say use official `vllm/vllm-openai-rocm`.
   - Resolution: use `vllm/vllm-openai-rocm:v0.20.1`.
   - Confidence: 93/100 because official docs plus live Docker manifest confirm it.

2. Contradiction: Qwen2.5 advertises 128K context, but model card says current config is 32K and long context needs YaRN/static scaling.
   - Resolution: default `--max-model-len 32768`; long context is a separate validation profile.
   - Confidence: 88/100 because the model card is clear, but actual available KV memory must be verified on the assigned AMD instance.

3. Contradiction: AMD Developer Cloud may have a public IP, but the project assumes no open HTTP ingress.
   - Resolution: use Cloudflare Tunnel outbound-only path regardless of public ingress.
   - Confidence: 82/100 because Cloudflare mechanics are verified; exact ADC firewall defaults are third-party/provider-specific.

## Negative results

- I did not find an official AMD Developer Cloud page that guarantees public inbound HTTP/HTTPS port exposure for arbitrary app services.
- I did not find a current official vLLM doc that gives a Qwen2.5-72B-on-MI300X-specific one-line command. The final command is assembled from official vLLM ROCm Docker docs, vLLM CLI docs, AMD MI300X specs, and the Qwen model card.
- I did not use any unofficial benchmark claim to decide `--max-model-len`.
- I did not confirm actual runtime load on a live MI300X instance in this step; no AMD instance was available in the local workspace.

## First-run checklist

1. On AMD VM:

```bash
rocminfo | head
docker --version
ls -l /dev/kfd /dev/dri
```

2. Start vLLM using the default command above.

3. Watch logs:

```bash
sudo docker logs -f infraagent-vllm-qwen25-72b
```

4. Confirm OpenAI-compatible model list:

```bash
curl -s http://127.0.0.1:8000/v1/models \
  -H "Authorization: Bearer $VLLM_API_KEY" | jq
```

5. Start LangGraph API on `127.0.0.1:8010`.

6. Start named Cloudflare Tunnel to `http://localhost:8010`.

7. Set HF Space secrets and test one non-streaming request.

## Research snapshot

### Research Slug

- Slug: `qwen-rocm-hf-tunnel`

### Query Type

- Type: new
- Depth: Standard
- Evidence quality: high

### Query Log

| Query | Found | Used |
|---|---:|---:|
| `site:docs.vllm.ai ROCm docker vLLM image rocm vllm-openai latest` | vLLM ROCm install docs | yes |
| `docs.vllm.ai latest deployment docker rocm vllm/vllm-openai rocm image` | vLLM Docker deployment docs | yes |
| `vLLM official ROCm Docker image tag rocm vllm-openai Docker Hub` | Docker Hub tags | yes |
| `site:rocm.docs.amd.com vLLM ROCm Docker MI300X Qwen2.5 72B` | AMD ROCm vLLM docs | yes |
| `site:huggingface.co/docs/hub spaces docker gradio streamlit external API outgoing requests` | HF Spaces networking/docs | yes |
| `Cloudflare Tunnel official docs cloudflared tunnel run locally-managed Linux headless expose localhost HTTPS` | Cloudflare Tunnel docs | yes |
| `ngrok Linux agent free static domain http tunnel official docs authtoken headless` | ngrok agent docs | partial fallback |
| `AMD Developer Cloud documentation SSH ports firewall public IP expose port` | AMD cloud specs and SSH/Jupyter docs | partial |

### Key Sources

| URL | Date | Type | Why it mattered |
|---|---|---|---|
| https://docs.vllm.ai/en/latest/getting_started/installation/gpu/?device=rocm | current docs, checked 2026-05-09 | official docs | confirms ROCm support and official image family |
| https://docs.vllm.ai/en/latest/deployment/docker/ | current docs, checked 2026-05-09 | official docs | gives ROCm Docker run pattern |
| https://hub.docker.com/r/vllm/vllm-openai-rocm/tags | checked 2026-05-09 | primary registry | confirms current tags |
| https://rocm.docs.amd.com/en/latest/how-to/rocm-for-ai/inference/benchmark-docker/vllm.html | current docs, checked 2026-05-09 | AMD docs | confirms AMD defers latest deployment to upstream vLLM |
| https://huggingface.co/docs/hub/spaces-overview | current docs, checked 2026-05-09 | official docs | confirms networking limits and secrets |
| https://developers.cloudflare.com/tunnel/ | current docs, checked 2026-05-09 | official docs | confirms outbound-only public tunneling |
| https://huggingface.co/Qwen/Qwen2.5-72B-Instruct | checked 2026-05-09 | model card | confirms BF16, model size, vLLM path, context caveat |

### Freshness

- Checked on: 2026-05-09 02:20 Europe/Minsk
- Current enough: yes for image tags and network topology.
- Stale or unresolved: actual AMD instance firewall defaults and runtime Qwen2.5-72B memory headroom must be verified on the assigned VM.

### Main Contradictions

- `rocm/vllm` legacy vs `vllm/vllm-openai-rocm` current: resolved in favor of upstream vLLM image.
- 128K model capability vs 32K current config: resolved in favor of 32K default.
- Public IP possible vs no public HTTP assumption: resolved by outbound Cloudflare Tunnel.

### What is still unknown

- Exact ROCm driver/runtime version on the assigned AMD Developer Cloud image.
- Whether the assigned VM is 1x or 8x MI300X.
- Whether the hackathon provider firewall already exposes app ports.
- Runtime memory headroom for 64K+ contexts.

### Confidence

- Overall: 86/100
- Docker image choice: 93/100
- Default vLLM command: 84/100
- Cloudflare Tunnel topology: 90/100
- HF Spaces outbound HTTPS compatibility: 91/100
- Long-context profile: 65/100 until live MI300X test

### Provenance

- Sources reviewed: 18
- Sources used: 18
- Sources rejected: old source-build vLLM docs, deprecated AMD image examples, Reddit/community posts, unofficial mirrors
- Major verified claims:
  - Official vLLM ROCm image is `vllm/vllm-openai-rocm`.
  - Docker tags `latest`, `v0.20.1`, and `nightly` exist.
  - HF Spaces allows outbound 80/443/8080 and supports secrets.
  - Cloudflare Tunnel is outbound-only and can route public hostnames to localhost services.
  - Qwen2.5-72B-Instruct is BF16 and current config is 32K.
- Major inferred claims:
  - One MI300X 192GB should fit Qwen2.5-72B BF16 at 32K with conservative concurrency.
  - LangGraph belongs on AMD VM next to vLLM for latency/control.
- Blocked checks:
  - No live AMD MI300X runtime test in this environment.
  - No actual Cloudflare domain/account configured here.

### Handoff

Next agent should:

1. Run the Docker command on the actual AMD VM.
2. If OOM occurs, lower `--gpu-memory-utilization` to `0.85`, `--max-num-seqs` to `8`, or temporarily test `--max-model-len 16384`.
3. Confirm `/v1/models` and one chat completion before building LangGraph.
4. Expose LangGraph, not vLLM, through Cloudflare.
5. Put backend URL/API key into HF Space secrets.

[P-18 V2 COMPLETE: 2026-05-09 02:20 | Type: new | Depth: Standard | Check: Critical 5/5 | Important 5/5 | Recommended 4/4 | Confidence: 86/100]
