/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strnstr.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: donkim <donkim@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/06 13:59:00 by donkim            #+#    #+#             */
/*   Updated: 2026/10/20 18:51:57 by donkim           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_strnstr(const char *big, const char *little, size_t len)
{
	size_t	l_len;

	if (!*little)
		return ((char *)big);
	l_len = ft_strlen(little);
	while (l_len <= len && *big)
	{
		if (ft_strncmp(big, little, l_len) == 0)
			return ((char *)big);
		big++;
		len--;
	}
	return (NULL);
}
