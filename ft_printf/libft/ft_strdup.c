/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strdup.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: donkim <donkim@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/06 13:58:18 by donkim            #+#    #+#             */
/*   Updated: 2026/10/21 11:19:21 by donkim           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_strdup(const char *s)
{
	char	*d;
	size_t	size;

	size = ft_strlen(s) + 1;
	d = malloc(size);
	if (d)
		ft_memcpy(d, s, size);
	return (d);
}
