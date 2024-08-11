provider "aws" {
  region = var.aws_region
}

# Create a VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "Main VPC"
  }
}

# Create public subnets
resource "aws_subnet" "public_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "Public Subnet 1"
  }
}

resource "aws_subnet" "public_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.aws_region}b"

  tags = {
    Name = "Public Subnet 2"
  }
}

# Create the Elastic Beanstalk application
resource "aws_elastic_beanstalk_application" "employee_attrition" {
  name        = "employee-attrition"
  description = "Employee Attrition Prediction Application"
}

# Create the Elastic Beanstalk environment
resource "aws_elastic_beanstalk_environment" "employee_attrition_env" {
  name                = "employee-attrition-env"
  application         = aws_elastic_beanstalk_application.employee_attrition.name
  solution_stack_name = "64bit Amazon Linux 2023 v4.1.1 running Python 3.9"

  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "EnvironmentType"
    value     = "LoadBalanced"
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "ServiceRole"
    value     = "aws-elasticbeanstalk-service-role"
  }

  setting {
    namespace = "aws:elbv2:listener:80"
    name      = "ListenerEnabled"
    value     = "true"
  }

  setting {
    namespace = "aws:elbv2:listener:80"
    name      = "Protocol"
    value     = "HTTP"
  }

  setting {
    namespace = "aws:elbv2:listener:80"
    name      = "Rules"
    value     = <<EOF
[
  {
    "PathPatternCondition": {
      "Values": [
        "*"
      ]
    },
    "TargetGroup": {
      "Code": "default"
    },
    "Priority": 1
  }
]
EOF
  }

  setting {
    namespace = "aws:elasticbeanstalk:container:docker"
    name      = "DockerImage"
    value     = "${var.ecr_repository_url}:${var.image_tag}"
  }

  setting {
    namespace = "aws:elasticbeanstalk:container:docker"
    name      = "DockerCommand"
    value     = "gunicorn --bind 0.0.0.0:5010 application:app"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "BUCKET_NAME"
    value     = var.s3_bucket_name
  }

  setting {
    namespace = "aws:elasticbeanstalk:application"
    name      = "Application Healthcheck URL"
    value     = "/health"
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "VPCId"
    value     = aws_vpc.main.id
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "Subnets"
    value     = "${aws_subnet.public_1.id},${aws_subnet.public_2.id}"
  }
}

variable "aws_region" {
  description = "AWS region to create resources in"
  type        = string
  default     = "eu-north-1"
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket for storing model artifacts"
  type        = string
  default     = "attritionproject"
}

variable "ecr_repository_url" {
  description = "URL of the ECR repository containing the Docker image"
  type        = string
}

variable "image_tag" {
  description = "Tag of the Docker image to be deployed"
  type        = string
}

output "environment_name" {
  description = "Name of the Elastic Beanstalk environment"
  value       = aws_elastic_beanstalk_environment.employee_attrition_env.name
}

output "application_name" {
  description = "Name of the Elastic Beanstalk application"
  value       = aws_elastic_beanstalk_application.employee_attrition.name
}

output "environment_url" {
  description = "URL of the Elastic Beanstalk environment"
  value       = aws_elastic_beanstalk_environment.employee_attrition_env.cname
}
