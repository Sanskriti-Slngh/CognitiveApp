#ifndef _CLIENT_H_
#define _CLIENT_H_

#define REQ_READ_ACCELERATION  0x51
#define REQ_READ_GYROSCOPE     0x52
#define REQ_READ_MAGNETOMETER  0x53
#define REQ_START_LED_GAME     0x54

#define BLUE_BUTTON_PIN     5
#define GREEN_BUTTON_PIN    3
#define RED_BUTTON_PIN      1

#define BLUE_LED_PIN        4
#define GREEN_LED_PIN       2
#define RED_LED_PIN         21

enum {
    BLUE_LED_IDX = 0,
    GREEN_LED_IDX,
    RED_LED_IDX,
    LED_GAME_NUM_LEDS
} led_idx_t;

typedef struct {
    int led_pin;
    int button_pin;
    int on_count;
    int success_count;
} led_data_t;

typedef struct {
    uint8_t   type;
    uint8_t   data[3];
} request_t;

typedef struct {
    uint8_t type;
    uint8_t reserved[3];
    union {
        struct {
            float x;
            float y;
            float z;
        } acc;

        struct {
            float x;
            float y;
            float z;
        } gyro;

        struct {
            float x;
            float y;
            float z;
        } mag;

        struct {
            unsigned short red_on_count;
            unsigned short red_success_count;
            unsigned short green_on_count;
            unsigned short green_success_count;
            unsigned short blue_on_count;
            unsigned short blue_success_count;
        } led_game;
    } u;
} response_t;


#endif // _CLIENT_H_
