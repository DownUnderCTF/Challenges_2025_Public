output "bucket_policy" {
  description = "Resource policy for the S3 bucket"
  value       = data.aws_iam_policy_document.allow_access_by_ua.json
}