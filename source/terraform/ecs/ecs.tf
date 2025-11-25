#Creating ECS for running dashboard

provider "aws" {
  region = "eu-west-2"
}

resource "aws_ecs_cluster" "c20-wishbone-ecs" {
  name = "c20-wishbone-ecs"
  setting {
    name = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_cluster_capacity_providers" "c20-wishbone-ecs-provider" {
  cluster_name = aws_ecs_cluster.c20-wishbone-ecs.name
  capacity_providers = ["FARGATE"]
}

#IAM role for executing tasks on the ECS
data "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"
}

resource "aws_ecs_task_definition" "wishbone-dashboard-task-definition" {
  family = "wishbone-dashboard-task-definition"
  network_mode = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  container_definitions = jsonencode([
    {
      name = "wishbone-dashboard-task"
      image = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c20-wishbone-dashboard-ecr:latest"
      essential = true
      environment = [
        {name = "ACCESS_KEY_ID", value = var.AWS_ACCESS_KEY},
      {name = "AWS_SECRET_ACCESS_KEY_ID", value = var.AWS_SECRET_ACCESS_KEY},
      {name = "BUCKET_NAME", value = var.BUCKET_NAME},
      {name = "DB_NAME", name = var.DB_NAME},
      {name = "PORT", value = var.PORT},
      {name = "RDS_HOST", value = var.RDS_HOST},
      {name = "RDS_PASSWORD", value = var.RDS_PASSWORD},
      {name = "RDS_USERNAME", value = var.RDS_USERNAME}
      ]
      portMappings = [
        {"containerPort": 8501,
        "protocol": "tcp"}
      ]
    }
  ])
  cpu = 512
  memory = 1024
  task_role_arn = data.aws_iam_role.ecs_task_execution_role.arn
  execution_role_arn = data.aws_iam_role.ecs_task_execution_role.arn
}

resource "aws_lb" "wishbone-dashboard-lb-2" {
  name = "wishbone-dashboard-lb-2"
  internal = false
  load_balancer_type = "application"
  security_groups = ["sg-016dc4cd70ac79a0e"]
  subnets = ["subnet-0c2e92c1b7b782543", "subnet-00c68b4e0ee285460", "subnet-0c47ef6fc81ba084a"]
}


resource "aws_lb_target_group" "wishbone_lb_target_group_3" {
  name     = "wishbone-lb-target-group-3"
  port     = 8501
  protocol = "HTTP"
  vpc_id   = "vpc-01b7a51a09d27de04"
  target_type = "ip"
  
}

resource "aws_lb_listener" "wishbone-dashboard-lb-listener-2" {
  load_balancer_arn = aws_lb.wishbone-dashboard-lb-2.arn
  port = 8501
  protocol = "HTTP"
  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.wishbone_lb_target_group_3.arn
  }
}

resource "aws_ecs_service" "wishbone-dashboard-service" {
  name = "wishbone-dashboard-service"
  cluster = aws_ecs_cluster.c20-wishbone-ecs.id
  task_definition = aws_ecs_task_definition.wishbone-dashboard-task-definition.arn
  desired_count = 1
  load_balancer {
    target_group_arn = aws_lb_target_group.wishbone_lb_target_group_3.arn
    container_name = "wishbone-dashboard-task"
    container_port = 8501
  }
  network_configuration {
    subnets = ["subnet-0c2e92c1b7b782543", "subnet-00c68b4e0ee285460", "subnet-0c47ef6fc81ba084a"]
    security_groups = ["sg-016dc4cd70ac79a0e"]
  }
}
