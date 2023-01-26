# MalNetLib

MalNetLib is a Python library for parsing PE files made with .NET (based on [dnlib](https://github.com/0xd4d/dnlib)).

## Installation

Install the library (available on [pypi.org](https://pypi.org/project/malnetlib/)):

```bash
$ python3 -m pip install malnetlib
```

Compile `dnlib.dll` (required for the project) :

```bash
# Debian
$ sudo apt install -y dotnet-sdk-6.0
# Arch
$ sudo pacman -S dotnet-sdk-6.0

$ git clone --depth=1 https://github.com/0xd4d/dnlib
$ cd dnlib
$ dotnet build
$ cd ..
$ cp ./dnlib/Examples/bin/Debug/net6.0/dnlib.dll .
$ rm -rf dnlib
```

## Examples

### NjRAT

> [NjRAT](https://malpedia.caad.fkie.fraunhofer.de/details/win.njrat) is a remote access trojan (RAT).

You can use `malnetlib` to extract the configuration of NjRAT which is stored inside .NET class attributes. Here is an example with the a sample of [NjRAT](https://tria.ge/230101-1z3k8sfh8v) and the script [njrat_extractor.py](https://github.com/xanhacks/malnetlib/blob/main/examples/njrat_extractor.py) :

```python
pe = DotNetPE(args.sample)
ok_class = pe.get_object("OK")
njrat_conf = {
	"host": ok_class.get_attribute("HH").get_value(),
	"port": ok_class.get_attribute("P").get_value(),
	"install_directory": "%" + ok_class.get_attribute("DR").get_value() + "%",
	"install_name": ok_class.get_attribute("EXE").get_value(),
	"startup": ok_class.get_attribute("sf").get_value(),
	"campain_id": b64decode(ok_class.get_attribute("VN").get_value()).decode("UTF-8"),
	"version": ok_class.get_attribute("VR").get_value(),
	"network_separator": ok_class.get_attribute("Y").get_value(),
	"mutex": ok_class.get_attribute("RG").get_value()
}
print(dumps(njrat_conf))
```

```json
{
  "host": "2.tcp.eu.ngrok.io",
  "port": "10008",
  "install_directory": "%TEMP%",
  "install_name": "server.exe",
  "startup": "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
  "campain_id": "HacKed",
  "version": "im523",
  "network_separator": "|'|'|",
  "mutex": "25ffb1a66b4748fe7537df7005cc8e55"
}
```

### vw0rm

> [VJW0rm](https://malpedia.caad.fkie.fraunhofer.de/details/win.vjw0rm) (aka Vengeance Justice Worm) is a publicly available, modular JavaScript RAT. Other variants include a Visual Basic Script (VBS) based worm titled vw0rm (Vengeance Worm).

You can use `malnetlib` to list and extract .NET resources from a `vw0rm` dropper.

```python
>>> from malnetlib.models import DotNetPE
>>> pe = DotNetPE("30d64daeb3e69ea6dde202a9d519f6ee17614af6e505dd2e5788017c3be4abd8")
>>> resources = pe.get_resources()
>>> resources
[<Resource Windows_Task_Manager.Resources.resources 0x0>, <Resource Windows_Task_Manager.proccesing.resources 0x4806>]
>>> resources[0].save("/tmp/output.bin")
```

```vbs
>>> resources[0].read()
b'[...]On error resume next\r\n\r\nj = array("WScript.Shell","Scripting.FileSystemObject","Shell.Application","Microsoft.XMLHTTP")
\r\ng = array("HKCU","HKLM","HKCU\\vw0rm","\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\","HKLM\\SOFTWARE\\Classes\\","REG_SZ","\\defaulticon\\")\r\ny=
array("winmgmts:","win32_logicaldisk","Win32_OperatingSystem","winmgmts:\\\\localhost\\root\\securitycenter","AntiVirusProduct")\r\n\r\nfunction go(m)\r\n
```

