#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <FluxGarage_RoboEyes.h>
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

#define OLED_MOSI 11   // SDA
#define OLED_CLK 13    // SCK
#define OLED_DC 8
#define OLED_RESET 9

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &SPI, OLED_DC, OLED_RESET, -1); // -1: no CS


roboEyes roboEyes;

void setup() {
  Serial.begin(9600);

  if (!display.begin(SSD1306_SWITCHCAPVCC)) {
    Serial.println(F("SSD1306 allocation failed"));
    while (true);
  }

/////////////////////////////////////////////////////////////////////////////////////////////////

  // roboEyes.setMood(HAPPY);
  roboEyes.setWidth(25, 25);   // narrower width
  roboEyes.setHeight(50, 20);  // taller height to get oval shape vertically
  roboEyes.setBorderradius(15, 15);
  roboEyes.setBorderradius(15, 15);

/////////////////////////////////////////////////////////////////////////////////////////////////

  roboEyes.begin(SCREEN_WIDTH, SCREEN_HEIGHT, 100); // screen-width, screen-height, max framerate
  // Define eye shapes, all values in pixels
  //roboEyes.setWidth(36, 36); // byte leftEye, byte rightEye
  //roboEyes.setHeight(36, 36); // byte leftEye, byte rightEye
  //roboEyes.setBorderradius(8, 8); // byte leftEye, byte rightEye
  //roboEyes.setSpacebetween(10); // int space -> can also be negative

  // Define some automated eyes behaviour
  roboEyes.setAutoblinker(ON, 8, 5); // Start auto blinker animation cycle -> bool active, int interval, int variation -> turn on/off, set interval between each blink in full seconds, set range for random interval variation in full seconds
  roboEyes.setIdleMode(ON, 2, 4); // Start idle animation cycle (eyes looking in random directions) -> turn on/off, set interval between each eye repositioning in full seconds, set range for random time interval variation in full seconds
    // Define mood, curiosity and position
  //roboEyes.setMood(DEFAULT); // mood expressions, can be TIRED, ANGRY, HAPPY, DEFAULT
  //roboEyes.setPosition(DEFAULT); // cardinal directions, can be N, NE, E, SE, S, SW, W, NW, DEFAULT (default = horizontally and vertically centered)
  //roboEyes.setCuriosity(ON); // bool on/off -> when turned on, height of the outer eyes increases when moving to the very left or very right

  // Set horizontal or vertical flickering
  //roboEyes.setHFlicker(ON, 2); // bool on/off, byte amplitude -> horizontal flicker: alternately displacing the eyes in the defined amplitude in pixels
  //roboEyes.setVFlicker(ON, 2); // bool on/off, byte amplitude -> vertical flicker: alternately displacing the eyes in the defined amplitude in pixels

  // Play prebuilt oneshot animations
  //roboEyes.anim_confused(); // confused - eyes shaking left and right
  //roboEyes.anim_laugh(); // laughing - eyes shaking up and down
  
  
  roboEyes.setCyclops(ON); // bool on/off -> if turned on, robot has only on eye
  roboEyes.setSpacebetween(-SCREEN_WIDTH / 3);  // Shift eye to the left
}
void loop() {
 roboEyes.update(); // update eyes drawings
}

