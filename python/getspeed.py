#get time from routes
#get distance from routes
#separate the time based on the colon
#multiply the first number by 60
#add to the seconds
#divide the distance by divide
#return the calculated speed to the routes
#the speed will also be added to the
def getspeed(time, distance, speed):
    distance = int(distance)
    timesplit = [int(x) for x in time.split(':')]
    timesplit[0] = timesplit[0]*60
    totaltime = sum(timesplit)
    speed = round(distance/totaltime, 2)
    return speed
