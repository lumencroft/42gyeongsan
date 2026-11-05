*This project has been created as part of the 42 curriculum by donkim.*

# ft_printf

## Description

ft_printf is a re-implementation of the libc printf() function. The goal is to learn how variadic functions work in C (stdarg.h).

### Supported conversions

| Conversion | Output |
|------------|--------|
| `%c` | a single character |
| `%s` | a string (`(null)` if the pointer is `NULL`) |
| `%p` | a `void *` in hexadecimal, prefixed with `0x` (`(nil)` if `NULL`) |
| `%d` / `%i` | a signed decimal integer |
| `%u` | an unsigned decimal integer |
| `%x` / `%X` | an unsigned integer in lowercase / uppercase hexadecimal |
| `%%` | a percent sign |

### Project structure

```
.
├── Makefile
├── README.md
├── ft_printf.h
├── ft_printf.c          # format loop and conversion dispatcher
├── ft_printf_utils.c    # output helpers (char, string, number, pointer)
└── libft/               # my libft (sources + Makefile)
```

## Instructions

### Build

```sh
make        # builds libft, then libftprintf.a at the root of the repository
make clean  # removes object files (including libft's)
make fclean # removes object files and libftprintf.a (including libft.a)
make re     # fclean + all
```

### Use

```c
#include "ft_printf.h"

int	main(void)
{
	ft_printf("%s has %d items (%x)\n", "cart", 42, 42);
	return (0);
}
```

```sh
cc main.c -I. -Ilibft -L. -lftprintf -o demo
```

## Resources

- `man 3 printf`, `man 3 stdarg`
- C reference for variadic arguments: https://en.cppreference.com/w/c/variadic
- The 42 Norm

### Use of AI

AI (Claude, by Anthropic) was used during this project for the following tasks:

- **Code review of my first draft.** I wrote the initial structure (separate handlers per conversion type). The review pointed out the out-of-bounds read when `%` is the last character of the format string.
- **Testing.** Output and return values were compared with the real `printf()` using a throwaway test program (including `INT_MIN`, `UINT_MAX`, `NULL` pointers and strings).
- **Drafting this README.**