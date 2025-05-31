package formatter

import (
	"regexp"
	"strings"
)

// FormatDocumentation formats raw documentation based on requested format
func FormatDocumentation(docs string) string {
	return cleanMarkdown(docs)
}

func cleanMarkdown(docs string) string {
	// Clean up common Gemini artifacts
	docs = strings.ReplaceAll(docs, "** ", "**")
	docs = strings.ReplaceAll(docs, " **", "**")
	docs = strings.ReplaceAll(docs, "* ", "*")
	docs = strings.ReplaceAll(docs, " *", "*")

	// Ensure proper code blocks
	docs = regexp.MustCompile("(?m)^```go$").ReplaceAllString(docs, "```go")
	docs = regexp.MustCompile("(?m)^```$").ReplaceAllString(docs, "```")

	return strings.TrimSpace(docs)
}
