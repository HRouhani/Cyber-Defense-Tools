

data "http" "myip" {
  url = "http://ipv4.icanhazip.com"
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ids attached to the cluster control plane"
  value       = module.eks.cluster_security_group_id
}

output "region" {
  description = "AWS region"
  value       = var.region
}

output "cluster_name" {
  description = "Kubernetes Cluster Name"
  value       = module.eks.cluster_name
}

/* output "ec2_linux_public_ip" {
  value = <<EOT



EOT
}
 */

output "igw_id" {
  value = module.vpc.igw_id
}


output "route_table_id" {
  #value = module.vpc.
  value = module.vpc.private_route_table_ids
}



output "summary" {
  value = <<EOT


***************************************************************************************************************************************************************
***************************************************************************************************************************************************************
***************************************************************************************************************************************************************
***************************************************************************************************************************************************************
***************************************************************************************************************************************************************
***************************************************************************************************************************************************************
***************************************************************************************************************************************************************




You need the Ec2 Instance id of the Worker node (EC2 Instance), something like "i-0a8e3fe273ca66fd4". If there are some Terminated EC2 instances, you see them as well with the following command which you need to ignore:

      ***  aws ec2 describe-instances | grep -i InstanceId


There are 2 ways to connect to worker nodes (EC2):

      
a. Session Manager
   
   requirements:  To initiate Session Manager sessions with your managed nodes by using the AWS Command Line Interface (AWS CLI), you must install the Session Manager plugin on your local machine.
                   Ubuntu:   curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb"
                             sudo dpkg -i session-manager-plugin.deb 


    ***  aws ssm start-session  --target <EC2 Instance ID>


b. EC2 Connect

    *** aws ec2-instance-connect ssh --instance-id <EC2 Instance ID> 




** for Testing purpose an Nginx webserver has been deployed. This setup is a simple web server demonstration using Nginx, a popular open-source HTTP server. The Pod runs an unprivileged Nginx container that serves a default welcome page over HTTP. The Service makes it accessible from outside the cluster via an AWS Elastic Load Balancer (ELB), since we're on EKS (Amazon's managed Kubernetes service).


- list all pods
  kubectl get pods -A

- describe the service
  kubectl -n security-team describe svc nginx-demo

- describe the Pod
  kubectl -n security-team describe pod nginx-demo-XXXXXXXXXXXXXX


- to get the external IP address to connect from outside over port 80
  kubectl -n security-team get svc nginx-demo


- to get a shell on the pod
  kubectl exec -it deployment/nginx-demo -- /bin/bash

EOT
}