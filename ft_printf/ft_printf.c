/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_printf.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: donkim <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/05 11:54:00 by donkim            #+#    #+#             */
/*   Updated: 2026/11/05 11:54:02 by donkim           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_printf.h"

static int	ft_print_arg(char spec, va_list *ap)
{
	if (spec == 'c')
		return (ft_print_char(va_arg(*ap, int)));
	if (spec == 's')
		return (ft_print_str(va_arg(*ap, char *)));
	if (spec == 'd' || spec == 'i')
		return (ft_print_nbr(va_arg(*ap, int)));
	if (spec == 'u')
		return (ft_print_base(va_arg(*ap, unsigned int), BASE_DEC));
	if (spec == 'x')
		return (ft_print_base(va_arg(*ap, unsigned int), BASE_HEX));
	if (spec == 'X')
		return (ft_print_base(va_arg(*ap, unsigned int), BASE_HEXUP));
	if (spec == 'p')
		return (ft_print_ptr(va_arg(*ap, void *)));
	return (ft_print_char('%'));
}

int	ft_printf(const char *format, ...)
{
	va_list	ap;
	int		count;

	count = 0;
	va_start(ap, format);
	while (*format)
	{
		if (*format == '%' && format[1] && ft_strchr("cspdiuxX%", format[1]))
		{
			count += ft_print_arg(format[1], &ap);
			format += 2;
		}
		else
			count += ft_print_char(*format++);
	}
	va_end(ap);
	return (count);
}
