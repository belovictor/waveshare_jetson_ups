#!/usr/bin/python

import rospy
from sensor_msgs.msg import BatteryState
from ina219 import INA219


class WaveshareJetsonUPS():

    def __init__(self, design_capacity=None):

        rospy.loginfo("Setting Up the Waveshare Jetson UPS node...")

        # Set up and title the ros node for this code
        rospy.init_node('waveshare_jetson_ups')

        # Create publishers for commanding velocity, angle, and robot states
        self._ros_pub_battery_state = rospy.Publisher('/battery_state', BatteryState, queue_size=5)
        self._design_capacity = design_capacity
        self._ina219 = INA219(i2c_bus=1, addr=0x42)

        rospy.loginfo("Waveshare Jetson UPS node publishers corrrectly initialized")


    def run(self):
        r = rospy.Rate(1.0)
        while not rospy.is_shutdown():
            bus_voltage = self._ina219.getBusVoltage_V()
            shunt_voltage = self._ina219.getShuntVoltage_mV() / 1000
            current = self._ina219.getCurrent_mA() / 1000
            power = self._ina219.getPower_W()
            soc = round((bus_voltage - 6) / 2.4 * 100)
            if (soc > 100):
                soc = 100
            if (soc < 0):
                soc = 0
            if current >0:
                isCharging = True
            else:
                isCharging = False
            # print("Bus voltage = {}, shunt voltage = {}, current = {}, power = {}, soc = {}, isCharging = {}".format(
            #     bus_voltage, shunt_voltage, current, power, soc, isCharging))
            battery_status = BatteryState()
            battery_status.voltage = bus_voltage
            battery_status.current = current
            battery_status.percentage = soc
            battery_status.location = "UPS"
            battery_status.present = True
            if self._design_capacity != None:
                battery_status.design_capacity = self._design_capacity
            # Waveshare Jetson UPS has 4 cells
            battery_status.power_supply_technology = BatteryState.POWER_SUPPLY_TECHNOLOGY_LION
            if isCharging:
                battery_status.power_supply_status = BatteryState.POWER_SUPPLY_STATUS_CHARGING
            else:
                battery_status.power_supply_status = BatteryState.POWER_SUPPLY_STATUS_DISCHARGING
            # print(battery_status)
            self._ros_pub_battery_state.publish(battery_status)
            r.sleep()

if __name__ == "__main__":
    ups = WaveshareJetsonUPS(design_capacity=rospy.get_param('design_capacity', None))
    ups.run()
