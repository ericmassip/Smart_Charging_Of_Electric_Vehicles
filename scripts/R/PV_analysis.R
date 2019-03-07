install.packages("plyr")
library(plyr)

# Get transactions table
PV_data <- read.table(file=file.choose(), header=TRUE, sep=",")

PV_data_bp <- PV_data

# Summary of the PV data
summary(PV_data_bp)

str(PV_data_bp)
PV_data_bp$date <- as.character(PV_data_bp$date)

PV_data_bp$date

#?strptime
PV_data_bp$date <- as.POSIXct(PV_data_bp$date, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")

PV_data_bp$date

# Plot density function based on time of the day

install.packages("ggplot2")
install.packages("lubridate")
install.packages("scales")
install.packages("hms")

library(ggplot2)
library(lubridate)
library(scales)
library(hms)


user_timings.sub$startTime_hms <- hms::hms(second(user_timings.sub$transactions_cleaned.sub.transactions.df.startTime), minute(user_timings.sub$transactions_cleaned.sub.transactions.df.startTime), hour(user_timings.sub$transactions_cleaned.sub.transactions.df.startTime))
user_timings.sub$startTime_hms <- as.POSIXct(user_timings.sub$startTime_hms)

# startTime density function not scaled
ggplot(user_timings.sub, aes(startTime_hms)) + 
  geom_density(fill = "red", alpha = 0.5) + #also play with adjust such as adjust = 0.5
  scale_x_datetime(breaks = date_breaks("2 hours"), labels=date_format("%H:%M"))

# startTime density function scaled
ggplot(user_timings.sub) + 
  geom_density( aes(x = startTime_hms, y = ..scaled..), fill = "red", alpha = 0.5) +
  labs(title = "Arrival time density function") +
  scale_x_datetime(breaks = date_breaks("2 hours"), labels=date_format("%H:%M"))

summary(user_timings.sub$startTime_hms)
quantile(user_timings.sub$startTime_hms)
var(user_timings.sub$startTime_hms)
sd(user_timings.sub$startTime_hms)


user_timings.sub$stopTime_hms <- hms::hms(second(user_timings.sub$transactions_cleaned.sub.transactions.df.stopTime), minute(user_timings.sub$transactions_cleaned.sub.transactions.df.stopTime), hour(user_timings.sub$transactions_cleaned.sub.transactions.df.stopTime))
user_timings.sub$stopTime_hms <- as.POSIXct(user_timings.sub$stopTime_hms)

ggplot(user_timings.sub, aes(stopTime_hms)) + 
  geom_density(fill = "red", alpha = 0.5) + #also play with adjust such as adjust = 0.5
  scale_x_datetime(breaks = date_breaks("2 hours"), labels=date_format("%H:%M"))

ggplot(user_timings.sub) + 
  geom_density( aes(x = stopTime_hms, y = ..scaled..), fill = "red", alpha = 0.5) +
  labs(title = "Departure time density function") +
  scale_x_datetime(breaks = date_breaks("2 hours"), labels=date_format("%H:%M"))

summary(user_timings.sub$stopTime_hms)
quantile(user_timings.sub$stopTime_hms)
var(user_timings.sub$stopTime_hms)
sd(user_timings.sub$stopTime_hms)


# Plot density function of time difference between arrival and departure times
user_timings.sub$timediff <- with(user_timings.sub, difftime(user_timings.sub$transactions_cleaned.sub.transactions.df.stopTime, user_timings.sub$transactions_cleaned.sub.transactions.df.startTime, units="hours"))

ggplot(user_timings.sub) + 
  geom_density( aes(x = timediff, y = ..scaled..), fill = "red", alpha = 0.5) +
  labs(title = "Time difference between arrival and departure time") +
  scale_x_continuous(breaks = c(1:15), labels = c(1:15), limits = c(NA,15), trans = "identity")

summary(user_timings.sub$timediff)
quantile(user_timings.sub$timediff)
var(user_timings.sub$timediff)
sd(user_timings.sub$timediff)