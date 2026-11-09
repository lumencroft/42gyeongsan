NAME		= get_next_line.a
BONUS_NAME	= get_next_line_bonus.a

CC			= cc
CFLAGS		= -Wall -Wextra -Werror
BUFFER_SIZE	?= 42
CPPFLAGS	= -D BUFFER_SIZE=$(BUFFER_SIZE)

SRCS		= get_next_line.c get_next_line_utils.c
BONUS_SRCS	= get_next_line_bonus.c get_next_line_utils_bonus.c
OBJS		= $(SRCS:.c=.o)
BONUS_OBJS	= $(BONUS_SRCS:.c=.o)

all: $(NAME)

$(NAME): $(OBJS)
	ar rcs $@ $^

bonus: $(BONUS_NAME)

$(BONUS_NAME): $(BONUS_OBJS)
	ar rcs $@ $^

%.o: %.c
	$(CC) $(CFLAGS) $(CPPFLAGS) -c $< -o $@

$(OBJS): get_next_line.h
$(BONUS_OBJS): get_next_line_bonus.h

test: $(SRCS) main.c
	$(CC) $(CFLAGS) $(CPPFLAGS) -g -fsanitize=address main.c $(SRCS) -o gnl_test

test_bonus: $(BONUS_SRCS) main_bonus.c
  	$(CC) $(CFLAGS) $(CPPFLAGS) -g -fsanitize=address,undefined main_bonus.c $(BONUS_SRCS) -o gnl_test_bonus

clean:
	rm -f $(OBJS) $(BONUS_OBJS)

fclean: clean
	rm -f $(NAME) $(BONUS_NAME) gnl_test

re: fclean all

.PHONY: all bonus test clean fclean re
