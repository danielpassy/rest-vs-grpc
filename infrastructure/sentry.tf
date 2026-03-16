resource "aws_ssm_parameter" "sentry_dsn" {
  name  = "/${var.project_name}/sentry_dsn"
  type  = "SecureString"
  value = var.sentry_dsn
}
