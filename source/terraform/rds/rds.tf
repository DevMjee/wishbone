provider "aws" {
  region = "eu-west-2"
}

#security group for the database
resource "aws_security_group" "c20-wishbone-sg" {
  name = "c20-wishbone-sg"
  description = "security group for games database"
  vpc_id = var.vpc_id

}

resource "aws_security_group_rule" "allow_postgres_ingress_rule" {
    security_group_id = aws_security_group.c20-wishbone-sg.id
    type              = "ingress"
    from_port         = 5432
    protocol          = "tcp"
    to_port           = 5432
    cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "allow_http_egress_rule" {
    security_group_id = aws_security_group.c20-wishbone-sg.id
    type              = "egress"
    from_port         = 80
    protocol          = -1
    to_port           = 80
    cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "allow_http_ingress_rule" {
    security_group_id = aws_security_group.c20-wishbone-sg.id
    type              = "ingress"
    from_port         = 80
    protocol          = -1
    to_port           = 80
    cidr_blocks       = ["0.0.0.0/0"]
}



resource "aws_db_subnet_group" "c20-wishbone-subnet-group" {
  name = "c20-wishbone-subnet-group"
  subnet_ids = ["subnet-0c47ef6fc81ba084a", "subnet-00c68b4e0ee285460", "subnet-0c2e92c1b7b782543"]
}

resource "aws_db_instance" "c20-wishbone-db" {
  identifier = "c20-wishbone-db"
  allocated_storage = 10
  engine = "Postgres"
  instance_class = "db.t3.micro"
  skip_final_snapshot = true
  vpc_security_group_ids = [aws_security_group.c20-wishbone-sg.id]
  db_subnet_group_name = "c20-wishbone-subnet-group"
  publicly_accessible = true
  username = var.username
  password = var.password
}