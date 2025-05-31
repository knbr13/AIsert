package generator

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

// Request and response structures for Gemini API
type geminiRequest struct {
	Contents []content `json:"contents"`
}

type content struct {
	Parts []part `json:"parts"`
}

type part struct {
	Text string `json:"text"`
}

type geminiResponse struct {
	Candidates []candidate `json:"candidates"`
}

type candidate struct {
	Content content `json:"content"`
}

// GenerateDocumentation generates documentation for Go code using Gemini API
func GenerateDocumentation(code, apiKey string) (string, error) {
	// Construct the prompt
	prompt := fmt.Sprintf(`You are an expert Go documentation generator. Generate comprehensive, professional documentation for the following Go code. 
Include:
1. Package overview
2. Function descriptions with parameters and return values
3. Type definitions and their purposes
4. Usage examples where appropriate
5. Any important notes about the code's behavior

Format the output in Markdown with proper headings and code blocks.

Go code:
%s`, code)

	// Create the request payload
	reqBody := geminiRequest{
		Contents: []content{
			{
				Parts: []part{
					{Text: prompt},
				},
			},
		},
	}

	// Marshal to JSON
	jsonBody, err := json.Marshal(reqBody)
	if err != nil {
		return "", fmt.Errorf("error marshaling request: %v", err)
	}

	// Create HTTP request
	url := fmt.Sprintf("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=%s", apiKey)
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonBody))
	if err != nil {
		return "", fmt.Errorf("error creating request: %v", err)
	}
	req.Header.Set("Content-Type", "application/json")

	// Send request
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("error sending request: %v", err)
	}
	defer resp.Body.Close()

	// Check response status
	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("API error: %s - %s", resp.Status, string(body))
	}

	// Parse response
	var geminiResp geminiResponse
	if err := json.NewDecoder(resp.Body).Decode(&geminiResp); err != nil {
		return "", fmt.Errorf("error decoding response: %v", err)
	}

	// Extract generated text
	if len(geminiResp.Candidates) == 0 || len(geminiResp.Candidates[0].Content.Parts) == 0 {
		return "", fmt.Errorf("no content generated")
	}

	return geminiResp.Candidates[0].Content.Parts[0].Text, nil
}
