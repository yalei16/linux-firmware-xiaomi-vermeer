# linux-firmware-xiaomi-vermeer

Redmi K70 / POCO F6 Pro（Qualcomm **SM8550**，代号 **vermeer**，WiFi 芯片 **WCN7850**）在 mainline Linux 上运行时需要的固件集合。

本仓库是 `linux-firmware` 的**固件子集**：只保留 vermeer 需要的文件，用于给自编译内核的 rootfs 补固件。

## 目录

```
xiaomi-vermeer/
├── ath12k/WCN7850/hw2.0/          # WiFi 7 (WCN7850)
│   ├── amss.bin                   # 主固件（MHI 加载）
│   ├── m3.bin                     # M3 固件
│   ├── board-2.bin                # BDF（板级校准数据）
│   ├── qdss.cfg  regdb.bin
└── qcom/
    ├── a740_sqe.fw  gmu_gen70200.bin
    └── sm8550/xiaomi/vermeer/     # GPU zap / 摄像头 ICP / 音频 aw882xx / 触控 goodix / VPU
```

## 构建产物

推送到 `main` 或手动触发 `build-firmware` workflow，会产出 `vermeer-firmware.tar.gz`（artifact），
内部已经是**去掉 `xiaomi-vermeer/` 前缀**的标准 `/lib/firmware` 目录结构：

```
ath12k/WCN7850/hw2.0/...
qcom/sm8550/xiaomi/vermeer/...
qcom/a740_sqe.fw
```

## 安装（设备上）

```sh
tar -C /lib/firmware -xzf vermeer-firmware.tar.gz
```

## ⚠️ board-2.bin 的 subsystem-device 陷阱（本仓库已自动修正）

`ath12k` 用**一整条字符串**匹配 BDF 条目。上游 dump 出来的条目是：

```
bus=pci,vendor=17cb,device=1107,subsystem-vendor=17cb,subsystem-device=0113,qmi-chip-id=2,qmi-board-id=255
```

而 mainline 下这台机器的 PCI 设备报的是 `subsystem-device=1107`，于是匹配失败，日志表现为：

```
ath12k ...: failed to fetch board data for bus=pci,...,qmi-board-id=255
```

`build-firmware` workflow 因此会自动执行一次**等长替换** `0113 → 1107`（只改 2 个字符，文件大小不变）。
若要手工做：

```sh
sed -i 's/subsystem-device=0113/subsystem-device=1107/' board-2.bin
python3 scripts/check-board2.py board-2.bin     # 打印所有 BDF 条目名
```

## 已知其余问题（不在本仓库范围内）

1. **加载时机**：内建（`CONFIG_ATH12K=y`）的 ath12k 在 t≈27s 探测，此时 UFS rootfs 尚未挂载 →
   `Direct firmware load for ath12k/WCN7850/hw2.0/amss.bin failed with error -2`。
   解决：固件放进 initramfs，或改成 `CONFIG_ATH12K=m` 由 udev 在 rootfs 就绪后加载；
   临时验证可在 shell 里 `echo 0000:01:00.0 > /sys/bus/pci/drivers/ath12k_wifi7_pci/bind`。
2. **QMI target ready 超时**：固件能加载、能打印 `chip_id 0x2 board_id 0xff soc_id 0x40170200` 与
   `fw_version`，但尚未出现 `wlan0`，需要继续查 DT 里 WCN7850 的供电/PMU 与 QMI 通道。
3. 本仓库**不含** `adsp.mbn` / `cdsp.mbn` / `modem` 固件（音频/传感器/基带另需，需从原厂镜像提取）。

## 许可证

固件为高通/小米专有二进制，仅用于在自有设备上运行 Linux。仓库脚本部分 `CC0-1.0`。
