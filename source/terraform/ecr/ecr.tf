# create one ECR for each of the docker images

provider "aws" {
  region = "eu-west-2"
}

#create ECR to store the ETL Docker Image
resource "aws_ecr_repository" "c20-wishbone-etl-ecr" {
  name = "c20-wishbone-etl-ecr"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = "dev"
    Project = "wishbone"
  }
}

# policy so that only one image is in the ECR at a time
resource "aws_ecr_lifecycle_policy" "c20-wishbone-etl-lifecycle-policy" {
  repository = aws_ecr_repository.c20-wishbone-etl-ecr.name

  policy = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Keep only latest image",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": 1
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}

#create ECR to store the Dashboard Docker Image
resource "aws_ecr_repository" "c20-wishbone-dashboard-ecr" {
  name = "c20-wishbone-dashboard-ecr"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = "dev"
    Project = "wishbone"
  }
}

# policy so that only one image is in the ECR at a time
resource "aws_ecr_lifecycle_policy" "c20-wishbone-dashboard-lifecycle-policy" {
  repository = aws_ecr_repository.c20-wishbone-dashboard-ecr.name

  policy = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Keep only latest image",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": 1
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}

#create ECR to store the Email Subscription Docker Image
resource "aws_ecr_repository" "c20-wishbone-email-subscription-ecr" {
  name = "c20-wishbone-email-subscription-ecr"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = "dev"
    Project = "wishbone"
  }
}

# policy so that only one image is in the ECR at a time
resource "aws_ecr_lifecycle_policy" "c20-wishbone-email-subscription-policy" {
  repository = aws_ecr_repository.c20-wishbone-email-subscription-ecr.name

  policy = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Keep only latest image",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": 1
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}

resource "aws_ecr_repository" "c20-wishbone-price-history-ecr" {
  name = "c20-wishbone-price-history-ecr"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = "dev"
    Project = "wishbone"
  }
}

# policy so that only one image is in the ECR at a time
resource "aws_ecr_lifecycle_policy" "c20-wishbone-price-history-lifecycle-policy" {
  repository = aws_ecr_repository.c20-wishbone-price-history-ecr.name

  policy = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Keep only latest image",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": 1
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}

resource "aws_ecr_repository" "c20-wishbone-tracking-tl-ecr" {
  name = "c20-wishbone-tracking-tl-ecr"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = "dev"
    Project = "wishbone"
  }
}

# policy so that only one image is in the ECR at a time
resource "aws_ecr_lifecycle_policy" "c20-wishbone-tracking-tl-lifecycle-policy" {
  repository = aws_ecr_repository.c20-wishbone-tracking-tl-ecr.name

  policy = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Keep only latest image",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": 1
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}

#create ECR to store the email verification Docker Image
resource "aws_ecr_repository" "c20-wishbone-verification-ecr" {
  name = "c20-wishbone-verification-ecr"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = "dev"
    Project = "wishbone"
  }
}

# policy so that only one image is in the ECR at a time
resource "aws_ecr_lifecycle_policy" "c20-wishbone-verification-lifecycle-policy" {
  repository = aws_ecr_repository.c20-wishbone-verification-ecr.name

  policy = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Keep only latest image",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": 1
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}


