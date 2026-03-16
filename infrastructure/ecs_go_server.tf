resource "aws_ecs_cluster" "main" {
  name = var.project_name
}

resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.project_name}-ecs-task-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_ecr" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "ecs_task_execution_ssm" {
  name = "${var.project_name}-ssm-read"
  role = aws_iam_role.ecs_task_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameters",
          "ssm:GetParameter",
        ]
        Resource = "arn:aws:ssm:${var.aws_region}:*:parameter/${var.project_name}/*"
      }
    ]
  })
}

resource "aws_ecs_task_definition" "go_server" {
  family                   = "${var.project_name}-go-server"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name  = "go-server"
      image = "${var.ecr_repo_go_server}:${var.image_tag}"
      portMappings = [
        {
          containerPort = 8080
          protocol      = "tcp"
        },
        {
          containerPort = 50051
          protocol      = "tcp"
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
          awslogs-group         = "/ecs/${var.project_name}/go-server"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

resource "aws_cloudwatch_log_group" "go_server" {
  name              = "/ecs/${var.project_name}/go-server"
  retention_in_days = 7
}

resource "aws_ecs_service" "go_server" {
  name            = "${var.project_name}-go-server"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.go_server.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = [aws_subnet.private_1.id, aws_subnet.private_2.id]
    security_groups = [aws_security_group.go_server.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.go_server_rest.arn
    container_name   = "go-server"
    container_port   = 8080
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.go_server_grpc.arn
    container_name   = "go-server"
    container_port   = 50051
  }

  depends_on = [
    aws_lb_listener.go_server_rest,
    aws_lb_listener.go_server_grpc,
  ]
}

# Internal ALB for REST (port 8080)
resource "aws_lb" "go_server_internal" {
  name               = "${var.project_name}-go-internal"
  internal           = true
  load_balancer_type = "application"
  security_groups    = [aws_security_group.go_server.id]
  subnets            = [aws_subnet.private_1.id, aws_subnet.private_2.id]

  tags = {
    Name = "${var.project_name}-go-internal-alb"
  }
}

resource "aws_lb_target_group" "go_server_rest" {
  name        = "${var.project_name}-go-rest"
  port        = 8080
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

resource "aws_lb_listener" "go_server_rest" {
  load_balancer_arn = aws_lb.go_server_internal.arn
  port              = 8080
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.go_server_rest.arn
  }
}

# NLB for gRPC (port 50051)
resource "aws_lb" "go_server_grpc" {
  name               = "${var.project_name}-go-grpc"
  internal           = true
  load_balancer_type = "network"
  subnets            = [aws_subnet.private_1.id, aws_subnet.private_2.id]

  tags = {
    Name = "${var.project_name}-go-grpc-nlb"
  }
}

resource "aws_lb_target_group" "go_server_grpc" {
  name        = "${var.project_name}-go-grpc"
  port        = 50051
  protocol    = "TCP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    protocol            = "TCP"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
  }
}

resource "aws_lb_listener" "go_server_grpc" {
  load_balancer_arn = aws_lb.go_server_grpc.arn
  port              = 50051
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.go_server_grpc.arn
  }
}
