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
      name = "wishbone-etl-task"
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
    }
  ])
  cpu = 512
  memory = 1024
  task_role_arn = data.aws_iam_role.ecs_task_execution_role.arn
  execution_role_arn = data.aws_iam_role.ecs_task_execution_role.arn
}
