library(tidyverse)

# set custom ggplot theme
theme_custom <- function(){
  theme_minimal() + 
    theme(text = element_text(family = "Helvetica"), 
          plot.background = element_rect(fill = NA, color = "gray95", size = 10),
          plot.margin = unit(c(1, 1, 1, 1), "cm"))
  }
theme_set(theme_custom())

# read in the data
setwd("~/Dropbox/Data/Projects/messages")
four_locos <- read_csv("Data/four_locos.csv", 
                       col_types = cols(date = col_date(format = "%Y-%m-%d"), 
                                        url = col_character()))

# top urls per person
four_locos %>% 
  filter(!is.na(url)) %>% 
  group_by(contact, url) %>% 
  tally() %>% 
  group_by(contact) %>% 
  slice_max(order_by = n, n = 5) %>%
  mutate(url = tidytext::reorder_within(url, n, contact)) %>% 
  ggplot(aes(x = url, y = n, fill = contact)) +
  geom_col() +
  tidytext::scale_x_reordered() +
  facet_wrap(~contact, scales = "free_y", ncol = 1) +
  coord_flip() +
  labs(title = "Top five most shared sites",
       subtitle = paste0(range(four_locos$date), collapse = " thru "),
       x = NULL,
       y = NULL) +
  theme(legend.position = 'none')
ggsave(filename = "Plots/top_five_urls.svg",
       device = 'svg',
       height = 8,
       width = 5)

# timeseries of text frequency in group thread
four_locos %>% 
  group_by(date, contact) %>% 
  tally() %>%
  group_by(contact) %>% 
  mutate(rolling_mean = zoo::rollmean(x = n, k = 7, fill = NA)) %>% 
  ggplot(aes(x = date, y = rolling_mean, group = contact, color = contact)) +
  geom_line(alpha = 0.7, size = 1.2) +
  geom_vline(xintercept = as.Date("2020-03-20"), color = 'grey60') +
  annotate(geom = 'text', x = as.Date('2020-03-10'), y = 25,
           label = 'NY stay-at-\nhome order: 3/20',
           hjust = 1, size = 3, family = 'Helvetica') +
  geom_vline(xintercept = as.Date("2020-05-25"), color = 'grey60') +
  annotate(geom = 'text', x = as.Date('2020-06-05'), y = 2,
           label = "George Floyd's\ndeath: 5/25",
           hjust = 0, size = 3, family = 'Helvetica') +
  labs(title = "Daily traffic in the group thread",
       subtitle = "7-day moving average",
       x = NULL,
       y = "Daily texts sent",
       color = NULL) +
  theme(legend.position = 'bottom')
ggsave(filename = "Plots/daily_traffic.svg",
       device = 'svg',
       height = 5,
       width = 8)

