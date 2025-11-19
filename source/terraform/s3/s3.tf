provider "aws" {
  region = "eu-west-2"
}

#creating the S3 bucket to store the games data
resource "aws_s3_bucket" "c20-wishbone-s3" {
  bucket = "c20-wishbone-s3"
  force_destroy = true
}

#specifies to not create a new version of the s3 every time the data is changed
resource "aws_s3_bucket_versioning" "c20-wishbone-s3-version" {
  bucket = aws_s3_bucket.c20-wishbone-s3.id
  versioning_configuration {
    status = "Disabled"
  }
}

