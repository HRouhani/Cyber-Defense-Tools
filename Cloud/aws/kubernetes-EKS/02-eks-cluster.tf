
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  #version = "19.16.0"
  version = "20.26.0"

  cluster_name    = local.cluster_name
  #cluster_version = "1.29"
  cluster_version = "1.34"
  # why it is important:
  # Our setup uses AWS IAM Identity Center (SSO) with short-lived sessions. SSO roles have complex ARNs (with paths like /aws-reserved/sso.amazonaws.com/eu-west-1/), and EKS doesn't auto-map them without explicit configuration. Enabling this handles that seamlessly, avoiding manual CLI steps or console tweaks.
  # It creates an aws_eks_access_entry resource for that ARN with type "STANDARD"
  enable_cluster_creator_admin_permissions = true

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # cannot disable public access since then the kubectl  toward k8s is not working
  cluster_endpoint_public_access = true
  #cluster_endpoint_private_access = true

  #create_kms_key = false
 /*  cluster_encryption_config = {
    resources        = ["secrets"]
    provider_key_arn = aws_kms_key.eks.arn
  }
 */

 # Use default AWS-managed encryption
  cluster_encryption_config = {
    resources = ["secrets"]
}
  #manage_aws_auth_configmap = true
  #create_aws_auth_configmap = true
  eks_managed_node_group_defaults = {
    #ami_type       = "AL2_x86_64"
    ami_type       = "AL2023_x86_64_STANDARD"
    disk_size      = 80
    instance_types = ["m5.large"]

  }
  eks_managed_node_groups = {
    complete = {
      name            = "security-team-managed-nodes-${random_string.suffix.result}"
      use_name_prefix = true

      #ami_type = "AL2_x86_64"
      ami_type  = "AL2023_x86_64_STANDARD"

      min_size     = 1
      max_size     = 2
      desired_size = 1

      public_ip = true
      network_interfaces = [{
        associate_public_ip_address = true
      }]

      capacity_type        = "SPOT"
      disk_size            = 80
      force_update_version = true
      instance_types       = ["m5.large", "m5n.large", "m5zn.large"]
      labels = {
        GithubRepo = "terraform-aws-eks"
        GithubOrg  = "terraform-aws-modules"
      }

      update_config = {
        max_unavailable_percentage = 50 
      }

      ebs_optimized           = true
      disable_api_termination = false
      vpc_security_group_ids  = [aws_security_group.additional.id]
      enable_monitoring       = true
      enable_key_rotation     = true


      block_device_mappings = {
        xvda = {
          device_name = "/dev/xvda"
          ebs = {
            volume_size           = 80
            volume_type           = "gp3"
            iops                  = 3000
            throughput            = 150
            encrypted             = true
            #kms_key_id            = aws_kms_key.ebs.arn
            delete_on_termination = true
          }
        }
      }

      create_iam_role          = true
      iam_role_name            = "security-team-iam-role"
      iam_role_use_name_prefix = false
      iam_role_description     = "EKS managed node group role"
      iam_role_tags = {
        Purpose = "Protector of the kubelet"
      }
      iam_role_additional_policies = {
        AmazonSSMManagedInstanceCore = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
        additional                   = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
        additional                   = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
        additional                   = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
        additional                   = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
      }

      tags = {
        ExtraTag = "EKS managed node group complete example"
      }
    }
  }

  # Open ssh Ports to worker node
  # Extend node-to-node security group rules
  node_security_group_additional_rules = {
    ingress_self_all = {
      description = "ssh to worker nodes"
      protocol    = "tcp"
      from_port   = 22
      to_port     = 22
      type        = "ingress"
      self        = true
    }
  }
}


# https://aws.amazon.com/blogs/containers/amazon-ebs-csi-driver-is-now-generally-available-in-amazon-eks-add-ons/ 
data "aws_iam_policy" "ebs_csi_policy" {
  arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
}

module "irsa-ebs-csi" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role-with-oidc"
  version = "4.7.0"

  create_role                   = true
  role_name                     = "AmazonEKSTFEBSCSIRole-${module.eks.cluster_name}"
  provider_url                  = module.eks.oidc_provider
  role_policy_arns              = [data.aws_iam_policy.ebs_csi_policy.arn]
  oidc_fully_qualified_subjects = ["system:serviceaccount:kube-system:ebs-csi-controller-sa"]
}



