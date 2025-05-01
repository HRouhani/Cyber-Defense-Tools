OpenBAS + Caldera Deployment (Docker)

This guide explains how to deploy OpenBAS with Caldera for breach and attack simulation using Docker. The setup script automates the entire process including prerequisites, environment config, and service startup.

#  Stack Overview

This setup includes:

    ✅ OpenBAS (BAS platform)

    ✅ PostgreSQL

    ✅ RabbitMQ

    ✅ MinIO

    ✅ MITRE ATT&CK Collector

    ✅ Atomic Red Team Collector

    ✅ Caldera (used for agent simulation)

    ✅ Healthcheck logic and auto-start


⚙️ Installation (One-liner)

Clone this repository and simply run:

```yaml
chmod +x openbash.sh
./openbas.sh
```

    📂 Logs will be stored in /var/log/openbas_user_data.log


# Access Points

Component       URL                      Credentials

OpenBAS         http://localhost:8080   admin@example.com / openbasAdmin123

Caldera         http://localhost:8888   red:red or blue:blue (from caldera.yml)



# Key Commands

Action         Command

Start all      docker-compose up -d

Stop all        docker-compose down

Restart specific   docker-compose restart <service>

View logs         docker-compose logs -f



#  Directory Layout

/opt/openbas/
├── docker/                 
│   ├── docker-compose.yml
│   ├── docker-compose.caldera.yml
│   ├── docker-compose.caldera-executor.yml
│   ├── caldera.yml
│   ├── .env
│   └── rabbitmq.conf
└── caldera/                 # Caldera repo (optional)



# Uninstallation / Cleanup

docker-compose down --remove-orphans
sudo rm -rf /opt/openbas


#  Post-Install Tips

Login to OpenBAS and configure simulations

Use Caldera for running red team tests

Monitor containers using docker ps

Check if collectors are healthy via docker inspect