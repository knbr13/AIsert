package cmd

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/spf13/cobra"

	"github.com/knbr13/aitestgen/pkg/formatter"
	"github.com/knbr13/aitestgen/pkg/generator"
)

var (
	inputFile    string
	outputFile   string
	inputFolder  string
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

		if inputFile != "" {
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
			return
		}

		if inputFolder != "" {
			var files []string
			err := filepath.Walk(inputFolder, func(path string, info os.FileInfo, err error) error {
				if err != nil {
					return err
				}
				if info.IsDir() {
					return nil
				}
				if strings.HasSuffix(path, ".go") && !strings.HasSuffix(path, "_test.go") {
					files = append(files, path)
				}
				return nil
			})
			if err != nil {
				fmt.Printf("Error walking folder: %v\n", err)
				os.Exit(1)
			}
			if len(files) == 0 {
				fmt.Println("No Go files found in folder.")
				os.Exit(1)
			}
			errors := make(map[string]error)
			for _, file := range files {
				content, err := os.ReadFile(file)
				if err != nil {
					errors[file] = fmt.Errorf("read error: %w", err)
					continue
				}
				tests, err := generator.GenerateUnitTests(string(content), openaiAPIKey)
				if err != nil {
					errors[file] = fmt.Errorf("generation error: %w", err)
					continue
				}
				outFile := strings.TrimSuffix(file, ".go") + "_test.go"
				if err := os.WriteFile(outFile, []byte(tests), 0644); err != nil {
					errors[file] = fmt.Errorf("write error: %w", err)
					continue
				}
				if err := formatter.RunGoImports(outFile); err != nil {
					errors[file] = fmt.Errorf("goimports error: %w", err)
					continue
				}
				fmt.Printf("Tests generated: %s\n", outFile)
			}
			if len(errors) > 0 {
				fmt.Println("Some files had errors:")
				for f, e := range errors {
					fmt.Printf("%s: %v\n", f, e)
				}
			}
			return
		}

		fmt.Println("You must specify either --file or --folder.")
		os.Exit(1)
	},
}

func init() {
	rootCmd.AddCommand(generateCmd)
	generateCmd.Flags().StringVarP(&inputFile, "file", "f", "", "Input Go file")
	generateCmd.Flags().StringVarP(&outputFile, "output", "o", "", "Output test file (only for single file mode)")
	generateCmd.Flags().StringVarP(&inputFolder, "folder", "d", "", "Input folder (recursively processes all Go files)")
	generateCmd.Flags().StringVarP(&openaiAPIKey, "key", "k", "", "OpenAI API key")
}
