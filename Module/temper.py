import seeed_mlx9064x
import RPi.GPIO as GPIO
import time

class Gpio_set:
    def __init__(self):
        self.TrigPin = 16
        self.EchoPin = 20
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.TrigPin, GPIO.OUT)
        GPIO.setup(self.EchoPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.mlx = seeed_mlx9064x.grove_mxl90641()
        self.frame = [0] * 192
        self.mlx.refresh_rate = seeed_mlx9064x.RefreshRate.REFRESH_4_HZ  # The fastest for raspberry 4
        self.start_time = -1
        self.end_time = -1
        
    def distance(self):
        while(True):
            GPIO.output(self.TrigPin, False)
            time.sleep(0.00001)
            GPIO.output(self.TrigPin, True)
            time.sleep(0.00001)
            GPIO.output(self.TrigPin, False)
            time_first = time.time()
                    
            while GPIO.input(self.EchoPin) == 0 :
                start_time = time.time()
                if start_time-time_first >= 5.0:
                    break
            if start_time-time_first >= 5.0:
                continue
    
            while GPIO.input(self.EchoPin) == 1 :
                end_time = time.time()
    

            duration = end_time - start_time
            distanceCm = duration * 17000
            distanceCm = round(distanceCm, 2)
            if distanceCm <= 100.0:
                #print("clear")
                return distanceCm
            else:
                continue

    def get_temp(self):
        while True:
            self.mlx.getFrame(self.frame)
            if self.frame[0] != 'nan':
                    
                max_temp = max(self.frame)
                #print("Max_temp = " , max_temp)
                    
                result = [num for num in self.frame if num <= 36.0]
                    
                result.sort(reverse=True)
                mean_temp = sum(result[0:3])/3.0           
                #print("mean_temp = ", round(mean_temp, 2))
                    
                distanceCm = self.distance()
                #print("cm:",distanceCm)
                    
                compen_temp = mean_temp + (2.0 + distanceCm / 25)
                #print("compen_temp = ", compen_temp)
                return compen_temp
                
        #except:
         #   print("retry!")
          #  self.get_temp(distanceCm)
"""          
a = Gpio_set()
while True:
    print(a.distance())
    time.sleep(1)
"""
