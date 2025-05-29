package cmd

import (
	"fmt"
	"os"
	"strings"

	"github.com/knbr13/ait/pkg/formatter"
	"github.com/knbr13/ait/pkg/generator"
	"github.com/spf13/cobra"
)

var (
	inputFile    string
	outputFile   string
	openaiAPIKey string
)

var generateCmd = &cobra.Command{
	Use:   "generate",
	Short: "Generate unit tests",
	Run: func(cmd *cobra.Command, args []string) {
		if openaiAPIKey == "" {
			openaiAPIKey = os.Getenv("API_KEY")
		}
		if openaiAPIKey == "" {
			fmt.Println("Missing API key")
			os.Exit(1)
		}

		content, err := os.ReadFile(inputFile)
		if err != nil {
			fmt.Printf("Error reading file: %v\n", err)
			os.Exit(1)
		}

		tests, err := generator.GenerateUnitTests(string(content), openaiAPIKey)
		if err != nil {
			fmt.Printf("Error generating tests: %v\n", err)
			os.Exit(1)
		}

		if outputFile == "" {
			outputFile = strings.TrimSuffix(inputFile, ".go") + "_test.go"
		}

		if err := os.WriteFile(outputFile, []byte(tests), 0644); err != nil {
			fmt.Printf("Error writing tests: %v\n", err)
			os.Exit(1)
		}

		if err := formatter.RunGoImports(outputFile); err != nil {
			fmt.Printf("Failed to run goimports: %v\n", err)
			os.Exit(1)
		}

		fmt.Printf("Tests generated: %s\n", outputFile)
	},
}

func init() {
	rootCmd.AddCommand(generateCmd)
	generateCmd.Flags().StringVarP(&inputFile, "file", "f", "", "Input Go file (required)")
	generateCmd.Flags().StringVarP(&outputFile, "output", "o", "", "Output test file")
	generateCmd.Flags().StringVarP(&openaiAPIKey, "key", "k", "", "OpenAI API key")
	generateCmd.MarkFlagRequired("file")
}
