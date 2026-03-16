resource "aws_ecs_task_definition" "fastapi_client" {
  family                   = "${var.project_name}-fastapi-client"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name  = "fastapi-client"
      image = "${var.ecr_repo_fastapi}:${var.image_tag}"
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "GO_SERVER_REST_URL"
          value = "http://${aws_lb.go_server_internal.dns_name}:8080"
        },
        {
          name  = "GO_SERVER_GRPC_HOST"
          value = aws_lb.go_server_grpc.dns_name
        },
        {
          name  = "GO_SERVER_GRPC_PORT"
          value = "50051"
        }
      ]
      secrets = [
        {
          name      = "SENTRY_DSN"
          valueFrom = aws_ssm_parameter.sentry_dsn.arn
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/${var.project_name}/fastapi-client"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

resource "aws_cloudwatch_log_group" "fastapi_client" {
  name              = "/ecs/${var.project_name}/fastapi-client"
  retention_in_days = 7
}

resource "aws_ecs_service" "fastapi_client" {
  name            = "${var.project_name}-fastapi-client"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.fastapi_client.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = [aws_subnet.private_1.id, aws_subnet.private_2.id]
    security_groups = [aws_security_group.fastapi_client.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.fastapi_public.arn
    container_name   = "fastapi-client"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.fastapi_public]
}

# Public ALB for FastAPI (port 8000)
resource "aws_lb" "fastapi_public" {
  name               = "${var.project_name}-fastapi-public"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.fastapi_client.id]
  subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]

  tags = {
    Name = "${var.project_name}-fastapi-public-alb"
  }
}

resource "aws_lb_target_group" "fastapi_public" {
  name        = "${var.project_name}-fastapi"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/health"
    protocol            = "HTTP"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
  }
}

resource "aws_lb_listener" "fastapi_public" {
  load_balancer_arn = aws_lb.fastapi_public.arn
  port              = 8000
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fastapi_public.arn
  }
}
