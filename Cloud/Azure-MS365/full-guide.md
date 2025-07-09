# 🛡️ Guide: Integrating Microsoft Defender XDR & Entra ID Security Logs into SIEM

**Focus:**  
This guide covers **Microsoft Defender XDR components** (accessible via `https://security.microsoft.com`) **and Microsoft Entra ID** (accessible via `https://entra.microsoft.com`), including:

- Defender for Endpoint, Office 365, Identity, and Cloud Apps  
- Microsoft Entra ID logs (Sign-ins, Audit Logs, Identity Protection)

📌 Logs from **Microsoft Defender for Cloud** (infrastructure & workload protection, `https://portal.azure.com`) will be addressed in a **separate guide**.



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

Integrating Microsoft Defender (XDR) & Entra ID logs with your SIEM enables full-spectrum threat monitoring and compliance tracking across:

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

Microsoft Defender XDR logs can be integrated into external SIEM platforms using two primary methods:

- **Azure Event Hub streaming** for near real-time telemetry and security alerts
- **Microsoft Graph Audit Logs API** for compliance, audit, and user activity logs

---

### A. Azure Event Hub Streaming *(Recommended for Security Events)*

Streams near real-time security telemetry and alerts using **Azure Event Hub**, which is supported by most SIEM platforms (e.g., IBM QRadar, Splunk, Elastic).

**Use Cases:**
- Security alerts and raw telemetry from:
  - Microsoft Defender for Endpoint (MDE)
  - Microsoft Defender for Identity (MDI)
  - Microsoft Defender for Office 365 (MDO)
- Sign-in and audit logs from **Microsoft Entra ID**
- Alerts from **Microsoft Defender for Cloud Apps (MDCA)**

✅ **Best for**: High-volume, time-sensitive logs that support threat detection and correlation. we can see the Data Flow Diagram here:

```
Microsoft 365 Defender (MDE, MDI, MDO) + Entra ID + Purview
                    |
                    | [Streaming API (pushes logs)] 
                    |
               Azure Event Hub
                    | [SIEM pulls logs]
                    |
              SIEM Ingestion Layer
                    | [Processing and Parsing]
                    |
                SIEM Console
                    | [Analysis and Correlation]
```

---

### B. Microsoft Graph Audit Logs API *(Recommended for Compliance and Audit Logs)*

Polls **audit and compliance logs** from Microsoft 365 using the modern **Microsoft Graph Audit Logs API**. This API offers broader coverage, better performance, and is actively maintained by Microsoft.

**Use Cases:**
- Unified Audit Logs (Exchange, SharePoint, Teams, OneDrive)  
- Microsoft Purview DLP events and Insider Risk indicators  
- Admin/user activity logs for compliance and forensic audits  

✅ **Best for**: Regulatory reporting, audit readiness, and deep forensic investigations.

📝 **Notes**:
- Typical polling interval: 5–30 minutes  
- Requires app registration and permissions like `AuditLog.Read.All`  
- Supported endpoints include:
  - `/auditLogs/signIns`
  - `/auditLogs/directoryAudits`
  - `/security/alerts`
  - `/identityProtection/riskyUsers`

---

### 🔁 (Optional) Legacy Option – Office 365 Management Activity API *(Deprecated)*

Still supported for backward compatibility but **being phased out** in favor of Microsoft Graph.

**Use Cases:**
- Mailbox access (Exchange Online)  
- File activity (SharePoint Online)  
- Admin actions (e.g., role changes, mailbox rules)  
- DLP and audit logs via `/contentType/` feeds

🟡 **Use only if** your SIEM (e.g., older QRadar DSMs) does not yet support Graph API.

📤 Legacy permissions:  
- `ActivityFeed.Read`  
- `ActivityFeed.ReadDlp`  
- `ServiceHealth.Read`


---

## 3. How to Verify Logging Is Active for Microsoft Defender XDR Components

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





## 4. 🧱 Architecture & Communication Overview

This section describes how logs from Microsoft Defender XDR components are delivered to SIEM using:

- **Azure Event Hub** for real-time streaming of security telemetry
- **Microsoft Graph API** (modern) or **Office 365 Management Activity API** (legacy) for compliance and audit logs

---

### 🔌 Communication & Protocol Matrix

| Component                     | Protocol | Port | Purpose                                     |
|------------------------------|----------|------|---------------------------------------------|
| Azure Event Hub              | AMQP     | 5671 | Real-time streaming of security events      |
| Azure Blob Storage           | HTTPS    | 443  | Offset tracking for Event Hub consumer group |
| Microsoft Graph API          | HTTPS    | 443  | Pull audit/compliance data from M365        |
| Office 365 Management API    | HTTPS    | 443  | Legacy method for audit log retrieval       |

---

### 🎯 QRadar Log Sources

- **Event Hub log source** → for high-volume Defender telemetry (MDE, MDI, MDO, MDCA)  
- **Graph API or Office 365 REST API log source** → for Unified Audit Log (UAL), DLP, admin activity

---


## A. ⚙️ Azure Event Hub Integration (Real-Time)

### Prerequisites

- Azure Subscription
- Event Hub Namespace & Event Hub created
- SAS policies (Send, Listen)
- Dedicated Consumer Group (e.g. `qradar-cg`)
- Azure Storage Account for checkpointing
- Defender Streaming API enabled

---

 
 # Azure Setup: Event Hub Configuration

This section describes how to configure Azure Event Hub for streaming Microsoft Defender XDR logs to a SIEM (e.g., QRadar or Splunk).  
We provide **both methods**:

- ✅ **Azure Portal** (GUI-based)
- ✅ **Azure CLI** (scriptable automation)

---

## 1️⃣ Create Event Hub Namespace and Event Hub

### 🔹 Via Azure Portal
1. Sign in to [https://portal.azure.com](https://portal.azure.com)
2. Go to **Event Hubs > + Create**
3. Create a new **Namespace**, e.g., `psiem-namespace`
4. Inside the namespace, create a new **Event Hub**, e.g., `security-logs-hub`


### 🔹 Via Azure CLI


```bash
az eventhubs namespace create --name psiem-namespace --resource-group <ResourceGroupName> --location <Location>

az eventhubs eventhub create --resource-group <ResourceGroupName> --namespace-name psiem-namespace --name security-logs-hub
```


## 2️⃣ Create Shared Access Policies (SAS Tokens)

### 🔹 Via Azure Portal

    - Go to your Event Hub Namespace

    - Open Shared access policies

    - Add two policies:

    - SendPolicy with only Send permission

    - ListenPolicy with only Listen permission

    - Copy the connection string for ListenPolicy - used by the SIEM for ingestion


### 🔹 Via Azure CLI

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


## 3️⃣ Create a Dedicated Consumer Group

A dedicated consumer group ensures isolated consumption by the SIEM, avoiding read conflicts.

### 🔹 Via Azure Portal

    - Open your Event Hub

    - Go to Consumer groups

    - Click + Add

    - Name it: qradar-cg


### 🔹 Via Azure CLI

```bash
az eventhubs eventhub consumer-group create \
  --resource-group <ResourceGroupName> \
  --namespace-name psiem-namespace \
  --eventhub-name security-logs-hub \
  --name qradar-cg
```


## 4️⃣ Create Azure Storage Account (for Checkpointing)

This storage account allows checkpoint tracking — essential for tracking read offsets between the SIEM and Event Hub.

### 🔹 Via Azure Portal

   - Go to Storage accounts > + Create

   - Name: qradarcheckpoints

   - Choose the same Resource Group and Region

   - After creation, go to Access keys

   - Copy one of the two Access Keys or generate a SAS



### 🔹 Via Azure CLI

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




## 5️⃣ Microsoft Defender Services → Event Hub Setup

Once your **Azure Event Hub** is configured, you can stream Microsoft Defender XDR logs in real time to your SIEM (e.g., QRadar or Splunk).

This section explains how to connect the following Defender services:

- Microsoft Entra ID (Azure AD)
- Microsoft Defender for Endpoint (MDE)
- Microsoft Defender for Identity (MDI)
- Microsoft Defender for Office 365 (MDO)
- Microsoft Defender for Cloud Apps (MDCA)

---

### 🔐 Microsoft Entra ID (Azure AD)

Enables forwarding of sign-in and audit logs.

#### Via Azure Portal

1. Go to [https://entra.microsoft.com](https://entra.microsoft.com)
2. Navigate to:  
   `Monitoring > Diagnostic Settings`
3. Click **+ Add Diagnostic Setting**
4. Enter a name (e.g., `aad-to-eventhub`)
5. Enable log categories:
   - `SignInLogs`
   - `AuditLogs`
6. Select **Stream to an Event Hub**
7. Choose your **Namespace** and **Event Hub**

#### Via Azure CLI

```bash
az monitor diagnostic-settings create \
  --resource <AADResourceID> \
  --name aad-to-eventhub \
  --event-hub-name security-logs-hub \
  --event-hub-authorization-rule-id <SASRuleID> \
  --event-hub-namespace psiem-namespace \
  --logs '[{"category":"AuditLogs","enabled":true},{"category":"SignInLogs","enabled":true}]'
```


### 🛡️ Microsoft Defender for Endpoint (MDE), Identity (MDI), and Office 365 (MDO)

These Microsoft Defender XDR components support **real-time log export** to Azure Event Hub via the **Microsoft 365 Defender Streaming API**.

---

#### Via Microsoft 365 Defender Portal

1. Go to [https://security.microsoft.com](https://security.microsoft.com)

2. Navigate to:  
   `Settings > Microsoft 365 Defender > Streaming API`

3. Click **Add Data Export**

4. Fill in the following fields:
   - **Name**: e.g., `defender-to-eventhub`
   - **Destination**: Stream to Event Hub
   - **Event Hub Namespace Resource ID**
   - **Event Hub Name**: e.g., `security-logs-hub`

5. Select telemetry tables to stream:
   - `DeviceEvents`
   - `DeviceNetworkEvents`
   - `DeviceFileEvents`
   - `DeviceProcessEvents`
   - `AlertInfo`
   - `AlertEvidence`
   - `EmailEvents`
   - `EmailUrlInfo`
   - `EmailAttachmentInfo`

✅ **Tip**: Only select the tables you actually need to reduce data volume and optimize SIEM ingestion cost.





## B. Office 365 REST API / Microsoft Graph Audit Logs API

This section explains how to ingest audit and compliance logs from Microsoft Defender into your SIEM using either the legacy **Office 365 Management Activity API** or the modern **Microsoft Graph Audit Logs API**.

### What It Covers

- Unified Audit Logs (Exchange, SharePoint, Teams)  
- Purview DLP & sensitivity label logs  
- Admin activity and policy enforcement  

**Important**: As of July 2025, the Office 365 Management Activity API is supported, but Microsoft is transitioning some workloads (e.g., Unified Audit Logs, Exchange, SharePoint activities) to the Microsoft Graph Audit Logs API. Both APIs are currently viable for integration, but prepare for Graph API adoption.

---

## 1️⃣ Setup with Office 365 Management Activity API (Legacy)

> Suitable for backward compatibility or SIEMs that do not yet support Microsoft Graph.

### Step-by-Step

#### ✅ Register an App in Microsoft Entra ID

- Go to [Microsoft Entra Admin Center](https://entra.microsoft.com)
- Navigate to: `Applications > App registrations > New registration`
- Alternative: Use [Azure Portal](https://portal.azure.com) under `Azure Active Directory`
- Fill in:
  - **Name**: `QRadar-M365-Integration`
  - **Supported account types**: *Single tenant*
  - Save the **Client ID** and **Tenant ID**

#### 🔐 Generate Client Secret

- Navigate to: `Certificates & secrets > New client secret`
- Choose an expiry (e.g., 24 months)
- Copy and store the secret value immediately

#### 🔑 Grant API Permissions

- Go to `API permissions > Add a permission`
- Choose **Office 365 Management APIs**
- Add the following **application permissions**:
  - `ActivityFeed.Read`
  - `ActivityFeed.ReadDlp`
  - `ServiceHealth.Read`
- Click **Grant admin consent**

#### 🧩 Configure in SIEM (e.g., QRadar or Splunk)

- Add log source: `Microsoft Office 365`
- Protocol: `Office 365 REST API`
- Input:
  - **Client ID**
  - **Client Secret**
  - **Tenant ID**
- Select log categories: Exchange, SharePoint, Azure AD, DLP
- ⚠️ **Note**: API is rate-limited (HTTP 429); QRadar handles this by backing off automatically

---

## 2️⃣ Setup with Microsoft Graph Audit Logs API (Recommended)

> Use this method for new deployments and future compatibility with Microsoft’s roadmap.

### Step-by-Step

#### ✅ Register an App in Microsoft Entra ID

- Go to [Microsoft Entra Admin Center](https://entra.microsoft.com)
- Navigate to: `Applications > App registrations > New registration`
- Fill in:
  - **Name**: `QRadar-Graph-Audit`
  - **Supported account types**: *Single tenant*
  - Save the **Client ID** and **Tenant ID**

#### 🔐 Generate Client Secret

- Go to `Certificates & secrets > New client secret`
- Choose an expiry (e.g., 24 months)
- Copy and store the secret value

#### 🔑 Grant API Permissions

- Go to `API permissions > Add a permission`
- Choose: `Microsoft Graph > Application permissions`
- Add:
  - `AuditLog.Read.All`
- Click **Grant admin consent**

#### 🧩 Configure in SIEM (e.g., QRadar)

- Add log source: `Microsoft Office 365`
- Protocol: `Microsoft Graph API`
- Input:
  - **Client ID**
  - **Client Secret**
  - **Tenant ID**
- Endpoint examples:
  - `https://graph.microsoft.com/v1.0/auditLogs/directoryAudits`
  - `https://graph.microsoft.com/v1.0/auditLogs/signIns`

> 📝 **Note**: Ensure QRadar DSM (Device Support Module) is updated to support Graph API parsing.

---

### ✅ Verification

You can validate your configuration by testing API queries:

```http
GET https://graph.microsoft.com/v1.0/auditLogs/directoryAudits
```


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
