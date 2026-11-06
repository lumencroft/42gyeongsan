*This project has been created as part of the 42 curriculum by donkim.*

# ft_printf

## Description

ft_printf is a re-implementation of the libc printf() function. The goal is to learn how variadic functions work in C.

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

## Algorithm and data structure

**Single pass, no buffer.** `ft_printf` walks the format string once and writes characters immediately, so no buffer or `malloc` is needed. Every helper returns how many characters it wrote, and `ft_printf` sums them up.

**Dispatcher.** `ft_print_arg` is a chain of `if` statements that reads the argument with `va_arg` using the right type and calls the matching helper. A chain was chosen over a function-pointer table because there are only a few conversions. `%%` and any unknown conversion print the character itself.

**`va_list` passed by pointer.** Passing it by value is not portable (on Windows x64 the caller's list did not advance), so the helpers receive `va_list *`.

**One recursive function for every base.** `ft_print_base` recurses on `n / len` first, then prints `base[n % len]`. The call stack holds the digits, so no array or `ft_itoa` is needed.

**Signed numbers.** `%d` prints `-` first, then the magnitude `-(size_t)n`, so `INT_MIN` does not overflow.

**Special values.** `NULL` prints `(null)` for `%s` and `(nil)` for `%p`, like glibc.

**Trade-off.** Each character is its own `write` call. This is slower than buffering but keeps the code simple.

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