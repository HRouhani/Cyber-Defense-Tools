# 21. Appendix — Recreate the Ollama and Open WebUI Lab on Ubuntu

> **Purpose:** Reproduce the practical environment from this module on a personal Ubuntu system without access to the OffSec Public Cloud Lab.
>
> **Recommended design:** Run Ollama and Open WebUI as separate Docker containers managed by Docker Compose. This keeps the environment reproducible, stores data persistently, and avoids host-to-container networking problems.
>
> **Last verified:** July 2026. Model names and container versions may change, so record the versions used for a long-lived lab.

---

## 21.1 Resulting Architecture

```text
Browser
  |
  | http://localhost:3000
  v
Open WebUI container
  |
  | http://ollama:11434
  v
Ollama container
  |
  v
Downloaded model files
```

Both services run locally. The example configuration binds the web interface and Ollama API to `127.0.0.1`, so they are not directly exposed to other computers on the network.

---

## 21.2 Prerequisites

Use a supported 64-bit Ubuntu release with:

- Internet access for downloading containers and models
- At least several gigabytes of free storage
- Docker Engine and the Docker Compose plugin
- A modern CPU; a supported GPU is optional but improves inference speed

Model files can range from a few gigabytes to hundreds of gigabytes. Start with a small model such as `llama3.2:1b` when using CPU-only hardware.

Check the system architecture:

```bash
uname -m
```

Common expected values are:

```text
x86_64
arm64 / aarch64
```

---

## 21.3 Install Docker Engine and Docker Compose

Remove conflicting distribution packages if they are present:

```bash
sudo apt remove -y \
  docker.io \
  docker-compose \
  docker-compose-v2 \
  docker-doc \
  podman-docker \
  containerd \
  runc
```

It is normal if Ubuntu reports that some packages are not installed.

Add Docker's official repository:

```bash
sudo apt update
sudo apt install -y ca-certificates curl

sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF_DOCKER
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF_DOCKER

sudo apt update
```

Install Docker Engine and the Compose plugin:

```bash
sudo apt install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin
```

Verify Docker:

```bash
sudo systemctl status docker --no-pager
sudo docker run --rm hello-world
sudo docker compose version
```

If Docker is not running:

```bash
sudo systemctl enable --now docker
```

> The examples below use `sudo docker`. Adding a user to the `docker` group is optional, but membership in that group grants highly privileged control over the host.

---

## 21.4 Create the Local LLM Lab Directory

Create a dedicated directory:

```bash
mkdir -p ~/llm-lab
cd ~/llm-lab
```

Generate a persistent secret for Open WebUI:

```bash
printf 'WEBUI_SECRET_KEY=%s\n' "$(openssl rand -hex 32)" > .env
chmod 600 .env
```

The same secret should be retained when the Open WebUI container is recreated. Changing it can invalidate existing login sessions.

Do not commit `.env` to Git:

```bash
printf '.env\n' > .gitignore
```

---

## 21.5 Create the Docker Compose Configuration

Create `compose.yaml`:

```bash
nano compose.yaml
```

Add the following content:

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    restart: unless-stopped
    volumes:
      - ollama-data:/root/.ollama
    ports:
      - "127.0.0.1:11434:11434"

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    restart: unless-stopped
    depends_on:
      - ollama
    ports:
      - "127.0.0.1:3000:8080"
    environment:
      OLLAMA_BASE_URL: http://ollama:11434
      WEBUI_SECRET_KEY: ${WEBUI_SECRET_KEY}
    volumes:
      - open-webui-data:/app/backend/data

volumes:
  ollama-data:
  open-webui-data:
```

### What This Configuration Does

| Configuration | Purpose |
|---|---|
| `ollama/ollama` | Runs the Ollama model server |
| `ghcr.io/open-webui/open-webui` | Runs the browser interface |
| `http://ollama:11434` | Lets Open WebUI reach Ollama by its Compose service name |
| `127.0.0.1:3000:8080` | Makes Open WebUI available only on the local computer |
| `127.0.0.1:11434:11434` | Makes the Ollama API available only on the local computer |
| Named volumes | Preserve models, chats, accounts, and settings after restarts |
| `restart: unless-stopped` | Restarts the services after a reboot unless manually stopped |

### Reproducible Versions

The tags `latest` and `main` change over time. They are convenient for a learning environment, but a long-lived or production-like lab should pin exact versions.

Conceptual example:

```yaml
image: ghcr.io/open-webui/open-webui:<specific-version>
```

Record the versions used:

```bash
sudo docker image ls ollama/ollama
sudo docker image ls ghcr.io/open-webui/open-webui
```

---

## 21.6 Start the Environment

From `~/llm-lab`, run:

```bash
sudo docker compose up -d
```

Check the service status:

```bash
sudo docker compose ps
```

Review startup logs if needed:

```bash
sudo docker compose logs -f ollama
```

In another terminal:

```bash
cd ~/llm-lab
sudo docker compose logs -f open-webui
```

Stop following logs with `Ctrl+C`. This does not stop the containers.

---

## 21.7 Verify the Ollama API

Check the Ollama version endpoint:

```bash
curl http://127.0.0.1:11434/api/version
```

A successful result is JSON similar to:

```json
{
  "version": "<installed-version>"
}
```

List downloaded models through the API:

```bash
curl http://127.0.0.1:11434/api/tags
```

At first, the model list may be empty because no model has been downloaded yet.

---

## 21.8 Download a Model

Pull the small model used in the OffSec chapter:

```bash
cd ~/llm-lab
sudo docker compose exec ollama ollama pull llama3.2:1b
```

List downloaded models:

```bash
sudo docker compose exec ollama ollama list
```

View model information:

```bash
sudo docker compose exec ollama ollama show llama3.2:1b
```

The output includes information such as:

- Architecture
- Parameter count
- Context length
- Embedding length
- Quantization
- License information

> If this exact model tag is unavailable in the future, select another small instruction model from the Ollama model library and document the chosen name and version.

---

## 21.9 Use Ollama from the Command Line

Start an interactive session:

```bash
sudo docker compose exec ollama ollama run llama3.2:1b
```

Enter a prompt:

```text
>>> What is the capital of France?
```

Exit the session:

```text
/bye
```

Send a single prompt without entering an interactive session:

```bash
sudo docker compose exec ollama \
  ollama run llama3.2:1b \
  "Explain self-attention in three sentences."
```

Show currently loaded models:

```bash
sudo docker compose exec ollama ollama ps
```

### Command Translation from the OffSec Lab

| OffSec lab command | Local Docker equivalent |
|---|---|
| `ollama list` | `sudo docker compose exec ollama ollama list` |
| `ollama ps` | `sudo docker compose exec ollama ollama ps` |
| `ollama show MODEL` | `sudo docker compose exec ollama ollama show MODEL` |
| `ollama run MODEL` | `sudo docker compose exec ollama ollama run MODEL` |
| `ollama pull MODEL` | `sudo docker compose exec ollama ollama pull MODEL` |

---

## 21.10 Access Open WebUI

On the same Ubuntu computer, open a browser and visit:

```text
http://localhost:3000
```

On the first visit:

1. Create the first account.
2. The first account becomes the Open WebUI administrator.
3. Use a strong, unique password.
4. Confirm that `llama3.2:1b` appears in the model selector.
5. Select the model and start a new chat.

If the model does not appear:

1. Open **Admin Settings**.
2. Open **Connections**.
3. Select the Ollama connection.
4. Verify that the URL is:

```text
http://ollama:11434
```

Do not use `localhost:11434` inside the Open WebUI container. Inside a container, `localhost` refers to that container itself, not the Ollama container.

---

## 21.11 Test the Ollama Generate API

Send a non-streaming request:

```bash
curl http://127.0.0.1:11434/api/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "llama3.2:1b",
    "prompt": "Why are bananas yellow?",
    "stream": false
  }'
```

A formatted version using Python:

```python
import requests

api_url = "http://127.0.0.1:11434/api/generate"

payload = {
    "model": "llama3.2:1b",
    "prompt": "Why are bananas yellow?",
    "stream": False,
}

response = requests.post(
    api_url,
    json=payload,
    timeout=120,
)
response.raise_for_status()

print(response.json()["response"])
```

Install the Python dependency if required:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests
```

Run the script:

```bash
python3 api_call.py
```

Always verify factual responses. A fluent answer can still be incorrect.

---

## 21.12 Access the Lab from Another Computer Safely

The provided Compose configuration listens only on `127.0.0.1`. This is intentional.

For an Ubuntu server without a local desktop, use an SSH tunnel from the client computer:

```bash
ssh -L 3000:127.0.0.1:3000 <user>@<server-ip>
```

Keep the SSH session open, then visit on the client computer:

```text
http://localhost:3000
```

To access the Ollama API through the same tunnel, forward both ports:

```bash
ssh \
  -L 3000:127.0.0.1:3000 \
  -L 11434:127.0.0.1:11434 \
  <user>@<server-ip>
```

The client can then use:

```text
http://localhost:3000
http://localhost:11434/api/version
```

This approach is safer than exposing Open WebUI or the unauthenticated Ollama API directly to the internet.

---

## 21.13 Start, Stop, and Restart the Lab

Run these commands from `~/llm-lab`.

### Stop Containers Without Deleting Them

```bash
sudo docker compose stop
```

### Start Existing Containers

```bash
sudo docker compose start
```

### Restart Services

```bash
sudo docker compose restart
```

### Stop and Remove Containers

```bash
sudo docker compose down
```

The named volumes remain, so models, accounts, settings, and chats are preserved.

### Delete the Entire Lab and Its Data

```bash
sudo docker compose down -v
```

> **Warning:** The `-v` option deletes the model and Open WebUI data volumes. This removes downloaded models, accounts, chats, and settings.

---

## 21.14 Update Ollama and Open WebUI

Pull updated images:

```bash
cd ~/llm-lab
sudo docker compose pull
```

Recreate the containers while preserving the volumes:

```bash
sudo docker compose up -d
```

Confirm the services:

```bash
sudo docker compose ps
curl http://127.0.0.1:11434/api/version
```

For a reproducible course environment, review release notes and pin versions instead of automatically following `latest` and `main`.

---

## 21.15 Back Up the Lab

List the volumes:

```bash
sudo docker volume ls
```

The exact volume names normally include the Compose project name, for example:

```text
llm-lab_ollama-data
llm-lab_open-webui-data
```

Create backups:

```bash
mkdir -p ~/llm-lab-backups

sudo docker run --rm \
  -v llm-lab_ollama-data:/data:ro \
  -v ~/llm-lab-backups:/backup \
  alpine \
  tar -czf /backup/ollama-data.tar.gz -C /data .

sudo docker run --rm \
  -v llm-lab_open-webui-data:/data:ro \
  -v ~/llm-lab-backups:/backup \
  alpine \
  tar -czf /backup/open-webui-data.tar.gz -C /data .
```

Adjust the volume names if `sudo docker volume ls` displays different names.

---

## 21.16 Optional GPU Acceleration

The CPU-only configuration works without a dedicated GPU, but generation may be slow.

GPU configuration depends on the hardware:

- NVIDIA requires the NVIDIA driver and NVIDIA Container Toolkit.
- AMD uses an Ollama ROCm image and access to the relevant GPU devices.
- Some Intel and AMD systems may use Vulkan support.

Because driver and device configuration varies, follow the current official Ollama Docker hardware instructions for the system in use.

Before configuring GPU access, verify that the host operating system can see the GPU.

NVIDIA example:

```bash
nvidia-smi
```

Do not assume the container is using the GPU. Confirm it through Ollama logs and system GPU-monitoring tools.

---

## 21.17 Troubleshooting

### Open WebUI Does Not Open

Check container status:

```bash
sudo docker compose ps
```

Check logs:

```bash
sudo docker compose logs --tail=100 open-webui
```

Confirm that the port is listening:

```bash
ss -lntp | grep 3000
```

---

### Open WebUI Shows No Models

Confirm the model exists:

```bash
sudo docker compose exec ollama ollama list
```

Test Ollama from inside the Open WebUI container:

```bash
sudo docker compose exec open-webui \
  python -c 'import requests; print(requests.get("http://ollama:11434/api/tags", timeout=10).json())'
```

Verify the connection URL in Open WebUI:

```text
http://ollama:11434
```

---

### Ollama API Does Not Respond

Check the service:

```bash
sudo docker compose ps ollama
sudo docker compose logs --tail=100 ollama
```

Test locally:

```bash
curl -v http://127.0.0.1:11434/api/version
```

---

### Model Download Fails

Check free disk space:

```bash
df -h
```

Check Docker storage usage:

```bash
sudo docker system df
```

Retry the pull:

```bash
sudo docker compose exec ollama ollama pull llama3.2:1b
```

---

### Responses Are Very Slow

Possible causes include:

- CPU-only inference
- A model that is too large for the available hardware
- Insufficient RAM or VRAM
- A very long context
- Multiple concurrent requests

Start with a smaller model and shorter prompts.

Check the running model:

```bash
sudo docker compose exec ollama ollama ps
```

---

### Port Is Already in Use

Check the conflicting process:

```bash
sudo ss -lntp | grep -E ':3000|:11434'
```

Change the host-side port in `compose.yaml` if necessary.

Example:

```yaml
ports:
  - "127.0.0.1:3001:8080"
```

Open WebUI would then be available at:

```text
http://localhost:3001
```

---

## 21.18 Security Notes for a Local Red-Team Lab

- Keep the Ollama API bound to localhost unless remote access is deliberately secured.
- Do not expose port `11434` directly to the public internet.
- Keep Open WebUI authentication enabled.
- The first Open WebUI account becomes administrator; protect it with a strong password.
- Do not store real secrets, production credentials, or sensitive customer data in prompts.
- Treat downloaded models and extensions as software supply-chain dependencies.
- Review generated code before running it.
- Use separate volumes or separate Compose projects for experiments that should not share chat history or data.
- Back up important work before updates.
- Pin container versions when repeatability matters.

---

## 21.19 Minimal End-to-End Checklist

```bash
# 1. Enter the lab directory
cd ~/llm-lab

# 2. Start Ollama and Open WebUI
sudo docker compose up -d

# 3. Pull a small model
sudo docker compose exec ollama ollama pull llama3.2:1b

# 4. Verify Ollama
curl http://127.0.0.1:11434/api/version
sudo docker compose exec ollama ollama list

# 5. Open the web interface
# Browser: http://localhost:3000

# 6. Run a CLI prompt
sudo docker compose exec ollama \
  ollama run llama3.2:1b \
  "Explain what an LLM prompt is."
```

At this point, the reader has a persistent local environment for completing the GUI, CLI, library, and API exercises from this module.
