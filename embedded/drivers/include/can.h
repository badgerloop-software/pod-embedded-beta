#ifndef __CAN_H__
#define __CAN_H__

#include <linux/can.h>
#include <stdint.h>

class Can {
 private:
  int sock;

 public:
  Can();
  int init();
  int canRead(struct can_frame *msg);
  int canSend(uint16_t id, uint8_t *data, int size);
};

#endif
