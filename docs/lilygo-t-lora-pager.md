<div align="center" markdown="1">
  <img src="../images/LilyGo_logo.png" alt="LilyGo logo" width="100"/>
</div>

<h1 align = "center">🌟LilyGo T-LoRa-Pager-MicroPython🌟</h1>

## `1` Overview

* This page introduces how to use the `LilyGO T-LoRa-Pager-MicroPython` 

  

## `2` Quick Start

> \[!IMPORTANT]
> Please upload the firmware before starting. For details, please refer to the [tutorial](../firmware/README.md)   

1. ### Arduino lab for micropython IDE

   1. Install [Arduino lab for micropython IDE](https://labs.arduino.cc/en/labs/micropython).
   2. Install **Desktop Version (Choose Linux or macOS or Windows)**

   3. Open the folder and open "Arduino Lab for MicroPython.exe".

      ![Arduino1](..\images\Arduino1.png)

   4. Connect the serial port.

      ![Arduino2](..\images\Arduino2.png)

   5. Click Run the program (If you want to Stop the program, please click Stop).

      ![Arduino3](C:\Users\Xinyuan\Desktop\GitHub\LilyGoLib-MicroPython\images\Arduino3.png)

   6. If you want to run the program automatically, please click file and then create a new code named "main.py". Select  "Board" Then write the code into main.py and save it. Reset the T-LoRa-Pager.

      ![Arduino4](..\images\Arduino4.png)

2. ### Thonny IDE

   1. Install [Thonny IDE]([Thonny, Python IDE for beginners](https://thonny.org/)) 

   2. Download version 4.1.7 or the latest version (Choose Linux or macOS or Windows)

      ![thonny1](..\images\thonny1.png)

   3. After installing the installation package, open Thonny IDE

   4. Click Configure interpreter

      ![thonny2](..\images\thonny2.png)

   5. Select MicroPython (ESP32)

      ![thonny3](..\images\thonny3.png)

   6. Select the corresponding port number and confirm

      ![thonny4](..\images\thonny4.png)

   7. Test run the program (Print "hello world" below is OK. You can use the shortcut key F5 to run the program and ctrl+F2 to end it)

      `print("hello world")`

      ![thonny5](..\images\thonny5.png)

   8. If you want to run the program automatically, please click Save, then select MicroPython device and name it main.py

      ![thonny6](..\images\thonny6.png)

      ![thonny7](..\images\thonny7.png)

   9. After successful saving, reset the T-LoRa-Pager

3. ### RT-Thread MicroPython

   1. Install [Python](https://www.python.org/downloads/) (according to you to download the corresponding operating system version, suggest to download version 3.7 or later), MicroPython requirement 3. X version, if you have already installed, you can skip this step).
   2. Install [Visual Studio Code](https://code.visualstudio.com/Download), Choose installation based on your system type.
   3. Open the "Extension" section of the Visual Studio Code software sidebar(Alternatively, use "<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>X</kbd>" to open the extension),Search for the "RT-Thread MicroPython" extension and download it.
   4. During the installation of the extension, you can go to GitHub to download the program. You can download the main branch by clicking on the "<> Code" with green text, or you can download the program versions from the "Releases" section in the sidebar.
   5. After the installation of the extension is completed, open the Explorer in the sidebar(Alternatively, use "<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>E</kbd>" go open it),Click on "Open Folder," locate the project code you just downloaded (the entire folder), and click "Add." At this point, the project files will be added to your workspace.
   6. Click on "<kbd>[Device Connected/Disconnected](../images/vscode1.png)</kbd>" at the lower left corner, and then click on the pop-up window "<kbd>[COMX](../images/vscode2.png)</kbd>" at the top to connect the serial port. A pop-up pops up at the lower right corner saying "<kbd>[Connection successful](../images/vscode3.png)</kbd>" and the connection is complete.
   7. After opening the code, click on“<kbd>[▶](../images/vscode4.png)</kbd>”at the lower left corner to run the program“<kbd>[Run this MicroPython file directly on the device](../images/vscode5.png)</kbd>”，Or use the<kbd>Alt</kbd>+<kbd>Q</kbd>），if you want to stop the program, click on the lower left corner of the“<kbd>[⏹](../images/vscode6.png.png)</kbd>”stop running the program.**(If you need to run the program automatically on the board, please copy the code to the "[main.py](../examples/main.py)" file under the "exampels" folder and save it. Select the "main.py" file with the left mouse button. Right-click the mouse and select "[Download this file/folder to device](../images/vscode7.png)", then press the reset button on the board to run the program automatically.)**

### Keyboard function settings and input methods

|                               |                               |
| ----------------------------- | ----------------------------- |
| Number and Symbol Mode        | Space + Key                   |
| Character capitalization mode | CAP + Key                     |
| Backlight control             | Left orange button + button B |

* In the factory firmware, the backlight can only be controlled when the input is allowed.

### T-LoRa-Pager Enter Upload Mode

> \[!IMPORTANT]
>
> 🤖 Operation is only required when the firmware cannot be uploaded. Under normal circumstances, this step does not need to be carried out..
> 
>Follow the steps below to put your device into upload mode
> 
>1. Connect the board via the USB-C cable
> 2. Hold down the **BOOT** key and press the **RST** key simultaneously
>
