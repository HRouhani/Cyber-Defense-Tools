# OpenCTI Terraform Deployment

This Terraform project automates the deployment of an OpenCTI environment on AWS. It creates all necessary infrastructure and installs OpenCTI and its dependencies using Docker.

## What It Does
This Terraform configuration will:

- Create a new **VPC** with a public subnet  
- Set up an **Internet Gateway** and routing  
- Deploy an **EC2 instance** using Ubuntu 24.04 (`ami-084568db4383264d4`) with instance type `r6i.2xlarge`  
- Allocate a **100 GiB root volume** to handle OpenCTI's resource needs  
- Automatically generate a **SSH key pair** and attach the public key to the EC2 instance  
- Save the **private key to `opencti_key.pem`** locally  
- Create a **Security Group** (`OpenCTI-mhp`) allowing access on:  
  - Port 22 (SSH)  
  - Port 80 (HTTP)  
  - Port 443 (HTTPS)  
  - Port 8080 (OpenCTI UI)  
- Attach an IAM role to enable **Session Manager (SSM)** for browser-based access  
- Automatically run the `opencti.sh` script to install OpenCTI using Docker  
- Automatically add MITRE ATT&CK connector and run `docker-compose up -d`

## How to Use

### 1. Initialize Terraform
```bash
terraform init
terraform apply
```

You will be prompted for confirmation. Terraform will:

    - Provision all infrastructure
    - SSH key will be saved to opencti_key.pem
    - The EC2 instance public IP will be printed at the end


### 2. Access OpenCTI

After deployment completes:

    Open your browser and navigate to:  http://<Public-IP>:8080

Or connect via SSH:

```bash
ssh -o IdentitiesOnly=yes -i opencti_key.pem ubuntu@<Public-IP>
```

Or use Session Manager from AWS Console (IAM role is automatically attached)


### 3. Docker Containers

To check the containers: 

    docker ps


Notes: 

    - OpenCTI is resource intensive, especially when syncing feeds. The root disk size is set to 100 GiB.

    - The opencti.sh script runs during instance boot, installs Docker, pulls the OpenCTI Docker setup, and starts services.

    - The MITRE connector is added automatically, since it does not require an API key.

    - For other feeds, manually update /opt/openCTI/docker/docker-compose.yml and then run:
      
      ```bash
    cd /opt/openCTI/docker
    docker-compose up -d

    if something fails:

    docker-compose down -v && docker-compose up -d
    ```


### 4. username & password

 ```bash
Username=admin@hrouhani.org
Password=hrouhani@OpenCTI-110
``` 

You can change it in opencti.sh file!