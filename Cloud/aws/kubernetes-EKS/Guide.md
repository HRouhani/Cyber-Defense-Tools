This guide explains how to resolve authentication issues when accessing an Amazon EKS cluster using AWS IAM Identity Center (formerly AWS SSO) temporary credentials. It covers the root cause and two main solutions: one integrated into Terraform during cluster creation, and another for existing clusters using manual AWS CLI steps (with options for read-only or admin access).

** Root Cause of the Issue
When deploying an EKS cluster (v1.30+ like), access is managed via Access Entries (not the deprecated aws-auth ConfigMap). The SSO-assumed IAM role (e.g., arn:aws:iam::869935083575:role/aws-reserved/sso.amazonaws.com/eu-west-2/AWSReservedSSO_HRZ-Project_5cefae3674499372627) isn't automatically added due to its temporary nature. This causes "You must be logged in to the server" errors in kubectl, and also lack visibilities for aws Portal. 


Initial check showing the missing entry:

aws eks list-access-entries --cluster-name security-team --region XXXX
{
    "accessEntries": [
        "arn:aws:iam::XXXXXXXXXXXXXXX:role/aws-service-role/eks.amazonaws.com/AWSServiceRoleForAmazonEKS",
        "arn:aws:iam::XXXXXXXXXXXXX:role/security-team-iam-role"
    ]
}


** Option 1: Solve During Terraform Deployment (Recommended for New Clusters)

The issue is that my SSO-assumed IAM role (arn:aws:iam::XXXXXXXXXXXXXX:role/AWSReservedSSO_HRZ-Project_5cefae3674499372627) is not listed in the cluster's access entries, as shown in our list-access-entries output. This prevents authentication via kubectl, even though we created the cluster. For EKS clusters version 1.30+, access is managed via Access Entries rather than the old aws-auth ConfigMap, and the cluster creator's role isn't always auto-added when using SSO (due to the temporary session nature). To fix this without needing additional IAM permissions, we have 2 options, whether solve it during the terraform deployment which i did here and if the cluster already exist we need to use manual option as I explained in the next part: 

to solve the issue, i used following line in 02-eks-cluster.tf

```
enable_cluster_creator_admin_permissions = true
```



This tells the EKS module to automatically create an Access Entry for the IAM principal (our SSO role) that runs terraform apply, mapping it to the system:masters Kubernetes group for full admin access.

to confirm we can run again the list-access-entries

test@test kubernetes-EKS (main*)$ aws eks list-access-entries --cluster-name $(terraform output -raw cluster_name) --region $(terraform output -raw region)
{
    "accessEntries": [
        "arn:aws:iam::869935083575:role/aws-reserved/sso.amazonaws.com/eu-west-2/AWSReservedSSO_HRZ-Project_5cefae3674499372627",
        "arn:aws:iam::869935083575:role/aws-service-role/eks.amazonaws.com/AWSServiceRoleForAmazonEKS",
        "arn:aws:iam::869935083575:role/security-team-iam-role"
    ]
}


it will automatically update the kubeconfig file during the cluster creation. Otherwise we can update the kubeconfig file ourselve again:

kubectl --kubeconfig ./kubeconfig create namespace security-team


This explicitly maps our SSO role as cluster admin.




** Option 2: Solve for an Existing Cluster (Manual Steps) ** 

For already-deployed clusters, use AWS CLI to add your SSO role. These steps grant read-only access by default (using AmazonEKSViewPolicy for viewing resources like pods/nodes without edits). Adjust for admin or namespace-specific as noted.


1. Retrieve Our SSO IAM Role ARN

```
aws iam get-role --role-name AWSReservedSSO_HRZ-Project_5cefae3674499372627 --query Role.Arn --output text
```

Expected output: Something like

arn:aws:iam::761135083533:role/aws-reserved/sso.amazonaws.com/eu-west-2/AWSReservedSSO_HRZ-Project_5cefae3674499372627



2. Create the Access Entry for Your Role

We need to registers our SSO role with the EKS cluster, allowing it to authenticate. Without this, we can't access the cluster at all.


```
aws eks create-access-entry \
  --cluster-name security-team \
  --principal-arn arn:aws:iam::761135083533:role/aws-reserved/sso.amazonaws.com/eu-west-2/AWSReservedSSO_HRZEstablishment-Project_5degfe43096b2044 \
  --type STANDARD \
  --region us-east-1
``` 

Pay attention that here the EKS cluster is in us-east-1 region, but our role arn is in another region.



3. Associate the Read-Only Policy

Then we need to attaches the AmazonEKSViewPolicy to our role, limiting to read-only actions (e.g., get/list/watch on most Kubernetes resources like pods, nodes, deployments, but no create/update/delete). It excludes sensitive items like Secrets for security.


```
aws eks associate-access-policy \
  --cluster-name security-team \
  --principal-arn arn:aws:iam::761135083533:role/aws-reserved/sso.amazonaws.com/eu-west-2/AWSReservedSSO_HRZEstablishment-Project_5degfe43096b2044 \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSViewPolicy \
  --access-scope type=cluster \
  --region us-east-1
```

** for Admin access we can use:  arn:aws:eks::aws:cluster-access-policy/AmazonEKSAdminViewPolicy

** For namespace-specific access: Change --access-scope type=cluster to --access-scope type=namespace --access-scope namespaces=NameSpaceName,default (list your namespaces).


** to confirm at the end our access entries

```
aws eks list-access-policies --cluster-name security-team --principal-arn <your-arn> --region us-east-1
```


** We should keep in mind that, from terminal since SSO is short-live, we need to keep update the kubeconfig

aws eks --region us-east-1 update-kubeconfig --name security-team --kubeconfig ./kubeconfig


we might need to set an env as well to be able to read kubeconfig:

export KUBECONFIG=./kubeconfig


To test:

```
kubectl get nodes  # Should list nodes
kubectl get pods -n security-team  # Should list pods in your namespace
```

