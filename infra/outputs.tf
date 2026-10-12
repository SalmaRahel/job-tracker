output "public_ip" {
  description = "Elastic IP of the instance."
  value       = aws_eip.app.public_ip
}

output "bucket_name" {
  description = "Value for BUCKET_NAME in backend/.env.prod."
  value       = aws_s3_bucket.cv.bucket
}

output "ssh_command" {
  description = "SSH command to reach the instance."
  value       = "ssh -i ${trimsuffix(var.public_key_path, ".pub")} ubuntu@${aws_eip.app.public_ip}"
}

output "vite_api_url" {
  description = "Value for VITE_API_URL in the root .env."
  value       = "http://${aws_eip.app.public_ip}/api"
}

output "cors_allowed_origins" {
  description = "Value for CORS_ALLOWED_ORIGINS in backend/.env.prod."
  value       = "http://${aws_eip.app.public_ip}"
}
