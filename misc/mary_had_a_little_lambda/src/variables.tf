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