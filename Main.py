# importing the necessary library
import json, time
import math
import statistics
from boltiot import Sms, Bolt



# Creating Class for storing all the device information
class Device(object):    
    SSID = 'Youe Twilio SSID' 
    AUTH_TOKEN = 'Your Twilio Auth_Token' 
    FROM_NUMBER = 'Your Twilio Account Number'
    TO_NUMBER = 'Your Number in which you want the message to be delivered'
    API_KEY = 'Your Bolt wifi module API key'
    DEVICE_ID = 'Your Bolt wifi moule Device Id'
    FRAME_SIZE = 5
    MUL_FACTOR = 10


# creating object of the Class so that it can be easily accessed 
device_info = Device()



# setting up upper bound and lower bound for z-score 
def compute_bounds(history_data,frame_size,factor):
    if len(history_data)<frame_size :
        return None

    if len(history_data)>frame_size :
        del history_data[0:len(history_data)-frame_size]
    Mn=statistics.mean(history_data)
    Variance=0
    for data in history_data :
        Variance += math.pow((data-Mn),2)
    Zn = factor * math.sqrt(Variance / frame_size)
    upper_bound = history_data[frame_size-1]+Zn
    lower_bound = history_data[frame_size-1]-Zn
    return [upper_bound,lower_bound]



# Initializing the z-score bolt and sms variable
mybolt = Bolt(device_info.API_KEY, device_info.DEVICE_ID)
sms = Sms(device_info.SSID, device_info.AUTH_TOKEN, device_info.TO_NUMBER, device_info.FROM_NUMBER)
history_data=[]


# Code for anomly detection
while True:
    response = mybolt.analogRead('A0')
    data = json.loads(response)
    if data['success'] != 1:
        print("Error during retriving the data.")
        print("Error:"+data['value'])
        time.sleep(10)
        continue

    print ("current light intensity is "+data['value'])
    sensor_value=0
    try:
        sensor_value = int(data['value'])
    except e:
        print("Error during parsing the response: ",e)
        continue

    bound = compute_bounds(history_data, device_info.FRAME_SIZE, device_info.MUL_FACTOR)
    if not bound:
        required_data_count = device_info.FRAME_SIZE - len(history_data)
        print("Need ",required_data_count," more data for calculating Z score")
        history_data.append(int(data['value']))
        time.sleep(5)
        continue

    try:
        if sensor_value > bound[0] :
            print("Sudden Increase in light intensity.")
            print("Sending an SMS.")
            response = sms.send_sms("Light is Turned ON")
            print("This is the response ",response)
        elif sensor_value < bound[1]:
            print("Sudden Decrease in light intensity.")
            print("Sending an SMS.")
            response = sms.send_sms("Light is Turned OFF")
            print("This is the response ",response)
        history_data.append(sensor_value);
    except Exception as e:
        print ("Error",e)
    time.sleep(5)
