# This script generates all the regressions and tables in the final paper
library(readr)
library(tidyverse)
library(lubridate)
library(stargazer)
library(fixest)
library(lfe)
library(data.table)

############## 
## Load data
##############


df <-read_csv("merged_data0524.csv")

df <- df %>%
  mutate(after = ifelse(date >ymd("2022-04-28"),1,0),
         no_regional_info = ifelse(contains_keyword,0,1))

# summary stat  
stargazer(as.data.table(df))


############## 
## PART I: RDD
##############

# looking at the day before and after the policy change
df_day <- df %>%
  filter(date > ymd("2022-04-26") & date < ymd("2022-04-30")) %>%
  mutate(after = ifelse(date > ymd("2022-04-28"),1,0),
         days_away = as.numeric(date - ymd("2022-04-28")))

df_day_plot <- df_day %>%
  group_by(days_away)%>%
  summarise(avg_score =mean(score, na.rm =T))
ggplot(df_day_plot, aes(x = days_away, y = avg_score))+
  geom_point()+
  geom_vline(xintercept = 0,color ="red")+
  theme_bw()

# looking at the week before and after the policy change
df_week <- df %>%
  filter(date > ymd("2022-04-20") & date < ymd("2022-05-06"))%>%
  mutate(after = ifelse(date > ymd("2022-04-28"),1,0),
         days_away = as.numeric(date - ymd("2022-04-28")))

df_week_plot <- df_week %>%
  group_by(days_away)%>%
  summarise(avg_score =mean(score, na.rm =T))
p1<-ggplot(df_week_plot, aes(x = days_away, y = avg_score))+
  geom_point()+
  geom_vline(xintercept = 0,color ="red")+
  theme_bw()+
  labs(x = "Days From IP Revealing",
       y = "Average Sentiment Score")
ggsave("D:/ecma31320/rdd_illustration.png", plot=p1, width = 8, height = 4)


# looking at the month before and after the policy change
df_month <- df %>%
  filter(date > ymd("2022-04-01") & date < ymd("2022-05-31"))%>%
  mutate(after = ifelse(date > ymd("2022-04-28"),1,0),
         days_away = as.numeric(date - ymd("2022-04-28")))

df_month_plot <- df_month %>%
  group_by(days_away)%>%
  summarise(avg_score =mean(score, na.rm =T))
ggplot(df_month_plot, aes(x = days_away, y = avg_score))+
  geom_point()+
  geom_vline(xintercept = 0,color ="red")+
  theme_bw()

mod_rd1 <- lm(score ~ after + days_away, data = df_day)
summary(mod_rd1)

mod_rd2 <- lm(score ~ after + days_away, data = df_week)
summary(mod_rd2)

mod_rd3 <- lm(score ~ after + days_away + I(days_away^2), data = df_week)
summary(mod_rd3)


mod_rd4 <- lm(score ~ after + days_away, data = df_month)
summary(mod_rd4)

mod_rd5 <- lm(score ~ after + days_away + I(days_away^2), data = df_month)
summary(mod_rd5)

stargazer(mod_rd1, mod_rd2, mod_rd3, mod_rd4, mod_rd5)


############## 
## PART II: DID
##############
sumdf <- read_csv("summary.csv")

df_with_control <- inner_join(sumdf, df)
# April 22 + May 22
df2 <- df_with_control %>%
  filter(date > ymd("2022-03-31") & date < ymd("2022-05-31"))%>%
  mutate(post = ifelse(date >ymd("2022-04-28"),1,0),
         no_regional_info = ifelse(region_info,0,1))

# Apr 22 + Apr 23
df3 <- df_with_control %>%
  filter(date < ymd("2022-04-29") | date > ymd("2022-05-31"))%>%
  mutate(post = ifelse(date >ymd("2022-04-28"),1,0),
         no_regional_info = ifelse(region_info,0,1))

mod01 <- lm(score~ post+no_regional_info + post*no_regional_info, data = df2)
mod02 <- lm(score~ post+no_regional_info + post*no_regional_info, data = df3)
summary(mod01)
summary(mod02)


mod03 <- lm(score~ post+no_regional_info + post*no_regional_info + rank, data = df2)
mod04 <- lm(score~ post+no_regional_info + post*no_regional_info + rank, data = df3)
summary(mod03)
summary(mod04)


stargazer(mod01, mod02, mod03, mod04, mod05, mod6)

stargazer(mod01, mod03, mod02, mod04, title="Regression Results", 
          column.labels=c("Apr 22 + May 22","Apr 22 + Apr 23"),
          column.separate = c(2,2),
          omit.stat="f", no.space=TRUE)



############## 
## PART III: Homophily
##############

