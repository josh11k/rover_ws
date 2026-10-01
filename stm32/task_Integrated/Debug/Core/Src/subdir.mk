################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (14.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Core/Src/fan_control.c \
../Core/Src/fan_driver.c \
../Core/Src/fan_protocol.c \
../Core/Src/herkulex.c \
../Core/Src/ina228.c \
../Core/Src/main.c \
../Core/Src/motor_manager.c \
../Core/Src/rover_heartbeat.c \
../Core/Src/rover_housekeeping.c \
../Core/Src/rover_protocol.c \
../Core/Src/rover_state.c \
../Core/Src/stm32g0xx_hal_msp.c \
../Core/Src/stm32g0xx_it.c \
../Core/Src/syscalls.c \
../Core/Src/sysmem.c \
../Core/Src/system_stm32g0xx.c \
../Core/Src/temperature_logger.c \
../Core/Src/temperature_sensor.c 

OBJS += \
./Core/Src/fan_control.o \
./Core/Src/fan_driver.o \
./Core/Src/fan_protocol.o \
./Core/Src/herkulex.o \
./Core/Src/ina228.o \
./Core/Src/main.o \
./Core/Src/motor_manager.o \
./Core/Src/rover_heartbeat.o \
./Core/Src/rover_housekeeping.o \
./Core/Src/rover_protocol.o \
./Core/Src/rover_state.o \
./Core/Src/stm32g0xx_hal_msp.o \
./Core/Src/stm32g0xx_it.o \
./Core/Src/syscalls.o \
./Core/Src/sysmem.o \
./Core/Src/system_stm32g0xx.o \
./Core/Src/temperature_logger.o \
./Core/Src/temperature_sensor.o 

C_DEPS += \
./Core/Src/fan_control.d \
./Core/Src/fan_driver.d \
./Core/Src/fan_protocol.d \
./Core/Src/herkulex.d \
./Core/Src/ina228.d \
./Core/Src/main.d \
./Core/Src/motor_manager.d \
./Core/Src/rover_heartbeat.d \
./Core/Src/rover_housekeeping.d \
./Core/Src/rover_protocol.d \
./Core/Src/rover_state.d \
./Core/Src/stm32g0xx_hal_msp.d \
./Core/Src/stm32g0xx_it.d \
./Core/Src/syscalls.d \
./Core/Src/sysmem.d \
./Core/Src/system_stm32g0xx.d \
./Core/Src/temperature_logger.d \
./Core/Src/temperature_sensor.d 


# Each subdirectory must supply rules for building sources it contributes
Core/Src/%.o Core/Src/%.su Core/Src/%.cyclo: ../Core/Src/%.c Core/Src/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m0plus -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32G071xx -c -I../Core/Inc -I../Drivers/STM32G0xx_HAL_Driver/Inc -I../Drivers/STM32G0xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32G0xx/Include -I../Drivers/CMSIS/Include -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfloat-abi=soft -mthumb -o "$@"

clean: clean-Core-2f-Src

clean-Core-2f-Src:
	-$(RM) ./Core/Src/fan_control.cyclo ./Core/Src/fan_control.d ./Core/Src/fan_control.o ./Core/Src/fan_control.su ./Core/Src/fan_driver.cyclo ./Core/Src/fan_driver.d ./Core/Src/fan_driver.o ./Core/Src/fan_driver.su ./Core/Src/fan_protocol.cyclo ./Core/Src/fan_protocol.d ./Core/Src/fan_protocol.o ./Core/Src/fan_protocol.su ./Core/Src/herkulex.cyclo ./Core/Src/herkulex.d ./Core/Src/herkulex.o ./Core/Src/herkulex.su ./Core/Src/ina228.cyclo ./Core/Src/ina228.d ./Core/Src/ina228.o ./Core/Src/ina228.su ./Core/Src/main.cyclo ./Core/Src/main.d ./Core/Src/main.o ./Core/Src/main.su ./Core/Src/motor_manager.cyclo ./Core/Src/motor_manager.d ./Core/Src/motor_manager.o ./Core/Src/motor_manager.su ./Core/Src/rover_heartbeat.cyclo ./Core/Src/rover_heartbeat.d ./Core/Src/rover_heartbeat.o ./Core/Src/rover_heartbeat.su ./Core/Src/rover_housekeeping.cyclo ./Core/Src/rover_housekeeping.d ./Core/Src/rover_housekeeping.o ./Core/Src/rover_housekeeping.su ./Core/Src/rover_protocol.cyclo ./Core/Src/rover_protocol.d ./Core/Src/rover_protocol.o ./Core/Src/rover_protocol.su ./Core/Src/rover_state.cyclo ./Core/Src/rover_state.d ./Core/Src/rover_state.o ./Core/Src/rover_state.su ./Core/Src/stm32g0xx_hal_msp.cyclo ./Core/Src/stm32g0xx_hal_msp.d ./Core/Src/stm32g0xx_hal_msp.o ./Core/Src/stm32g0xx_hal_msp.su ./Core/Src/stm32g0xx_it.cyclo ./Core/Src/stm32g0xx_it.d ./Core/Src/stm32g0xx_it.o ./Core/Src/stm32g0xx_it.su ./Core/Src/syscalls.cyclo ./Core/Src/syscalls.d ./Core/Src/syscalls.o ./Core/Src/syscalls.su ./Core/Src/sysmem.cyclo ./Core/Src/sysmem.d ./Core/Src/sysmem.o ./Core/Src/sysmem.su ./Core/Src/system_stm32g0xx.cyclo ./Core/Src/system_stm32g0xx.d ./Core/Src/system_stm32g0xx.o ./Core/Src/system_stm32g0xx.su ./Core/Src/temperature_logger.cyclo ./Core/Src/temperature_logger.d ./Core/Src/temperature_logger.o ./Core/Src/temperature_logger.su ./Core/Src/temperature_sensor.cyclo ./Core/Src/temperature_sensor.d ./Core/Src/temperature_sensor.o ./Core/Src/temperature_sensor.su

.PHONY: clean-Core-2f-Src

