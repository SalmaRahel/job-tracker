# job-tracker infrastructure

Terraform for one EC2 instance (Ubuntu 24.04), an Elastic IP, a private encrypted S3 bucket for CVs, and an IAM role that limits the instance to that bucket. Region: eu-north-1.

## Prerequisites

- Terraform >= 1.5
- AWS credentials configured locally (`aws configure`), allowed to create EC2, S3 and IAM resources
- Public key at `C:/Users/hp/.ssh/job-tracker-key.pub` (or set `public_key_path`)

## Steps

```
cd infra
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

Show the outputs at any time:

```
terraform output
```

Use them like this:

| Output | Goes to |
| --- | --- |
| `bucket_name` | `BUCKET_NAME` in `backend/.env.prod` |
| `vite_api_url` | `VITE_API_URL` in the root `.env` |
| `cors_allowed_origins` | `CORS_ALLOWED_ORIGINS` in `backend/.env.prod` |

## SSH

```
terraform output -raw ssh_command
```

Run the printed command. The app directory on the server is `/opt/job-tracker`. Log out and back in once so the `docker` group applies. First boot installs Docker in the background; check `cloud-init status --wait` before using it.

## Destroy

```
terraform destroy
```

The bucket has `force_destroy = true`, so it is removed with its objects.

## Cost

t3.medium in eu-north-1 is roughly 0.046 USD per hour, about 33 USD per month if left running. Add roughly 2.4 USD per month for the 30 GB gp3 volume, plus a public IPv4 charge of about 0.005 USD per hour. Check current AWS prices before relying on these numbers.

## After the demo

Run `terraform destroy` and delete the IAM access key used for Terraform in the AWS console. The instance, Elastic IP and volume keep billing until destroyed.
