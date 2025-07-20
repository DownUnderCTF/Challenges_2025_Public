variable "challenge_name" {
    description = "The name of the DuCTF challenge."
    type        = string
}
variable "aws_region" {
    description = "The AWS region to deploy to."
    type        = string
}
variable "unique_id" {
    description = "A suffix for resources requiring unique naming."
    type        = string
}
variable "flag" {
    description = "The flag for this challenge."
    type        = string
}
variable "presigned_url_file" {
    description = "The file with the presigned URL to share with challengers."
    type        = string
}
variable "url_expires_in_secs" {
    description = "How long after provisioning the presigned URL is valid (seconds)"
    type        = number
}