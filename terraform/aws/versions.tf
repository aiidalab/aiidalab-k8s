terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
    helm = {
      source = "hashicorp/helm"
      version = "~> 2.0"
    }
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "~> 1.11.1"
    }
    template = {
      source = "hashicorp/template"
      version = "~> 2.1"
    }
  }
  required_version = ">= 0.13"
}
