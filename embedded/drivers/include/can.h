#ifndef __CAN_H__
#define __CAN_H__

#include <linux/can.h>
#include <stdint.h>

#include <mutex>
#include <thread>
#include <vector>

using std::lock_guard;
using std::mutex;
using std::thread;
using std::vector;

template <typename T>
struct mutexVar {
 private:
  mutex mu;
  T value = -1;

 public:
  void setValue(T data) {
    lock_guard<mutex> l(mu);
    value = data;
  }
  T getValue(void) {
    lock_guard<mutex> l(mu);
    return value;
  }
};

class CanDevice;

class Can {
 private:
  int sock;
  bool isInit = false;
  mutex mu;
  vector<CanDevice *> devices;
  thread t;
  void loop();

 public:
  Can(){};
  ~Can();
  int init(const char *can_i);
  void add(CanDevice *c);
  int read(struct can_frame *msg);
  int send(int id, uint8_t *data, uint8_t size);
};

class CanDevice {
 public:
  CanDevice(Can &bus) : bus(bus) { bus.add(this); }
  Can &bus;
  virtual int parse(struct can_frame &msg) = 0;
};

#endif
