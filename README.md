# Bachelor Project

The system develops a prototype for artificial intelligence assisted automated optical alignment system (AIOAS) for hybrid photonics integration (HPI).
<br />
This application uses an MCS2 positioner on a Raspberry Pi 5, making it the first ever to use such device and all others mentioned below with a Raspberry Pi, allowing users to move the device's stages along three axes (X, Y, Z) and read their current positions. In addition, my project is designed to interface with a KDC001 motor controller and a connected motorized stage to perform precise linear motion control via a serial communication protocol. Moreover, the system interacts with a RayCi server via XML-RPC to perform laser beam analysis using a connected camera, which captures and records videos, and performs background calibration to enhance measurement accuracy.
A Basler camera captures photos or videos of hyperoptics on the chip that a laser passes through, a LaserSource sets and reads the current of the laser, and an Arroyo TecControl is used to set the temperature of the laser.
<br />
The GUI for this system integrates multiple advanced components and functionalities into a single, cohesive platform for the first time on a Raspberry Pi. This innovative GUI serves as the central control hub, providing users with an intuitive and user-friendly interface to manage and operate the various elements of the system.
This integration not only simplifies the operation of complex photonics experiments but also enhances the precision and efficiency of the alignment process. By consolidating these capabilities into one accessible platform, the system represents a significant advancement in the field of hybrid photonics integration.
<br />
camera.py is the main class and imports the other classes.
