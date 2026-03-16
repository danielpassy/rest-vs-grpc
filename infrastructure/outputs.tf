output "fastapi_alb_dns" {
  value = aws_lb.fastapi_public.dns_name
}

output "go_server_internal_alb_dns" {
  value = aws_lb.go_server_internal.dns_name
}

output "go_server_nlb_dns" {
  value = aws_lb.go_server_grpc.dns_name
}
