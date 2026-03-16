// Package main starts both REST and gRPC servers concurrently.
package main

// import groups stdlib packages together, then third-party, then internal.
// Aliases (e.g. sentrygo, pb, appgrpc) resolve name collisions between packages.
import (
	"context"
	"log"
	"net"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	sentrygo "github.com/getsentry/sentry-go"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/status"

	"github.com/danielpassy/rest-vs-grpc/apps/go-server/config"
	pb "github.com/danielpassy/rest-vs-grpc/apps/go-server/gen/gibberish/v1" // protobuf generated code
	appgrpc "github.com/danielpassy/rest-vs-grpc/apps/go-server/grpc"
	apprest "github.com/danielpassy/rest-vs-grpc/apps/go-server/rest"
)

func main() {
	if dsn := os.Getenv("SENTRY_DSN"); dsn != "" {
		sentrygo.Init(sentrygo.ClientOptions{Dsn: dsn})
	}

	ctx, cancel := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer cancel()

	lis, err := net.Listen("tcp", config.GRPCPort)
	if err != nil {
		log.Fatalf("failed to listen on %s: %v", config.GRPCPort, err)
	}

	s := grpc.NewServer(grpc.UnaryInterceptor(authUnaryInterceptor))
	pb.RegisterGibberishServiceServer(s, &appgrpc.Server{})

	go func() {
		log.Printf("gRPC server listening on %s", config.GRPCPort)
		if err := s.Serve(lis); err != nil {
			log.Printf("gRPC server stopped: %v", err)
		}
	}()

	srv := &http.Server{Addr: config.RESTPort, Handler: apprest.NewHandler()}
	go func() {
		log.Printf("REST server listening on %s", config.RESTPort)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Printf("REST server stopped: %v", err)
		}
	}()

	<-ctx.Done()
	log.Println("shutdown signal received, stopping servers...")

	srv.Shutdown(context.Background())
	s.GracefulStop()

	log.Println("servers stopped")
}

func authUnaryInterceptor(
	ctx context.Context,
	req any,
	_ *grpc.UnaryServerInfo,
	handler grpc.UnaryHandler,
) (any, error) {
	md, ok := metadata.FromIncomingContext(ctx)
	if !ok {
		return nil, status.Error(codes.Unauthenticated, "missing metadata")
	}

	values := md.Get("authorization")
	if len(values) == 0 || values[0] != config.AuthBearerPrefix+config.HardcodedToken {
		return nil, status.Error(codes.Unauthenticated, "invalid token")
	}

	return handler(ctx, req)
}
