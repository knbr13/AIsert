package utils

import (
	"os"
)

func GetEnv(name, fallback string) string {
	v := os.Getenv(name)
	if v == "" {
		return fallback
	}
	return v
}

func Range(start, end int) []int {
	if end < start {
		return []int{}
	}
	result := make([]int, end-start+1)
	for i := range result {
		result[i] = start + i
	}
	return result
}
