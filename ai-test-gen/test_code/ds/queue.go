package ds

import "errors"

// Queue is a simple integer queue (FIFO).
type Queue struct {
	items []int
}

// NewQueue creates a new empty queue.
func NewQueue() *Queue {
	return &Queue{items: []int{}}
}

// Enqueue adds an item to the end of the queue.
func (q *Queue) Enqueue(item int) {
	q.items = append(q.items, item)
}

// Dequeue removes and returns the item at the front of the queue.
// Returns an error if the queue is empty.
func (q *Queue) Dequeue() (int, error) {
	if q.IsEmpty() {
		return 0, errors.New("queue is empty")
	}
	item := q.items[0]
	q.items = q.items[1:]
	return item, nil
}

// Peek returns the item at the front of the queue without removing it.
// Returns an error if the queue is empty.
func (q *Queue) Peek() (int, error) {
	if q.IsEmpty() {
		return 0, errors.New("queue is empty")
	}
	return q.items[0], nil
}

// IsEmpty returns true if the queue has no elements.
func (q *Queue) IsEmpty() bool {
	return len(q.items) == 0
}

// Size returns the number of elements in the queue.
func (q *Queue) Size() int {
	return len(q.items)
}
