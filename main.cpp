#include <Arduino.h>
#include <SPIMemory.h>
#DEFINE SSP SS

SPIFlash flash(SSP); //setup spi flash w/ cs set to D1(GPIO5)
void setup()
{
  flash.begin(); //init
  Serial.begin(9600);
}

enum State
{
  READY,
  WRITE,
  READ,
  ERASE
};
State state = READY;
char rbuf[37];
char ibuf[32];

//spi flash offsets.
int wr_offset = 0x0;
int rd_offset = 0x0;
uint8_t bcount = 0x0;

//COMMANDS: (4 letter)
//IGNR -> IGNORE & CONTINUE
//WRIT -> WRITE
//STOP -> STOP EVERYTHING && RETURN TO READY
//READ -> READ

//DATA SENT FROM PC SHOULD BE [CMD(4) + DATA(32)]

union packed
{
  uint32_t int32;
  byte bytes[4];
};

void clearBufs()
{
  for (int i = 0; i < 37; i++)
    rbuf[i] = 0;
  for (int i = 0; i < 32; i++)
    ibuf[i] = 0;
}

void loop()
{
  switch (state)
  {
  case READY:
    if (Serial.available() > 0)
    {
      Serial.readBytes(rbuf, 4);
      if (strncmp(rbuf, "WRIT", 4) == 0)
        state = WRITE;
      else if (strncmp(rbuf, "RDID", 4) == 0)
      {
        packed JEDEC;
        JEDEC.int32 = flash.getJEDECID();
        Serial.write(JEDEC.bytes, 4);
      }
      else if (strncmp(rbuf, "READ", 4) == 0)
      {
        byte cbuf[4];
        Serial.readBytes(cbuf, 4);
        uint32_t addr;
        addr = (int)*(cbuf) << 24; //send from pc using big endian
        addr += (int)*(cbuf + 1) << 16;
        addr += (int)*(cbuf + 2) << 8;
        addr += (int)*(cbuf + 3);
        char rrbuf[32];
        bool result = flash.readCharArray(addr, rrbuf, 32);
        if (result)
        {
          Serial.print("PASS");
          Serial.write(rrbuf, 32);
        }
        else
          Serial.print("FAIL");
      }
      else if (strncmp(rbuf, "ERAS", 4) == 0)
      {
        bool result = flash.eraseChip();
        clearBufs();
        if (result)
          Serial.print("PASS");
        else
          Serial.print("FAIL");
      }
      else if (strncmp(rbuf, "ECHO", 4) == 0)
        Serial.print("REDY");
      else
        state = READY;
    }
    else
    {
      state = READY;
    }
    break;
  case WRITE:
    if (Serial.available() > 3)
    {
      Serial.readBytes(rbuf, 37); //CMD(4) + COUNT(1) + DATA(32)
      bcount = (int)*(rbuf + 4);
      if (strncmp(rbuf, "IGNR", 4) == 0)
      {
        //open spi if closed
        //write *data* to spi and confirm somehow
        bcount = (int)*(rbuf + 4);
        //write *ibuf*(data) to spi
        bool result = flash.writeCharArray(wr_offset, rbuf + 5, bcount);
        wr_offset = wr_offset+bcount;
        //done
        if (result)
          Serial.print("PASS");
        else
          Serial.print("FAIL");
      }
      else if (strncmp(rbuf, "WRIT", 4) == 0) //WRIT while already in WRITE indicates a start pos change specified in hex(data)
      {
        state = WRITE;
        wr_offset = (int)*(rbuf + 5) << 24; //send from pc using big endian
        wr_offset += (int)*(rbuf + 6) << 16;
        wr_offset += (int)*(rbuf + 7) << 8;
        wr_offset += (int)*(rbuf + 8);
        Serial.print("OKAY");
        packed l;
        l.int32 = wr_offset;
        Serial.write(l.bytes, 4);
      }
      else if (strncmp(rbuf, "STOP", 4) == 0) //RETURN TO READY
      {
        state = READY;
        Serial.print("OKAY");
      }
    }
    break;
  default:
    break;
  }
}
