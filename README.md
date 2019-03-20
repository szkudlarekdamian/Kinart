# Kinart
Create art using Kinect and your hand



_____________________________

### Libfreenect errors:
1. Could not open audio: -4:
    - it's not an important error
2. USB device disappeared, cancelling stream 81 :( USB camera marked dead, stopping streams:
    - to handle this error log in as root ("sudo -i") and run  "echo -1 > /sys/module/usbcore/parameters/autosuspend"
  https://devtalk.nvidia.com/default/topic/746596/embedded-systems/usb3-port-not-providing-continuous-power-/post/4239121/#4239121
