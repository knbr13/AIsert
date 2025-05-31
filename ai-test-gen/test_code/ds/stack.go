package ds

import "errors"

// Stack is a generic stack implementation for integers.
type Stack struct {
	items []int
}

// NewStack creates a new empty stack.
func NewStack() *Stack {
	return &Stack{items: []int{}}
}

// Push adds an item to the top of the stack.
func (s *Stack) Push(item int) {
	s.items = append(s.items, item)
}

// Pop removes and returns the top item from the stack.
// Returns an error if the stack is empty.
func (s *Stack) Pop() (int, error) {
	if s.IsEmpty() {
		return 0, errors.New("stack is empty")
	}
	index := len(s.items) - 1
	item := s.items[index]
	s.items = s.items[:index]
	return item, nil
}

// Peek returns the top item without removing it.
// Returns an error if the stack is empty.
func (s *Stack) Peek() (int, error) {
	if s.IsEmpty() {
		return 0, errors.New("stack is empty")
	}
	return s.items[len(s.items)-1], nil
}

// IsEmpty returns true if the stack has no elements.
func (s *Stack) IsEmpty() bool {
	return len(s.items) == 0
}

// Size returns the number of elements in the stack.
func (s *Stack) Size() int {
	return len(s.items)
}
