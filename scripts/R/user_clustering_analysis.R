# User Clustering analysis

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

timediff.num <- clustering_analysis[, -1]
timediff.std <- scale(timediff.num, center=TRUE, scale= TRUE)
summary(timediff.std)

ed <- dist(timediff.std,method = "euclidean" )
sed <- ed*ed
round(as.matrix(sed),1)

hc_w <- hclust(sed, method = "ward.D2")
# visualise the hierarchical clustering:Dendogram
fviz_dend(hc_w)

fviz_nbclust(timediff.std, FUNcluster= hcut, method = "silhouette", k.max=4)

fviz_dend(hc_w, k=2,
          k_colors=c("red","blue"),
          color_labels_by_k=TRUE)

nhc <- kmeans(timediff.std, 2)
nhc
center <- nhc$centers
print(center, digits=2)

timediff.cluster <- data.frame(clustering_analysis[,1], nhc$cluster)
orderBy(~ nhc.cluster, data=timediff.cluster)

fviz_cluster(nhc, data=timediff.std,
             palette=c("red","blue"),
             ellipse.type="euclid", # concentration ellipse
             star.plot=TRUE ,# add segments from centroids to obs
             repel=TRUE # avoid label overplotting
)


clustering_analysis$transactions.userId
timediff <- data.frame(clustering_analysis$transactions.userId, clustering_analysis$transactions.user_timings.sub.timediff)
timediff$clustering_analysis.transactions.user_timings.sub.timediff <- as.numeric(timediff$clustering_analysis.transactions.user_timings.sub.timediff)
randomdf <- clustering_analysis[which(clustering_analysis$transactions.userId == "04974FFAB63780"),]
avector <- randomdf[,4]
class(avector)
plot(avector)
#randomdf
#plot(randomdf$transactions.user_timings.sub.timediff)

userIds <- clustering_analysis$transactions.userId
userIds <- unique(userIds)
class(userIds)

randomdf <- clustering_analysis[which(clustering_analysis$transactions.userId == "04974FFAB63780"),]
avector <- randomdf[,4]
plot(avector, main="Frequency of connectionTime for user 04974FFAB63780", 
     xlab="Transaction", 
     ylab="connectionTime (h)",
     type="o",
     col="blue")

png("~/Projects/MAI/Thesis/graphs/user_connectionTime_frequency_graphs/heatmap.png", width = 465, height = 225, units='mm', res = 300)
plot(avector)
dev.off()

for (userId in userIds) {
  randomdf <- clustering_analysis[which(clustering_analysis$transactions.userId == userId),]
  avector <- randomdf[,4]
  plot(avector)
}
