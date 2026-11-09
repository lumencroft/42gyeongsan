/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   get_next_line_utils_bonus.c                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: donkim <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/09 17:47:00 by donkim            #+#    #+#             */
/*   Updated: 2026/11/09 17:47:00 by donkim           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "get_next_line_bonus.h"

void	copy(char *dst, char *src, size_t n)
{
	while (n--)
		*dst++ = *src++;
}

size_t	ft_strlen(char *s)
{
	size_t	len;

	len = 0;
	while (s && s[len])
		len++;
	return (len);
}

size_t	chunk_len(char *s, int *done)
{
	size_t	len;

	len = 0;
	while (s[len] && s[len] != '\n')
		len++;
	*done = (s[len] == '\n');
	return (len + *done);
}

void	shift(char *buf, size_t n)
{
	size_t	j;

	j = 0;
	while (buf[n])
		buf[j++] = buf[n++];
	buf[j] = '\0';
}
