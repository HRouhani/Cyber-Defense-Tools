# This Terraform configuration sets up:
# - A new VPC
# - A public subnet
# - Security group for OpenCTI
# - EC2 instance (Ubuntu 24.04, r6i.2xlarge, 100GiB root)
# - Uploads and runs OpenCTI setup script on boot
# - Enables SSM Session Manager access
# - Saves SSH private key to a file via null_resource (NEW)

provider "aws" {
  region = "us-east-1"
}

resource "tls_private_key" "ssh" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "opencti_key" {
  key_name   = "opencti-key"
  public_key = tls_private_key.ssh.public_key_openssh
}

resource "null_resource" "save_ssh_key" {
  provisioner "local-exec" {
    command = "echo '${tls_private_key.ssh.private_key_pem}' > opencti_key.pem && chmod 400 opencti_key.pem"
  }
}

resource "aws_iam_role" "ssm_role" {
  name = "opencti-ssm-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Principal = {
          Service = "ec2.amazonaws.com"
        },
        Effect = "Allow",
        Sid    = ""
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ssm_policy_attachment" {
  role       = aws_iam_role.ssm_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_instance" "opencti_ec2" {
  ami                         = "ami-084568db4383264d4"
  instance_type               = "r6i.2xlarge"
  subnet_id                   = aws_subnet.opencti_subnet.id
  vpc_security_group_ids      = [aws_security_group.opencti_sg.id]
  key_name                    = aws_key_pair.opencti_key.key_name
  iam_instance_profile        = aws_iam_instance_profile.ssm_profile.name
  associate_public_ip_address = true

  root_block_device {
    volume_size = 100
    volume_type = "gp3"
  }

  user_data = file("./opencti.sh")

  tags = {
    Name = "OpenCTI-Instance"
  }

  depends_on = [null_resource.save_ssh_key]
}

resource "aws_iam_instance_profile" "ssm_profile" {
  name = "opencti-ssm-profile"
  role = aws_iam_role.ssm_role.name
}

resource "aws_vpc" "opencti_vpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "opencti_subnet" {
  vpc_id                  = aws_vpc.opencti_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "us-east-1a"
}

resource "aws_internet_gateway" "opencti_igw" {
  vpc_id = aws_vpc.opencti_vpc.id
}

resource "aws_route_table" "opencti_rt" {
  vpc_id = aws_vpc.opencti_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.opencti_igw.id
  }
}

resource "aws_route_table_association" "opencti_rta" {
  subnet_id      = aws_subnet.opencti_subnet.id
  route_table_id = aws_route_table.opencti_rt.id
}

resource "aws_security_group" "opencti_sg" {
  name        = "OpenCTI-mhp"
  description = "Security group for OpenCTI"
  vpc_id      = aws_vpc.opencti_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

output "ec2_public_ip" {
  value = aws_instance.opencti_ec2.public_ip
}

output "ssh_private_key" {
  value     = tls_private_key.ssh.private_key_pem
  sensitive = true
}
