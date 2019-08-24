import threading
import datetime
class Time_test:
    def test(self,strs):
        print(strs)

        print('当前线程数为{}'.format(threading.activeCount()))
        timer = threading.Timer(2,self.test,["adga"])

        timer.start()
        print(timer)

print('当前线程数为{}'.format(threading.activeCount()))
test1 = Time_test()
timer=threading.Timer(2,test1.test,['egag'])
timer.start()
print('start,当前线程数为{}'.format(threading.activeCount()))
