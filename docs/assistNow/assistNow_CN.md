<div align="center" markdown="1">
  <img src="https://www.u-blox.com/logo.png" alt="LilyGo logo" width="100"/>
</div>

<h1 align = "center">🌟u-blox AssistNow Usage Guide🌟</h1>

### [English](./assistNow.md)

### 可用设备

| 设备 | |
| -------------------- | --- |
| [T-Deck Plus][1] | ✅ |
| [T-Deck Pro][2] | ✅ |
| [T-LoRa-Pager][3] | ✅ |
| [T-Watch-S3-Plus][4] | ✅ |
| [T-Watch-Ultra][5] | ✅ |
| [T-Beam-Supreme][6] | ✅ |

[1]: https://lilygo.cc/products/t-deck-plus-1
[2]: https://lilygo.cc/products/t-deck-pro
[3]: https://lilygo.cc/products/t-lora-pager
[4]: https://lilygo.cc/products/t-watch-s3-plus
[5]: https://lilygo.cc/products
[6]: https://lilygo.cc/products/t-beam-supreme

> \[!IMPORTANT]
> * 本文档仅适用于使用 **u-blox M10 系列** 的设备，其他设备无法使用本文档
> * 以上列出的设备均可使用此方法写入星历数据。未列出的设备不支持

### Step1:设备刷入GPS回环固件,如果是LilyGoLib中的设备,在出厂固件，在GPS界面内,将 **NMEA to Serial** 开关切换到Enabled

![app1](./images/app1.jpg)

![app2](./images/app2.jpg)


## Step2:注册 Thingstream 账号

1. 登录 [u-blox Thingstream](https://portal.thingstream.io/)注册账号

![ThingstreamRegister](./images/ThingstreamRegister.jpg)

2. 申请 AssistNow Token

![AssistNowToken1](./images/AssistNowToken1.jpg)

3. 创建一个Profile

![AssistNowToken2](./images/AssistNowToken2.jpg)

![AssistNowToken3](./images/AssistNowToken3.jpg)

4. 查看Token,这个Token将在后面的步骤上使用

![AssistNowToken4](./images/AssistNowToken4.jpg)


## Step3:使用u-cetnter2 将星历数据发送给设备

1. 下载 [u-center2 >= V25.06.18](https://www.u-blox.com/en/product/u-center)

2. 注册u-center2账号,并且登录账号

![ucenter2login](./images/ucenter2login.jpg)

3. 选择设备的端口和波特率

![start1](./images/ucetner2-start1.jpg)

4. 查看是否正常检测到GPS信息

![start2](./images/ucetner2-start2.jpg)

5. 在下图位置上,使用 AssistNow,填入在Thingstream中申请的AssistNow 的token

![start3](./images/ucetner2-start3.jpg)

6. 如果Token正确,那么图标将变成绿色

![start4](./images/ucetner2-start4.jpg)

7. 点击Download 下载GPS星历数据,请保持默认设置,天数最多只能一天

![start5](./images/ucetner2-start5.jpg)

8. 点击传输按钮,将星历发送到设备上

![start6](./images/ucetner2-start6.jpg)

9. 等待传输完成,如果传输失败,请多重试几次

![start7](./images/ucetner2-start7.jpg)

10. 下图显示的是传输成功的提示

![start8](./images/ucetner2-start8.jpg)


## Step4:测试实际效果

1. 将 **NMEA to Serial** 开关切换为Disable,将设备放置在户外，有了AssistNow的加速,GPS定位速度将大大的提高.
2. 如果是其他Ublox的设备,请刷入其他的设备的出厂固件
3. 在不关闭GPS设备的情况下，GPS星历数据将保持一天的有效期,如果设备断电,GPS星历数据将丢失.请按照上面的方法重新将星历数据发送到设备.如果数据超过了一天的有效期,请更新星历数据