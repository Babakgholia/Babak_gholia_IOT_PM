'''

APM:

Salam babak jan , daryaft shod das khosh


'''



import paho.mqtt.client as mqtt
import time
import adafruit_dht as dht
from typing import Dict, Optional
import random
class Device:
    '''main class for device management'''
    
    def __init__(self, topic, mqtt_broker, port = 1883):
        self.topic = topic
        self.topic_list = topic.split('/')
        self.location=self.topic_list[0]
        self.group=self.topic_list[1]
        self.device_type=self.topic_list[2]
         self.name=self.topic_list[3]
        self.status_topic = f"{self.topic}/status"  #prepared adress for requesting stat from broker
        
        self.mqtt_broker=mqtt_broker
        self.port=port
        self.mqtt_client = mqtt.Client()
        self.current_status = None  
        self.status_received = False  
        
        self.mqtt_client.on_message = self._message  #auto reciving device status on messages from broker
    def _message(self,message):
        stat = message.payload.decode()
        if message.topic == self.status_topic:
            self.current_status = stat
            self.status_received = True
            
    def connect(self):  #making a mqtt connection and keeping it alive for messages from server
        try:
            self.mqtt_client.connect(self.mqtt_broker, self.port)
            self.mqtt_client.loop_start()
            self.mqtt_client.subscribe(self.status_topic)
            print(f'Device {self.name} connected and subscribed to status topic.')
        except Exception as e:   
            print(f"Connection error for {self.name}: {e}")
            
    def disconnect(self):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        print(f'Device {self.name} disconnected.')
       
    def turn_on(self):    #publishing a Turn_on request to broker
        self.mqtt_client.publish(self.topic, 'Turn_on')
        print(f'Device {self.name} turned on.')
        
    def turn_off(self):   #publishing a Turn_off request to broker
        self.mqtt_client.publish(self.topic, 'Turn_off')
        print(f'Device {self.name} turned off.')
        
    def status(self, timeout :Optional[int]= 2) -> str:  #getting device status from broker manually if needed
        self.status_received = False
        self.mqtt_client.publish(self.topic, 'status_request')
        start_time = time.time()
        while not self.status_received and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        if self.current_status is not None:
            return self.current_status
        return "unknown"

class Sensor:
    '''main class for sensor management'''
    def __init__(self, topic:str, pin:int=4):
        self.topic = topic
        self.topic_list = self.topic.split('/')
        self.location = self.topic_list[0]
        self.group = self.topic_list[1]
        self.sensor_type = self.topic_list[2]
        self.name = self.topic_list[3]
        self.pin = pin
        self.last_reading_value = None
    
    def read_sensor(self):   #sending a read request to sensor
        try:
            humidity, temperature = dht.read_retry(dht.DHT22, self.pin)
            if self.sensor_type == 'thermosets':
                self.last_reading_value = temperature
            else:
                self.last_reading_value = humidity
        except Exception as e:
            print(f"Error reading sensor {self.name}: {e}")
            self.last_reading_value = None
        return self.last_reading_value
class Admin_panel:
    '''class to manage all devices and sensors'''
    def __init__(self,gp: Optional[Dict] = None):
        self.gp = gp or {}
        self.devices: Dict[str, Device] = {} #saves topic as the adress and device as the instance of the main class for better usage in class
        self.sensors: Dict[str, Sensor] = {}  #saves topic as the adress and sensor as the instance of the main class for better usage in class
        self._initialize_devices()   #auto arranging devices and sensors on creating an instance of class
        
    def _initialize_devices(self):  #sorting datas like the example in bottom
        for location, groups in self.gp.items():
            for group, device_types in groups.items():
                for device_type, devices in device_types.items():
                    for device_name, config in devices.items():
                        topic = f"{location}/{group}/{device_type}/{device_name}"
                        if device_type in ['termometers']:
                            self.sensors[topic] = Sensor(topic=topic, pin=config['pin'])
        
                        else:
                            self.devices[topic] = Device(topic=topic, mqtt_broker=config['mqtt'], port=config['port'])
                            self.devices[topic].connect()
                            
    def create_gp(self, location: str, group: str, device_type: str, devices: Dict):  #creating a group if neccessary for arranging and prepration
        if location not in self.gp:
            self.gp[location] = {}
        if group not in self.gp[location]:
            self.gp[location][group] = {}
        self.gp[location][group][device_type] = devices
        self._initialize_devices()  
    
    def add_device(self, location: str, group: str, device_type: str, device_name: str, config: f'{Dict} must include mqtt_broker and port for device and pin for sensor'): #automaticly creates groups if not exists no need to def create_gp
        if location not in self.gp:
            self.gp[location] = {}
        if group not in self.gp[location]:
            self.gp[location][group] = {}
        if device_type not in self.gp[location][group]:
            self.gp[location][group][device_type] = {}
        if device_name not in self.gp[location][group][device_type]:
            self.gp[location][group][device_type][device_name] = config
            topic = f"{location}/{group}/{device_type}/{device_name}"
        else :
            print('device already exists')
        
        if device_type in ['termometers']: # can be complited with other sensors group
            pin = config.get('pin', 4)
            self.sensors[topic] = Sensor(topic, pin)
        else:                      #for devices other than read_only sensors
            self.devices[topic] = Device(topic, config['mqtt'], config['port'])
            self.devices[topic].connect()

    def ghost_walk(self,duration):              #randomly turns lamps on and off in 15 to 30 minute time period
        lamp_topics = [topic for topic, device in self.devices.items() if device.device_type == "lamps"]
        start_time=time.time()
        while (time.time() - start_time) < duration:
            target1, target2 = random.sample(lamp_topics, 2)
            device1 = self.devices[target1]
            device2 = self.devices[target2]
            
            device1.turn_on()
            device2.turn_on()
            
            time.sleep(random.choice([900,1800]))
            
            device1.turn_off()
            device2.turn_off()
            
    def turn_on_devices_in_group(self, group_name: str):
        for topic, device in self.devices.items():
            if f"/{group_name}/" in topic:  #prevents simiraty mistakes in matching gp_name
                device.turn_on()
    
    def turn_off_devices_in_group(self, group_name: str):
        for topic, device in self.devices.items():
            if f"/{group_name}/" in topic:  #prevents simiraty mistakes in matching gp_name
                device.turn_off()
    
    def turn_on_all(self): #turns on all devices at same time!!!!
        for device in self.devices.values():
            device.turn_on()
    
    def turn_off_all(self):
        for device in self.devices.values(): #turns off all devices at same time
            device.turn_off()
    
    def get_sensor_status_in_group(self, group_name: str) -> Dict[str, float]:  #returns status of all sensors in a same group as a dict
        sensor_status = {}
        for topic, sensor in self.sensors.items():
            if f"/{group_name}/" in topic:
                sensor_status[sensor.name] = sensor.read_sensor()
        return sensor_status
            
    def get_device_status_in_group(self, group_name: str) -> str: #returns status of all devises in a same group as a string 
        status_list = []
        for topic, device in self.devices.items():
            if f"/{group_name}/" in topic:
                status = device.status()
                status_list.append(f"{device.name}: {status}")
        return ", ".join(status_list)
    
    def get_status_in_device_type(self, device_type: str) -> str: #returns device status of those with same type(e.g. 'lamps')
        status_list = []
        for device in self.devices.values():
            if device.device_type == device_type:
                status = device.status()
                status_list.append(f"{device.name} ({device.location}/{device.group}): {status}")
        return "\n".join(status_list)






'''
example_gp={'home':{
                    'kitchen':{
                                'lamps':{ 
                                            'lamp1':{'mqtt':'any','port':1883},
                                            'lamp2':{'mqtt':'any','port':1883}},
                        
                                'termometers':{ 
                                            'termo1':{'pin':3},
                                            'termo2':{'pin':2}},},
                    'bedroom':{
                                'lamps':{
                                            'lamp1':{'mqtt':'any','port':1883},
                                            'lamp2':{'mqtt':'any','port':1883}},
                                'camera':{
                                            'camera1':{'mqtt':'any','port':1883},
                                            'camera2':{'mqtt':'any','port':1883}}}}}'''
