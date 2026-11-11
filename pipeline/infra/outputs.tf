output "bucket" { value = aws_s3_bucket.data.bucket }
output "ecr_repository" { value = aws_ecr_repository.porikit.repository_url }
output "job_queue" { value = aws_batch_job_queue.gpu.name }
output "job_definition_task" { value = aws_batch_job_definition.task.name }
output "github_role_arn" { value = aws_iam_role.github.arn }
