variable "region" {
  description = "AWS region (Stockholm keeps the photos in the EU and is closest to Pori)"
  type        = string
  default     = "eu-north-1"
}
variable "instance_types" {
  description = "GPU instance types Batch may use (one GPU each). Check availability in the region."
  type        = list(string)
  default     = ["g5.xlarge", "g4dn.xlarge", "g6.xlarge"]
}
variable "max_vcpus" {
  description = "Upper limit for the whole compute environment: 16 = at most four 4-vCPU GPU machines at once"
  type        = number
  default     = 16
}
variable "use_spot" {
  description = "Spot instances: much cheaper, may be interrupted (jobs are retried)"
  type        = bool
  default     = true
}
variable "max_hours" {
  description = "Hard time limit per job"
  type        = number
  default     = 8
}
variable "night_enabled" {
  description = "Run the queue every night"
  type        = bool
  default     = true
}
variable "night_cron" {
  description = "When the night run starts (Europe/Helsinki)"
  type        = string
  default     = "cron(0 22 * * ? *)"
}
variable "results_days" {
  description = "How long night results are kept in S3"
  type        = number
  default     = 60
}
variable "github_repo" {
  description = "owner/repo allowed to use the GitHub Actions role"
  type        = string
  default     = "villeaklinikkasomero/porin-kopterilento"
}
variable "create_github_oidc" {
  description = "Create the GitHub OIDC provider (set false if the account already has one)"
  type        = bool
  default     = true
}
