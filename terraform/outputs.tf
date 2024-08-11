output "elastic_beanstalk_application_name" {
  value = aws_elastic_beanstalk_application.eb_app.name
}

output "elastic_beanstalk_environment_url" {
  value = aws_elastic_beanstalk_environment.eb_env.endpoint_url
}

output "vpc_id" {
  value = aws_vpc.main_vpc.id
}

output "public_subnet_ids" {
  value = [aws_subnet.public_subnet_a.id, aws_subnet.public_subnet_b.id]
}

output "security_group_id" {
  value = aws_security_group.eb_sg.id
}
