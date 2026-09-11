variable "namespace" {
    type        = string
    description = "Kubernetes namespace to deploy the application into."
    default     = "homework"
}

variable "environment" {
    type        = string
    description = "Value passed to the application's ENVIRONMENT variable."
    default     = "prod"
}

variable "image_repository" {
    type        = string
    description = "Container image repository for the application."
    default     = "myapp"
}

variable "image_tag" {
    type        = string
    description = "Container image tag to deploy."
    default     = "latest"
}

variable "release_name" {
    type        = string
    description = "Helm release name."
    default     = "homework"
}

variable "kube_config_path" {
    type        = string
    description = "Path to the kubeconfig file used by the providers."
    default     = "~/.kube/config"
}