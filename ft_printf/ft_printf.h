/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_printf.h                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: donkim <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/05 11:54:27 by donkim            #+#    #+#             */
/*   Updated: 2026/11/05 11:54:30 by donkim           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef FT_PRINTF_H
# define FT_PRINTF_H

# include <stdarg.h>
# include "libft.h"

# define BASE_DEC "0123456789"
# define BASE_HEX "0123456789abcdef"
# define BASE_HEXUP "0123456789ABCDEF"

int	ft_printf(const char *format, ...);
int	ft_print_char(char c);
int	ft_print_str(char *s);
int	ft_print_nbr(int n);
int	ft_print_base(unsigned long n, char *base);
int	ft_print_ptr(void *p);

#endif
