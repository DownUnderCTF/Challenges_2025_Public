provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Challenge     = var.challenge_name
    }
  }
}

data "aws_caller_identity" "current" {}
locals {
    account_id = data.aws_caller_identity.current.account_id
}

####---- Admin IAM User ----####
##
resource "aws_iam_access_key" "devopsadmin-key" {
  user    = aws_iam_user.devopsadmin.name
}

resource "aws_iam_user" "devopsadmin" {
  name = "devopsadmin"
}

resource "aws_iam_user_policy" "devopsadmin_restrict" {
  name   = "restricted"
  user   = aws_iam_user.devopsadmin.name
  policy = data.aws_iam_policy_document.devopsadmin_policy.json
}

data "aws_iam_policy_document" "devopsadmin_policy" {
  statement {
    effect    = "Allow"
    actions   = [
        "iam:ListUserPolicies",
        "iam:GetUserPolicy"
    ]
    resources = [aws_iam_user.devopsadmin.arn]
  }
  statement {
    effect    = "Allow"
    actions   = [
        "lambda:ListFunctions"
    ]
    resources = ["*"]
  }
  statement {
    effect    = "Allow"
    actions   = [
        "lambda:GetFunction",
    ]
    resources = [aws_lambda_function.main_function.arn]
  }
  statement {
    effect    = "Allow"
    actions   = [
        "iam:GetRole",
    ]
    resources = [aws_iam_role.lambda_role.arn]
  }
}

####---- Lambda Function ----####
##
resource "aws_iam_role_policy" "lambda_policy" {
    name    = "lambda_policy"
    role    = aws_iam_role.lambda_role.id
    policy  = data.aws_iam_policy_document.lambda_role_policy.json
}

resource "aws_iam_role" "lambda_role" {
    name    = "lambda_role"
    assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
}

resource "null_resource" "pip_install" {
  triggers = {
    shell_hash = "${sha256(file("lambda_src/requirements.txt"))}"
  }

  provisioner "local-exec" {
    command = "python3 -m pip install -r lambda_src/requirements.txt -t lambda_src/layer/python"
  }
}

data "archive_file" "layer" {
  type        = "zip"
  source_dir  = "lambda_src/layer"
  output_path = "lambda_src/layer.zip"
  depends_on  = [null_resource.pip_install]
}

resource "aws_lambda_layer_version" "layer" {
  layer_name          = "main-layer"
  filename            = data.archive_file.layer.output_path
  source_code_hash    = data.archive_file.layer.output_base64sha256
  compatible_runtimes = ["python3.13"]
}

data "archive_file" "lambda_code" {
  type        = "zip"
  source_file = "lambda_src/yakbase.py"
  output_path = "yakbase.zip"
}

resource "aws_lambda_function" "main_function" {
    function_name     = "yakbase"
    filename          = data.archive_file.lambda_code.output_path
    role              = aws_iam_role.lambda_role.arn
    handler           = "yakbase.lambda_handler"
    runtime           = "python3.13"
    source_code_hash  = filebase64sha256(data.archive_file.lambda_code.output_path)
    layers           = [aws_lambda_layer_version.layer.arn]
    timeout           = 30
}

data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    actions   = ["sts:AssumeRole"]
    effect      = "Allow"
    principals  {
        type        = "Service"
        identifiers = ["lambda.amazonaws.com"]
    }
    principals  {
        type        = "AWS"
        identifiers = [aws_iam_user.devopsadmin.arn]
    }
  }
}

data "aws_iam_policy_document" "lambda_role_policy" {
  statement {
    effect    = "Allow"
    actions   = [
        "logs:*",
    ]
    resources = ["*"]
  }
  statement {
    effect    = "Allow"
    actions   = [
        "ssm:GetParameter",
    ]
    resources = [
        "*"
    ]
    condition {
      test     = "StringEquals"
      variable = "aws:ResourceTag/Challenge"
      values   = [var.challenge_name]
    }
  }
}

####---- SSM Param for DB Password, and Flag ;-) ----####
##
resource "aws_ssm_parameter" "db_secret" {
  name        = "/production/database/password"
  description = "Keep this secret!"
  type        = "SecureString"
  value       = var.flag

  tags = {
    environment = "production"
  }
}