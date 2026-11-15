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

static void	fill(int fd, char *buf, char **line, int *done)
{
	ssize_t	n;

	n = read(fd, buf, BUFFER_SIZE);
	if (n < 0)
	{
		free(*line);
		*line = NULL;
		n = 0;
	}
	buf[n] = '\0';
	*done = (n == 0);
}

static char	*append(char *line, char *buf, size_t n)
{
	char	*res;
	size_t	len;

	len = len_to(line, '\0');
	res = malloc(len + n + 1);
	if (res)
	{
		copy(res, line, len);
		copy(res + len, buf, n);
		res[len + n] = '\0';
	}
	free(line);
	return (res);
}

static void	join(char **line, char *buf, int *done)
{
	size_t	len;

	len = len_to(buf, '\n');
	*done = (buf[len] == '\n');
	len += *done;
	*line = append(*line, buf, len);
	if (!*line)
		*done = 1;
	copy(buf, buf + len, len_to(buf + len, '\0') + 1);
}

static char	*next_line(int fd, char *buf)
{
	char	*line;
	int		done;

	line = NULL;
	done = 0;
	while (!done)
	{
		if (!buf[0])
			fill(fd, buf, &line, &done);
		if (!done)
			join(&line, buf, &done);
	}
	return (line);
}

char	*get_next_line(int fd)
{
	static char	*buf[OPEN_MAX];
	char		*line;

	if (fd < 0 || fd >= OPEN_MAX || BUFFER_SIZE <= 0)
		return (NULL);
	if (!buf[fd])
	{
		buf[fd] = malloc(BUFFER_SIZE + 1);
		if (!buf[fd])
			return (NULL);
		buf[fd][0] = '\0';
	}
	line = next_line(fd, buf[fd]);
	if (!buf[fd][0])
	{
		free(buf[fd]);
		buf[fd] = NULL;
	}
	return (line);
}
