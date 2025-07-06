# 🛡️ Guide: Integrating Microsoft Defender (XDR) Security Logs into SIEM

- Focus: Microsoft 365 Defender components accessible via https://security.microsoft.com
- 📌 A separate guide will cover Microsoft Defender for Cloud, accessible via https://portal.azure.com


# Introduction

This guide explains how to integrate Microsoft Defender (XDR) logs with external SIEMs such as IBM QRadar, Splunk, Elastic or even Sentinel to enable centralized threat detection, compliance monitoring, and incident response. It is intended for security analysts, cloud administrators, and SIEM engineers with access to:

    - An Azure subscription with Event Hub and Storage Account permissions
    - Microsoft 365 E5 or equivalent licenses (including Defender and Entra ID components)


## Why Integrate Defender XDR with Your SIEM?

Microsoft Defender XDR is a unified platform that correlates security signals from across the Microsoft 365 ecosystem:

🧠 Core Benefits:

    - Cross-domain threat correlation (identity, endpoint, email, cloud apps)

    - Incident grouping with full attack timeline and context

    - AI-driven automatic remediation (self-healing)

    - Centralized hunting & investigation via Kusto-like queries



## ✅ Onboarding Microsoft Defender (XDR) Logs into Your SIEM

Modern Security Operations Centers (SOCs) require comprehensive visibility across identities, endpoints, email, and SaaS activity to effectively detect and respond to threats.
Microsoft Defender (XDR), offers rich security telemetry — but to operationalize it, these logs must be ingested into a centralized SIEM such as IBM QRadar, Splunk, or Elastic.

This guide focuses exclusively on onboarding logs from Microsoft Defender XDR components available via https://security.microsoft.com.
    📌 Logs from infrastructure/cloud workloads (Microsoft Defender for Cloud) will be covered in a separate guide.

---

## 🎯 Why Collect Microsoft Logs?

Collecting logs from Microsoft Defender is essential for:

- **🛡️ Threat Detection**  
  Detect phishing, endpoint compromise, credential theft, lateral movement, malware, and SaaS abuse — all across a unified attack surface.

- **📋 Regulatory Compliance & Audit Readiness**  
  Ensure tamper-proof audit trails and fulfill requirements for standards such as GDPR, HIPAA, ISO 27001, and NIS2. Logs from Entra ID, Purview, and Unified Audit Logs provide essential evidence.

- **🚨 Incident Response**  
  Correlate activity across identities, devices, mailboxes, and cloud apps to reconstruct the full attack path and enable targeted, automated remediation.

---

## 🔍 Microsoft Defender XDR Components That Generate Logs

Microsoft Defender XDR is built on multiple specialized components, each focused on a specific security domain. Together, they provide rich, cross-domain telemetry for detection, investigation, and response — and all generate logs that can be ingested into a SIEM.

---

## 🔐 Identity – Microsoft Entra ID (formerly Azure AD)

Captures identity and access-related activity:

- Sign-in attempts and MFA status  
- Risky users and risky sign-ins (via Entra ID Protection)  
- Role changes, group modifications, admin actions  
- Conditional Access policy outcomes  

📤 **Log sources**: `SignInLogs`, `AuditLogs`, `RiskyUsers`, `RiskDetections`  
✅ **Streamable via**: Azure Diagnostic Settings → Event Hub  
🟡 **Note**: Requires **Microsoft Entra ID P2** license for risky user signals.

---

## 🖥️ Endpoints – Microsoft Defender for Endpoint (MDE)

Provides advanced endpoint telemetry:

- Malware detections, exploit attempts, and behavioral anomalies  
- Process, file, network, and registry activity  
- Device inventory and risk scoring  
- Vulnerability insights and exposure data  

📤 **Log sources**: `DeviceEvents`, `DeviceNetworkEvents`, `AlertInfo`, `VulnerabilityAssessmentResults`, `ProcessEvents`  
✅ **Streamable via**: Microsoft 365 Defender Streaming API → Event Hub  
🟡 **Note**: Full telemetry requires **Defender for Endpoint P2**.

---

## 🏢 On-prem Active Directory – Microsoft Defender for Identity (MDI)

Monitors domain controller traffic to detect:

- Credential theft (e.g., Pass-the-Hash, DCSync, Golden Ticket, Kerberoasting)  
- Reconnaissance and lateral movement  
- Suspicious admin behavior and service account misuse  

📤 **Log sources**: `IdentityInfo`, `Alerts`, `SuspectedActivity`, `HoneytokenActivity`  
✅ **Streamable via**: Event Hub or portal API  
🟡 **Note**: Requires **sensors installed on all on-prem Domain Controllers**.

---

## 📧 Email & Collaboration – Microsoft Defender for Office 365 (MDO)

Secures email and Microsoft 365 collaboration platforms:

- Phishing attempts and malicious attachments  
- Malicious URLs (via Safe Links)  
- Abnormal forwarding rules and inbox manipulation  
- User clicks on malicious links  

📤 **Log sources**: `EmailEvents`, `EmailUrlInfo`, `ThreatIntelligence`, `EmailAttachmentInfo`  
✅ **Streamable via**: Microsoft 365 Defender Streaming API  
🟡 **Note**: Some logs (e.g., message trace) are only available via **Unified Audit Log** or **Microsoft Graph API**.

---

## ☁️ Cloud Applications – Microsoft Defender for Cloud Apps (MDCA)

Enhances visibility and control over SaaS usage:

- Impossible travel and anomalous login patterns  
- OAuth abuse and risky third-party apps  
- Data exfiltration and policy violations  
- Shadow IT and unsanctioned app usage  

📤 **Log sources**: `MCASAlerts`, `CloudDiscoveryEvents`, `AppGovernanceAlerts`, `UserActivityLogs`  
✅ **Streamable via**: Event Hub  
🟡 **Note**: Deep activity data often requires access via **MCAS API** or **portal download**.

---

## 🛡️ Microsoft Defender Vulnerability Management (MDVM)

Tracks asset exposure and vulnerability risk:

- CVE insights and severity scoring  
- Security posture assessments per device  
- Patch recommendations and remediation tasks  

📤 **Log sources**: `DeviceTvmSoftwareVulnerabilities`, `DeviceTvmSecureConfigurationStates`  
🟡 **Streamability**: Partial; mostly available via **Advanced Hunting** or **Graph Security API**  
🟡 **Note**: Requires **MDE P2** with **MDVM add-on** or **Microsoft 365 E5**.

---

## 🌐 Microsoft Defender for Cloud

Focuses on infrastructure, cloud workloads, and posture management (CNAPP):

- CSPM misconfigurations, vulnerability alerts, container risks  
- VM, storage, and database-level protections  

📤 **Log sources**: Azure Activity Logs, `SecurityAlert`, `SecurityRecommendation`  
❌ **Not natively part of XDR streaming**  
📝 **Note**: Handled via **Azure Monitor / Sentinel / Event Hub**, not integrated directly into XDR.

---

## 🔒 Microsoft Data Loss Prevention (DLP)

Protects sensitive data in emails, files, and chats:

- Policy match events (e.g., credit card detection in email/file)  
- Data transfer violations and sensitive info exposure  

📤 **Log sources**: Purview Audit Logs, Unified Audit Logs  
🟡 **Streamability**: Not directly streamable — access via **Graph API** or **O365 Management API**  
🟡 **Note**: Part of **Microsoft Purview** and requires configuration of DLP policies.

---

## 🔍 App Governance

Secures OAuth-based apps connected to Microsoft 365:

- Excessive permissions granted to third-party apps  
- Abnormal data access or sharing patterns  
- Token misuse and risky app behavior  

📤 **Log sources**: `AppGovernanceAlerts`, `OAuthActivityLogs`  
🟡 **Streamability**: Available via **API** and **MDCA integration**  
🟡 **Note**: Requires **App Governance** license (not included by default).

---

## 👤 Microsoft Purview Insider Risk Management

Monitors internal user behavior for risk indicators:

- Data exfiltration patterns  
- Confidential data transfers  
- Policy violations and behavioral anomalies  

📤 **Log sources**: Purview alerts, Unified Audit Logs  
🟡 **Streamability**: Not directly streamable — typically accessed via **compliance center** or **Graph API**  
🟡 **Note**: Requires **Purview IRM licensing** and sensitive data policies to be configured.


---

## 🧩 Why Send Logs to a SIEM?

By centralizing Microsoft logs in your SIEM:

- 🔄 **Cross-layer correlation**  
  Link identity, endpoint, email, and cloud events for multi-vector attack detection.

- 📊 **Behavioral detection**  
  Baseline normal activity and detect anomalies across systems and users.

- 🔍 **Single point of investigation**  
  Unified visibility and response across Microsoft 365 and other systems.

---
 

## 🎯 Objective Summary: Why Integrate These Defender Components with SIEM?

Integrating Microsoft Defender XDR with your SIEM enables full-spectrum threat monitoring and compliance tracking across:

| Component                        | Use in SIEM                            |
|----------------------------------|----------------------------------------|
| **Entra ID / Azure AD**          | Sign-in risk detection, identity audit, lateral movement via compromised credentials |
| **Defender for Endpoint (MDE)**  | Malware detection, process telemetry, device risk scoring, MITRE mapping |
| **Defender for Identity (MDI)**  | On-prem AD attack detection: DCSync, Pass-the-Hash, Kerberoasting |
| **Defender for Office 365 (MDO)**| Phishing, inbox rule abuse, email click behavior |
| **Unified Audit Logs / Purview** | Full user & admin activity trail for forensics, GDPR, HIPAA audits |
| **Defender for Cloud Apps (MDCA)**| SaaS anomaly detection, OAuth risk, cloud app policy violations |

➡️ This integration supports unified alerting, faster investigation, and compliance reporting in SIEM tools like QRadar, Splunk, and Sentinel.


# Sending Logs to External SIEM Solutions

Organizations that rely on external SIEM platforms (e.g., IBM QRadar, Splunk, Elastic) must collect Microsoft 365 and Entra ID logs.

- Methods for Sending Logs from Microsoft 365 to SIEM:

    🔄 Method 1: Azure Event Hub (Streaming API) 
    
    Near real-time log streaming from Microsoft security products.
    Ideal for high-volume security telemetry such as:

        - Azure AD (Entra ID) sign-in and audit logs

        - Microsoft Defender for Endpoint (MDE)

        - Microsoft Defender for Identity (MDI)

        - Microsoft Defender for Office 365 (MDO)

        - Microsoft Defender for Cloud Apps (MCAS)

    🔄 Method 2: Polling-Based APIs for Audit and Compliance Logs (REST API)
    
    Some Microsoft 365 logs cannot be streamed via Event Hub and require polling-based APIs. These methods are used primarily for:

        - 📋 Audit logs

        - ⚖️ Compliance data

        - 👤 User activity monitoring

    ⏱️ Polling latency: typically 5–30 minutes

    ✅ This method includes two REST API options:


        # Method 2A: Office 365 Management Activity API (Legacy)

        This is the traditional method for retrieving audit logs. Still supported in 2025, but Microsoft is gradually deprecating it in favor of the Graph API for some workloads.

        Log Types (sources):


        - Exchange Online (mailbox access)
        - SharePoint Online (file access)
        - Microsoft Teams (team creation and activity logs)
        - Microsoft Purview (DLP and compliance events)
        - Unified Audit Logs (consolidated user/admin activities)
        - Use Case: Compliance monitoring, user activity tracking, and audit reporting.

        Use Case:

        Compliance monitoring, internal audits, forensic investigations.

        Configuration:

            - Register an Azure App (via Entra/Azure Portal)
            - Assign permissions:

                ActivityFeed.Read
                ActivityFeed.ReadDlp

            Grant admin consent
            Configure in SIEM using the Office 365 REST API protocol



        # Method 2B: Microsoft Graph Audit Logs API

        The modern REST API approach using Microsoft Graph. Offers better performance, scalability, and future support.

        Log Types:

        - Exchange Online (mailbox access)
        - SharePoint Online (file access)
        - Microsoft Teams (team creation and activity logs)
        - Microsoft Purview (DLP and compliance events)
        - Unified Audit Logs (via /auditLogs/directoryAudits and /auditLogs/signIns)


        Use Case: Same as Office 365 Management API, with improved performance and support for newer features.

        Configuration: Requires app registration in the Microsoft Entra Admin Center or Azure Portal, with the AuditLog.Read.All permission. Ensure SIEM part like Microsoft Office 365 DSM in Qradar is updated to support Graph API.


Important: As of July 2025, the Office 365 Management Activity API is supported, but Microsoft is transitioning some workloads to the Microsoft Graph Audit Logs API. Use Method 2B for new deployments or to prepare for future deprecation.


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
