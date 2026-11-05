/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_printf_utils.c                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: donkim <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/05 11:54:17 by donkim            #+#    #+#             */
/*   Updated: 2026/11/05 11:54:20 by donkim           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_printf.h"

int	ft_print_char(char c)
{
	ft_putchar_fd(c, 1);
	return (1);
}

int	ft_print_str(char *s)
{
	if (!s)
		s = "(null)";
	ft_putstr_fd(s, 1);
	return (ft_strlen(s));
}

int	ft_print_base(size_t n, char *base)
{
	size_t	len;
	int		count;

	len = ft_strlen(base);
	count = 1;
	if (n >= len)
		count += ft_print_base(n / len, base);
	ft_putchar_fd(base[n % len], 1);
	return (count);
}

int	ft_print_ptr(void *p)
{
	int	count;

	if (!p)
		return (ft_print_str("(nil)"));
	count = ft_print_str("0x");
	return (count + ft_print_base((size_t)p, BASE_HEX));
}

int	ft_print_nbr(int n)
{
	int	count;

	count = 0;
	if (n < 0)
	{
		count += ft_print_char('-');
		return (count + ft_print_base(-(size_t)n, BASE_DEC));
	}
	return (ft_print_base(n, BASE_DEC));
}
