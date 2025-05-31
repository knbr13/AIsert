```markdown
# Package ds

Package `ds` provides a simple implementation of a stack data structure for integers. The stack follows the Last-In, First-Out (LIFO) principle.

## Type Definitions

### Stack

```go
type Stack struct {
	items []int
}
```

`Stack` is the main type representing the stack data structure. It internally uses a slice of integers (`items`) to store the stack elements.

## Function Descriptions

### NewStack

```go
func NewStack()*Stack
```

`NewStack` creates and returns a new, empty stack.

**Returns:**

- `*Stack`: A pointer to a newly created empty stack.

**Example:**

```go
package main

import (
	"fmt"
	"your_module/ds" // Replace "your_module" with your actual module path
)

func main() {
	stack := ds.NewStack()
	fmt.Println(stack.IsEmpty()) // Output: true
}
```

### Push

```go
func (s*Stack) Push(item int)
```

`Push` adds a new `item` to the top of the stack.

**Parameters:**

- `item` `int`: The integer value to be added to the stack.

**Example:**

```go
package main

import (
	"fmt"
	"your_module/ds" // Replace "your_module" with your actual module path
)

func main() {
	stack := ds.NewStack()
	stack.Push(10)
	stack.Push(20)
	fmt.Println(stack.Size()) // Output: 2
}
```

### Pop

```go
func (s*Stack) Pop() (int, error)
```

`Pop` removes and returns the item at the top of the stack. If the stack is empty, it returns an error.

**Returns:**

- `int`: The value of the item that was removed from the top of the stack.
- `error`: An error if the stack is empty. Returns `nil` otherwise.

**Example:**

```go
package main

import (
	"fmt"
	"your_module/ds" // Replace "your_module" with your actual module path
)

func main() {
	stack := ds.NewStack()
	stack.Push(10)
	stack.Push(20)

	item, err := stack.Pop()
	if err != nil {
		fmt.Println("Error:", err)
		return
	}
	fmt.Println("Popped:", item) // Output: Popped: 20
	fmt.Println(stack.Size())    // Output: 1

	_, err = stack.Pop()
	if err != nil {
		fmt.Println("Error:", err)
		return
	}

	_, err = stack.Pop()
	if err != nil {
		fmt.Println("Error:", err) // Output: Error: stack is empty
	}
}
```

**Notes:**

-  It is crucial to handle the potential error returned by `Pop` to prevent unexpected behavior if the stack is empty.

### Peek

```go
func (s*Stack) Peek() (int, error)
```

`Peek` returns the item at the top of the stack without removing it. If the stack is empty, it returns an error.

**Returns:**

- `int`: The value of the item at the top of the stack.
- `error`: An error if the stack is empty. Returns `nil` otherwise.

**Example:**

```go
package main

import (
	"fmt"
	"your_module/ds" // Replace "your_module" with your actual module path
)

func main() {
	stack := ds.NewStack()
	stack.Push(10)
	stack.Push(20)

	item, err := stack.Peek()
	if err != nil {
		fmt.Println("Error:", err)
		return
	}
	fmt.Println("Peeked:", item) // Output: Peeked: 20
	fmt.Println(stack.Size())    // Output: 2 (Size remains unchanged)

	stack = ds.NewStack()
	_, err = stack.Peek()

	if err != nil {
		fmt.Println("Error:", err) // Output: Error: stack is empty
	}
}
```

**Notes:**

- It is crucial to handle the potential error returned by `Peek` to prevent unexpected behavior if the stack is empty.

### IsEmpty

```go
func (s*Stack) IsEmpty() bool
```

`IsEmpty` returns `true` if the stack is empty (contains no elements), and `false` otherwise.

**Returns:**

- `bool`: `true` if the stack is empty, `false` otherwise.

**Example:**

```go
package main

import (
	"fmt"
	"your_module/ds" // Replace "your_module" with your actual module path
)

func main() {
	stack := ds.NewStack()
	fmt.Println("Is Empty:", stack.IsEmpty()) // Output: Is Empty: true
	stack.Push(10)
	fmt.Println("Is Empty:", stack.IsEmpty()) // Output: Is Empty: false
}
```

### Size

```go
func (s*Stack) Size() int
```

`Size` returns the number of elements currently in the stack.

**Returns:**

- `int`: The number of elements in the stack.

**Example:**

```go
package main

import (
	"fmt"
	"your_module/ds" // Replace "your_module" with your actual module path
)

func main() {
	stack := ds.NewStack()
	fmt.Println("Size:", stack.Size()) // Output: Size: 0
	stack.Push(10)
	stack.Push(20)
	fmt.Println("Size:", stack.Size()) // Output: Size: 2
}
```