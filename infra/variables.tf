variable "aws_region" {
  description = "AWS region. The account is fixed to eu-north-1."
  type        = string
  default     = "eu-north-1"
}

variable "project_name" {
  description = "Name prefix and value of the Project tag."
  type        = string
  default     = "job-tracker"
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
  default     = "t3.medium"
}

variable "root_volume_size" {
  description = "Root volume size in GB."
  type        = number
  default     = 30
}

variable "public_key_path" {
  description = "Path to the PUBLIC ssh key file."
  type        = string
  default     = "C:/Users/hp/.ssh/job-tracker-key.pub"
}

variable "ssh_allowed_cidr" {
  description = "CIDR allowed to reach port 22. Login is key-only."
  type        = string
  default     = "0.0.0.0/0"
}
