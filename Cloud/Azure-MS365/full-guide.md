## Introduction

This guide details how to integrate Microsoft 365 and Azure security logs into IBM QRadar for centralized threat detection, compliance monitoring, and incident response. It is intended for security analysts, cloud administrators, and SIEM engineers with access to:
- An Azure subscription with Event Hub and Storage Account permissions
- Microsoft 365 E5 or equivalent licenses (including Defender and Entra ID components)



# Onboard Microsoft Logs into SIEM

Collecting logs from Microsoft 365/Azure and its security subcomponents is essential for:

- **Threat Detection**
- **Compliance Monitoring**
- **Incident Response**

Microsoft 365 provides security telemetry across:

- **Identity** (Microsoft Entra ID)
- **Endpoints** (Defender for Endpoint)
- **On-prem AD** (Defender for Identity)
- **Email & Collaboration** (Defender for Office 365)
- **Cloud Applications** (Defender for Cloud Apps)

By integrating these into **SIEM**, the SOC gains:

- Centralized alert correlation  
- Advanced detection via behavioral analysis  
- Visibility into user, device, and cloud behaviors  

---

## 1.  Objective

Integrate the following Microsoft 365/Azure services with SIEM solution:

###  Microsoft Entra ID (Azure AD)
- **Threat Detection**: Detects suspicious login behavior (e.g., impossible travel, failed MFA, leaked credentials).
- **Compliance**: Tracks all identity-related administrative actions (e.g., role changes, group assignments) for audit purposes.
- **Incident Response**: Reconstructs authentication events and directory changes to analyze attacker movements and unauthorized access.

###  Microsoft Defender for Endpoint (MDE)
- **Threat Detection**: Captures real-time endpoint threats like malware, exploits, and lateral movement using behavioral analytics and MITRE mappings.
- **Compliance**: Demonstrates endpoint protection controls and system posture (e.g., vulnerabilities, patch status).
- **Incident Response**: Provides rich telemetry (process, file, network) to investigate endpoint compromise and correlate with other signals.

###  Microsoft Defender for Identity (MDI)
- **Threat Detection**: Monitors on-prem AD for brute force attacks, credential theft, privilege escalation, and suspicious lateral movement.
- **Compliance**: Detects use of insecure protocols and anomalous access to directory services for policy enforcement.
- **Incident Response**: Shows full AD attack chain (e.g., DCSync, Golden Ticket use) for containment and recovery.

###  Microsoft 365 Unified Audit Log / Purview Compliance
- **Threat Detection**: Flags unusual user behavior across Exchange, SharePoint, OneDrive, and Teams (e.g., mass downloads, auto-forwarding rules).
- **Compliance**: Central audit trail of all user/admin activity—critical for GDPR, HIPAA, and SOX audits.
- **Incident Response**: Reconstructs the sequence of actions performed by compromised accounts across Microsoft 365 services.

###  Microsoft Defender for Cloud Apps (MDCA)
- **Threat Detection**: Detects anomalous cloud usage patterns like impossible travel, suspicious app consent, or mass downloads.
- **Compliance**: Enforces and logs data protection policies (e.g., external sharing of sensitive files).
- **Incident Response**: Correlates identity and app activities across cloud services to trace data misuse or exfiltration.



# Sending Logs to External SIEM Solutions

Organizations that rely on external SIEM platforms (e.g., IBM QRadar, Splunk, Elastic) must collect Microsoft 365 and Entra ID logs.

- Methods for Sending Logs from Microsoft 365 to SIEM:

    Method 1: Azure Event Hub (Streaming API) 
    
    Near real-time log streaming from Microsoft security products.
    Ideal for high-volume security telemetry such as:

        - Azure AD (Entra ID) sign-in and audit logs

        - Microsoft Defender for Endpoint (MDE)

        - Microsoft Defender for Identity (MDI)

        - Microsoft Defender for Office 365 (MDO)

        - Microsoft Defender for Cloud Apps (MCAS)

    Method 2: Polling-Based APIs for Audit and Compliance Logs (REST API)
    
    Polling-based methods required for audit, compliance, and productivity logs that do not support streaming (5-30 minute latency).

# Method 2A: Office 365 Management Activity API (REST API)

Traditional method for retrieving audit and compliance logs. Supported as of July 2025 but being phased out for some workloads.

Log Types:


- Exchange Online (mailbox access)
- SharePoint Online (file access)
- Microsoft Teams (team creation and activity logs)
- Microsoft Purview (DLP and compliance events)
- Unified Audit Logs (consolidated user/admin activities)
- Use Case: Compliance monitoring, user activity tracking, and audit reporting.

Configuration: Requires app registration in the Microsoft Entra Admin Center or Azure Portal, with permissions like ActivityFeed.Read and ActivityFeed.ReadDlp.



# Method 2B: Microsoft Graph Audit Logs API

Newer alternative for audit and compliance logs, recommended for future compatibility as Microsoft transitions from the Office 365 Management API.

Log Types:

- Exchange Online (mailbox access)
- SharePoint Online (file access)
- Microsoft Teams (team creation and activity logs)
- Microsoft Purview (DLP and compliance events)
- Unified Audit Logs (via /auditLogs/directoryAudits and /auditLogs/signIns)


Use Case: Same as Office 365 Management API, with improved performance and support for newer features.

Configuration: Requires app registration in the Microsoft Entra Admin Center or Azure Portal, with the AuditLog.Read.All permission. Ensure QRadar’s Microsoft Office 365 DSM is updated to support Graph API.


Important: As of July 2025, the Office 365 Management Activity API is supported, but Microsoft is transitioning some workloads to the Microsoft Graph Audit Logs API. Use Method 2B for new deployments or to prepare for future deprecation.

Description and Purpose

    Azure Event Hub Streaming
    Uses Diagnostic Settings or the Defender Streaming API to stream logs to an Azure Event Hub, from which an external SIEM can pull logs in near real-time. This method is preferred for detecting threats and responding quickly to incidents with rich JSON telemetry.

    Office 365 REST API
    Microsoft 365 provides a REST API that exposes the Unified Audit Log. This method is required for audit trails and compliance monitoring, especially for services that cannot send events to Event Hub.

---

## 2. 🔧 Integration Methods Overview

### A. Azure Event Hub Streaming (Recommended for Security Events)

Streams security telemetry and alerts in near real-time using Event Hub and QRadar’s Event Hub protocol.

**Use Cases:**
- Defender alerts (MDE, MDI, MDO)  
- Entra ID sign-ins and audit logs  
- Defender for Cloud Apps alerts  

---

### B. Office 365 REST API (Required for Compliance Logs)

Polls audit/compliance logs from Microsoft 365 using the official Microsoft APIs.

**Use Cases:**
- Unified Audit Log (Exchange, SharePoint, Teams)  
- Microsoft Purview DLP & compliance events  
- Admin/user activity for audits  

---

## 3. How to Verify Logging Is Active for Microsoft 365 Security Sources

## Microsoft Entra ID (Azure AD)
- Sign-in Logs and Audit Logs are enabled by default.
- Go to: [https://entra.microsoft.com](https://entra.microsoft.com)
  - Navigate to:
    - `Identity > Monitoring > Sign-in Logs`
    - `Identity > Monitoring > Audit Logs`
- If using P2:
  - Check under `Protection > Identity Protection`
    - `Risky sign-ins`
    - `Risky users`
    - `Risk detections`
- If logs are visible and updating → Logging is active.

---

## Microsoft Defender for Endpoint (MDE)
- Go to: [https://security.microsoft.com](https://security.microsoft.com)
  - Check under:
    - `Endpoints > Device inventory` → See if devices are listed.
    - `Endpoints > Alerts` → See if alerts exist.
    - `Advanced Hunting` → Run sample queries for events.
- Also verify onboarding under:
  - `Settings > Endpoints > Device management`
-  If devices are onboarded and logs show activity → Logging is active.

---

## Microsoft Defender for Identity (MDI)
- Sensors must be installed on Domain Controllers.
- Go to: [https://security.microsoft.com](https://security.microsoft.com)
  - Navigate to:
    - `Assets > Identities` → List of users/computers.
    - `Identities > Alerts` → Presence of security alerts.
    - `Settings > Identities` → Sensor status and honeytoken settings.
- If alerts and inventory are populated → Logging is active.

---

## Microsoft 365 Unified Audit Log
- Go to: [https://purview.microsoft.com](https://purview.microsoft.com)
  - Navigate to:
    - `Solutions > Audit`
- If not enabled:
  - Click **“Start recording”**.
- Run a search:
  - Set a recent date range.
  - Choose activity types (e.g., “Send message”, “Access file”).
- If search returns results → Audit logging is active.

---

##  Microsoft Defender for Cloud Apps (MDCA)
- Go to: [https://security.microsoft.com](https://security.microsoft.com)
  - Navigate to:
    - `Cloud Apps > Alerts`
    - `Cloud Apps > Activities`
- Or use the legacy portal: `https://<tenant>.portal.cloudappsecurity.com`
  - Check for dashboards, recent alerts, and activity logs.
-  If alerts or activity logs are visible → Logging is active.





## 4. Architecture & Communication

| Component                | Protocol | Port | Purpose                              |
|--------------------------|----------|------|--------------------------------------|
| Azure Event Hub          | AMQP     | 5671 | Streams security telemetry           |
| Azure Blob Storage       | HTTPS    | 443  | Checkpoint tracking (offsets)        |
| Office 365 REST API      | HTTPS    | 443  | Poll audit logs from M365            |

Two QRadar log sources are used:

 **Event Hub** log source for security telemetry  
 **Office 365 REST API** for compliance data  

---



## A. Event Hub Integration

### Prerequisites

- Azure Subscription
- Event Hub Namespace & Event Hub created
- SAS policies (Send, Listen)
- Dedicated Consumer Group (e.g. `qradar-cg`)
- Azure Storage Account for checkpointing
- Defender Streaming API enabled

---

 
 # Azure Setup: Event Hub Configuration


1. Create Event Hub Namespace & Event Hub

 Create Event Hub Namespace & Event Hub (Portal)

Open the Azure Portal

Go to Event Hubs > + Create

Create a new Namespace (e.g. psiem-namespace)

Inside the Namespace, create an Event Hub (e.g. security-logs-hub)

Azure CLI:


```bash
az eventhubs namespace create --name psiem-namespace --resource-group <ResourceGroupName> --location <Location>

az eventhubs eventhub create --resource-group <ResourceGroupName> --namespace-name psiem-namespace --name security-logs-hub
```



2. Create SAS Policies

    - Go to your Event Hub Namespace

    - Open Shared access policies

    - Add two policies:

    - SendPolicy with only Send permission

    - ListenPolicy with only Listen permission

    - Copy the connection string for ListenPolicy


```bash
# Send policy
az eventhubs namespace authorization-rule create \
  --resource-group <ResourceGroupName> \
  --namespace-name psiem-namespace \
  --name SendPolicy \
  --rights Send

# Listen policy
az eventhubs namespace authorization-rule create \
  --resource-group <ResourceGroupName> \
  --namespace-name psiem-namespace \
  --name ListenPolicy \
  --rights Listen

# Get Listen policy connection string
az eventhubs namespace authorization-rule keys list \
  --resource-group <ResourceGroupName> \
  --namespace-name psiem-namespace \
  --name ListenPolicy
```


3. Create a Dedicated Consumer Group

    - Open your Event Hub

    - Go to Consumer groups

    - Click + Add

    - Name it: qradar-cg


Azure CLI:

```bash
az eventhubs eventhub consumer-group create \
  --resource-group <ResourceGroupName> \
  --namespace-name psiem-namespace \
  --eventhub-name security-logs-hub \
  --name qradar-cg
```


4. Create Azure Storage Account for Checkpointing 

   - Go to Storage accounts > + Create

   - Name: qradarcheckpoints

   - Choose the same Resource Group and Region

   - After creation, go to Access keys

   - Copy one of the two Access Keys or generate a SAS


```bash
az storage account create \
  --name qradarcheckpoints \
  --resource-group <ResourceGroupName> \
  --location <Location> \
  --sku Standard_LRS

# Get access keys
az storage account keys list \
  --resource-group <ResourceGroupName> \
  --account-name qradarcheckpoints
```


Network Requirements

- Open TCP 5671 outbound to *.servicebus.windows.net for Event Hub

- Open TCP 443 outbound to *.blob.core.windows.net for Azure Storage




### Microsoft Services → Event Hub Setup

#### Microsoft Entra ID (Azure AD)
- Navigate to [https://entra.microsoft.com](https://entra.microsoft.com)
- Go to `Monitoring > Diagnostic Settings`
- Click **+ Add Diagnostic Setting**
  - Name: `aad-to-eventhub`
  - Enable: `AuditLogs`, `SignInLogs`
  - Choose: `Stream to Event Hub`
  - Select your Event Hub namespace and Event Hub

##### CLI:
```bash
az monitor diagnostic-settings create \
  --resource <AADResourceID> \
  --name aad-to-eventhub \
  --event-hub-name security-logs-hub \
  --event-hub-authorization-rule-id <SASRuleID> \
  --event-hub-namespace psiem-namespace \
  --logs '[{"category":"AuditLogs","enabled":true},{"category":"SignInLogs","enabled":true}]'
  ```


🔹 Microsoft Defender (MDE, MDI, MDO)

    Go to https://security.microsoft.com

    Navigate to Settings > Microsoft 365 Defender > Streaming API

    Click Add Data Export

        Name: defender-to-eventhub

        Choose: Forward events to Event Hub

        Enter: Event Hub Namespace Resource ID & Name

        Select tables: DeviceEvents, AlertInfo, EmailEvents, etc.

🔹 Defender for Cloud Apps (MCAS)

    Go to: https://portal.cloudappsecurity.com

    Navigate to Settings > Security Extensions > SIEM

    Choose: Send alerts to Event Hub

        Enter: Event Hub Namespace, Name, and SAS token






## B. Office 365 REST API

Office 365 REST API Integration

### What It Covers

- Unified Audit Logs (Exchange, SharePoint, Teams)  
- Purview DLP & sensitivity label logs  
- Admin activity and policy enforcement  

**Important**: As of July 2025, the Office 365 Management Activity API is supported, but Microsoft is transitioning some workloads (e.g., Unified Audit Logs, Exchange, SharePoint activities) to the Microsoft Graph Audit Logs API. Both APIs are currently viable for integration, but prepare for Graph API adoption.

### Setup Steps

    We propose the second option to use the Graph API

#### Setup Steps (Office 365 Management Activity API)
 **Register App in Microsoft Entra ID**
   - In [Microsoft Entra Admin Center](https://entra.microsoft.com), go to **Applications > App Registrations > New Registration**.
     - **Alternative**: Use the [Azure Portal](https://portal.azure.com) and navigate to **Azure Active Directory > App Registrations > New Registration**.
   - Name: e.g., `QRadar-M365-Integration`
   - Supported account types: **Accounts in this organizational directory only (Single tenant)**
   - Note: Client ID, Tenant ID
 **Generate Client Secret**
   - In the same portal (Entra Admin Center or Azure Portal), go to **Certificates & secrets > New client secret**.
   - Set expiry (e.g., 24 months) and copy the secret value immediately.
 **Grant API Permissions**
   - In **API permissions**, add **application** permissions:
     - `ActivityFeed.Read`
     - `ActivityFeed.ReadDlp`
     - `ServiceHealth.Read`
   - Click **Grant admin consent for <tenant>**.
 **Configure SIEM (like splunk QRadar)**
   - Add log source: **Microsoft Office 365**
   - Protocol: **Office 365 REST API**
   - Enter: Client ID, Client Secret, Tenant ID
   - Select event filters: Azure AD, Exchange, SharePoint, General, DLP
   - **Note**: API enforces rate limits; QRadar backs off on HTTP 429 errors.

#### Setup Steps (Microsoft Graph Audit Logs API)
**When to Use**: For organizations preparing for Microsoft’s transition or accessing newer audit log features.
 **Register App in Microsoft Entra ID**
   - In [Microsoft Entra Admin Center](https://entra.microsoft.com), go to **Applications > App Registrations > New Registration**.
     - **Alternative**: Use the [Azure Portal](https://portal.azure.com) and navigate to **Azure Active Directory > App Registrations > New Registration**.
   - Name: e.g., `QRadar-Graph-Audit`
   - Supported account types: **Accounts in this organizational directory only (Single tenant)**
   - Note: Client ID, Tenant ID
 **Generate Client Secret**
   - In **Certificates & secrets**, create a new secret (e.g., 24 months expiry).
   - Copy the secret value.
 **Grant API Permissions**
   - Add **application** permission: `AuditLog.Read.All`
   - Click **Grant admin consent for <tenant>**.
 **Configure QRadar**
   - Add log source: **Microsoft Office 365**
   - Protocol: **Microsoft Graph API** (ensure QRadar DSM is updated to support Graph API).
   - Enter: Client ID, Client Secret, Tenant ID
   - Endpoint: `https://graph.microsoft.com/v1.0/auditLogs/directoryAudits` (for Entra ID) or `https://graph.microsoft.com/v1.0/auditLogs/signIns` (for sign-ins)
   - **Note**: Check IBM QRadar DSM release notes for Graph API support and event parsing.
 **Verification**
   - Query the Graph API (e.g., `GET https://graph.microsoft.com/v1.0/auditLogs/directoryAudits`) using PowerShell or Postman.
   - Confirm events in QRadar’s Log Activity tab under Microsoft Office 365 DSM.


### Required Network Access

| **Service**          | **Protocol** | **Port** | **Host**                      | **Purpose**             |
|----------------------|--------------|----------|-------------------------------|-------------------------|
| Azure AD OAuth       | HTTPS        | 443      | login.microsoftonline.com     | Token exchange          |
| Office 365 API       | HTTPS        | 443      | manage.office.com             | Audit data retrieval    |
| Microsoft Graph API  | HTTPS        | 443      | graph.microsoft.com           | Audit data retrieval    |




## 8. Log Source Mapping

| Log Type                            | Method | Notes                                      |
|-------------------------------------|--------|--------------------------------------------|
| Azure AD Sign-in Logs               | A      | Only via Event Hub                         |
| Azure AD Audit Logs                 | A or B | Both supported                             |
| Defender Alerts (MDE/MDI/MDO)       | A      | Defender Streaming API                     |
| Defender for Cloud Apps Alerts      | A      | SIEM connector → Event Hub                 |
| Exchange Mailbox Audit              | B      | Via Office 365 REST API                    |
| SharePoint / OneDrive Activity      | B      | Via REST API                               |
| Teams Events                        | B      | API “General” category                     |
| Microsoft Purview DLP Events        | B      | API only (not streamable via Event Hub)    |
| Unified Audit Log (All Activities)  | B      | REST API only                              |
| Microsoft 365 Service Health        | B      | Optional; via REST API                     |

---

##  Final Recommendation

Use **both methods** for comprehensive security:

-  **Event Hub** → For alerts, raw telemetry, near real-time events  
-  **Office 365 REST API** → For audit, compliance, user & admin actions  

### Benefits:

-  Correlate endpoint, identity, and cloud events  
-  Detect threats not visible from a single source  
-  Meet compliance and auditing needs  

➡️ Keep DSMs up to date  
➡️ Create custom fields if needed  
➡️ Monitor parsing and ingestion health regularly  

---
