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

