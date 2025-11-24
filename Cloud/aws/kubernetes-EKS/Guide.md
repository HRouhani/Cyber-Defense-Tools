at first when i deployed the cluster i got:

hrouhan@hrz kubernetes-EKS (main*)$ aws eks list-access-entries --cluster-name security-team-do9h --region us-east-1
{
    "accessEntries": [
        "arn:aws:iam::869935083575:role/aws-service-role/eks.amazonaws.com/AWSServiceRoleForAmazonEKS",
        "arn:aws:iam::869935083575:role/security-team-iam-role"
    ]
}


iThe issue is that your SSO-assumed IAM role (arn:aws:iam::869935083575:role/AWSReservedSSO_MHPFoundation-ProjectDeveloper_5cefae57606b2022) is not listed in the cluster's access entries, as shown in your list-access-entries output. This prevents authentication via kubectl, even though you created the cluster. For EKS clusters version 1.30+ (yours is 1.34), access is managed via Access Entries rather than the old aws-auth ConfigMap, and the cluster creator's role isn't always auto-added when using SSO (due to the temporary session nature). To fix this without needing additional IAM permissions, update your Terraform configuration to explicitly grant admin access to the cluster creator (your SSO role).


to solve the issue, i used following line in 02-eks-cluster.tf

enable_cluster_creator_admin_permissions = true

This tells the EKS module to automatically create an Access Entry for the IAM principal (your SSO role) that runs terraform apply, mapping it to the system:masters Kubernetes group for full admin access.

to confirm we can run again the list-access-entries

hrouhan@hrz kubernetes-EKS (main*)$ aws eks list-access-entries --cluster-name $(terraform output -raw cluster_name) --region $(terraform output -raw region)
{
    "accessEntries": [
        "arn:aws:iam::869935083575:role/aws-reserved/sso.amazonaws.com/eu-west-1/AWSReservedSSO_MHPFoundation-ProjectDeveloper_5cefae57606b2022",
        "arn:aws:iam::869935083575:role/aws-service-role/eks.amazonaws.com/AWSServiceRoleForAmazonEKS",
        "arn:aws:iam::869935083575:role/security-team-iam-role"
    ]
}


it will automatically update the kubeconfig file during the cluster creation


This explicitly maps your SSO role as cluster admin.



** What if the cluster already deployed ** 

If the EKS cluster already exist, we can follow these steps to get ReadOnly or Admin Access to the cluster. To solve this issue, we need to add our SSO IAM role as a read-only (if needed Admin access) user via EKS Access Entries.


1. Retrieve Our SSO IAM Role ARN

```
aws iam get-role --role-name AWSReservedSSO_MHPFoundation-ProjectDeveloper_5cefae57606b2022 --query Role.Arn --output text
```

Expected output: Something like

arn:aws:iam::761135083533:role/aws-reserved/sso.amazonaws.com/eu-west-2/AWSReservedSSO_HRZEstablishment-Project_5degfe43096b2044



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

