provider "aws" {
  region = "eu-west-2"
}

resource "aws_iam_role" "wishbone-price-history-lambda-role" {
  name = "wishbone-price-history-lambda-role"
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

resource "aws_iam_policy" "wishbone-price-history-lambda-s3-access" {
  name        = "wishbone-price-history-lambda-s3-access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Effect   = "Allow"
        Resource = ["arn:aws:s3:::c20-wishbone-s3","arn:aws:s3:::c20-wishbone-s3/*"]
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "wishbone-crawler-attach-s3-permission" {
  role = aws_iam_role.wishbone-price-history-lambda-role.name
  policy_arn = aws_iam_policy.wishbone-price-history-lambda-s3-access.arn
}

resource "aws_iam_role_policy_attachment" "price-history-lambda-provide-rds-access" {
  role = aws_iam_role.wishbone-price-history-lambda-role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonRDSFullAccess"
}

resource "aws_iam_role_policy_attachment" "price-history-lambda-provide-execution-role" {
  role = aws_iam_role.wishbone-price-history-lambda-role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "wishbone-price-history-lambda-athena-access" {
  role = aws_iam_role.wishbone-price-history-lambda-role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonAthenaFullAccess"
}

resource "aws_lambda_function" "wishbone-price-history-lambda" {
    function_name = "wishbone-price-history-lambda"
    role = aws_iam_role.wishbone-price-history-lambda-role.arn
    package_type = "Image"
    image_uri = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c20-wishbone-price-history-ecr:latest"
    architectures = ["x86_64"]
    environment {
    variables = {
      ACCESS_KEY_ID = var.AWS_ACCESS_KEY
      AWS_SECRET_ACCESS_KEY_ID = var.AWS_SECRET_ACCESS_KEY
      BUCKET_NAME = var.BUCKET_NAME
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