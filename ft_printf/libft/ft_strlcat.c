/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strlcat.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: donkim <donkim@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/06 13:58:45 by donkim            #+#    #+#             */
/*   Updated: 2026/10/19 15:04:20 by donkim           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

size_t	ft_strlcat(char *dst, const char *src, size_t size)
{
	size_t	dst_len;

	dst_len = 0;
	while (dst_len < size && dst[dst_len])
		dst_len++;
	if (size == dst_len)
		return (dst_len + ft_strlen(src));
	return (dst_len + ft_strlcpy(dst + dst_len, src, size - dst_len));
}
