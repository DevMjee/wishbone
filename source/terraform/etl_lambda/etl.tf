provider "aws" {
  region = "eu-west-2"
}

resource "aws_iam_role" "wishbone-etl-role" {
    name = "wishboone-etl-role"
    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Action = "sts:AssumeRole"
                Effect = "Allow"
                Principal = {
                    Service = "lambda.amazonaws.com"
                }
            },
        ]
    })
}

resource "aws_iam_role_policy_attachment" "etl-lambda-provide-rds-access" {
  role = aws_iam_role.wishbone-etl-role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonRDSFullAccess"
}

resource "aws_iam_role_policy_attachment" "name" {
  role = aws_iam_role.wishbone-etl-role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "wishbone-etl-lambda" {
  function_name = "wishbone-etl-lambda"
  role = aws_iam_role.wishbone-etl-role.arn
  package_type = "Image"
  image_uri = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c20-wishbone-etl-ecr:latest"
  architectures = ["x86_64"]
  environment {
    variables = {
      DB_NAME = var.DB_NAME
      PORT = var.PORT
      RDS_HOST = var.RDS_HOST
      RDS_PASSWORD = var.RDS_PASSWORD
      RDS_USERNAME = var.RDS_USERNAME
      
    }
  }
  memory_size = 1024
  timeout = 60
}