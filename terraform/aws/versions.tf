terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
    helm = {
      source = "hashicorp/helm"
      version = "~> 2.1.2"
    }
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "~> 2.2.0"
    }
    template = {
      source = "hashicorp/template"
      version = "~> 2.1"
    }
  }
  required_version = ">= 0.13"
}

variable "eks_kubernetes_version" {
  default = "1.20"
}
