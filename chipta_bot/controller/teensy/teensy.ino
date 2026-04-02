#include <micro_ros_arduino.h>
#include <stdio.h>
#include <rcl/rcl.h>
#include <rcl/error_handling.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>
#include <geometry_msgs/msg/twist.h>
#include <std_msgs/msg/int64.h>

#define RPWM1 23   // fr    
#define LPWM1 22     
#define RPWM2 18     //fl
#define LPWM2 19      
#define RPWM3  2    // rr
#define LPWM3 4
#define RPWM4  5    // rl
#define LPWM4 21

#define FR_ENC_A 34   // fr    
#define FR_ENC_B 35    
#define FL_ENC_A 32     //fl
#define FL_ENC_B 33      
#define RR_ENC_A  26    // rr
#define RR_ENC_B 25
#define RL_ENC_A  14    // rl
#define RL_ENC_B 27

rcl_publisher_t fr_enc_pub;
rcl_publisher_t fl_enc_pub;
rcl_publisher_t rr_enc_pub;
rcl_publisher_t rl_enc_pub;
rcl_subscription_t pwm_subscriber;
rclc_executor_t executor;
rcl_allocator_t allocator;
rclc_support_t support;
rcl_node_t node;
rcl_timer_t timer;

std_msgs__msg__Int64 fr_enc_msg; 
std_msgs__msg__Int64 fl_enc_msg; 
std_msgs__msg__Int64 rr_enc_msg; 
std_msgs__msg__Int64 rl_enc_msg; 

volatile long fr_enc_value = 0;
// int32_t fr_last_enc_value = 0;
volatile long fl_enc_value = 0;
// int32_t fl_last_enc_value = 0;
volatile long rr_enc_value = 0;
// int32_t rr_last_enc_value = 0;
volatile long rl_enc_value = 0;
// int32_t rl_last_enc_value = 0;

std_msgs__msg__Int64 pwm_msg;   
bool micro_ros_init_successful;

int16_t rr_pwm;
int16_t rl_pwm;
int16_t fr_pwm;
int16_t fl_pwm;
int64_t combined_value;

#define LED_PIN 13
#define RCCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){error_loop();}}
#define RCSOFTCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){error_loop();}}

void error_loop(){
  while(1){
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    delay(100);
  }
}

void bts_driver(int rpwm, int lpwm, int pwm) {

  if (pwm > 0) {
    analogWrite(rpwm, pwm);   
    analogWrite(lpwm, 0);     
  } 
  else if (pwm < 0) {
    analogWrite(rpwm, 0);     
    analogWrite(lpwm, abs(pwm));
  } 
  else {
    analogWrite(rpwm, 0);     
    analogWrite(lpwm, 0);     
  }
}

void smartElex_driver(int dir, int pwm_pin, int value) {

  if (value > 0) {
    digitalWrite(dir, LOW);
    analogWrite(pwm_pin, value);   
  } 
  else if (value < 0) {
    digitalWrite(dir, HIGH);
    analogWrite(pwm_pin, abs(value));   
  } 
  else {
    analogWrite(pwm_pin, 0); 
  }
}

void pwm_decode(int64_t combined_value) {
  
  rr_pwm = (combined_value % 1000)-255;           
  combined_value /= 1000;
  rl_pwm = (combined_value % 1000)-255;           
  combined_value /= 1000;
  fr_pwm = (combined_value % 1000)-255;           
  combined_value /= 1000;
  fl_pwm = (combined_value % 1000)-255; 

  bts_driver(RPWM1, LPWM1, fr_pwm);    // fr
  bts_driver(RPWM2, LPWM2, fl_pwm);   // fl
  bts_driver(RPWM3, LPWM3, rr_pwm);    // rr
  bts_driver(RPWM4, LPWM4, rl_pwm);    // rl
}


void PWM_callback(const void * msgin) {
  const std_msgs__msg__Int64 * msg = (const std_msgs__msg__Int64 *)msgin;
  
  combined_value = msg->data;   

  // Serial.println(combined_value);
  pwm_decode(combined_value);

}

void IRAM_ATTR update_fr_enc() {
  if (digitalRead(FR_ENC_A) == digitalRead(FR_ENC_B))  fr_enc_value--;
  else fr_enc_value++;
}
void IRAM_ATTR update_fl_enc() {
  if (digitalRead(FL_ENC_A) == digitalRead(FL_ENC_B)) fl_enc_value++;
  else fl_enc_value--;
}
void IRAM_ATTR update_rr_enc() {
  if (digitalRead(RR_ENC_A) == digitalRead(RR_ENC_B)) rr_enc_value--;
  else rr_enc_value++;
}
void IRAM_ATTR update_rl_enc() {
  if (digitalRead(RL_ENC_A) == digitalRead(RL_ENC_B)) rl_enc_value++;
  else rl_enc_value--;
}

void setup() {

  Serial.begin(115200);

  pinMode(RPWM1,OUTPUT);
  pinMode(LPWM1,OUTPUT);
  pinMode(RPWM2,OUTPUT);
  pinMode(LPWM2,OUTPUT);
  pinMode(RPWM3,OUTPUT);
  pinMode(LPWM3,OUTPUT);
  pinMode(RPWM4,OUTPUT);
  pinMode(LPWM4,OUTPUT);


  pinMode(FR_ENC_A,INPUT);
  pinMode(FR_ENC_B,INPUT);
  attachInterrupt(digitalPinToInterrupt(FR_ENC_A), update_fr_enc, RISING);
  fr_enc_msg.data = 0;

  pinMode(FL_ENC_A,INPUT);
  pinMode(FL_ENC_B,INPUT);
  attachInterrupt(digitalPinToInterrupt(FL_ENC_A), update_fl_enc, RISING);
  fl_enc_msg.data = 0;  

  pinMode(RR_ENC_A,INPUT);
  pinMode(RR_ENC_B,INPUT);
  attachInterrupt(digitalPinToInterrupt(RR_ENC_A), update_rr_enc, RISING);
  rr_enc_msg.data = 0;

  pinMode(RL_ENC_A,INPUT);
  pinMode(RL_ENC_B,INPUT);
  attachInterrupt(digitalPinToInterrupt(RL_ENC_A), update_rl_enc, RISING);
  rl_enc_msg.data = 0;


  Serial.println("aagya idhar pench");
  set_microros_transports();
  // set_microros_serial_transports();

  // set_microros_wifi_transports("OPPO", "123456789", "192.168.100.23", 8888);
  // Serial.print("wifi chalgya pencho\n\n");
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);  
  
  // delay(2000);I

  allocator = rcl_get_default_allocator();

   //create init_options
  RCCHECK(rclc_support_init(&support, 0, NULL, &allocator));

  // create node
  RCCHECK(rclc_node_init_default(&node, "micro_ros_arduino_node", "", &support));

  // publisher for the enc 
  RCCHECK(rclc_publisher_init_default(
    &fr_enc_pub,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int64),
    "fr_encoder_ticks"));
  RCCHECK(rclc_publisher_init_default(
    &fl_enc_pub,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int64),
    "fl_encoder_ticks"));
  RCCHECK(rclc_publisher_init_default(
    &rr_enc_pub,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int64),
    "rr_encoder_ticks"));
  RCCHECK(rclc_publisher_init_default(
    &rl_enc_pub,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int64),
    "rl_encoder_ticks"));

  // create subscriber for pwm 
  RCCHECK(rclc_subscription_init_default(
    &pwm_subscriber,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int64),
    "pwm"));
  

  // create executor
  RCCHECK(rclc_executor_init(&executor, &support.context, 1, &allocator));
  RCCHECK(rclc_executor_add_subscription(&executor,
                                         &pwm_subscriber, 
                                         &pwm_msg, 
                                         &PWM_callback, 
                                         ON_NEW_DATA));

  // create publisher fo9r enc 
  
  digitalWrite(LED_PIN, LOW);
}

void loop() {
  RCCHECK(rclc_executor_spin_some(&executor, RCL_MS_TO_NS(100)));

  // int a = digitalRead(RL_ENC_A);
  // int b = digitalRead(RL_ENC_B);
  // Serial.print("A");
  // Serial.println(a);
  // Serial.print("B");
  // Serial.println(b);
  //enc data 
  fr_enc_msg.data = fr_enc_value;
  rcl_publish(&fr_enc_pub, &fr_enc_msg, NULL);
  fl_enc_msg.data = fl_enc_value;
  rcl_publish(&fl_enc_pub, &fl_enc_msg, NULL);
  rr_enc_msg.data = rr_enc_value;
  rcl_publish(&rr_enc_pub, &rr_enc_msg, NULL);
  rl_enc_msg.data = rl_enc_value;
  rcl_publish(&rl_enc_pub, &rl_enc_msg, NULL);
}