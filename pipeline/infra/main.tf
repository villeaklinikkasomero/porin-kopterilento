# Porin kopterilento – graphics pipeline on AWS
#   S3 bucket (photos, data bundle, queue, results) · ECR repository (porikit image)
#   AWS Batch on GPU Spot instances that scale to zero · nightly schedule · GitHub Actions role (OIDC)
# Usage: terraform init && terraform apply   (see pipeline/README.md)

terraform {
  required_version = ">= 1.6"
  required_providers {
    aws    = { source = "hashicorp/aws", version = ">= 5.60" }
    random = { source = "hashicorp/random", version = ">= 3.6" }
  }
}

provider "aws" {
  region = var.region
  default_tags { tags = { project = "porin-kopterilento" } }
}

data "aws_caller_identity" "me" {}
data "aws_vpc" "default" { default = true }
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "random_id" "suffix" { byte_length = 3 }

# ------------------------------------------------------------------ storage
resource "aws_s3_bucket" "data" {
  bucket = "pori-kopteri-${random_id.suffix.hex}"
}
resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}
resource "aws_s3_bucket_lifecycle_configuration" "data" {
  bucket = aws_s3_bucket.data.id
  rule {
    id     = "old-results"
    status = "Enabled"
    filter { prefix = "results/" }
    expiration { days = var.results_days }
  }
}

resource "aws_ecr_repository" "porikit" {
  name                 = "porikit"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
}
resource "aws_ecr_lifecycle_policy" "porikit" {
  repository = aws_ecr_repository.porikit.name
  policy = jsonencode({ rules = [{ rulePriority = 1, description = "keep 5 images", selection = { tagStatus = "any", countType = "imageCountMoreThan", countNumber = 5 }, action = { type = "expire" } }] })
}

# ------------------------------------------------------------------ IAM
data "aws_iam_policy_document" "ec2_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}
resource "aws_iam_role" "instance" {
  name               = "porikit-batch-instance"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume.json
}
resource "aws_iam_role_policy_attachment" "instance_ecs" {
  role       = aws_iam_role.instance.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}
resource "aws_iam_instance_profile" "instance" {
  name = "porikit-batch-instance"
  role = aws_iam_role.instance.name
}

data "aws_iam_policy_document" "ecs_tasks_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}
data "aws_iam_policy_document" "bucket_rw" {
  statement {
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.data.arn]
  }
  statement {
    actions   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = ["${aws_s3_bucket.data.arn}/*"]
  }
}
resource "aws_iam_role" "job" {
  name               = "porikit-job"
  assume_role_policy = data.aws_iam_policy_document.ecs_tasks_assume.json
}
resource "aws_iam_role_policy" "job_bucket" {
  role   = aws_iam_role.job.id
  policy = data.aws_iam_policy_document.bucket_rw.json
}

# ------------------------------------------------------------------ Batch: GPU Spot, scales to zero
resource "aws_security_group" "batch" {
  name   = "porikit-batch"
  vpc_id = data.aws_vpc.default.id
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_batch_compute_environment" "gpu" {
  compute_environment_name_prefix = "porikit-gpu-"
  type                            = "MANAGED"
  compute_resources {
    type                = var.use_spot ? "SPOT" : "EC2"
    allocation_strategy = var.use_spot ? "SPOT_PRICE_CAPACITY_OPTIMIZED" : "BEST_FIT_PROGRESSIVE"
    instance_type       = var.instance_types
    min_vcpus           = 0
    max_vcpus           = var.max_vcpus
    instance_role       = aws_iam_instance_profile.instance.arn
    subnets             = data.aws_subnets.default.ids
    security_group_ids  = [aws_security_group.batch.id]
    ec2_configuration { image_type = "ECS_AL2023_NVIDIA" }
  }
  lifecycle { create_before_destroy = true }
}

resource "aws_batch_job_queue" "gpu" {
  name     = "porikit-gpu"
  state    = "ENABLED"
  priority = 1
  compute_environment_order {
    order               = 1
    compute_environment = aws_batch_compute_environment.gpu.arn
  }
}

locals {
  image = "${aws_ecr_repository.porikit.repository_url}:latest"
  env = [
    { name = "PORI_BUCKET", value = aws_s3_bucket.data.bucket },
    { name = "PORI_GPU", value = "1" },
    { name = "AWS_DEFAULT_REGION", value = var.region },
  ]
}

resource "aws_batch_job_definition" "night" {
  name                  = "porikit-night"
  type                  = "container"
  platform_capabilities = ["EC2"]
  timeout { attempt_duration_seconds = var.max_hours * 3600 }
  retry_strategy {
    attempts = 3
    evaluate_on_exit {
      on_status_reason = "Host EC2*"   # Spot reclaimed the machine: try again
      action           = "RETRY"
    }
    evaluate_on_exit {
      on_reason = "*"
      action    = "EXIT"
    }
  }
  container_properties = jsonencode({
    image   = local.image
    command = ["porikit", "night"]
    jobRoleArn = aws_iam_role.job.arn
    resourceRequirements = [
      { type = "VCPU", value = "4" },
      { type = "MEMORY", value = "14000" },
      { type = "GPU", value = "1" },
    ]
    environment = local.env
    linuxParameters = { sharedMemorySize = 2048 }
  })
}

# same image, any command (porikit bake ..., porikit auto ...): submitted from GitHub Actions or the CLI
resource "aws_batch_job_definition" "task" {
  name                  = "porikit-task"
  type                  = "container"
  platform_capabilities = ["EC2"]
  timeout { attempt_duration_seconds = var.max_hours * 3600 }
  retry_strategy { attempts = 2 }
  container_properties = jsonencode({
    image   = local.image
    command = ["porikit", "layout"]
    jobRoleArn = aws_iam_role.job.arn
    resourceRequirements = [
      { type = "VCPU", value = "4" },
      { type = "MEMORY", value = "14000" },
      { type = "GPU", value = "1" },
    ]
    environment = local.env
    linuxParameters = { sharedMemorySize = 2048 }
  })
}

# ------------------------------------------------------------------ nightly run of the queue
data "aws_iam_policy_document" "scheduler_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }
  }
}
resource "aws_iam_role" "scheduler" {
  name               = "porikit-scheduler"
  assume_role_policy = data.aws_iam_policy_document.scheduler_assume.json
}
resource "aws_iam_role_policy" "scheduler" {
  role = aws_iam_role.scheduler.id
  policy = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["batch:SubmitJob"], Resource = [
    aws_batch_job_queue.gpu.arn, "arn:aws:batch:${var.region}:${data.aws_caller_identity.me.account_id}:job-definition/porikit-night*"] }] })
}
resource "aws_scheduler_schedule" "night" {
  name                         = "porikit-night"
  state                        = var.night_enabled ? "ENABLED" : "DISABLED"
  schedule_expression          = var.night_cron
  schedule_expression_timezone = "Europe/Helsinki"
  flexible_time_window { mode = "OFF" }
  target {
    arn      = "arn:aws:scheduler:::aws-sdk:batch:submitJob"
    role_arn = aws_iam_role.scheduler.arn
    input = jsonencode({ JobName = "porikit-night", JobQueue = aws_batch_job_queue.gpu.arn, JobDefinition = aws_batch_job_definition.night.arn })
  }
}

# ------------------------------------------------------------------ GitHub Actions (OIDC, no stored keys)
resource "aws_iam_openid_connect_provider" "github" {
  count           = var.create_github_oidc ? 1 : 0
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}
locals {
  oidc_arn = var.create_github_oidc ? aws_iam_openid_connect_provider.github[0].arn : "arn:aws:iam::${data.aws_caller_identity.me.account_id}:oidc-provider/token.actions.githubusercontent.com"
}
data "aws_iam_policy_document" "github_assume" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [local.oidc_arn]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_repo}:*"]
    }
  }
}
resource "aws_iam_role" "github" {
  name               = "porikit-github"
  assume_role_policy = data.aws_iam_policy_document.github_assume.json
}
resource "aws_iam_role_policy" "github" {
  role = aws_iam_role.github.id
  policy = jsonencode({ Version = "2012-10-17", Statement = [
    { Effect = "Allow", Action = ["ecr:GetAuthorizationToken"], Resource = "*" },
    { Effect = "Allow", Action = ["ecr:BatchCheckLayerAvailability", "ecr:CompleteLayerUpload", "ecr:InitiateLayerUpload", "ecr:PutImage", "ecr:UploadLayerPart", "ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"], Resource = aws_ecr_repository.porikit.arn },
    { Effect = "Allow", Action = ["batch:SubmitJob", "batch:DescribeJobs", "batch:ListJobs"], Resource = "*" },
    { Effect = "Allow", Action = ["s3:ListBucket"], Resource = aws_s3_bucket.data.arn },
    { Effect = "Allow", Action = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"], Resource = "${aws_s3_bucket.data.arn}/*" },
  ] })
}
