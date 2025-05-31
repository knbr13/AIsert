package utils

import (
	"strings"
	"unicode"
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

// Contains checks whether a string slice contains a particular string.
func Contains(slice []string, item string) bool {
	for _, v := range slice {
		if v == item {
			return true
		}
	}
	return false
}

// ReverseString returns the reverse of the input string.
func ReverseString(s string) string {
	runes := []rune(s)
	for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
		runes[i], runes[j] = runes[j], runes[i]
	}
	return string(runes)
}

// IsPalindrome checks whether a given string is a palindrome (case-insensitive, ignoring spaces and punctuation).
func IsPalindrome(s string) bool {
	var cleaned []rune
	for _, r := range s {
		if unicode.IsLetter(r) || unicode.IsNumber(r) {
			cleaned = append(cleaned, unicode.ToLower(r))
		}
	}
	for i, j := 0, len(cleaned)-1; i < j; i, j = i+1, j-1 {
		if cleaned[i] != cleaned[j] {
			return false
		}
	}
	return true
}

func CountVowels(s string) int {
	count := 0
	for _, r := range strings.ToLower(s) {
		if strings.ContainsRune("aeiou", r) {
			count++
		}
	}
	return count
}

func RemoveDuplicateChars(s string) string {
	seen := make(map[rune]bool)
	var result []rune
	for _, r := range s {
		if !seen[r] {
			seen[r] = true
			result = append(result, r)
		}
	}
	return string(result)
}
