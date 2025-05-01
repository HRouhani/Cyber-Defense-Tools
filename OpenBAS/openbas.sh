#!/bin/bash

set -e
exec > /var/log/openbas_user_data.log 2>&1

# CONFIG ########################################################
INSTALL_DIR="/opt/openbas"
DOCKER_REPO_OPENBAS="https://github.com/OpenBAS-Platform/docker.git"
DOCKER_REPO_CALDERA="https://github.com/OpenBAS-Platform/caldera.git"
ENV_FILE="$INSTALL_DIR/docker/.env"
CALDERA_YML_FILE="$INSTALL_DIR/docker/caldera.yml"
RABBIT_CONF_FILE="$INSTALL_DIR/docker/rabbitmq.conf"
SYSTEM_RABBIT_CONF_DIR="/etc/rabbitmq"
SYSTEM_RABBIT_CONF_FILE="$SYSTEM_RABBIT_CONF_DIR/rabbitmq.conf"

# INSTALL DEPENDENCIES #########################################
echo "[+] Updating system and installing Docker dependencies"
sleep 100
for i in {1..5}; do
    sudo apt update && sudo apt install -y docker.io docker-compose git curl jq uuid-runtime cloud-guest-utils && break
    echo "Attempt $i failed, retrying in 10 seconds..."
    sleep 10

done

sudo systemctl enable docker && sudo systemctl start docker

# SETUP FOLDER STRUCTURE ######################################
echo "[+] Creating installation directory at $INSTALL_DIR..."
sudo mkdir -p "$INSTALL_DIR"
sudo chown "$USER:$USER" "$INSTALL_DIR"

# CLONE REPOSITORIES ##########################################
echo "[+] Cloning OpenBAS and Caldera repos..."
git clone "$DOCKER_REPO_OPENBAS" "$INSTALL_DIR/docker"
git clone "$DOCKER_REPO_CALDERA" "$INSTALL_DIR/caldera"

### MODIFY docker-compose.yml FOR RABBITMQ CONFIG PATH ######################
echo "[+] Updating docker-compose.yml to use absolute path for RabbitMQ config..."
sed -i "/rabbitmq:/,/restart:/ {/source:/s|source:.*|source: /opt/openbas/docker/rabbitmq.conf|}" "$INSTALL_DIR/docker/docker-compose.yml"

# COPY Caldera config file if needed (already included in OpenBAS repo now)
if [ -f "$INSTALL_DIR/docker/caldera.yml" ]; then
    echo "[+] Caldera configuration found in OpenBAS repo."
else
    echo "[-] Caldera configuration not found in expected location. Exiting."
    exit 1
fi

# CREATE .env FILE ###########################################
echo "[+] Creating .env file..."
cat <<EOF > "$ENV_FILE"
POSTGRES_USER=openbas
POSTGRES_PASSWORD=openbasPass123
KEYSTORE_PASSWORD=openbasKey123
MINIO_ROOT_USER=openbasMinio
MINIO_ROOT_PASSWORD=openbasMinioPass
RABBITMQ_DEFAULT_USER=openbasRabbit
RABBITMQ_DEFAULT_PASS=openbasRabbitPass
SPRING_MAIL_HOST=smtp.example.com
SPRING_MAIL_PORT=465
SPRING_MAIL_USERNAME=openbas@example.com
SPRING_MAIL_PASSWORD=mailpass123
SPRING_MAIL_PROPERTIES_MAIL_SMTP_AUTH=true
SPRING_MAIL_PROPERTIES_MAIL_SMTP_SSL_ENABLE=true
SPRING_MAIL_PROPERTIES_MAIL_SMTP_STARTTLS_ENABLE=false
OPENBAS_MAIL_IMAP_ENABLED=false
OPENBAS_MAIL_IMAP_HOST=imap.example.com
OPENBAS_MAIL_IMAP_PORT=993
OPENBAS_MAIL_IMAP_AUTH=true
OPENBAS_MAIL_IMAP_SSL_ENABLE=true
OPENBAS_MAIL_IMAP_STARTTLS_ENABLE=false
OPENBAS_ADMIN_EMAIL=admin@example.com
OPENBAS_ADMIN_PASSWORD=openbasAdmin123
OPENBAS_ADMIN_TOKEN=a65effa0-c537-4732-a3dd-a6d0a23d9c98
OPENBAS_BASE_URL=http://localhost:8080
CALDERA_URL=http://caldera:8888
CALDERA_PUBLIC_URL=http://localhost:8888
CALDERA_API_KEY=changemeapikey
INJECTOR_CALDERA_ENABLE=true
EXECUTOR_CALDERA_ENABLE=true
COLLECTOR_CALDERA_ENABLE=false
COLLECTOR_CALDERA_ID=4beb7ea4-3216-4034-8938-f2044d51212e
COLLECTOR_MITRE_ATTACK_ID=3050d2a3-291d-44eb-8038-b4e7dd107436
COLLECTOR_ATOMIC_RED_TEAM_ID=0f2a85c1-0a3b-4405-a79c-c65398ee4a76
OPENBAS_HEALTHCHECK_KEY=32ddca9b-0cc3-4db0-a917-808ee7825487
EOF

# CREATE RabbitMQ CONFIG FILES #########################################
echo "[+] Creating RabbitMQ config file in project and system directories..."
sudo mkdir -p "$SYSTEM_RABBIT_CONF_DIR"
cat <<EOF | sudo tee "$RABBIT_CONF_FILE" "$SYSTEM_RABBIT_CONF_FILE"
max_message_size = 536870912
consumer_timeout = 86400000
EOF

# PATCH docker-compose.yml to include OPENBAS_HEALTHCHECK_KEY in environment block of OpenBAS
echo "[+] Adding OPENBAS_HEALTHCHECK_KEY to OpenBAS environment block..."
sed -i "/- OPENBAS_ADMIN_TOKEN=.*/a \      - OPENBAS_HEALTHCHECK_KEY=\${OPENBAS_HEALTHCHECK_KEY}" "$INSTALL_DIR/docker/docker-compose.yml"

# START OPENBAS + CALDERA ##########################################
echo "[+] Starting OpenBAS and Caldera stack..."
cd "$INSTALL_DIR/docker"

# To install only OpenBAS
docker-compose up -d


# Install OpenBAS together with Caldera
docker-compose -f docker-compose.yml \
  -f docker-compose.caldera.yml \
  -f docker-compose.caldera-executor.yml \
  up -d

sleep 60

echo "[✓] OpenBAS should be available at: http://localhost:8080"
echo "[✓] Caldera should be available at: http://localhost:8888"
