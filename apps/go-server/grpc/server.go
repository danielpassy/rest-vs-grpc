// Package grpc implements the GibberishService gRPC server.
package grpc

import (
	"context"

	pb "github.com/danielpassy/rest-vs-grpc/apps/go-server/gen/gibberish/v1"
	"github.com/danielpassy/rest-vs-grpc/apps/go-server/processor"
	"github.com/danielpassy/rest-vs-grpc/apps/go-server/schema"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

// Server implements GibberishServiceServer.
type Server struct {
	pb.UnimplementedGibberishServiceServer
}

// Process maps the incoming proto payload to schema types, runs the processor, and returns the result.
func (s *Server) Process(_ context.Context, req *pb.GibberishPayload) (*pb.ProcessResult, error) {
	items := make([]schema.Item, len(req.Items))
	for i, it := range req.Items {
		items[i] = schema.Item{
			ID:       it.Id,
			Label:    it.Label,
			Value:    it.Value,
			Tags:     it.Tags,
			Metadata: it.Metadata,
		}
	}

	payload := schema.GibberishPayload{
		RequestID: req.RequestId,
		Timestamp: req.Timestamp,
		Source:    req.Source,
		Items:     items,
		Checksum:  req.Checksum,
	}

	result, err := processor.Process(payload)
	if err != nil {
		return nil, status.Errorf(codes.InvalidArgument, "%s", err.Error())
	}

	return &pb.ProcessResult{
		RequestId:   result.RequestID,
		ProcessedAt: result.ProcessedAt,
		ItemCount:   result.ItemCount,
		ValueSum:    result.ValueSum,
		DominantTag: result.DominantTag,
		Status:      result.Status,
	}, nil
}
