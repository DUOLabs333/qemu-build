import subprocess, os
#Menu bar is 56 pixels


SOCKET=os.path.join(self.workdir,"qemu-monitor.sock")
Down("sudo pkill -9 qemu-system-aarch64")
Run(f"""sudo env "DYLD_FALLBACK_LIBRARY_PATH=qemu/lib" qemu/bin/qemu-system-aarch64
-M virt,accel=hvf 
-m 8G
-cpu host
-smp {Run("getconf _NPROCESSORS_ONLN",pipe=True,track=False).strip()}
-kernel Linux.utm/Data/Image 
-initrd Linux.utm/Data/initramfs-linux.img 
-append "root=/dev/vda rw console=ttyAMA0 video=Virtual-1:2880x1690@60"

-monitor unix:{SOCKET},server,nowait

-device pcie-root-port,id=pcie

-drive if=none,file=Linux.utm/Data/Arch.img,format=raw,index=0,media=disk,id=drive1
-device virtio-blk-pci,addr=0x0.0x5,backend_defaults=on,bus=pcie,drive=drive1

-audiodev coreaudio,id=audio,out.fixed-settings=false
-device ich9-intel-hda,bus=pcie,addr=0x0.0x0,multifunction=on
-device hda-micro,audiodev=audio

-device virtio-net-pci,addr=0x0.0x3,bus=pcie,netdev=net0,mac=1E:4C:16:AE:DF:6B
-netdev vmnet-shared,id=net0

{'-icount sleep=off' if 'no-sleep' in self.flags else ''}

-device virtio-gpu-gl-pci,addr=0x0.0x1,bus=pcie,edid=off,xres=2880,yres=1690
-display cocoa,gl=es,full-grab=on,zoom-to-fit=on,zoom-interpolation=on

-device virtio-keyboard-pci,addr=0x0.0x2,bus=pcie

-chardev qemu-vdagent,id=spice,name=vdagent
-device virtio-serial-pci,addr=0x0.0x6,bus=pcie
-device virtserialport,chardev=spice,name=com.redhat.spice.0

-device qemu-xhci,id=usb-controller-0

""".replace("\n"," "))

while True:
    if os.path.exists(SOCKET):
        Run(f"sudo chown $(whoami) {SOCKET}", track=False)
        break


#-run-with user="$(id -u):$(id -g)"

#-device usb-host,hostbus=0,hostport=1
#utils.shell_command(["service","stop","wireguard"],block=False)
#utils.shell_command(["service","stop","arch"],block=False)
#subprocess.Popen(["service","stop","arch"])

#icount sleep=off --- Makes it really smooth, but very CPU-intensive
#-virtfs local,path=shared,mount_tag=Macbook,security_model=none

#-netdev vmnet-bridged,id=net0,ifname=en0
#-netdev vmnet-shared,id=net0

#-device usb-host,productid=0x4ee7,vendorid=0x18d1 
#-device usb-host,productid=0x55a9,vendorid=0x0781

#-device virtio-sound-pci,addr=0x0.0x0,bus=pcie,multifunction=on,audiodev=audio,streams=1

"""
-device qemu-xhci,id=usb-controller-0
-device usb-host,productid=0x4ee7,vendorid=0x18d1 
-device usb-host,productid=0x55a9,vendorid=0x0781
"""

#/Applications/Tunnelblick.app/Contents/Resources/openvpnstart loadKexts 2
#defaults  write  net.tunnelblick.tunnelblick  doNotLaunchOnLogin  -bool  yes

"""
-drive if=none,file=/dev/disk4,format=raw,index=3,media=disk,id=drive3,cache=writethrough
-device virtio-blk-pci,addr=0x0.0x7,backend_defaults=on,bus=pcie,drive=drive3
"""

"""
-netdev tap,id=net1,ifname=tap1,script=$HOME/qemu-ifup,downscript=$HOME/qemu-ifdown
-device virtio-net-pci,addr=0x0.0x7,bus=pcie,netdev=net1,mac=1E:4C:16:AE:DF:6B
"""

"-device virtio-mouse-pci"

"""
-device virtio-net-pci,addr=0x0.0x3,bus=pcie,netdev=net0,mac=1E:4C:16:AE:DF:6B
-netdev vmnet-shared,id=net0
"""

"""
-spice unix=on,addr=35C1D817-F239-4E48-9C11-ED4947F9C4C3.spice,disable-ticketing=on,image-compression=off,playback-compression=off,streaming-video=off,gl=on

-uuid 35C1D817-F239-4E48-9C11-ED4947F9C4C3
"""

"""
-netdev stream,id=vlan,addr.type=unix,addr.path=/Users/system/Downloads/network-qemu.sock -device virtio-net-pci,netdev=vlan,mac=5a:94:ef:e4:0c:ee
"""

"""
-append "root=/dev/vda rw console=ttyAMA0 video=Virtual-1:2885x1690@60"
"""