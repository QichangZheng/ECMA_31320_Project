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
sumdf <- read_csv("summary.csv")


df <- df %>%
  mutate(after = ifelse(date >ymd("2022-04-28"),1,0),
         no_regional_info = ifelse(region_info,0,1),
         week = floor_date(date, unit = "week"))

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

df_with_control <- inner_join(sumdf, df)
# April 22 + May 22
df2 <- df_with_control %>%
  filter(date > ymd("2022-03-31") & date < ymd("2022-05-31"))%>%
  mutate(after = ifelse(date >ymd("2022-04-28"),1,0),
         no_regional_info = ifelse(region_info,0,1))

# Apr 22 + Apr 23
df3 <- df_with_control %>%
  filter(date < ymd("2022-04-29") | date > ymd("2022-05-31"))%>%
  mutate(after = ifelse(date >ymd("2022-04-28"),1,0),
         no_regional_info = ifelse(region_info,0,1))

mod01 <- lm(score~ after+no_regional_info + after*no_regional_info, data = df2)
mod02 <- lm(score~ after+no_regional_info + after*no_regional_info, data = df3)
summary(mod01)
summary(mod02)


mod03 <- lm(score~ after+no_regional_info + after*no_regional_info + rank, data = df2)
mod04 <- lm(score~ after+no_regional_info + after*no_regional_info + rank, data = df3)
summary(mod03)
summary(mod04)


stargazer(mod01, mod02, mod03, mod04, mod05, mod6)

stargazer(mod01, mod03, mod02, mod04, title="Regression Results", 
          column.labels=c("Apr 22 + May 22","Apr 22 + Apr 23"),
          column.separate = c(2,2),
          omit.stat="f", no.space=TRUE)



############## 
## PART III: Robustness checks
##############

# RD with regional  controls
mod_rd01 <- lm(score ~ after + days_away + no_regional_info + no_regional_info*after, data = df_day)
summary(mod_rd01)

mod_rd02 <- lm(score ~ after + days_away+ no_regional_info + no_regional_info*after, data = df_week)
summary(mod_rd02)

mod_rd03 <- lm(score ~ after + days_away + I(days_away^2)+ no_regional_info + no_regional_info*after, data = df_week)
summary(mod_rd03)


mod_rd04 <- lm(score ~ after + days_away+ no_regional_info + no_regional_info*after, data = df_month)
summary(mod_rd04)

mod_rd05 <- lm(score ~ after + days_away + I(days_away^2)+ no_regional_info + no_regional_info*after, data = df_month)
summary(mod_rd05)

stargazer(mod_rd01, mod_rd02, mod_rd03, mod_rd04, mod_rd05)



# rdd placebo test


df_week3 <- df %>%
  filter(date > ymd("2023-04-15") & date < ymd("2023-04-30"))%>%
  mutate(after = ifelse(date > ymd("2023-04-22"),1,0),
         days_away = as.numeric(date - ymd("2023-04-22")))




mod_rd23 <- lm(score ~ after + days_away, data = df_week3)
summary(mod_rd23)

mod_rd24 <- lm(score ~ after + days_away + I(days_away^2), data = df_week3)
summary(mod_rd24)

mod_rd25 <- lm(score ~ after + days_away +  no_regional_info + no_regional_info*after, data = df_week3)
summary(mod_rd25)

mod_rd26 <- lm(score ~ after + days_away + I(days_away^2)+ no_regional_info + no_regional_info*after, data = df_week3)
summary(mod_rd26)

stargazer(mod_rd23, mod_rd24, mod_rd25, mod_rd26)



# daily estimate
df22 <- df2 %>%
  mutate(date = factor(date))
mod07 <- lm(score~ date+no_regional_info + date*no_regional_info + rank, data = df22)

summary(mod07)

mod07$coefficients[59:113]


dates <-unique(arrange(df2,date)$date)

dates <- dates[-1]
plotdf <- data.frame("date"= dates, "estimate" = mod07$coefficients[59:113])
ggplot(plotdf, aes(x = date,y = estimate))+
  geom_vline(xintercept = ymd("2022-04-28"),color ="red")+
  geom_point()+
  geom_smooth(method = 'glm')+
  theme_bw()+
  labs(y = "Daily Estimate")

# clustered standard errors

clu01 <- felm(score~ after+no_regional_info + after*no_regional_info|0|0|week, data = df2)
clu02 <- felm(score~ after+no_regional_info + after*no_regional_info+rank|0|0|week, data = df2)
summary(clu01)
summary(clu02)
clu03 <- felm(score ~ after + days_away|0|0|week, data = df_week)
clu04 <- felm(score ~ after + days_away + I(days_away^2)|0|0|week, data = df_week)
summary(clu03)
summary(clu04)

stargazer(clu03, clu04, clu01, clu02)
