import winsound
import time

def beep():
  for i in range(0, 3):
    winsound.Beep(2000, 100)
  for i in range(0, 3):
    winsound.Beep(2000, 400)
  for i in range(0, 2):
    winsound.Beep(2000, 50)
  time.sleep(0.7)

if __name__=="__main__":
  beep()
  beep()
  beep()