terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~> 2.28.1"
    }
  }
  required_version = ">= 0.13"
}
