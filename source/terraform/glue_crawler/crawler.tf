provider "aws" {
  region = "eu-west-2"
}

resource "aws_glue_catalog_database" "wishbone-glue-db" {
  name = "wishbone-glue-db"
}

resource "aws_iam_role" "wishbone-crawler-role" {
  name = "wishbone-crawler-role"
  assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Action = "sts:AssumeRole"
                Effect = "Allow"
                Principal = {
                    Service = "glue.amazonaws.com"
                }
            },
        ]
    })
}

resource "aws_iam_policy" "wishbone-crawler-s3-access" {
  name        = "test_policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Effect   = "Allow"
        Resource = ["arn:aws:s3:::c20-wishbone-s3","arn:aws:s3:::c20-wishbone-s3/*"]
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "wishbone-crawler-attach-s3-permission" {
  role = aws_iam_role.wishbone-crawler-role.name
  policy_arn = aws_iam_policy.wishbone-crawler-s3-access.arn
}

resource "aws_iam_role_policy_attachment" "wishbone-crawler-attach-glue-service-role" {
  role = aws_iam_role.wishbone-crawler-role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_glue_crawler" "wishbone-crawler" {
  name = "c20-wishbone-crawler"
  role = aws_iam_role.wishbone-crawler-role.arn
  database_name = aws_glue_catalog_database.wishbone-glue-db.name
  s3_target {
    path = "s3://c20-wishbone-s3"
  }
}