#ifndef __mcp__h__
#define __mcp__h__

#include "i2c.h"

#define MCP_DIRA_REG    0x00
#define MCP_DIRB_REG    0x01
#define MCP_GPIOA_REG   0x12
#define MCP_GPIOB_REG   0x13

#define MCP_NUM_PINS    16

static const uint8_t rick_directions[16] = 
{
    1, 0, 1, 1, 1, 1, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 1
};

static const uint8_t morty_directions[16] =
{
    0, 0, 0, 0, 1, 1, 1, 1,
    1, 1, 0, 0, 1, 0, 1, 1
};

class Mcp23017: private I2c {
    private:
        int clear_settings();
        int set_dir(int pin, uint8_t dir);
        uint8_t get_dir(int pin);
    public:
        Mcp23017(int bus, int addr);
        int begin(const uint8_t directions[]);
        uint8_t get_state(int pin);
        int set_state(int pin, uint8_t val);
};
#endif
