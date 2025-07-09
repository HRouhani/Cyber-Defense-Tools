# Microsoft 365 and Defender XDR Log Integration with IBM QRadar

This document outlines the integration of Microsoft 365 (productivity suite), Microsoft Defender XDR (security alerts), and Microsoft Entra ID (identity logs) into SIEM solutions like IBM QRadar which can be used with the similar methods for most of the other SIEM solutions like splunk. It uses a hybrid approach: Azure Event Hubs for real-time streaming of Entra ID and Defender XDR events, and the Office 365 Management Activity API for polling unified audit logs. The configuration uses a client secret for authentication (preferred certificates).

arouhan is an example name here for the tenant!


## Azure AD App Registration (for API Access)

Register an application in Microsoft Entra ID (Azure AD) for QRadar to authenticate and call APIs:

	1	Create a new App Registration in the arouhan Azure AD tenant (Azure Portal > Azure Active Directory > App registrations > New registration):
	◦	Name: e.g. QRadar-arouhan-GraphAPI-Collector
	◦	Supported account types: Accounts in this organizational directory.
	◦	Redirect URI: Leave blank or set to http://localhost
	◦	Once created, note the Application (Client) ID and Directory (Tenant) ID (you will need these in QRadar).

	2	Create a Client Secret for the app (Azure AD > App registrations > Your app > Certificates & Secrets > New client secret). Copy and save the secret value immediately – it will be hidden on refresh. This will serve as the authentication key for QRadar (client secret is preferred for simplicity, instead of a certificate).

	3	Assign API Permissions (API Permissions > Add a permission):

	◦	Microsoft Graph > Application permissions:
	⁃	SecurityEvents.Read.All (for Microsoft Defender XDR alerts via Graph Security API)
	⁃	Optional (if using Entra ID P2): Directory.Read.All, IdentityRiskyUser.Read.All, IdentityRiskEvent.Read.All, Reports.Read.All
	⁃	Optional (for future-proofing audit log access via Graph): AuditLog.Read.All

	◦	APIs my organization uses > Search for Office 365 Management APIs > Application permissions:
	⁃	ActivityFeed.Read (to read unified audit logs)
	⁃	ActivityFeed.ReadDlp (to read DLP events)
			  # note:  These permissions are not part of the Microsoft Graph API; they are listed under the Office 365 Management APIs in the Azure AD App Registration portal, and is for Microsoft 365 Unified Audit Log via Office 365 REST API which still uses Office 365 REST API

 		# After selecting the permissions, Grant admin consent for the tenant so that the app can access these scopes without user interaction. This registration will be used by QRadar to pull M365 audit logs and Defender alerts via Graph API.

## Enable Microsoft 365 Logging Services

```bash
Before configuring QRadar, ensure the relevant logging is active in the arouhan Microsoft 365 tenant:
	•	Unified Audit Log (Purview Audit) – This is usually enabled by default for E5 or E3 with compliance add-on. Verify in the Microsoft Purview compliance portal under Audit that audit recording is turned On. If not, enable it to start collecting audit events across Exchange, SharePoint, Teams, Azure AD, etc.
	•	Microsoft Defender (XDR) Alerts – Ensure that Microsoft Defender is generating alerts. In the Microsoft Defender portal (security.microsoft.com), under Settings > Microsoft Defender XDR , verify that alerting is active (it should be by default for Defender for Endpoint/Identity/Office, etc.). No special switch is needed, but confirm incidents/alerts are being generated in the portal.
	•	Entra ID Sign-In and Audit Logs – Azure AD (Entra ID) automatically logs sign-ins and audit events. You can confirm by checking Azure AD > Monitoring > Sign-in logs and Audit logs in the Azure Portal. These logs will be streamed via Event Hub in our integration.
```

## Azure Event Hub Configuration (Real-Time Telemetry)
Use Azure Event Hubs to stream high-volume telemetry (like sign-in logs and advanced hunting events) to QRadar with minimal latencyl. The following steps assume you have appropriate Azure access in the arouhan tenant:
	1	Create an Event Hubs Namespace (Azure Portal > Create a resource > Event Hubs). For example:
	◦	Namespace name: arouhan-psiem (this is an example naming convention for arouhan’s SIEM integration).
	◦	Pricing tier/capacity: choose based on expected throughput (Standard tier is usually sufficient).
	2	Create an Event Hub within the namespace (Azure Portal > your Event Hubs namespace > Event Hubs > + Event Hub):
	◦	Name: e.g. security-logs-hub (an event hub to receive security logs).
	◦	You may use one hub for multiple sources (Azure AD, Defender) or separate hubs per source. Here we use a single hub for simplicity.
	3	Create a Consumer Group on the Event Hub (Azure Portal > your Event Hub > Consumer Groups > + Consumer Group):
	◦	Name: e.g. arouhan-psiem-cg (avoid using the default $Default group in production).
	◦	QRadar will use this consumer group when reading events.
	4	Create Shared Access Policies (SAS) for the Event Hub:
	◦	Under your Event Hubs namespace (or the specific hub), go to Shared access policies. Create two policies:
	▪	SendPolicy – with Send permissions. QRadar won’t use this directly, but Azure services (like Azure AD diagnostics and Defender streaming) will use this to send data to the hub.
	▪	ListenPolicy – with Listen (and Read) permissions. QRadar will use this to listen for events.
	◦	After creating each policy, copy the Connection string–primary key value. You will use the ListenPolicy connection string in the QRadar configuration for the Event Hubs protocol.
	5	Create an Azure Storage Account (if not already) for Event Hub checkpointing (this is required by QRadar’s Event Hubs protocol to track offsets). For example:
	◦	Name: arouhancheckpoint (any unique name).
	◦	General-purpose v2 storage in the same region as the event hub is recommended.
	◦	After creation, go to Access keys and copy the connection string for the storage account (this will be configured in QRadar). Ensure the storage account allows blob access (the QRadar Event Hub connector will create a blob container named qradar for tracking checkpoints).
	6	Stream Entra ID Logs to Event Hub: Configure Azure AD to send logs to the Event Hub:
	◦	In Azure Portal, navigate to Azure AD > Monitoring > Diagnostic settings. Add a new diagnostic setting (e.g., aad-to-eventhub).
	◦	Categories: Select SignInLogs and AuditLogs (these correspond to user sign-ins and directory audit events).
	◦	Destination: Choose Stream to an Event Hub. Select the arouhan-psiem Event Hubs namespace and the security-logs-hub event hub. Ensure the SendPolicy connection string (namespace authorization rule) is used by Azure (the portal will handle this when you select the namespace and hub). Save the diagnostic setting.
	◦	Result: Entra ID sign-in and audit events will now stream to the event hub in real-time.
	7	Stream Microsoft (365) Defender Logs to Event Hub: In the Microsoft (365) Defender portal:
	◦	Go to  Settings > Microsoft Defender XDR > Streaming API
	◦	Click Add . Configure as follows:
	▪	Name: e.g. defender-to-eventhub.
	▪	Destination: Forward events to Azure Event Hub. Provide the Event Hub Namespace Resource ID and Event Hub Name (for the arouhan-psiem namespace and security-logs-hub we created). This grants Defender permission to send to the hub.
			Event Hub Namespace Resource ID:
			Find this in the Azure Portal under: 	Event Hubs > arouhan-psiem > Properties

	▪	Event Types: Select the telemetry types to stream. For example:
	▪	Device events (DeviceEvents, DeviceFileEvents, DeviceNetworkEvents, DeviceLogonEvents, DeviceProcessEvents.)
	▪	Alert Info/Evidence (if you want alerts via streaming as well – though alerts will also be pulled via Graph, streaming them can provide real-time duplicates)
	▪	Email events (EmailEvents, EmailAttachmentInfo, etc., if Defender for Office 365 is in use)
	▪	Choose all relevant tables needed for your monitoring. (These correspond to the Advanced Hunting schema events.)
	▪	Save the configuration. Microsoft Defender for Endpoint/Office/Identity will now push the selected event telemetry to the Event Hub in real-time.
Note: The Streaming API sends raw events in a JSON structure under a records array for each message. QRadar’s DSM for Microsoft 365 Defender (Advanced Hunting events) will parse these events, but ensure your QRadar is on a recent DSM version that supports these event types.



# QRadar Configuration – Log Sources
In QRadar, you will set up three log sources to cover the different data streams for arouhan:
	1	Entra ID Logs via Event Hub – for Azure AD sign-in and audit events (real-time).
	2	Microsoft 365 Defender Alerts via Graph API – for security alerts (near-real-time, polled).
	3	Microsoft 365 Audit Logs via Graph API – for unified audit log events (polled periodically).
Each log source is configured through the QRadar Admin interface (Admin > Data Sources > Log Sources > Add). Below are the details for each:


## 1. Entra ID (Azure AD) Logs – Event Hub Integration
This log source pulls Azure AD sign-in and audit logs from the Event Hub:
	•	Log Source Name: e.g. Entra ID @ AzureADarouhanprod (a descriptive name indicating Entra ID logs for arouhan prod).
	•	Log Source Type: Microsoft Entra ID (this DSM covers Azure AD logs).
	•	Protocol Type: Microsoft Azure Event Hubs (built-in protocol for Event Hub integration)
	•	Log Source Identifier: sb://arouhan-psiem.servicebus.windows.net – the Event Hubs namespace URI for arouhan (replace with your actual namespace).
	•	Authentication Method: SAS (Shared Access Signature).
	•	Event Hub Connection String: Use Event Hub Connection String: Yes – provide the ListenPolicy connection string (from the Event Hub’s SAS policy with Listen rights). This string includes the namespace, hub name, and SAS key. For example:Endpoint=sb://arouhan-psiem.servicebus.windows.net/;SharedAccessKeyName=ListenPolicy;SharedAccessKey=<key>;EntityPath=security-logs-hub.
	•	Consumer Group: arouhan-psiem-cg – the consumer group name created for QRadar.
	•	Use Storage Account Connection String: Yes – provide the Azure Storage account connection string (from the storage account’s access keys) for checkpointing. This allows QRadar to track read offsets in the event hub (it will use/create a blob container named qradar).
	•	Format Azure Linux Events to Syslog: No (not needed for JSON logs).
	•	Convert VNet Flow Logs to IPFIX: No.
	•	Use As A Gateway Log Source: No.
	•	Proxy Settings: If QRadar requires a proxy to reach Azure (as in many corporate networks), configure Use Proxy: Yes. For example:
	◦	Proxy Host: XXX (replace with your arouhan proxy if different; this was used in the reference environment).
	◦	Proxy Port: 3128.
	◦	Proxy Username/Password: (if required by your proxy; often left blank for unauthenticated proxies).
	•	EPS Throttle: e.g. 10000 EPS (events per second) – a high cap to ensure QRadar doesn’t drop bursts of events.
	•	Click Test Connection. If configured correctly, QRadar should show a successful connection to the event hub. Then Save the log source.
<small>After a few minutes, this log source should start receiving Azure AD events. In the Log Activity tab, verify events labeled with the “Microsoft Entra ID” DSM are appearing.</small>



## 2. Microsoft Defender Alerts – Graph Security API
This log source uses the Microsoft Graph Security API to poll for security alerts (incidents) from Microsoft 365 Defender (covering Defender for Endpoint, Defender for Office 365, Defender for Identity, etc., via the unified Graph security interface):
	•	Log Source Name: e.g. Defender XDR @ D4M365arouhanprod  
	•	Log Source Type: Microsoft 365 Defender (Note: QRadar DSM retains this name due to legacy branding)
	•	Protocol Type: Microsoft Graph Security API (built-in protocol for Graph Security alerts).
	•	Log Source Identifier: A unique ID for this source (can be any string). For example, use arouhan-MASC-1. This is just an internal identifier for QRadar logs – you can use arouhan-GraphAlerts or similar if preferred.
	•	Tenant ID: [arouhan Tenant ID] – the Azure AD Tenant ID (GUID) for your arouhan tenant (from the App Registration earlier).
	•	Client ID: [Application (Client) ID] of the QRadar-arouhan-GraphAPI-Collector app you created.
	•	Client Secret: [Client Secret value] from the app registration. (Use the secret string created earlier; QRadar will store it encrypted.)
	•	API: Select Alerts V2 (/alerts_v2). This specifies using the v2 Alerts Graph endpoint (which provides unified Defender alerts via Microsoft Graph).
	•	Service: Select Other (or “Microsoft 365 Defender” if available – in some QRadar versions, the service field may not be prominently used; “Other” is typically used when not specifying a particular sub-service).
	•	Event Filter: (Optional) You can leave blank to collect all available alerts, or use OData filters if you only want specific alerts (not common; usually leave empty to get all alerts).
	•	Use Proxy: Yes (if needed, similarly to above). For example, Proxy Host XXXX.com, Port 3128.
	•	Login Endpoint: login.microsoftonline.com (the OAuth token endpoint for Azure AD – default for public Azure).
	•	Graph API Endpoint: https://graph.microsoft.com (the Microsoft Graph base URL).
	•	Recurrence: 5M – poll every 5 minutes. (This means QRadar will query the Graph API for new alerts every 5 minutes. Adjust as needed, but 5 minutes is a good default to balance timeliness and API usage.)
	•	EPS Throttle: 5000 (alerts are fewer, but set a reasonable cap).
	•	Click Test Connection – QRadar will attempt to authenticate to Graph and fetch a sample alert. On success (“Successfully queried Microsoft Graph Security API”), Save the log source.
The QRadar Microsoft 365 Defender DSM will parse incoming alerts (via the Graph Security API). Ensure that your QRadar version/DSM supports the alerts v2 schema. According to IBM, the Microsoft 365 Defender DSM can collect alerts from the Defender Alerts v2 API via the Graph protocolibm.com (requiring the SecurityEvents.Read.All permission we configuredibm.com).


## 3. Microsoft 365 Unified Audit Log via Office 365 REST API
This log source polls the Microsoft 365 Unified Audit Log (UAL) for events across Azure AD, Exchange, SharePoint, Teams, and DLP using the Office 365 REST API protocol, which connects to the Office 365 Management Activity API (https://manage.office.com). As of April 2025, this API is fully supported with no announced retirement date (Microsoft Learn). The Microsoft Graph API for Audit Logs protocol is not currently available in QRadar’s Microsoft Office 365 DSM.

	•	Log Source Name: M365 @ M365arouhanprod
	•	Log Source Type: Microsoft Office 365
	◦	In QRadar’s Log Source Management (Admin > Data Sources > Log Sources > Add), select Microsoft Office 365. This DSM collects unified audit log events via the Office 365 REST API protocol in QRadar 7.4+ (IBM Docs).
	•	Protocol Type: Office 365 REST API
	•	Log Source Identifier: arouhan-MS365-Prod
	•	Tenant ID: [arouhan Tenant ID]
	•	Client ID: [From QRadar-arouhan-GraphAPI-Collector]
	•	Client Secret: [From QRadar-arouhan-GraphAPI-Collector]
	•	Event Filter:
	◦	Azure Active Directory (sign-in and directory audit events)
	◦	Exchange (Exchange Online events, e.g., mailbox access)
	◦	SharePoint (SharePoint and OneDrive activities)
	◦	General (Teams, PowerBI, Stream, and other services not in dedicated categories)
	◦	DLP (Data Loss Prevention events)
	•	Use Proxy: Yes
	◦	Proxy IP/Hostname: XXXX.com
	◦	Proxy Port: 3128
	◦	Proxy Username/Password: [Leave blank or specify]
	•	Advanced Options:
	◦	Management Activity API URL: https://manage.office.com
	◦	Azure AD Sign-in URL: https://login.microsoftonline.com
	◦	EPS Throttle: 5000
	•	Test Connection: Verify QRadar fetches audit logs (“Connected. Waiting for events…”).
	•	Verification: Check Log Activity for Microsoft Office 365 DSM events (5–30 minute delay) (Microsoft Learn). Use:

    ```bash
	SELECT * FROM events WHERE logsourcetype = 'Microsoft Office 365' LAST 1 HOUR
    ```

Note: Ensure the Azure AD app (QRadar-arouhan-GraphAPI-Collector) has ActivityFeed.Read and ActivityFeed.ReadDlp permissions (Microsoft Learn). Monitor Microsoft for any API retirement announcements and IBM for DSM updates supporting Microsoft Graph API for Audit Logs (IBM App Exchange). Test parsing in a non-production environment (Reddit).


Additional Configuration: Handling Duplicates
Using both Azure Event Hubs (for Microsoft Entra ID and Microsoft 365 Defender events) and the Office 365 Management Activity API (for Microsoft Office 365 audit logs) may result in duplicate events in QRadar, as some events (e.g., Azure AD sign-in events) could appear in both streams. To manage duplicates:
	•	Deduplication Rule: Create a QRadar rule to drop or flag duplicate events. Extract a unique identifier (e.g., Id for Azure AD events or RecordId for audit logs) as a Custom Event Property (CEP), named eventId.
	◦	In QRadar, go to Log Activity > Add Filter > Custom Event Property to define eventId by extracting Id or RecordId from event payloads (IBM Docs).
	◦	Create a Rule (Rules > Actions > New Event Rule):
	▪	Condition: Detect when two events have the same eventId within a 5-minute window across log sources (Microsoft Entra ID, Microsoft Office 365).
	▪	Action: Suppress or throttle the duplicate event (e.g., drop the second event).
	•	Alternative: Reduce overlap by limiting event types in the Microsoft Office 365 log source (e.g., exclude Azure Active Directory events if covered by Event Hubs). Retaining both sources provides backup and cross-validation.
	•	Verify Duplicates: Run this AQL query in QRadar to identify duplicates:

```bash
SELECT "eventId", COUNT(*)
FROM events
WHERE logsourcetype IN ('Microsoft Entra ID', 'Microsoft Office 365')
  AND "eventId" IS NOT NULL
GROUP BY "eventId"
HAVING COUNT(*) > 1
LAST 1 HOURS
```


Monitoring and Verification
Monitor Azure and QRadar to ensure proper event collection:
	•	In QRadar:
	◦	Go to Log Activity and filter by:
	▪	Microsoft Entra ID (Event Hub events, e.g., Azure AD sign-ins, audits).
	▪	Microsoft 365 Defender (Graph Security API alerts).
	▪	Microsoft Office 365 (audit logs via Office 365 REST API).
	◦	Run this AQL query to check event counts:
	SELECT logsourcetype, COUNT(*)
	FROM events
	WHERE logsourcetype IN ('Microsoft Entra ID', 'Microsoft 365 Defender', 'Microsoft Office 365')
	GROUP BY logsourcetype
	LAST 15 MINUTES

	•	In Azure:
	◦	Check Event Hub metrics (Azure Portal > Event Hubs > [your hub] > Metrics) for incoming messages (Microsoft Learn).
	◦	Verify API calls in Azure AD app’s audit logs (Azure Portal > Microsoft Entra ID > Audit logs) to confirm QRadar polling.
	◦	Test scenarios (e.g., user login, file access) to ensure events appear in QRadar.
	•	Troubleshooting: If events are missing, check QRadar log source status, network connectivity, or Azure AD app permissions (ActivityFeed.Read, ActivityFeed.ReadDlp for Office 365 REST API) (Microsoft Learn).

Network and Firewall Considerations
Ensure QRadar can reach these endpoints (TCP 443 HTTPS):
	•	Azure AD/Authentication:
	◦	login.microsoftonline.com (OAuth token retrieval)
	•	Office 365 Management API:
	◦	manage.office.com (audit log retrieval via Office 365 REST API)
	•	Azure Event Hub and Storage:
	◦	[your-namespace].servicebus.windows.net (e.g., arouhan-psiem.servicebus.windows.net)
	◦	*.blob.core.windows.net (Azure Blob Storage for checkpoints)
	•	Firewall: Allow outbound connections from QRadar’s Collector/Console. If the Event Hub has network restrictions, enable “Allow access from all networks” or specify QRadar’s IP in the Event Hub’s network settings (Microsoft Learn).
Notes and Best Practices
	•	API Status: The Office 365 Management Activity API is supported as of April 2025 with no retirement announced (Microsoft Learn). The Microsoft Graph API for Audit Logs protocol is not available in QRadar’s Microsoft Office 365 DSM but may be added in future updates (IBM Docs).
	•	DSM Updates: Ensure QRadar DSMs (Microsoft Entra ID, Microsoft 365 Defender, Microsoft Office 365) are updated to 7.4+ via Admin > DSM Editor or IBM’s auto-update service (IBM App Exchange).
	•	Performance: Monitor EPS for Event Hub logs in QRadar. Filter noisy categories in Azure Diagnostic Settings if needed. The 5-minute polling interval for Office 365 REST API balances timeliness and API load.
	•	Security: Rotate the Azure AD app’s Client Secret periodically and restrict access to the app (QRadar-arouhan-GraphAPI-Collector) due to its high permissions.
	•	Future-Proofing: Add AuditLog.Read.All permission to prepare for potential Graph API adoption. Monitor Microsoft and IBM for API or DSM updates (Microsoft Learn, IBM App Exchange).
Sources
	•	IBM Docs - Microsoft Office 365 DSM
	•	IBM Docs - Microsoft 365 Defender DSM
	•	Microsoft Learn - Office 365 Management Activity API
	•	Microsoft Learn - Azure Event Hubs Monitoring
	•	Reddit - QRadar Office 365 Log Issues


