package math

import "fmt"

// Add two integers
func Add(a, b int) int {
	return a + b
}

// Divide two integers
func Divide(a, b int) (int, error) {
	if b == 0 {
		return 0, fmt.Errorf("division by zero")
	}
	return a / b, nil
}
