package utils

func IsPrime(n int) bool {
	if n <= 1 {
		return false
	}
	for i := 2; i*i <= n; i++ {
		if n%i == 0 {
			return false
		}
	}
	return true
}

// Factorial calculates the factorial of a non-negative integer.
func Factorial(n int) int {
	if n < 0 {
		panic("negative input not allowed")
	}
	if n == 0 || n == 1 {
		return 1
	}
	return n * Factorial(n-1)
}

// Sum returns the sum of a slice of integers.
func Sum(nums []int) int {
	total := 0
	for _, n := range nums {
		total += n
	}
	return total
}

func Max(nums []int) int {
	if len(nums) == 0 {
		panic("empty slice")
	}
	max := nums[0]
	for _, v := range nums[1:] {
		if v > max {
			max = v
		}
	}
	return max
}

func GCD(a, b int) int {
	for b != 0 {
		a, b = b, a%b
	}
	return a
}
