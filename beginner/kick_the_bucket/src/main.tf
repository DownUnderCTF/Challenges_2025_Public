provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Challenge = var.challenge_name
    }
  }
}
data "aws_caller_identity" "current_user" {}
locals {
  account_id = data.aws_caller_identity.current_user.account_id
}

resource "aws_iam_access_key" "pipeline" {
  user = aws_iam_user.pipeline.name
}

resource "aws_iam_user" "pipeline" {
  name = "pipeline"
}

resource "aws_s3_bucket" "kickme" {
  bucket = "kickme-${var.unique_id}"
}

resource "aws_s3_object" "file" {
  bucket  = aws_s3_bucket.kickme.id
  key     = "flag.txt"
  content = var.flag
}

resource "null_resource" "url" {
  triggers = {
    build_number = "${timestamp()}"
  }

  provisioner "local-exec" {
    command = "printf '%s' $(AWS_ACCESS_KEY_ID=${aws_iam_access_key.pipeline.id} AWS_SECRET_ACCESS_KEY=${aws_iam_access_key.pipeline.secret} AWS_REGION=${var.aws_region} aws s3 presign s3://${aws_s3_bucket.kickme.bucket}/${aws_s3_object.file.key} --expires-in ${var.url_expires_in_secs}) > ${var.presigned_url_file}"
  }

  depends_on = [
    aws_iam_access_key.pipeline
  ]
}

resource "aws_s3_bucket_policy" "allow_access_by_ua" {
  bucket = aws_s3_bucket.kickme.id
  policy = data.aws_iam_policy_document.allow_access_by_ua.json
}

resource "aws_s3_bucket_ownership_controls" "kickme" {
  bucket = aws_s3_bucket.kickme.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_public_access_block" "kickme" {
  bucket = aws_s3_bucket.kickme.id

  block_public_acls       = false
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_acl" "kickme" {
  depends_on = [
    aws_s3_bucket_ownership_controls.kickme,
    aws_s3_bucket_public_access_block.kickme
  ]

  bucket = aws_s3_bucket.kickme.id
  acl    = "public-read"
}

data "aws_iam_policy_document" "allow_access_by_ua" {
  statement {
    principals {
      type = "AWS"
      identifiers = [
        aws_iam_user.pipeline.arn
      ]
    }

    actions = [
      "s3:GetObject"
    ]
    effect = "Allow"

    resources = [
      aws_s3_bucket.kickme.arn,
      "${aws_s3_bucket.kickme.arn}/flag.txt"
    ]
    condition {
      test     = "StringLike"
      variable = "aws:UserAgent"
      values = [
        "aws-sdk-go*"
      ]
    }
  }
}
