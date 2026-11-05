*This project has been created as part of the 42 curriculum by donkim.*

# Libft

## Description
Libft is a foundational project in the 42 school curriculum. The main goal of this project is to build a custom C static library (`libft.a`) by re-implementing standard C library functions (`libc`), as well as developing additional utility functions and linked list manipulation functions from scratch without relying on non-permitted external libraries.

### Overview of Functions

- **Part 1 - Libc Functions**:
  - **Memory Operations**: `ft_memset`, `ft_bzero`, `ft_memcpy`, `ft_memmove`, `ft_memchr`, `ft_memcmp`, `ft_calloc`
  - **String Operations**: `ft_strlen`, `ft_strlcpy`, `ft_strlcat`, `ft_strchr`, `ft_strrchr`, `ft_strncmp`, `ft_strnstr`, `ft_strdup`
  - **Character Checks & Conversions**: `ft_isalpha`, `ft_isdigit`, `ft_isalnum`, `ft_isascii`, `ft_isprint`, `ft_toupper`, `ft_tolower`, `ft_atoi`

- **Part 2 - Additional Functions**:
  - **String Manipulation & Allocation**: `ft_substr`, `ft_strjoin`, `ft_strtrim`, `ft_split`, `ft_itoa`, `ft_strmapi`, `ft_striteri`
  - **File Descriptor Output**: `ft_putchar_fd`, `ft_putstr_fd`, `ft_putendl_fd`, `ft_putnbr_fd`

- **Part 3 - Linked List Operations**:
  - **List Creation & Traversal**: `ft_lstnew`, `ft_lstadd_front`, `ft_lstsize`, `ft_lstlast`, `ft_lstadd_back`
  - **List Deletion & Mapping**: `ft_lstdelone`, `ft_lstclear`, `ft_lstiter`, `ft_lstmap`

## Instructions

### Compilation
Compile the library using the provided `Makefile` in the project root:

- `make` or `make all`: Compiles all mandatory functions (Parts 1, 2, and 3) and generates the `libft.a` archive.
- `make clean`: Removes intermediate object (`.o`) files.
- `make fclean`: Removes object files and the `libft.a` library file.
- `make re`: Recompiles the entire library from scratch.

### Usage
Include `libft.h` in your C source files and link `libft.a` during compilation:

`#include "libft.h"`

Compilation example:
`cc -Wall -Wextra -Werror main.c -L. -lft`

## Resources
- [C Reference Documentation](https://en.cppreference.com/w/c)
- UNIX Manual Pages (`man 3 malloc`, `man 3 free`, `man 2 write`)

### AI Usage
AI tools (Gemini) were used during this project for the following specific tasks:
- **Concept & Logic Verification**: Analyzing edge cases for dynamic memory allocation, string parsing, and linked list pointer updates.
- **Debugging & Code Review**: Tracking memory leak scenarios (`valgrind` / `leaks`) in functions like `ft_split` and `ft_lstmap`.
- **Documentation**: Structuring the `README.md` file according to 42 curriculum Chapter V standards.