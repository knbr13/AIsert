package formatter

import "os/exec"

func RunGoImports(filePath string) error {
	cmd := exec.Command("goimports", "-w", filePath)
	return cmd.Run()
}
