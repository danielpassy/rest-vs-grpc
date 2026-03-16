package processor

import (
	"strings"
	"testing"

	"github.com/danielpassy/rest-vs-grpc/apps/go-server/schema"
)

// makePayload builds a GibberishPayload with a correctly computed checksum for the given items.
func makePayload(items []schema.Item) schema.GibberishPayload {
	var checksum int32
	for _, item := range items {
		if len(item.ID) > 0 {
			checksum += int32(uint8(item.ID[0]))
		}
	}
	return schema.GibberishPayload{
		RequestID: "req-1",
		Timestamp: "2026-01-01T00:00:00Z",
		Source:    "test",
		Items:     items,
		Checksum:  checksum,
	}
}

func TestProcess(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name        string
		payload     schema.GibberishPayload
		wantErr     bool
		errContains string
		wantCount   int32
		wantSum     float32
		wantTag     string
		wantStatus  string
	}{
		{
			name: "valid payload returns correct result",
			payload: makePayload([]schema.Item{
				{ID: "a1", Label: "first", Value: 1.5, Tags: []string{"foo", "bar", "foo"}},
				{ID: "b2", Label: "second", Value: 2.5, Tags: []string{"bar", "baz"}},
			}),
			wantErr:    false,
			wantCount:  2,
			wantSum:    4.0,
			wantTag:    "bar", // foo=2, bar=2, baz=1 — tie between foo and bar; "bar" < "foo" alphabetically
			wantStatus: "ok",
		},
		{
			name: "dominant tag tie broken alphabetically",
			payload: makePayload([]schema.Item{
				{ID: "c3", Label: "third", Value: 0, Tags: []string{"zebra", "apple"}},
				{ID: "d4", Label: "fourth", Value: 0, Tags: []string{"zebra", "apple"}},
			}),
			wantErr:    false,
			wantCount:  2,
			wantSum:    0,
			wantTag:    "apple", // both appear twice; "apple" < "zebra"
			wantStatus: "ok",
		},
		{
			name: "checksum mismatch returns error",
			payload: schema.GibberishPayload{
				RequestID: "req-bad",
				Items: []schema.Item{
					{ID: "e5", Value: 1.0, Tags: []string{"x"}},
				},
				Checksum: 0, // deliberately wrong
			},
			wantErr:     true,
			errContains: "checksum mismatch",
		},
		{
			name:       "empty tags yields empty dominant_tag",
			payload:    makePayload([]schema.Item{{ID: "f6", Value: 3.0, Tags: nil}}),
			wantErr:    false,
			wantCount:  1,
			wantSum:    3.0,
			wantTag:    "",
			wantStatus: "ok",
		},
		{
			name:       "empty items list",
			payload:    makePayload([]schema.Item{}),
			wantErr:    false,
			wantCount:  0,
			wantSum:    0,
			wantTag:    "",
			wantStatus: "ok",
		},
	}

	for _, tc := range tests {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			result, err := Process(tc.payload)

			if tc.wantErr {
				if err == nil {
					t.Fatalf("expected error but got nil")
				}
				if tc.errContains != "" && !strings.Contains(err.Error(), tc.errContains) {
					t.Errorf("error %q does not contain %q", err.Error(), tc.errContains)
				}
				return
			}

			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if result.ItemCount != tc.wantCount {
				t.Errorf("ItemCount: got %d, want %d", result.ItemCount, tc.wantCount)
			}
			if result.ValueSum != tc.wantSum {
				t.Errorf("ValueSum: got %v, want %v", result.ValueSum, tc.wantSum)
			}
			if result.DominantTag != tc.wantTag {
				t.Errorf("DominantTag: got %q, want %q", result.DominantTag, tc.wantTag)
			}
			if result.Status != tc.wantStatus {
				t.Errorf("Status: got %q, want %q", result.Status, tc.wantStatus)
			}
			if result.RequestID != tc.payload.RequestID {
				t.Errorf("RequestID: got %q, want %q", result.RequestID, tc.payload.RequestID)
			}
			if result.ProcessedAt == "" {
				t.Error("ProcessedAt should not be empty")
			}
		})
	}
}
