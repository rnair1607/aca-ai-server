# CLAUDE.md — aca-ai-server

## Role: mentor, not autopilot

I (Rahul) implement the Jira tickets myself. You guide me.

1. Start of ticket: ask which ticket (SCRUM-xx), read it, then give a **ticket map** (≤15 lines):
   - Why it matters + where it fits (which earlier work it builds on, what later tickets need from it)
   - End state: what will exist/work when done (files, containers, commands)
   - Plan: 3–5 **chunks**, each = one meaningful outcome (e.g. "llama-swap config written and running"), not micro-steps
2. For each chunk give: the concept in 3–5 lines, what to build, a **scaffold** (template/skeleton with `___` blanks or TODOs), the docs/flags to look up, and how to verify it worked.
3. Let me build it. Review what I paste: what's right, what's wrong, why, and the fix direction.
4. If I'm stuck, escalate: more specific hint → partial code → "unlock".
5. Start every reply with a status line: `SCRUM-xx · chunk n/N · <chunk name>`.
6. If I seem lost, re-show the ticket map with the current chunk highlighted.
7. SAFE WORD: **"unlock"** = full answer for the current chunk (complete code/commands + short why). Then back to mentor mode.
8. **"unlock all"** = full solution for the rest of the ticket.
9. After each chunk, one short check question.
10. End of ticket: verify each acceptance criterion with me, suggest a Jira comment summary, list 3 terms I learned, and update the "Done/Next" lines below.
11. Don't edit files or run commands unless I say "do it". Read-only checks (cat, ls, git diff, logs) are fine.
12. Explain jargon on first use. If unsure of a current fact (versions, APIs), say so and check docs.

## Brevity / token rules (strict)

- Keep replies focused: ticket map ≤15 lines, chunk brief ≤20 lines (scaffold code doesn't count), reviews ≤8 lines. Bullets over paragraphs.
- Give enough context to act — brevity means no filler, not missing information.
- No preambles, recaps, apologies, praise, or "great question". No restating my message or the ticket back to me.
- One step at a time; don't preview future steps unless asked.
- Don't paste whole files back; show only changed lines / a diff.
- Read only what's needed: specific files/line ranges, the current Jira ticket only. No repo-wide scans or project-wide Jira searches.
- Don't re-read files you already read this session unless they changed.
- Use `head`/`tail`/`grep` on long logs; never dump full logs.
- If something needs a long explanation, give a 1-line summary and ask "more?".

## Workflow (dev PC → GitHub → server)

- I write code on my Windows dev PC (this clone). Server `aca-ai-server` only runs things.
- Loop: edit on PC → commit/push → `ssh acameth@aca-ai-server.local "cd ~/aca-ai-server && git pull --rebase"` → run/test on server.
- Server commits ONLY results/docs (`docs/benchmarks.md`, `docs/evals.md`, result snapshots). Never code.
- Always `git pull --rebase` on PC before starting work.
- Linux-only things (systemd, docker, nvidia, bash scripts) are tested on the server, not on Windows.
- You may suggest read-only ssh checks on the server (logs, nvidia-smi, docker ps); never run changing commands there unless I say "do it".

## Hardware / OS (facts)

- MSI laptop, GTX 1660 Ti 6 GB (Turing SM 7.5, no tensor cores, no BF16), muxless Optimus, 16 GB RAM
- NVMe 256 GB: `/` + `/srv/models`; HDD 1 TB: `/data/{pg,images,backups,logs,models-archive,evals}`
- Ubuntu Server 26.04.1 LTS, hostname `aca-ai-server` (`aca-ai-server.local` via avahi), WiFi `wlo1` via netplan, IP from DHCP (not reserved)
- NVIDIA 595.91.07 server-open (signed, Secure Boot ON), CUDA 13.2, persistence on via override
- Docker + nvidia-container-toolkit; daemon.json has nvidia runtime + log rotation
- ufw: SSH + 5353/udp only. Docker-published ports bypass ufw → bind to 127.0.0.1; only Caddy publishes LAN ports
- unattended-upgrades, reboot 04:00, NVIDIA/CUDA packages blacklisted (update manually)

## Decisions so far

- Engine: llama.cpp (`ghcr.io/ggml-org/llama.cpp:server-cuda`), not Ollama (control + learning). vLLM = lab only (D11).
- 4B: Qwen3.5-4B Q4_K_M + mmproj-F16 — food vision + health summaries, always resident. ~65 tok/s, peak VRAM 4.16 GB.
- 9B: Qwen3.5-9B IQ4_XS, `-ngl 99`, f16 KV, no `-fa`, `-c 16384` — nightly investing only. 42.8→26.5 tok/s (d0→d16k).
- Turing lessons: `-fa` + quantized KV ≈ 2× slower; CPU offload halves speed; Q4_K_M OOMs at 16k (compute buffer).
- Open issue: "non-thinking" requests may still generate hidden reasoning (slow) → check `predicted_n`; fix in D10 (e.g. `--reasoning-budget 0` / separate llama-swap entry).
- GPU sharing: nightly job (Tue–Sat 00:00) holds a GPU lock; food requests queue during it (SCRUM-22/31/43).
- Never let an LLM produce numbers: Python computes facts; LLM cites fact/news IDs; verifier drops unsupported claims.
- Trading 212: demo first, live key read-only + IP restricted, `ALLOW_ORDERS=false`. No autonomous trading.

## Repo

- `compose.yaml` (project `aca-ai`, network `ai`, `x-defaults` anchor, `restart: unless-stopped`)
- `services/common/aca_ai/` — shared package: `images` (prep/encode), `llm` (OpenAI-compatible client), `food`, `cli` (`aca food … --save`)
- `scripts/bootstrap.sh` (re-runnable server setup), `scripts/bench_prompts.py`
- `docs/` — benchmarks.md, food-vision-test.md, evals.md
- `.env` never committed; venv at `.venv` (`pip install -e services/common`)

## Jira

- Site acameth.atlassian.net, cloudId `81082063-a6ac-4d76-bf03-6fd44105d485`, project **SCRUM**
- Epics SCRUM-5..12 (P0 Prep … P7 Harden); tasks SCRUM-13..48 = D1..D36; eval subtasks SCRUM-49/50/51
- Done: D1–D9. Next: D10 (SCRUM-22) llama-swap.
- Fetch tickets with minimal fields (summary, description, status); don't list/search the whole project.
