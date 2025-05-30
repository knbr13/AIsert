package cmd

import (
	"fmt"
	"os"
	"os/exec"

	"github.com/spf13/cobra"
)

var (
	coverProfile string
	testPackage  string
)

var coverCmd = &cobra.Command{
	Use:   "cover",
	Short: "Run tests and generate coverage profile",
	Run: func(cmd *cobra.Command, args []string) {
		if testPackage == "" {
			testPackage = "./..."
		}

		testCmd := exec.Command("go", "test", testPackage, "-coverprofile", coverProfile)
		testCmd.Stdout = os.Stdout
		testCmd.Stderr = os.Stderr

		fmt.Printf("Running tests for package: %s\n", testPackage)
		if err := testCmd.Run(); err != nil {
			fmt.Printf("Error running tests: %v\n", err)
			os.Exit(1)
		}

		fmt.Printf("Coverage profile generated: %s\n", coverProfile)
	},
}

var viewCoverCmd = &cobra.Command{
	Use:   "view-cover",
	Short: "Visualize coverage profile in browser",
	Run: func(cmd *cobra.Command, args []string) {
		viewCmd := exec.Command("go", "tool", "cover", "-html", coverProfile)
		viewCmd.Stdout = os.Stdout
		viewCmd.Stderr = os.Stderr

		fmt.Printf("Opening coverage visualization for: %s\n", coverProfile)
		if err := viewCmd.Run(); err != nil {
			fmt.Printf("Error opening coverage: %v\n", err)
			os.Exit(1)
		}
	},
}

func init() {
	rootCmd.AddCommand(coverCmd)
	rootCmd.AddCommand(viewCoverCmd)

	coverCmd.Flags().StringVarP(&coverProfile, "output", "o", "coverage.out", "Coverage profile filename")
	coverCmd.Flags().StringVarP(&testPackage, "package", "p", "", "Package to test (default './...')")

	viewCoverCmd.Flags().StringVarP(&coverProfile, "input", "i", "coverage.out", "Coverage profile filename")
}
