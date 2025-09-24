import os
from dataclasses import dataclass, field


@dataclass
class TestConfig:
    # color: str = "auto"
    vmlinux_path: str = os.path.join(os.getcwd(), "kernel/vmlinux")
    image_path: str = os.path.join(os.getcwd(), "rootfs.ext2")
    outputdir: str = os.path.join(os.getcwd(), "test")
    frequency: float = 0.1
    wait_timeout: float = 30.0
    qemu_gdbstub_port: str = "1234"
    qemu_bin: str = "qemu-system-riscv64"
    qemu_args: list[str] = field(
        default_factory=lambda: [
            "-kernel",
            os.path.join(os.getcwd(), "kernel/arch/riscv/boot/Image"),
            "-drive",
            "file=/zju-os/rootfs.ext2,format=raw,id=hd0,if=none",
            "-device",
            "virtio-blk-device,drive=hd0",
            "-netdev",
            "user,id=net0",
            "-device",
            "virtio-net-device,netdev=net0",
            "-append",
            "root=/dev/vda ro console=ttyS0",
            "-s",
            "-S",
        ]
    )


config = TestConfig()
