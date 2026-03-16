// Package processor contains the pure business logic for validating and processing a GibberishPayload.
package processor

import (
	"fmt"
	"sort"
	"time"

	"github.com/danielpassy/rest-vs-grpc/apps/go-server/schema"
)

// Process validates the payload checksum, aggregates item values, and identifies the dominant tag.
//
// Checksum is defined as the sum of the first byte (uint8) of each item ID cast to int32.
// If the computed checksum does not match payload.Checksum an error is returned.
// dominant_tag is the most-frequent tag across all items; ties are broken alphabetically.
func Process(payload schema.GibberishPayload) (schema.ProcessResult, error) {
	// Validate checksum: sum of first byte of each item ID.
	var computed int32
	for _, item := range payload.Items {
		if len(item.ID) > 0 {
			computed += int32(uint8(item.ID[0]))
		}
	}
	if computed != payload.Checksum {
		return schema.ProcessResult{}, fmt.Errorf("checksum mismatch: expected %d, got %d", payload.Checksum, computed)
	}

	// Sum all item values.
	var valueSum float32
	for _, item := range payload.Items {
		valueSum += item.Value
	}

	// Build tag frequency map.
	freq := make(map[string]int)
	for _, item := range payload.Items {
		for _, tag := range item.Tags {
			freq[tag]++
		}
	}

	// Find the dominant tag: highest frequency, alphabetically first on tie.
	dominantTag := ""
	maxCount := 0
	// Collect and sort tag keys so tie-breaking is deterministic.
	tags := make([]string, 0, len(freq))
	for tag := range freq {
		tags = append(tags, tag)
	}
	sort.Strings(tags)
	for _, tag := range tags {
		count := freq[tag]
		if count > maxCount {
			maxCount = count
			dominantTag = tag
		}
	}

	return schema.ProcessResult{
		RequestID:   payload.RequestID,
		ProcessedAt: time.Now().UTC().Format(time.RFC3339),
		ItemCount:   int32(len(payload.Items)),
		ValueSum:    valueSum,
		DominantTag: dominantTag,
		Status:      "ok",
	}, nil
}
