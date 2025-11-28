provider "aws" {
  region = "eu-west-2"
}

resource "aws_iam_role" "wishbone-verification-role" {
  name = "wishbone-verification-role"
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

resource "aws_iam_role_policy_attachment" "wishbone-verification-lambda-execution-role" {
  role = aws_iam_role.wishbone-verification-role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "wishbone-verification-lambda-rds-access" {
  role = aws_iam_role.wishbone-verification-role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonRDSFullAccess"
}

resource "aws_iam_role_policy_attachment" "wishbone-verification-lambda-ses-access" {
  role = aws_iam_role.wishbone-verification-role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSESFullAccess"
}

resource "aws_lambda_function" "wishbone-verification-lambda" {
    function_name = "wishbone-verification-lambda"
    role = aws_iam_role.wishbone-verification-role.arn
    package_type = "Image"
    image_uri = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c20-wishbone-verification-ecr:latest"
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