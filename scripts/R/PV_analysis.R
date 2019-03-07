install.packages("plyr")
library(plyr)

# Get transactions table
PV_analysis <- read.table(file=file.choose(), header=TRUE, sep=",")


# Keep only interesting rows
transactions_cleaned.sub <- data.frame(transactions.df$RowKey, transactions.df$chargingStationId, transactions.df$connectorId, transactions.df$idTag, transactions.df$startTime, transactions.df$stopTime, transactions.df$curPower, transactions.df$maxPowerSeen, transactions.df$chg3phase)


# Summary of the HistoricalTransactions table
#summary(transactions_cleaned.sub)


# Filter table for only production rows
#transactions_production.sub <- transactions_cleaned.sub[grep("production", transactions_cleaned.sub$transactions.df.deployment),]


# Filter table for transactions that have stopTime
#transactions_production_time.sub <- transactions_production.sub[-which(transactions_production.sub$transactions.df.stopTime == ""), ]


# Filter table for transactions that have chg3phase (if they don't, normally it means the connection stopped too soon or there was a problem of some kind)
#transactions_production_time_chg3phase.sub <- transactions_production_time.sub[-which(transactions_production_time.sub$transactions.df.chg3phase == ""), ]


summary(transactions_cleaned.sub)


# Create subset of production transactions keeping only startTime and stopTime columns
user_timings.sub <- data.frame(transactions_cleaned.sub$transactions.df.startTime, transactions_cleaned.sub$transactions.df.stopTime)

str(user_timings.sub)
class(user_timings.sub$transactions_cleaned.sub.transactions.df.startTime)
class(user_timings.sub$transactions_cleaned.sub.transactions.df.stopTime)

user_timings.sub$transactions_cleaned.sub.transactions.df.startTime <- as.character(user_timings.sub$transactions_cleaned.sub.transactions.df.startTime)
class(user_timings.sub$transactions_cleaned.sub.transactions.df.startTime)
user_timings.sub$transactions_cleaned.sub.transactions.df.stopTime <- as.character(user_timings.sub$transactions_cleaned.sub.transactions.df.stopTime)
class(user_timings.sub$transactions_cleaned.sub.transactions.df.stopTime)

?strptime
user_timings.sub$transactions_cleaned.sub.transactions.df.startTime <- as.POSIXct(user_timings.sub$transactions_cleaned.sub.transactions.df.startTime, format = "%Y-%m-%dT%H:%M:%SZ", tz = "UTC")
user_timings.sub$transactions_cleaned.sub.transactions.df.stopTime <- as.POSIXct(user_timings.sub$transactions_cleaned.sub.transactions.df.stopTime, format = "%Y-%m-%dT%H:%M:%S", tz = "UTC")


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