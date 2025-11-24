
resource "random_string" "suffix" {
  length  = 4
  special = false
  upper   = false
}


provider "aws" {
  region = var.region
}

# The Availability Zones data source allows access to the list of AWS Availability Zones which can be accessed by an AWS account within the region configured in the provider.
data "aws_availability_zones" "available" {}

locals {
  cluster_name = "security-team-${random_string.suffix.result}"
}


module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = "security-team-vpc-${random_string.suffix.result}"

  cidr = "10.0.0.0/16"
  # Create subnets in the first two available availability zones which is required for a eks deployment
  azs = slice(data.aws_availability_zones.available.names, 0, 2)

  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.3.0/24", "10.0.4.0/24"]

  #  one single NAT Gateway in one availability zone 

  enable_nat_gateway     = true
  single_nat_gateway     = true
  one_nat_gateway_per_az = false
  enable_dns_hostnames   = true
  create_igw             = true


  enable_flow_log                      = true
  create_flow_log_cloudwatch_iam_role  = true
  create_flow_log_cloudwatch_log_group = true

  tags = {
    Environment = "Secuity Team Testing"
  }

}
