package cmd

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"

	"github.com/knbr13/aitestgen/pkg/formatter"
	"github.com/knbr13/aitestgen/pkg/generator"
	"github.com/spf13/cobra"
)

var (
	docInputFile   string
	docOutputFile  string
	docInputFolder string
	docAPIKey      string
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

		if docInputFile != "" {
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

			docs = formatter.FormatDocumentation(docs)

			if err := os.WriteFile(docOutputFile, []byte(docs), 0644); err != nil {
				fmt.Printf("Error writing documentation: %v\n", err)
				os.Exit(1)
			}

			fmt.Printf("documentation generated for file: %s\n", docOutputFile)
		} else if docInputFolder != "" {
			var files []string
			err := filepath.Walk(docInputFolder, func(path string, info os.FileInfo, err error) error {
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
			var wg sync.WaitGroup
			wg.Add(len(files))
			for _, file := range files {
				go func(file string) {
					defer wg.Done()
					content, err := os.ReadFile(file)
					if err != nil {
						fmt.Printf("Error reading file: %v\n", err)
						os.Exit(1)
					}

					docs, err := generator.GenerateDocumentation(string(content), docAPIKey)
					if err != nil {
						fmt.Printf("Error generating documentation: %v\n", err)
						os.Exit(1)
					}

					ext := filepath.Ext(file)
					outf := strings.TrimSuffix(file, ext) + "_doc.md"

					docs = formatter.FormatDocumentation(docs)

					if err := os.WriteFile(outf, []byte(docs), 0644); err != nil {
						fmt.Printf("Error writing documentation: %v\n", err)
						os.Exit(1)
					}

					fmt.Printf("documentation generated for file: %s\n", outf)
				}(file)
			}
			wg.Wait()
			return
		}
		fmt.Println("You must specify either --file or --folder.")
		os.Exit(1)
	},
}

func init() {
	rootCmd.AddCommand(docCmd)
	docCmd.Flags().StringVarP(&docInputFile, "file", "f", "", "Input Go file (required)")
	docCmd.Flags().StringVarP(&docInputFolder, "folder", "d", "", "Input folder (recursively processes all Go files)")
	docCmd.Flags().StringVarP(&docOutputFile, "output", "o", "", "Output documentation file")
	docCmd.Flags().StringVarP(&docAPIKey, "key", "k", "", "Gemini API key")
}
