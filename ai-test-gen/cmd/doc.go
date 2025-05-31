package cmd

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/knbr13/aitestgen/pkg/formatter"
	"github.com/knbr13/aitestgen/pkg/generator"
	"github.com/spf13/cobra"
)

var (
	docInputFile  string
	docOutputFile string
	docAPIKey     string
)

var docCmd = &cobra.Command{
	Use:   "doc",
	Short: "Generate documentation for Go code",
	Run: func(cmd *cobra.Command, args []string) {
		if docAPIKey == "" {
			docAPIKey = os.Getenv("API_KEY")
		}
		if docAPIKey == "" {
			fmt.Println("Missing API key")
			os.Exit(1)
		}

		content, err := os.ReadFile(docInputFile)
		if err != nil {
			fmt.Printf("Error reading file: %v\n", err)
			os.Exit(1)
		}

		docs, err := generator.GenerateDocumentation(string(content), docAPIKey)
		if err != nil {
			fmt.Printf("Error generating documentation: %v\n", err)
			os.Exit(1)
		}

		if docOutputFile == "" {
			ext := filepath.Ext(docInputFile)
			docOutputFile = strings.TrimSuffix(docInputFile, ext) + "_doc.md"
		}
		fmt.Printf("input: %q, output: %q\n", docInputFile, docOutputFile)

		docs = formatter.FormatDocumentation(docs)

		if err := os.WriteFile(docOutputFile, []byte(docs), 0644); err != nil {
			fmt.Printf("Error writing documentation: %v\n", err)
			os.Exit(1)
		}

		fmt.Printf("Documentation generated: %s\n", docOutputFile)
	},
}

func init() {
	rootCmd.AddCommand(docCmd)
	docCmd.Flags().StringVarP(&docInputFile, "file", "f", "", "Input Go file (required)")
	docCmd.Flags().StringVarP(&docOutputFile, "output", "o", "", "Output documentation file")
	docCmd.Flags().StringVarP(&docAPIKey, "key", "k", "", "Gemini API key")
	docCmd.MarkFlagRequired("file")
}
