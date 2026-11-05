*This project has been created as part of the 42 curriculum by donkim.*

# ft_printf

## Description

`ft_printf` is a re-implementation of the libc `printf()` function. The goal of the project is to learn how variadic functions work in C (`stdarg.h`) and how to structure a small program so that new features can be added without rewriting it.

The library is built as `libftprintf.a` and exposes a single function:

```c
int	ft_printf(const char *format, ...);
```

It returns the number of characters printed, like the original `printf()`.

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

The original `printf()` buffer management is intentionally not reimplemented: every character is written right away with `write()`.

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

`libftprintf.a` is created with `ar` and already contains the libft objects, so a single library is enough to link.

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

## Algorithm and data structure

**Single pass, no buffer.** `ft_printf` walks the format string once. A character that is not part of a conversion is written immediately. When a `%` is followed by a supported conversion character, the matching handler is called and the pointer jumps over both characters. Every handler returns the number of characters it wrote, and `ft_printf` simply accumulates them. Because nothing is stored, there is no `malloc`, no `free`, and no buffer size to manage, which also matches the subject's rule of not implementing the original buffering.

**One dispatcher.** `ft_print_arg(char spec, va_list *ap)` receives the conversion character and reads the argument with `va_arg` using the correct type (`int`, `unsigned int`, `char *`, `void *`). Each branch is one line, so adding a new conversion means adding one line and one helper. An `if` chain was chosen over a function-pointer table because there are only nine conversions and the chain is the shortest and easiest code to read while staying within the Norm's 25-line limit.

**`va_list` passed by pointer.** The `va_list` is passed as `va_list *` to the dispatcher. Passing it by value and then continuing to use it in the caller is undefined behavior according to the C standard (it only works on some platforms), so the pointer is the portable choice.

**One recursive function for all bases.** `ft_print_base(unsigned long n, char *base)` prints `n` in the base defined by the length of the `base` string:

- `%u` uses `"0123456789"`
- `%x` uses `"0123456789abcdef"`
- `%X` uses `"0123456789ABCDEF"`
- `%p` uses the lowercase hexadecimal digits after printing `0x`

The function prints the higher digits first by recursing on `n / base_len`, then prints the current digit `base[n % base_len]`. The call stack acts as the digit stack, so digits come out in the right order without a temporary array or `ft_itoa`. The recursion depth is at most 20 for a 64-bit value, so it is safe. Using `unsigned long` lets the same function handle `unsigned int` values and 64-bit pointers.

**Signed numbers.** For `%d`/`%i`, `ft_print_nbr` prints `-` for negative values and then prints the magnitude with `ft_print_base`. The magnitude is computed as `-(long long)n`, so `INT_MIN` does not overflow.

**Edge cases.**

- `%s` with `NULL` prints `(null)`, and `%p` with `NULL` prints `(nil)`, as glibc does.
- A `%` at the very end of the format string, or followed by an unsupported character, is printed as a normal character. This is undefined behavior in libc, so the choice only has to be safe, not identical.

## Resources

- `man 3 printf`, `man 3 stdarg`
- C reference for variadic arguments: https://en.cppreference.com/w/c/variadic
- The 42 Norm

### Use of AI

AI (Claude, by Anthropic) was used during this project for the following tasks:

- **Code review of my first draft.** I wrote the initial structure (separate handlers per conversion type). The review pointed out the out-of-bounds read when `%` is the last character of the format string, the missing `%u` handling, and the `va_list` by-value passing.
- **Restructuring and implementation.** The dispatcher on the conversion character and the shared `ft_print_base` helper were proposed and written with the help of AI, and the final `ft_printf.c` / `ft_printf_utils.c` come from that work.
- **Testing.** Output and return values were compared with the real `printf()` using a throwaway test program (including `INT_MIN`, `UINT_MAX`, `NULL` pointers and strings).
- **Understanding Norm errors** reported by `norminette`.
- **Drafting this README.**

I have read and understood all the code that is submitted, and I can explain and modify it.
