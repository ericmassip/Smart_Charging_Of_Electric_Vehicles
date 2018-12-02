# User Frequency of connectionTime Analysis

install.packages("fpc")
install.packages("factoextra")
install.packages("doBy")
library(factoextra)
library(fpc)
library(doBy)

#transactions <- read.csv(file=file.choose(), header=TRUE, sep=",")

transactions <- data.frame(user_timings.sub$startTime_hms, user_timings.sub$stopTime_hms, user_timings.sub$timediff)
transactions$userId <- transactions_cleaned.sub$transactions.df.idTag
summary(transactions)

clustering_analysis <- data.frame(transactions$userId, transactions$user_timings.sub.startTime_hms, transactions$user_timings.sub.stopTime_hms, transactions$user_timings.sub.timediff)
clustering_analysis$transactions.userId <- as.character(clustering_analysis$transactions.userId)
clustering_analysis$transactions.user_timings.sub.timediff <- as.numeric(clustering_analysis$transactions.user_timings.sub.timediff)

userIds <- clustering_analysis$transactions.userId
userIds <- unique(userIds)

for (userId in userIds) {
  transactionsTimeDiffForThisUserId <- clustering_analysis[which(clustering_analysis$transactions.userId == userId),]
  vectorizedTransactionsTimeDiffForThisUserId <- transactionsTimeDiffForThisUserId[,4]
  
  filename <- paste("~/Projects/MAI/Thesis/graphs/user_connectionTime_frequency_graphs/", userId, ".png", sep="")
  graphTitle <- paste("Frequency of connectionTime for user", userId)
  
  png(filename, width = 150, height = 150, units='mm', res = 300)
  plot(vectorizedTransactionsTimeDiffForThisUserId, 
       main=graphTitle, 
       xlab="Transaction Nr", 
       ylab="connectionTime (h)",
       type="o",
       col="blue",
       xaxt="n",
       yaxt="n",
       ylim=c(0, 15))
  axis(side = 1, at = seq(0, length(vectorizedTransactionsTimeDiffForThisUserId), by = 1))
  axis(side = 2, at = seq(0, 15, by = 1))
  dev.off()
}