import time
import math
import smbus
import threading

# 定义PCA9685类
class PCA9685:

	# 寄存器地址定义
	__SUBADR1            = 0x02
	__SUBADR2            = 0x03
	__SUBADR3            = 0x04
	__MODE1              = 0x00
	__PRESCALE           = 0xFE
	__LED0_ON_L          = 0x06
	__LED0_ON_H          = 0x07
	__LED0_OFF_L         = 0x08
	__LED0_OFF_H         = 0x09
	__ALLLED_ON_L        = 0xFA
	__ALLLED_ON_H        = 0xFB
	__ALLLED_OFF_L       = 0xFC
	__ALLLED_OFF_H       = 0xFD

	# 类的构造函数
	def __init__(self, address=0x40, debug=False):
	
    	self.bus = smbus.SMBus(1)		# 选择I2C1
    	self.address = address
    	self.debug = debug
    	if (self.debug):
    		print("Reseting PCA9685")
    	self.write(self.__MODE1, 0x00)
	
	# 向PCA9685发送数据
	def write(self, reg, value):
    	self.bus.write_byte_data(self.address, reg, value)
    	if (self.debug):
      		print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))
	  
	# 从PCA9685读出数据
	def read(self, reg):
    	result = self.bus.read_byte_data(self.address, reg)
    	if (self.debug):
      		print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
    	return result
	
	# 设置PCA9685的频率
	def setPWMFreq(self, freq):
	
	    prescaleval = 25000000.0    
	    prescaleval /= 4096.0       
	    prescaleval /= float(freq)
	    prescaleval -= 1.0
	    if (self.debug):
	      	print("Setting PWM frequency to %d Hz" % freq)
	      	print("Estimated pre-scale: %d" % prescaleval)
	    prescale = math.floor(prescaleval + 0.5)
	    if (self.debug):
	      	print("Final pre-scale: %d" % prescale)

		# 先设置为睡眠模式，才能设置PCA9685的频率
	    oldmode = self.read(self.__MODE1);
	    newmode = (oldmode & 0x7F) | 0x10        
	    self.write(self.__MODE1, newmode)        
	    self.write(self.__PRESCALE, int(math.floor(prescale)))
	    self.write(self.__MODE1, oldmode)
	    time.sleep(0.005)
	    self.write(self.__MODE1, oldmode | 0x80)
	
	# 向LED0的ON、OFF的高位和低位寄存器写入值
  	def setPWM(self, channel, on, off):
	
	    self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
	    self.write(self.__LED0_ON_H+4*channel, on >> 8)
	    self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
	    self.write(self.__LED0_OFF_H+4*channel, off >> 8)
	    if (self.debug):
	      	print("channel: %d  LED_ON: %d LED_OFF: %d" % (channel,on,off))
	  
	def setServoPulse(self, channel, pulse):
		pulse = pulse*4096/20000   
		self.setPWM(channel, 0, int(pulse))

class Server(threading.Thread):

    def run(self): 
	
        global Step0,Step1,Step2,Step3
		global data
        # 进入永真循环 
        while True:  
			data = input();
            if not data:   
                break  
            if data == "Stop":
                Step0 = 0
                Step1 = 0
                Step2 = 0
                Step3 = 0
            elif data == "Forward":
                Step0 = -250
            elif data == "Backward":
                Step0 = 250
            elif data == "TurnLeft":
                Step1 = -250
            elif data == "TurnRight":
                Step1 = 250
            elif data == "Up":
                Step2 = -250
            elif data == "Down":
                Step2 = 250
            elif data == "Left":
                Step3 = 250
            elif data == "Right":
                Step3 = -250
            print(data)    
            
			
def timerfunc():
	global Step0,Step1,Step2,Step3
	global Pos0,Pos1,Pos2,Pos3
	global pwm

	if(Step0 != 0):
		Pos0 += Step0
		if(Pos0 >= 2500): 
			Pos0 = 2500
		if(Pos0 <= 500):
			Pos0 = 500
		pwm.setServoPulse(0,Pos0)    
		
	if(Step1 != 0):
		Pos1 += Step1
		if(Pos1 >= 2500): 
			Pos1 = 2500
		if(Pos1 <= 500):
			Pos1 = 500
		pwm.setServoPulse(1,Pos1)   
	
	if(Step2 != 0):
		Pos2 += Step2
		if(Pos2 >= 2500): 
			Pos2 = 2500
		if(Pos2 <= 500):
			Pos2 = 500
		pwm.setServoPulse(2,Pos2)   
		
	if(Step3 != 0):
		Pos3 += Step3
		if(Pos3 >= 2500): 
			Pos3 = 2500
		if(Pos3 <= 500):
			Pos3 = 500
		pwm.setServoPulse(3,Pos3)   
	
	global t        
	t = threading.Timer(0.02, timerfunc)
	t.start()

# 实例化PCA9685类
pwm = PCA9685(0x40)
pwm.setPWMFreq(50)

Pos0 = 1500  
Pos1 = 1500 
Pos2 = 1500 
Pos3 = 1500 

Step0 = 0  
Step1 = 0  
Step2 = 0  
Step3 = 0  

# 开启线程
t = threading.Timer(0.02, timerfunc)
t.setDaemon(True)
t.start()
# 开启线程
server = Servers()
server.start()


