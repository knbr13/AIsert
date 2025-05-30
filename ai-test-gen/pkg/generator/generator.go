package generator

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
)

const systemPrompt = `You are an expert Go developer. Generate comprehensive unit tests for the provided Go function using the standard testing package. Your output MUST be valid, compilable, idiomatic Go code, free of syntax errors, and ready to use. Do NOT output broken, incomplete, or partial tests. Include:
1. Table-driven tests with subtests
2. Edge cases and boundary conditions
3. Descriptive test names (TestFunctionNameCase)
4. Error cases where applicable
5. Only output valid Go test code with package declaration
6. Include benchmark stubs (BenchmarkXxx) where applicable
7. Prefer table-driven tests
8. Cover zero-value inputs
9. Test error returns
10. Make sure you are importing just the packages you are using
11. Do not output any explanations, only the code block.`

// Gemini API request structures
type (
	GeminiRequest struct {
		Contents []Content `json:"contents"`
	}

	Content struct {
		Parts []Part `json:"parts"`
	}

	Part struct {
		Text string `json:"text"`
	}

	GeminiResponse struct {
		Candidates []Candidate `json:"candidates"`
	}

	Candidate struct {
		Content Content `json:"content"`
	}
)

func GenerateUnitTests(code, apiKey string) (string, error) {
	fullPrompt := systemPrompt + "\n\nGenerate tests for this Go function:\n\n" + code

	// Create Gemini API request
	reqBody := GeminiRequest{
		Contents: []Content{
			{
				Parts: []Part{
					{Text: fullPrompt},
				},
			},
		},
	}

	jsonBody, err := json.Marshal(reqBody)
	if err != nil {
		return "", fmt.Errorf("error marshaling request: %w", err)
	}

	url := fmt.Sprintf("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=%s", apiKey)
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonBody))
	if err != nil {
		return "", fmt.Errorf("error creating request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("API request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("API returned %d: %s", resp.StatusCode, string(body))
	}

	var geminiResp GeminiResponse
	if err := json.NewDecoder(resp.Body).Decode(&geminiResp); err != nil {
		return "", fmt.Errorf("error decoding response: %w", err)
	}

	if len(geminiResp.Candidates) == 0 || len(geminiResp.Candidates[0].Content.Parts) == 0 {
		return "", fmt.Errorf("no content in API response")
	}

	return extractCodeBlock(geminiResp.Candidates[0].Content.Parts[0].Text), nil
}

func extractCodeBlock(content string) string {
	start := strings.Index(content, "```go")
	if start == -1 {
		start = strings.Index(content, "```")
		if start == -1 {
			return content
		}
		start += 3
	} else {
		start += 5
	}

	end := strings.LastIndex(content, "```")
	if end <= start {
		return content
	}

	return content[start:end]
}
