install.packages("plyr")
library(plyr)

# Get transactions table
PV_data <- read.table(file=file.choose(), header=TRUE, sep=",")

PV_data_bp <- PV_data

# Summary of the PV data
summary(PV_data_bp)

#str(PV_data_bp)
PV_data_bp$date <- as.character(PV_data_bp$date)
PV_data_bp$power_sum <- as.numeric(PV_data_bp$power_sum)

#PV_data_bp$date

#?strptime
PV_data_bp$date <- as.POSIXlt(PV_data_bp$date, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")

#PV_data_bp$date$mon + 1

# Plot density function based on time of the day

install.packages("ggplot2")
install.packages("lubridate")
install.packages("scales")
install.packages("hms")

library(ggplot2)
library(lubridate)
library(scales)
library(hms)

PV_data_bp$month <- ifelse(PV_data_bp$date$mon + 1 == 1, "Jan", 
                           ifelse(PV_data_bp$date$mon + 1 == 2, "Feb",
                                  ifelse(PV_data_bp$date$mon + 1 == 3, "Mar",
                                         ifelse(PV_data_bp$date$mon + 1 == 4, "Apr",
                                                ifelse(PV_data_bp$date$mon + 1 == 5, "May",
                                                       ifelse(PV_data_bp$date$mon + 1 == 6, "Jun",
                                                              ifelse(PV_data_bp$date$mon + 1 == 7, "Jul",
                                                                     ifelse(PV_data_bp$date$mon + 1 == 8, "Aug",
                                                                            ifelse(PV_data_bp$date$mon + 1 == 9, "Sep",
                                                                                   ifelse(PV_data_bp$date$mon + 1 == 10, "Oct",
                                                                                          ifelse(PV_data_bp$date$mon + 1 == 11, "Nov",
                                                                                                 ifelse(PV_data_bp$date$mon + 1 == 12, "Dec", "Don't know what month I live in"))))))))))))

PV_data_bp_year <- PV_data_bp[which(PV_data_bp$power_sum > 0), ]
PV_data_bp_year$date_hms <- hms::hms(second(PV_data_bp_year$date), minute(PV_data_bp_year$date), hour(PV_data_bp_year$date))
PV_data_bp_year$date_hms <- as.POSIXct(PV_data_bp_year$date_hms)

PV_data_bp_summer <- PV_data_bp[which(PV_data_bp$power_sum > 0 & (PV_data_bp$month == "Jun" | PV_data_bp$month == "Jul" | PV_data_bp$month == "Aug")), ]
PV_data_bp_summer$date_hms <- hms::hms(second(PV_data_bp_summer$date), minute(PV_data_bp_summer$date), hour(PV_data_bp_summer$date))
PV_data_bp_summer$date_hms <- as.POSIXct(PV_data_bp_summer$date_hms)

PV_data_bp_autumn <- PV_data_bp[which(PV_data_bp$power_sum > 0 & (PV_data_bp$month == "Sep" | PV_data_bp$month == "Oct" | PV_data_bp$month == "Nov")), ]
PV_data_bp_autumn$date_hms <- hms::hms(second(PV_data_bp_autumn$date), minute(PV_data_bp_autumn$date), hour(PV_data_bp_autumn$date))
PV_data_bp_autumn$date_hms <- as.POSIXct(PV_data_bp_autumn$date_hms)

PV_data_bp_winter <- PV_data_bp[which(PV_data_bp$power_sum > 0 & (PV_data_bp$month == "Dec" | PV_data_bp$month == "Jan" | PV_data_bp$month == "Feb")), ]
PV_data_bp_winter$date_hms <- hms::hms(second(PV_data_bp_winter$date), minute(PV_data_bp_winter$date), hour(PV_data_bp_winter$date))
PV_data_bp_winter$date_hms <- as.POSIXct(PV_data_bp_winter$date_hms)

PV_data_bp_spring <- PV_data_bp[which(PV_data_bp$power_sum > 0 & (PV_data_bp$month == "Mar" | PV_data_bp$month == "Apr" | PV_data_bp$month == "May")), ]
PV_data_bp_spring$date_hms <- hms::hms(second(PV_data_bp_spring$date), minute(PV_data_bp_spring$date), hour(PV_data_bp_spring$date))
PV_data_bp_spring$date_hms <- as.POSIXct(PV_data_bp_spring$date_hms)

PV_data_bp_Jan <- PV_data_bp[which(PV_data_bp$month == "Jan" & PV_data_bp$power_sum > 0), ]
PV_data_bp_Jan$date_hms <- hms::hms(second(PV_data_bp_Jan$date), minute(PV_data_bp_Jan$date), hour(PV_data_bp_Jan$date))
PV_data_bp_Jan$date_hms <- as.POSIXct(PV_data_bp_Jan$date_hms)

# PV_data density function not scaled
ggplot(aes(x = date_hms, y = power_sum), data = PV_data_bp_autumn) +
  geom_point(aes(colour = factor(month))) +
  scale_x_datetime(breaks = date_breaks("1 hour"), labels=date_format("%H:%M")) +
  scale_y_continuous(breaks = c(0, 50000, 100000, 150000, 200000, 250000, 300000), limits = c(0,300000)) +
  labs(title = "PV_data Autumn density function")

#geom_bin2d
#geom_count (similar to point but it's counting, not very useful I think)
#geom_density2d or geom_density_2d (weird)
#geom_jitter (same as point)
#geom_line (it has a weird line in the middle)
#geom_point
#geom_polygon
#geom_step
