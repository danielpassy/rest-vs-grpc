package rest

import (
	"encoding/json"
	"net/http"

	"github.com/danielpassy/rest-vs-grpc/apps/go-server/config"
	"github.com/danielpassy/rest-vs-grpc/apps/go-server/processor"
	"github.com/danielpassy/rest-vs-grpc/apps/go-server/schema"
)

// NewHandler returns an http.Handler with all REST routes registered.
func NewHandler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("POST /process", handleProcess)
	return mux
}

func handleProcess(w http.ResponseWriter, r *http.Request) {
	if r.Header.Get(config.AuthHeader) != config.AuthBearerPrefix+config.HardcodedToken {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusUnauthorized)
		json.NewEncoder(w).Encode(map[string]string{"error": "invalid token"})
		return
	}

	var payload schema.GibberishPayload

	dec := json.NewDecoder(r.Body)
	dec.DisallowUnknownFields()

	if err := dec.Decode(&payload); err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	result, err := processor.Process(payload)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(result)
}
