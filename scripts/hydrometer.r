#!/usr/bin/Rscript

# Note - doesn't filter by version as yet - TODO

# Install package
library(zoo)

## CO@ and tVOC PLOT

png(filename="../static/tilt_hydrometer_gravity.png", width = 1024, height = 768, unit = "px")

# 2021-01-01 00:00:06
# 2025-02-28 23:55:02
setAs("character","myDate", function(from) as.POSIXlt(from, format="%Y-%m-%d %H:%M:%S") )
rawdata <- read.csv("../data/hydrometer.csv", col.names=c('Date.Time','Tilt','Roll', 'Temp', 'Bv', 'SG', 'Board'), colClasses=c('myDate','double','double','double','double', 'double', 'character'), header=FALSE)

# filter out any duff readings
cleandata <- subset(rawdata, SG>=1.0 & SG<=1.05)
attach(cleandata)
summary(cleandata)

## add extra space to right margin of plot within frame
par(mar=c(5, 5, 5, 5) + 0.1)

plot(Date.Time,SG,type="b",lwd=5,pch=20,main="Gravity and Temperature over Time",col="darkorange",xlab="Date/Time",ylab="",ylim=c(1,1.050), axes="FALSE")
r <- as.POSIXct(round(range(Date.Time), "days"))
axis.POSIXct(1, at=seq(r[1], r[2], by = "1 days"), format = "%d")
grid(nx=NA,ny=NULL)

axis(2, ylim=c(1,1.050), col="darkorange",col.axis="darkorange",las=1)
mtext("Gravity",side=2,col="darkorange",line=-1.5)
box()

par(new=TRUE)
plot(Date.Time,Temp,type="b",lwd=5,pch=20,col="red",xlab="",ylab="",ylim=c(0,50),axes=FALSE)

par(new=TRUE)
plot(Date.Time,Bv,type="b",lwd=5,pch=20,col="black",xlab="",ylab="",ylim=c(0,6),axes=FALSE)
axis(4, ylim=c(0,6), col="black",col.axis="black",las=1)
mtext("Battery Voltage",side=4,col="black",line=-1.5)

detach(cleandata)
