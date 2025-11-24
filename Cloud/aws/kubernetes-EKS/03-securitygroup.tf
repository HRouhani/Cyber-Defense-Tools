

resource "aws_security_group" "additional" {
  name_prefix = "security-team-sg-ssh-${random_string.suffix.result}"
  vpc_id      = module.vpc.vpc_id

  /*   ingress {
    description       = "Cluster SG to Nodes"
    from_port = 0
    to_port   = 22
    protocol  = "tcp"
   # cidr_blocks      = ["0.0.0.0/0"]
    security_groups   = [module.eks.cluster_security_group_id, module.eks.cluster_primary_security_group_id]
  } */

  ingress {
    description     = "ssh to worker nodes"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    cidr_blocks     = ["0.0.0.0/0"]
    security_groups = [module.eks.cluster_security_group_id, module.eks.cluster_primary_security_group_id]
  }
}
