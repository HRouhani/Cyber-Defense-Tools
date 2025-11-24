 resource "null_resource" "configmap2" {
  depends_on = [module.eks]

  provisioner "local-exec" {
    command = <<EOT
set -e
# Wait for cluster to become ready
sleep 90

# Update kubeconfig using AWS CLI
aws eks --region ${var.region} update-kubeconfig --name ${module.eks.cluster_name} --kubeconfig ./kubeconfig

# Ensure we can reach cluster
kubectl --kubeconfig ./kubeconfig get nodes || (echo "Cluster not ready yet" && exit 1)

# Apply manifests
kubectl --kubeconfig ./kubeconfig create namespace security-team || true
kubectl --kubeconfig ./kubeconfig apply -f service-account.yaml
kubectl --kubeconfig ./kubeconfig apply -f nginx-pod.yaml
kubectl --kubeconfig ./kubeconfig apply -f roles.yaml
kubectl --kubeconfig ./kubeconfig apply -f roleBinding.yaml

EOT
  }
} 


/* 
 resource "aws_ecr_repository" "security-team-ecr" {
  name                 = "security-team-repo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}  */