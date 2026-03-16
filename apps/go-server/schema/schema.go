// Package schema defines the shared data structures used by both REST and gRPC handlers.
package schema

// Item represents a single labelled value with optional tags and metadata.
type Item struct {
	ID       string            `json:"id"`
	Label    string            `json:"label"`
	Value    float32           `json:"value"`
	Tags     []string          `json:"tags"`
	Metadata map[string]string `json:"metadata"`
}

// GibberishPayload is the inbound request envelope.
type GibberishPayload struct {
	RequestID string  `json:"request_id"`
	Timestamp string  `json:"timestamp"`
	Source    string  `json:"source"`
	Items     []Item  `json:"items"`
	Checksum  int32   `json:"checksum"`
}

// ProcessResult is the outbound response after processing a GibberishPayload.
type ProcessResult struct {
	RequestID   string  `json:"request_id"`
	ProcessedAt string  `json:"processed_at"`
	ItemCount   int32   `json:"item_count"`
	ValueSum    float32 `json:"value_sum"`
	DominantTag string  `json:"dominant_tag"`
	Status      string  `json:"status"`
}
