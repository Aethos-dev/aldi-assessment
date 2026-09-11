output "namespace" {
    description = "Namespace the application was deployed into."
    value       = kubernetes_namespace.homework.metadata[0].name
}

output "release_name" {
    description = "Name of the Helm release."
    value       = helm_release.homework.name
}

output "release_status" {
    description = "Status of the Helm release."
    value       = helm_release.homework.status
}

