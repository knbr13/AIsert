package handlers

import (
	"encoding/json"
	"net/http"
	"strings"
)

// UserRequest represents a sample user input for validation.
type UserRequest struct {
	Name  string `json:"name"`
	Email string `json:"email"`
	Age   int    `json:"age"`
}

// GreetHandler returns a greeting message from a query param (?name=John).
func GreetHandler(w http.ResponseWriter, r *http.Request) {
	name := r.URL.Query().Get("name")
	if name == "" {
		http.Error(w, "Missing 'name' parameter", http.StatusBadRequest)
		return
	}
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Hello, " + name + "!"))
}

// EchoJSONHandler echos back the JSON body received.
func EchoJSONHandler(w http.ResponseWriter, r *http.Request) {
	var data map[string]interface{}
	err := json.NewDecoder(r.Body).Decode(&data)
	if err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(data)
}

// ValidateUserHandler validates the UserRequest JSON body.
func ValidateUserHandler(w http.ResponseWriter, r *http.Request) {
	var req UserRequest
	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	if req.Name == "" || len(req.Name) < 2 {
		http.Error(w, "Invalid name", http.StatusBadRequest)
		return
	}

	if !strings.Contains(req.Email, "@") {
		http.Error(w, "Invalid email", http.StatusBadRequest)
		return
	}

	if req.Age <= 0 {
		http.Error(w, "Invalid age", http.StatusBadRequest)
		return
	}

	w.WriteHeader(http.StatusOK)
	w.Write([]byte("User is valid"))
}

// PingHandler is a simple ping endpoint for testing.
func PingHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("pong"))
}
