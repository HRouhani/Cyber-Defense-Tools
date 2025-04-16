# Cyber-Defense-Tools

All Feeds connector can be find here:  https://github.com/OpenCTI-Platform/connectors/tree/master/external-import

This section explains how to integrate additional threat intelligence feeds into your OpenCTI platform using Docker Compose. Each connector listed below represents a specific data source (e.g. VirusTotal, AlienVault, MITRE, etc.) and can be configured directly in your docker-compose.yml.

By enabling these connectors, OpenCTI will automatically ingest and enrich data with indicators of compromise (IOCs), threat actors, malware, TTPs, and more — enhancing your overall cyber defense capabilities.

Each feed is easy to enable:

    Simply copy the configuration block into your Docker Compose file

    Adjust a few environment variables (e.g., API keys)

    Run docker-compose up -d to activate the connector

You’ll find step-by-step examples for the most widely used and valuable threat feeds below.



1. VirusTotal LiveHunt Feed

Add this to your docker-compose.yml file (at the end):

```yaml
connector-virustotal-livehunt-notifications:
    image: opencti/connector-virustotal-livehunt-notifications:6.6.4
    environment:
      - OPENCTI_URL=http://opencti:8080
      - OPENCTI_TOKEN=${OPENCTI_ADMIN_TOKEN}
      - CONNECTOR_ID=Virustotal_Livehunt_Notifications
      - "CONNECTOR_NAME=VirusTotal Livehunt Notifications"
      - CONNECTOR_SCOPE=StixFile,Indicator,Incident
      - CONNECTOR_LOG_LEVEL=error
      - VIRUSTOTAL_LIVEHUNT_NOTIFICATIONS_API_KEY=ChangeME # Private API Key
      - VIRUSTOTAL_LIVEHUNT_NOTIFICATIONS_INTERVAL_SEC=300 # Time to wait in seconds between subsequent requests
      - VIRUSTOTAL_LIVEHUNT_NOTIFICATIONS_CREATE_ALERT=True # Set to true to create alerts
      - VIRUSTOTAL_LIVEHUNT_NOTIFICATIONS_EXTENSIONS='exe,dll' # (Optional) Comma separated filter to only download files matching these extensions
      - VIRUSTOTAL_LIVEHUNT_NOTIFICATIONS_MIN_FILE_SIZE=1000 # (Optional) Don't download files smaller than this many bytes
      - VIRUSTOTAL_LIVEHUNT_NOTIFICATIONS_MAX_FILE_SIZE=52428800 # (Optional) Don't download files larger than this many bytes
      - VIRUSTOTAL_LIVEHUNT_NOTIFICATIONS_MAX_AGE_DAYS=3 # Only create the alert if the first submission of the file is not older than `max_age_days`
      - VIRUSTOTAL_LIVEHUNT_NOTIFICATIONS_MIN_POSITIVES=5 # (Optional) Don't download files with less than this many vendors marking malicious
      - VIRUSTOTAL_LIVEHUNT_NOTIFICATIONS_CREATE_FILE=True # Set to true to create file object linked to the alerts
      - VIRUSTOTAL_LIVEHUNT_NOTIFICATIONS_UPLOAD_ARTIFACT=False # Set to true to upload the file to opencti
      - VIRUSTOTAL_LIVEHUNT_NOTIFICATIONS_CREATE_YARA_RULE=True # Set to true to create yara rule linked to the alert and the file
      - VIRUSTOTAL_LIVEHUNT_NOTIFICATIONS_DELETE_NOTIFICATION=False # Set to true to remove livehunt notifications
      - VIRUSTOTAL_LIVEHUNT_NOTIFICATIONS_FILTER_WITH_TAG="mytag" # Filter livehunt notifications with this tag
    restart: always
    depends_on:
      opencti:
        condition: service_healthy
```

Change only the VIRUSTOTAL_LIVEHUNT_NOTIFICATIONS_API_KEY value.
Then run:



docker-compose up -d


2. AlienVault OTX Feed

   https://otx.alienvault.com/logout

```yaml
    connector-alienvault:                                                                                                                                                                 
    image: opencti/connector-alienvault:6.6.4                                                                                                                                           
    environment:
      - OPENCTI_URL=http://opencti:8080
      - OPENCTI_TOKEN=${OPENCTI_ADMIN_TOKEN}
      - CONNECTOR_ID=alienvault-connector
      - CONNECTOR_NAME=AlienVault OTX
      - CONNECTOR_SCOPE=alienvault
      - CONNECTOR_LOG_LEVEL=error
      - CONNECTOR_DURATION_PERIOD=PT30M
      - ALIENVAULT_BASE_URL=https://otx.alienvault.com
      - ALIENVAULT_API_KEY=Change-Me
      - ALIENVAULT_TLP=White
      - ALIENVAULT_CREATE_OBSERVABLES=true
      - ALIENVAULT_CREATE_INDICATORS=true
      - ALIENVAULT_PULSE_START_TIMESTAMP=2023-01-01T00:00:00
      - ALIENVAULT_REPORT_TYPE=threat-report
      - ALIENVAULT_REPORT_STATUS=New
      - ALIENVAULT_GUESS_MALWARE=false
      - ALIENVAULT_GUESS_CVE=false
      - ALIENVAULT_EXCLUDED_PULSE_INDICATOR_TYPES=FileHash-MD5,FileHash-SHA1
      - ALIENVAULT_ENABLE_RELATIONSHIPS=true
      - ALIENVAULT_ENABLE_ATTACK_PATTERNS_INDICATES=false
      - ALIENVAULT_INTERVAL_SEC=1800
      - ALIENVAULT_DEFAULT_X_OPENCTI_SCORE=50
      - ALIENVAULT_X_OPENCTI_SCORE_IP=60
      - ALIENVAULT_X_OPENCTI_SCORE_DOMAIN=70
      - ALIENVAULT_X_OPENCTI_SCORE_HOSTNAME=75 
      - ALIENVAULT_X_OPENCTI_SCORE_EMAIL=70
      - ALIENVAULT_X_OPENCTI_SCORE_FILE=85
      - ALIENVAULT_X_OPENCTI_SCORE_URL=80
      - ALIENVAULT_X_OPENCTI_SCORE_MUTEX=60
      - ALIENVAULT_X_OPENCTI_SCORE_CRYPTOCURRENCY_WALLET=80
    restart: always
    depends_on:
      opencti:
        condition: service_healthy
```

    Change ALIENVAULT_API_KEY and then:

    docker-compose up -d


    3. MITRE ATT&CK (TTPs)

```yaml
      connector-mitre:
    image: opencti/connector-mitre:6.6.4
    environment:
      - OPENCTI_URL=http://opencti:8080
      - OPENCTI_TOKEN=${OPENCTI_ADMIN_TOKEN}
      - CONNECTOR_ID=mitre-connector
      - CONNECTOR_NAME=MITRE ATT&CK
      - CONNECTOR_SCOPE=tool,report,malware,identity,campaign,intrusion-set,attack-pattern,course-of-action,x-mitre-data-source,x-mitre-data-component,x-mitre-matrix,x-mitre-tactic,x-mitre-collection
      - CONNECTOR_RUN_AND_TERMINATE=false
      - CONNECTOR_LOG_LEVEL=error
      - MITRE_REMOVE_STATEMENT_MARKING=true
      - MITRE_INTERVAL=7
    restart: always
    depends_on:
      opencti:
        condition: service_healthy
```

   Nothing to change here unless you want to tweak the sync interval or give it a different connector ID.

 

