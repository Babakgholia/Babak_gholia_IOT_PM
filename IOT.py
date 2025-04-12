import paho.mqtt.client as mqtt
import time
class Device:
    
    def __init__(self, topic, mqtt_broker, port = 1883):
        self.topic = topic
        self.topic_list = topic.split('/')
        self.location=self.topic_list[0]
        self.group=self.topic_list[1]
        self.device_type=self.topic_list[2]
        self.name=self.topic_list[3]
        self.status_topic = f"{self.topic}/status"
        
        self.mqtt_broker=mqtt_broker
        self.port=port
        self.mqtt_client = mqtt.Client()
        self.current_status = None  
        self.status_received = False  
        
        self.mqtt_client.on_message = self._message
    def _message(self,message):
        stat = message.payload.decode()
        if message.topic == f"{self.topic}/status":
            self.current_status = stat
            self.status_received = True
            self.last_update = time.time() 
            
    def connect(self):
        self.mqtt_client.connect(self.mqtt_broker, self.port)
        self.mqtt_client.loop_start()
        self.mqtt_client.subscribe(self.status_topic)
        print('Client connected and subscribed to status topic.')
        
    def disconnect(self):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        print('Client disconnected.')
       
    def turn_on(self):
        self.mqtt_client.publish(self.topic, 'Turn_on')
        print('Device turned on.')
        
    def turn_off(self):
        self.mqtt_client.publish(self.topic, 'Turn_off')
        print('Device turned off.')
        
    def status(self,timeout=2):
        self.status_received = False
        self.mqtt_client.publish(self.topic, 'status_request')
        start_time = time.time()
        while not self.status_received and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        if self.current_status is not None:
            return self.current_status
        return "unknown"
    
class Admin_panel(Device):
    
    def __init__(self, topic, mqtt_broker,port):
        super().__init__(topic, mqtt_broker,port)
        self.groups = {}
        
        
    def create_gp(self, gp_name):
        
        if gp_name not in self.groups:
            self.groups[gp_name] = []
            print(f'group {gp_name} is created')
        else:
            print('your group name is existed already')        
    
    
    def add_device(self,gp_name):
        self.groups[gp_name].append(self.topic)

    def create_multiple_devices(self,group_name,device_type,number_of_devices):
        
        if group_name in self.groups:
            for i in range(1,number_of_devices+1):
                topic=f'home/{group_name}/{device_type}/{device_type}{i}'
                new_device=Device(topic)
                
                self.add_device_to_group(group_name, new_device)
                
                #print...
                

        else:
            pass
    def turn_on_devices_in_group(self,group_name):
        
        if group_name in self.groups:
            
            devices_list=self.groups[group_name]
            
            for device in devices_list:   
                device.turn_on()
            
            
            
            
        else:
            pass
    def trun_on_all(self):
        '''hameye device haro roshan kone
        tooo hame group ha 
        
        
        '''
        pass
        
    def turn_off_all(self):
        '''hameye devcie haro khamosh kone'''
        pass
    
        

    def get_status_in_group(self,group_name):
        
        '''living_room y matn print mikone mige lamp1 on , klamp2 off , lamp3 ,..'''
        pass
    
    
    
    
    def get_status_in_device_type(self,device_type):
        
        ''' device=lamps --> tamame lamp haro status mohem nabashe tooye living rome kojas'''
        pass
#import Adafruity_DHT
class sensor():
    def __init__(self,topic,pin=100):
        self.topic=topic
        self.topic_list=self.topic.split('/')
        self.location=self.topic_list[0]
        self.group=self.topic_list[1]
        self.sensor_type=self.topic_list[2]
        self.name=self.topic_list[3]
        
    def create_sensor():
        pass
    def status_in_group():
        pass
    def read_sensor(self):
        humidity, temperature=Adafruiy_DHT.read_retry(Adafruiy_DHT.DHT22,self.pin)
        
        if self.sensor_type=='thermosets':
            return temperature
        else:
            return humidity
        #import numpy
        #a=numpy.uniform(20,25)
        #return a
        pass
    def get_status_sensor_in_group(self,group_name):
        
        '''
        
        sensor haye yek goroh ro biad doone dooen status ro pas bde
        
        '''
        pass
        
if __name__ == '__main__':
    a1 = 'home/kitchen/lamps/lamp1'
    '''a2 = Device(a1, mqtt_broker = 'broker.emqx.io')
    a2.connect()
    a2.ture_on()
    a2.ture_off()'''
    a2=sensor('home/paking/thermosets/thermo100',pin=431723689473674626392267349727)
    a3=Admin_panel(a1, 'broker.emqx.io')
    a3.create_gp('parking')
    a3.add_device('parking')
    print(a3.groups)


'''def setup_gpio(self):
        
        #GPIO.setup(adad,GPIO.OUT)
        #age lamp --> 17
        #ag dar --> 27
        #ag fan --> 22
        
        #---->
        if self.device_type=='lamps':
            GPIO.setup(17,GPIO.OUT)
        
        elif self.device_type=='doors':
            GPIO.setup(27,GPIO.OUT)
            
        elif self.device_type=='fans':
            GPIO.setup(22,GPIO.OUT)
            
        #elif self.device_type..'''