/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   get_next_line_bonus.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: donkim <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/09 17:47:00 by donkim            #+#    #+#             */
/*   Updated: 2026/11/09 17:47:00 by donkim           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "get_next_line_bonus.h"

static int	fill(char **line, char *buf, int fd)
{
	ssize_t	n;

	if (buf[0])
		return (1);
	n = read(fd, buf, BUFFER_SIZE);
	if (n < 0)
	{
		free(*line);
		*line = NULL;
		n = 0;
	}
	buf[n] = '\0';
	return (n > 0);
}

static int	join(char **line, char *buf)
{
	char	*res;
	size_t	len1;
	size_t	len2;
	int		done;

	len1 = str_len(*line);
	len2 = chunk_len(buf, &done);
	res = malloc(len1 + len2 + 1);
	if (res)
	{
		copy(res, *line, len1);
		copy(res + len1, buf, len2);
		res[len1 + len2] = '\0';
	}
	free(*line);
	*line = res;
	shift(buf, len2);
	return (done || !res);
}

char	*get_next_line(int fd)
{
	char		*line;
	static char	*buf[OPEN_MAX];

	if (fd < 0 || fd >= OPEN_MAX || BUFFER_SIZE <= 0)
		return (NULL);
	if (!buf[fd])
	{
		buf[fd] = malloc(BUFFER_SIZE + 1);
		if (!buf[fd])
			return (NULL);
		buf[fd][0] = '\0';
	}
	line = NULL;
	while (fill(&line, buf, fd))
	{
		if (join(&line, buf[fd]))
			return (line);
	}
	free(buf[fd]);
	buf[fd] = NULL;
	return (line);
}
