#ifndef _MotorController__H__
#define _MotorController__H__

#include <stdint.h>  // for uint16_t, uint32_t, uint8_t

#include "can.h"  // for CAN (ptr only), CANDevice
struct can_frame;

#define MotorController_EEPROM_SEND_ID 0xC1
#define MotorController_CLR_FAULTS_ID 0xC1
#define COMMAND_MESSAGE_ID 0xC0

#define WR_SUCCESS_BIT 2

class MotorController : public CANDevice {
 private:
  int motorControllerEnHeartbeat();
  int motorControllerClrFaults();
  int motorControllerInvDis();
  int motorControllerInvEn();
  int motorControllerInvForward20();
  int motorControllerInvForward30();
  int motorControllerCmdNoTorque();
  int motorControllerDischarge();
  int motorControllerIdleHb();
  int motorControllerSendHbMsg(uint16_t torque);
  int motorControllerWriteEeprom(uint16_t addr, uint16_t val);
  int motorControllerReadEeprom(uint16_t addr);
  int motorControllerCmdResponseParse(uint8_t* motorControllerData,
                                      uint16_t filter, bool write);
  int motorControllerInvEnNoTorque();

 public:
  virtual int parser(uint32_t id, uint8_t* data, uint32_t filter);
  virtual int validMsg(can_frame* can_mesg);
  MotorController(CAN* c);
  ~MotorController(){};
  virtual int begin();
};
#endif
