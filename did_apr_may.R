library(readr)
library(tidyverse)
library(lubridate)
library(stargazer)
library(fixest)
library(lfe)
library(data.table)

## Load data

df <- read_csv("merged_data_0508.csv")

sumdf <- read_csv("summary.csv")

df_with_control <- inner_join(sumdf, df)


df2 <- df %>%
  filter(date > ymd("2022-03-31") & date < ymd("2022-05-31"))%>%
  mutate(post = ifelse(date >ymd("2022-04-28"),1,0),
         no_regional_info = ifelse(region_info,0,1))

keywords <- df2 %>%
  group_by(keyword)%>%
  summarise(ct =n_distinct(no_regional_info))%>%
  filter(ct ==2)
  
df2_cut <- df2 %>%
  inner_join(keywords)

df3 <- df %>%
  filter(date < ymd("2022-04-29") | date > ymd("2022-05-31"))%>%
  mutate(post = ifelse(date >ymd("2022-04-28"),1,0),
         no_regional_info = ifelse(region_info,0,1))


mod01 <- lm(score~ post+no_regional_info + post*no_regional_info, data = df2)
mod02 <- lm(score~ post+no_regional_info + post*no_regional_info, data = df3)
summary(mod)


mod03 <- lm(score~ post+no_regional_info + post*no_regional_info + rank, data = df2)
mod04 <- lm(score~ post+no_regional_info + post*no_regional_info + rank, data = df3)
summary(mod03)
summary(mod04)

mod05 <- felm(score~ post+no_regional_info + post*no_regional_info |keyword, data = df2)
mod06 <- felm(score~ post+no_regional_info + post*no_regional_info |keyword, data = df3)
summary(mod05)
summary(mod06)

stargazer(mod01, mod02, mod03, mod04, mod05, mod6)

stargazer(mod01, mod03, mod02, mod04, title="Regression Results", 
          align=TRUE, dep.var.labels=c("Apr 22 + May 22","Apr 22 + Apr 23"), 
          omit.stat="f", no.space=TRUE)




ggplot(df2, aes(x = factor(date),y = score))+
  geom_point()+
  theme_bw()


# overview of data
num_sum1 <- df2 %>%
  drop_na()%>%
  group_by(date)%>%
  summarise(mean_score = mean(score, na.rm =T),
            unique_keyword = n_distinct(keyword))

avg <- ggplot(num_sum1, aes(x = date,y = mean_score))+
  geom_vline(xintercept = ymd("2022-04-28"),color ="red")+
  geom_hline(yintercept = quantile_score, color ="blue")+
  geom_point()+
  geom_line()+
  geom_smooth()+
  theme_bw()+
  labs(y = "Average Sentiment Score")
ggsave("D:/ecma31320/avg sentiment.png", plot=avg, width = 10, height = 6)


plotdf <- df2_cut %>%
  drop_na()%>%
  group_by(date, no_regional_info)%>%
  summarise(mean_score = mean(score, na.rm =T),
            unique_keyword = n_distinct(keyword))%>%
  mutate(no_regional_info = as.factor(no_regional_info))
ggplot(plotdf, aes(x = date,y = mean_score, color = no_regional_info))+
  geom_vline(xintercept = ymd("2022-04-28"),color ="red")+
  geom_point()+
  geom_smooth(method = 'loess')+
  theme_bw()+
  labs(y = "Average Sentiment Score")

week_sum <- df2 %>%
  mutate(week = floor_date(date, unit = "week"))%>%
  mutate(negative_sentiment =ifelse(score >0.8,1,0))%>%
  group_by(week,no_regional_info)%>%
  summarise(negative_post_ct = sum(negative_sentiment,na.rm=T),
            total_post_ct = n(),
            avg_sentiment = mean(score, na.rm =T))%>%
  mutate(negative_perc = negative_post_ct/total_post_ct)
  


ggplot(week_sum, aes(x = week, y = negative_perc, color = factor(no_regional_info)))+
  geom_point()+
  geom_line()+
  geom_vline(xintercept = ymd("2022-04-28"),color ="red")+
  theme_bw()


quantile_by_date <- df2%>%
  group_by(date)%>%
  summarise(bottom10 = quantile(score,probs = .8, na.rm =T))

df2_cut <- df2%>%
  drop_na()%>%
  inner_join(quantile_by_date)%>%
  filter(score > bottom10)


plotdf2 <- df2_cut %>%
  group_by(date, no_regional_info)%>%
  summarise(mean_score = mean(score, na.rm =T),
            unique_keyword = n_distinct(keyword))%>%
  mutate(no_regional_info = as.factor(no_regional_info))
ggplot(plotdf2, aes(x = date,y = mean_score, color = no_regional_info))+
  geom_vline(xintercept = ymd("2022-04-28"),color ="red")+
  geom_point()+
  geom_line()+
  geom_smooth()+
  theme_bw()+
  labs(y = "Average Sentiment Score")


# daily estimate

df22 <- df2 %>%
  mutate(date = factor(date))
mod07 <- lm(score~ date+no_regional_info + date*no_regional_info + rank, data = df22)

summary(mod07)

mod07$coefficients[59:113]
plotdf <- data.frame("date"= dates, "estimate" = mod07$coefficients[59:113])
ggplot(plotdf, aes(x = date,y = estimate))+
  geom_vline(xintercept = ymd("2022-04-28"),color ="red")+
  geom_point()+
  geom_smooth(method = 'glm')+
  theme_bw()+
  labs(y = "Daily Estimate")

dates <-unique(arrange(df2,date)$date)

dates <- dates[-1]

#
quantile_score <- quantile(df2$score,probs = .5, na.rm =T)
# median score

num_sum <- df2 %>%
  drop_na()%>%
  mutate(negative_sentiment =ifelse(score >quantile_score,1,0))%>%
  group_by(date,region_info)%>%
  summarise(negative_post_ct = sum(negative_sentiment,na.rm=T),
            total_post_ct = n())%>%
  mutate(negative_perc = negative_post_ct/total_post_ct)

ggplot(num_sum, aes(x = date,y =negative_post_ct, color =region_info))+
  geom_vline(xintercept = ymd("2022-04-28"),color ="red")+
  geom_point()+
  geom_line()+
  theme_bw()+
  labs(y = "Percentage of Negtaive-Sentiment Posts")


quantile_score <- quantile(df2$score,probs = .9, na.rm =T)
# median score

num_sum <- df2 %>%
  drop_na()%>%
  mutate(negative_sentiment =ifelse(score >0.85,1,0))%>%
  group_by(date,region_info)%>%
  summarise(negative_post_ct = sum(negative_sentiment,na.rm=T),
            total_post_ct = n())%>%
  mutate(negative_perc = negative_post_ct/total_post_ct)


num_sum_reg <- num_sum %>%
  mutate(post = ifelse(date >=ymd("2022-04-28"),1,0),
         no_regional_info = ifelse(region_info,0,1))
mod2 <- lm(negative_perc~ post+no_regional_info + post*no_regional_info, data = num_sum_reg)

summary(mod2)
####
quantile_score <- quantile(df3$score,probs = .9, na.rm =T)
num_sum3 <- df3 %>%
  drop_na()%>%
  mutate(negative_sentiment =ifelse(score >0.857,1,0))%>%
  group_by(date,region_info)%>%
  summarise(negative_post_ct = sum(negative_sentiment,na.rm=T),
            total_post_ct = n())%>%
  mutate(negative_perc = negative_post_ct/total_post_ct)


num_sum_reg3 <- num_sum3 %>%
  mutate(post = ifelse(date >=ymd("2022-04-28"),1,0),
         no_regional_info = ifelse(region_info,0,1))
mod3 <- lm(negative_perc~ post+no_regional_info + post*no_regional_info, data = num_sum_reg3)

summary(mod3)

stargazer(mod2)

# further cut of the data
quantile_by_date <- df2 %>%
  group_by(date)%>%
  summarise(top_1 = quantile(score,probs = .05, na.rm =T),
            bottom1 = quantile(score,probs = .95, na.rm =T))

df_cut <- df2 %>%
  drop_na()%>%
  inner_join(quantile_by_date)%>%
  filter(score >top_1 &score < bottom1)

quantile_score <- quantile(df_cut$score,probs = .5, na.rm =T)
hist1<- ggplot(df2, aes(x= score))+
  geom_histogram()+
  geom_vline(xintercept = quantile_score, color = "red")+
  theme_bw()+
  labs(x= "sentiment score")

hist2<- ggplot(df_cut, aes(x= score))+
  geom_histogram()+
  geom_vline(xintercept = quantile_score, color = "red")+
  theme_bw()+
  labs(x= "sentiment score")
ggsave("D:/ecma31320/hist2.png", plot=hist2, width = 8, height = 6)



quantile_score <- quantile(df_cut$score,probs = .8, na.rm =T)
df_cut <- df_cut %>%
  mutate(negative_sentiment =ifelse(score >quantile_score,1,0))


num_sum <- df_cut %>%
  group_by(date,region_info)%>%
  summarise(negative_post_ct = sum(negative_sentiment,na.rm=T),
            total_post_ct = n())%>%
  mutate(negative_perc = negative_post_ct/total_post_ct)

ggplot(num_sum, aes(x = date,y = negative_perc, color =region_info))+
  geom_vline(xintercept = ymd("2022-04-28"),color ="red")+
  geom_point()+
  geom_smooth()+
  theme_bw()+
  labs(y = "Percentage of Negtaive-Sentiment Posts")
ggsave("D:/ecma31320/did_0401_0528.png", plot=p0, width = 8, height = 6)




# regression
df_cut3 <- df_cut %>%
  mutate(post = ifelse(date >=ymd("2022-04-28"),1,0),
         has_regional_info = ifelse(region_info,1,0))




mod <- lm(score~ post+has_regional_info + post*has_regional_info, data = df_cut3)

summary(mod)
stargazer(mod)

num_sum <- num_sum %>%
  mutate(post = ifelse(date >=ymd("2022-04-28"),1,0))
  

mod2 <- lm(negative_perc~ post+region_info + post*region_info, data = num_sum)

summary(mod2)

stargazer(mod2)

quantile_by_date2 <- df %>%
  group_by(date)%>%
  summarise(top_1 = quantile(score,probs = .4, na.rm =T),
            bottom1 = quantile(score,probs = .99, na.rm =T))

df_cut3 <- df %>%
  drop_na()%>%
  inner_join(quantile_by_date2)%>%
  filter(score <top_1)
score_sum <- df_cut3 %>%
  mutate(post = ifelse(date >=ymd("2022-04-28"),1,0),
         has_regional_info = ifelse(region_info,1,0))%>%
  filter(date >ymd("2022-04-25")&date <ymd("2022-05-01"))%>%
  group_by(date, has_regional_info)%>%
  summarise(ct = n(),
            avg_score =mean(score,na.rm=T))

p4 <- ggplot(score_sum, aes(x = date,y = avg_score, color =factor(has_regional_info)))+
  geom_vline(xintercept = ymd("2022-04-28"),color ="red")+
  geom_point()+
  geom_line()+
  theme_bw()+
  labs(y = "Mean Sentiment Score")

ggsave("D:/ecma31320/avg_sentiment_score.png", plot=p4, width = 8, height = 6)


hist1 <- ggplot(df, aes(x= score))+
  geom_histogram()+
  theme_bw()+
  labs(x= "sentiment score")

ggsave("D:/ecma31320/hist1.png", plot=hist1, width = 8, height = 6)




score_sum <- df2 %>%
  filter(date >ymd("2022-04-25")&date <ymd("2022-05-01"))%>%
  group_by(date, has_regional_info)%>%
  summarise(ct = n(),
            avg_score =mean(score,na.rm=T))

p2 <- ggplot(score_sum, aes(x = date,y = avg_score, color =factor(has_regional_info)))+
  geom_vline(xintercept = ymd("2022-04-28"),color ="red")+
  geom_point()+
  geom_line()+
  theme_bw()+
  labs(y = "Mean Sentiment Score")


ggsave("D:/ecma31320/y_mean_sentiment.png", plot=p2, width = 8, height = 6)











### RD: examine the general trend
df <- read_csv("merged_data0524.csv")

df_day <- df %>%
  filter(date == ymd("2022-04-28")) %>%
  mutate(ip_revealed = ifelse(is.na(ip_loc),0,1))
  

df_day%>%
  group_by(ip_revealed)%>%
  summarise(ct=n())


df_week <- df %>%
  filter(date > ymd("2022-04-20") & date < ymd("2022-05-06"))%>%
  mutate(after = ifelse(date >=ymd("2022-04-28"),1,0))

mod_rd1 <- lm(score ~ ip_revealed, data = df_day)
summary(mod_rd1)

mod_rd2 <- lm(score ~ after, data = df_week)
summary(mod_rd2)


