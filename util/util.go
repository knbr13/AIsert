package util

import (
	"os"
	"strings"
)

func ConcatStrings(strs ...string) string {
	var n int
	for _, s := range strs {
		n += len(s)
	}
	var sb strings.Builder
	sb.Grow(n)
	for _, s := range strs {
		sb.WriteString(s)
	}
	return sb.String()
}

func GetEnv(name, fallback string) string {
	v := os.Getenv(name)
	if v == "" {
		return fallback
	}
	return v
}
