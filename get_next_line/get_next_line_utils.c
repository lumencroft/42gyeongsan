/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   get_next_line_utils.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: donkim <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/09 17:51:07 by donkim            #+#    #+#             */
/*   Updated: 2026/11/09 17:51:09 by donkim           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "get_next_line.h"

void	copy(char *dst, char *src, size_t n)
{
	while (n--)
		*dst++ = *src++;
}

size_t	len_to(char *s, char c)
{
	size_t	len;

	len = 0;
	while (s && s[len] && s[len] != c)
		len++;
	return (len);
}
