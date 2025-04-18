#!/bin/bash                                                                                                                                                                             
                                                                                                                                                                                        
set -e       
exec > /var/log/opencti_user_data.log 2>&1                                                                                                                                                        
                                                                                                                                                                                        
# CONFIG ########################################################

INSTALL_DIR="/opt/openCTI"                                                                                                                                                              
DOCKER_REPO="https://github.com/OpenCTI-Platform/docker.git"                                                                                                                            
ENV_FILE="$INSTALL_DIR/docker/.env"                                                                                                                                                     
RABBIT_CONF_FILE="$INSTALL_DIR/docker/rabbitmq.conf"                                                                                                                                    
SYSTEM_RABBIT_CONF_DIR="/etc/rabbitmq"                                                                                                                                                  
SYSTEM_RABBIT_CONF_FILE="$SYSTEM_RABBIT_CONF_DIR/rabbitmq.conf"                                                                                                                         
OPENCTI_PUBLIC_IP="54.158.175.39"                                                                                                                                                       
                                                                                                                                                                                        
# INSTALL DEPENDENCIES  #########################################                                                                                                                                                      
echo "[+] Updating system and installing Docker dependencies..."  

# Wait a bit for cloud-init to fully complete
sleep 100 

# Retry logic in case apt repo isn't ready immediately
for i in {1..5}; do
    sudo apt update && sudo apt install -y docker.io docker-compose git curl jq cloud-guest-utils && break
    echo "Attempt $i failed, retrying in 10 seconds..."
    sleep 10
done

sudo systemctl enable docker && sudo systemctl start docker                                                                                                                            
                                                                                                                                                                                        
### SETUP FOLDER STRUCTURE ######################################                                                                                                                                                          
echo "[+] Creating installation directory at $INSTALL_DIR..."                                                                                                                           
sudo mkdir -p "$INSTALL_DIR"                                                                                                                                                            
sudo chown "$USER:$USER" "$INSTALL_DIR"                                                                                                                                                 
                                                                                                                                                                                        
### CLONE OPENCTI REPO #########################################                                                                                                                                                             
echo "[+] Cloning OpenCTI Docker repository to $INSTALL_DIR..."                                                                                                                         
git clone "$DOCKER_REPO" "$INSTALL_DIR/docker"     

### MODIFY docker-compose.yml FOR RABBITMQ CONFIG PATH ######################
echo "[+] Updating docker-compose.yml to use absolute path for RabbitMQ config..."
sed -i "/rabbitmq:/,/restart:/ {/source:/s|source:.*|source: /opt/openCTI/docker/rabbitmq.conf|}" "$INSTALL_DIR/docker/docker-compose.yml"

### SET KERNEL PARAM FOR ELASTICSEARCH #############################################
echo "[+] Setting vm.max_map_count..."
echo "vm.max_map_count=1048575" | sudo tee -a /etc/sysctl.conf
sudo sysctl -w vm.max_map_count=1048575

### CREATE .env FILE ###########################################
echo "[+] Creating .env file..."
cat <<EOF > "$ENV_FILE"
OPENCTI_ADMIN_EMAIL=admin@hrouhani.org
OPENCTI_ADMIN_PASSWORD=hrouhani@OpenCTI-110
OPENCTI_ADMIN_TOKEN=c75a53e7-c3eb-4410-a27a-2cc33c58c9de
OPENCTI_BASE_URL=http://$OPENCTI_PUBLIC_IP:8080
OPENCTI_HEALTHCHECK_ACCESS_KEY=32ddca9b-0cc3-4db0-a917-808ee7825487
MINIO_ROOT_USER=5a6f3c20-ea2d-4d63-ac0d-abd9eb3b225d
MINIO_ROOT_PASSWORD=bcf6a855-78d2-4fba-b2f7-c08e035943ce
RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest
ELASTIC_MEMORY_SIZE=6G
CONNECTOR_HISTORY_ID=c35edae1-09d7-4e9c-9305-ffe3feddad77
CONNECTOR_EXPORT_FILE_STIX_ID=35c381b8-88e4-4398-a514-51a726cf1a6a
CONNECTOR_EXPORT_FILE_CSV_ID=25fa888b-0885-4a03-9693-940a852d01f8
CONNECTOR_IMPORT_FILE_STIX_ID=fa81161a-4300-49e2-9d5a-2265f2225c53
CONNECTOR_EXPORT_FILE_TXT_ID=82aa8cb4-60dc-419e-af1d-cf81fc265c04
CONNECTOR_IMPORT_DOCUMENT_ID=12d61164-1325-4f8d-9633-33017ea6c1bc
CONNECTOR_ANALYSIS_ID=55b7849d-adfe-450f-9ef0-51fea9d9049a
SMTP_HOSTNAME=localhost
EOF

# CREATE RabbitMQ CONFIG FILES #########################################
echo "[+] Creating RabbitMQ config file in project and system directories..."
sudo mkdir -p "$SYSTEM_RABBIT_CONF_DIR"
cat <<EOF | sudo tee "$RABBIT_CONF_FILE" "$SYSTEM_RABBIT_CONF_FILE"
max_message_size = 536870912
consumer_timeout = 86400000
EOF

# START OPENCTI ##########################################################
echo "[+] Starting OpenCTI with Docker Compose..."
cd "$INSTALL_DIR/docker"
docker-compose up -d

echo "[✓] OpenCTI is deployed and reachable at: http://$OPENCTI_PUBLIC_IP:8080"

