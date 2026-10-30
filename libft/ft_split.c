/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_split.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: donkim <donkim@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/06 13:58:11 by donkim            #+#    #+#             */
/*   Updated: 2026/10/19 11:12:34 by donkim           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

static void	*free_all(char **res, size_t i)
{
	while (i--)
		free(res[i]);
	free(res);
	return (NULL);
}

static size_t	word_len(char const *s, char c)
{
	size_t	len;

	len = 0;
	while (s[len] && s[len] != c)
		len++;
	return (len);
}

static size_t	count_words(char const *s, char c)
{
	size_t	count;

	count = 0;
	while (*s)
	{
		if (*s == c)
			s++;
		else
		{
			s += word_len(s, c);
			count++;
		}
	}
	return (count);
}

static char	**fill_words(char **res, char const *s, char c)
{
	size_t	count;
	size_t	len;

	count = 0;
	while (*s)
	{
		if (*s == c)
			s++;
		else
		{
			len = word_len(s, c);
			res[count] = ft_substr(s, 0, len);
			if (!res[count])
				return (free_all(res, count));
			s += len;
			count++;
		}
	}
	res[count] = NULL;
	return (res);
}

char	**ft_split(char const *s, char c)
{
	char	**res;

	if (!s)
		return (NULL);
	res = malloc(sizeof(char *) * (count_words(s, c) + 1));
	if (!res)
		return (NULL);
	return (fill_words(res, s, c));
}
