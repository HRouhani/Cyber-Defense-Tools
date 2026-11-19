# Local LLM Improper Output Handling Lab — Kali Linux

A standalone, intentionally vulnerable training environment for Chapter 8. It demonstrates **stored XSS, server-side template injection (SSTI), server-side request forgery (SSRF), OS command injection, and SQL injection** through downstream handling of attacker-influenced content. It includes an optional **real local LLM transform** through Ollama, plus literal fixture mode for deterministic results.

> **Safety:** These services are intentionally insecure. Run only on your own isolated Kali VM or another machine you control. The web interface binds to `127.0.0.1:8508`. Do **not** change this to `0.0.0.0`, enable remote port forwarding, or expose the containers to a production network. No private files, credentials, or live cloud metadata are required. The application has synthetic data only.

## 1. Requirements

- Kali Linux with Docker Engine and Docker Compose v2.
- Ideally **8–10 GB RAM available to Kali** if running Ollama and a browser simultaneously; lighter workloads may run with less. CPU-only inference works but can be slow.
- Approximately **8–12 GB free disk space** for the images, containers, and downloaded model.
- Network access **during initial installation and model downloads**. Afterwards, the exercise data is local.

Install packages:

```bash
sudo apt update
sudo apt install -y docker.io git curl jq
sudo systemctl enable --now docker
```

Verify Docker and Compose:

```bash
sudo docker --version
sudo docker compose version
```

If `docker compose` is unavailable, install the Compose v2 plugin available for your Kali version (often `docker-compose-plugin`), or consult the Kali Docker documentation. Do not assume the older `docker-compose` executable accepts identical commands.

## 2. Repository layout

Copy the complete `labs/improper-output-lab/` directory from this chapter's ZIP into your repository:

```text
labs/improper-output-lab/
├── README.md
├── Dockerfile
├── nginx.conf
├── compose.yaml
├── requirements.txt
├── app.py
├── internal_service.py
├── public_service.py
└── test_lab.py
```

Run all following commands from `labs/improper-output-lab/`.

## 3. Build and start containers

```bash
cd labs/improper-output-lab
sudo docker compose -f compose.yaml up -d --build
sudo docker compose -f compose.yaml ps
```

Pull the **local** language model once:

```bash
sudo docker compose -f compose.yaml exec ollama ollama pull llama3.2:1b
sudo docker compose -f compose.yaml exec ollama ollama list
```

**Note:** Ollama is a separate service inside Docker. If you already have Ollama installed on your Kali host, the two instances are independent. The model must be pulled inside the Compose `ollama` service for the optional LLM transform.

Open **http://127.0.0.1:8508** in a browser and verify:

```bash
curl -s http://127.0.0.1:8508/health | jq
```

Expected response contains `"status": "ok"` and `"lab_model": "llama3.2:1b"`.

The training target has five separate, locally reachable routes. A minimal **Nginx gateway** forwards the localhost port to the isolated web container; the vulnerable backend itself is not attached to the external ingress network. The synthetic *internal* service (`internal:8765`) has **no published port** on Kali; the web container can access it on the private Docker network. The isolated Ollama API is also not published to Kali. A separate `model-download` network allows Ollama to obtain its model weights at setup time; the web and mock services have no direct internet egress through that network.

## 4. First: trace the data flow

```text
[Browser input]
      |
      v
[Literal fixture OR Ollama text transform]
      |
      v
[Untrusted stored field / tool argument]
      |
      +--> HTML preview (XSS)
      +--> Jinja template compilation (SSTI)
      +--> HTTP client (SSRF)
      +--> shell invocation (command injection)
      +--> database query (SQL injection)
```

In **literal fixture mode**, the LLM is bypassed: the goal is to reproduce and isolate a downstream flaw reliably. In **Ollama transform mode** (available on all five exercises), the model rewrites the field before it reaches the sink. Compare the recorded value to the original prompt to see if the payload survived. A successful fixture test **does not** prove that the LLM can be persuaded to generate the same payload.

## 5. Exercise A — Stored XSS

Go to **Invoice → stored XSS and SSTI**.

Customer name:

```html
<img src=x onerror=alert('LAB-XSS')>
```

Service description: `Security review`.

1. Use **Literal fixture** mode, click **Create invoice**.
2. Open **XSS vulnerable preview**. The browser should show an alert saying `LAB-XSS`.
3. Open **XSS hardened preview**. The payload should appear as literal text instead of executable markup.
4. Repeat with **Ollama transform**. Compare the *actual stored values* shown after submission; the model may modify or reject the string.

**Root cause:** Marking untrusted text as safe HTML (`|safe`) lets it reach an HTML sink unescaped. **Fix:** Autoescape in the correct output context, remove unsafe HTML, and apply CSP as an additional layer.

## 6. Exercise B — SSTI

Create a new invoice:

- Customer name: `Ada Example`
- Service description: `{{ 7 * 7 }}`
- Mode: Literal fixture

Open the **SSTI vulnerable preview**; the rendered service value becomes **49**. The **SSTI hardened preview** preserves `{{ 7 * 7 }}` literally.

Now create an invoice with:

```jinja2
{{ lab_flag }}
```

The vulnerable preview displays the fictional value `FLAG{template-context-educational}`. This is a deliberate, synthetic marker, **not a real secret**. The vulnerable path uses Jinja's sandbox to limit demonstration risk, but compiling user-controlled text as a template is still an unsafe design pattern. Sandboxing is **not** a substitute for keeping templates static.

**Root cause:** Using untrusted data as a template *source* instead of passing it to a fixed template as a variable. **Fix:** Keep template source static; pass only typed, escaped values.

## 7. Exercise C — SSRF

Open **Server-side fetch → SSRF**.

Start with:

```text
http://public-service:8766/hello
```

Both vulnerable and hardened modes should accept this public lab destination.

Next use:

```text
http://internal:8765/metadata
```

- **Vulnerable:** Returns fictional instance and model information from the server-only Docker service.
- **Hardened:** Returns a block message.

This is a genuine network-boundary demonstration: the `internal` service is reachable to the web backend but is **not published to the browser host**. For safety, even vulnerable mode is scoped by code to the two fictional Docker services; it cannot fetch arbitrary internet targets or real cloud metadata.

**Root cause:** The application allowed an untrusted URL to select a backend-accessible destination. **Fix:** Strict destination allowlist, network egress control, no redirects, and validated DNS/IP handling.

## 8. Exercise D — OS command injection

Open **Host check → command injection** and submit:

```text
127.0.0.1; echo LAB_CMD_OK
```

- **Vulnerable:** The result includes `LAB_CMD_OK` as a separate line because the payload was interpolated into a shell command.
- **Hardened:** Rejects the value because it is not a single valid IP address.

This is deliberately an **echo-based simulated host check**, not a real Nmap or ICMP scan. The unsafe shell command runs as a non-root user inside a resource-limited, read-only Docker container. No OS-level attacker persistence is needed or intended.

**Root cause:** Building a shell command string from an untrusted model/tool argument and running it with `shell=True`. **Fix:** Validated typed arguments and shell-free execution (`subprocess.run([...], shell=False)`); use narrow tools instead of generic shell access.

## 9. Exercise E — SQL injection

Open **Invoice lookup → SQL injection**.

First enter `Ada Example` to retrieve its single synthetic record. Next enter:

```sql
' OR 1=1 --
```

- **Vulnerable:** SQL string concatenation returns all three fictional invoice rows.
- **Hardened:** The query uses a bound SQL parameter and returns no match.

**Root cause:** Building a SQL statement by concatenating untrusted text. **Fix:** Parameter binding, narrowly scoped queries, and restricted database accounts. If an LLM generates an entire SQL statement, use explicit tool APIs or a validation/approval layer rather than trusting LLM-generated SQL.

## 10. Testing via curl (no browser required)

Example: send an SSRF probe:

```bash
curl -s -X POST http://127.0.0.1:8508/fetch \
  --data-urlencode 'target=http://internal:8765/metadata' \
  --data-urlencode 'mode=vulnerable'
```

Inspect the activity log:

```bash
curl -s http://127.0.0.1:8508/events
```

## 11. Why these tests are valid, and what they do **not** prove

| Demonstration | What it proves | What it does not prove |
|---|---|---|
| Literal fixture → XSS alert | Unsafe HTML rendering executes user-controlled markup | That a particular model will preserve the payload |
| LLM transform → stored suspicious content | A model can pass dangerous characters to a sink in this run | That all prompts or models will do so |
| Jinja expression → 49 | Untrusted text is compiled as a template | That arbitrary OS code execution is possible |
| Internal service reached | Backend can reach a destination outside normal allowlist | That any cloud credential or real metadata is exposed |
| Shell marker appears | Shell command string interpreted metacharacters | That a real port scan was performed |
| SQL returns extra rows | Query structure was altered by input | That a production database is affected |

## 12. Optional tools for deeper testing

- **OWASP ZAP** — intercept and replay local web requests: https://www.zaproxy.org/
- **mitmproxy** — capture HTTP flows: https://mitmproxy.org/
- **OWASP Juice Shop** — complementary traditional XSS, SSTI, and SSRF exercises: https://github.com/juice-shop/juice-shop
- **OWASP LLMForge** — complementary LLM-security challenges: https://github.com/SasanLabs/LLMForge
- **garak** — scan language-model behavior; it does not automatically validate every downstream sink: https://github.com/NVIDIA/garak

## 13. Stop and reset

```bash
sudo docker compose -f compose.yaml down
```

Reset models too (removes downloaded Ollama weights stored in the named volume):

```bash
sudo docker compose -f compose.yaml down -v
```

The synthetic invoice records and training activity log are stored in memory, so stopping the web container clears them.

## 14. Run local smoke tests

After starting the containers, run the included deterministic unit tests within the web container:

```bash
sudo docker compose -f compose.yaml exec web python test_lab.py
```

The tests check expected vulnerable/hardened behavior with synthetic inputs. They mock the actual network request for SSRF verification and therefore do not access real external infrastructure. They do **not** perform model inference. A separate manual exercise is required to validate actual Ollama behavior.

## 15. Troubleshooting

| Problem | Resolution |
|---|---|
| `docker compose` unknown | Install Compose v2; check Kali package names, or use the v1 binary only after checking its compatibility |
| Port 8508 in use | Stop the conflicting process or choose another **localhost** port in `compose.yaml` |
| `503` from Ollama transform | Run `docker compose exec ollama ollama pull llama3.2:1b` and wait for completion |
| CPU load high | Use literal fixture mode; keep only one Ollama request running at a time |
| Model download cannot connect | Verify that the `ollama` service is connected to `model-download` network and the VM has initial internet access |
| Images cannot build | Check `sudo docker compose logs`, and verify disk space with `df -h` |
| Input produces different LLM output | Inspect actual stored fields; the model is stochastic and may refuse or transform the value |
| JavaScript alert doesn't appear | Check that you opened **vulnerable** preview, not safe preview, and that payload survived Ollama if selected |

## References

- OWASP LLM05:2025: https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/
- Jinja sandbox limitations: https://jinja.palletsprojects.com/en/stable/sandbox/
- OWASP SSTI prevention: https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Template_Injection_Prevention_Cheat_Sheet.html
- Flask templating and autoescaping: https://flask.palletsprojects.com/en/stable/templating/
- Python sqlite3 parameters: https://docs.python.org/3/library/sqlite3.html
