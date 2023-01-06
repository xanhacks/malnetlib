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

[NJRat](https://malpedia.caad.fkie.fraunhofer.de/details/win.njrat) is a remote access trojan (RAT). You can use `malnetlib` to extract the configuration of NjRAT which is stored inside .NET class attributes.

Here is an example with the a sample of [NjRAT](https://tria.ge/230101-1z3k8sfh8v) and the script [njrat_extractor.py](https://github.com/xanhacks/malnetlib/blob/main/examples/njrat_extractor.py) :

```bash
$ python3 njrat_extractor.py -h
usage: njrat_extractor.py [-h] sample

positional arguments:
  sample      Path to the sample file.

options:
  -h, --help  show this help message and exit
$ python3 njrat_extractor.py a04136fe0299b81fe404d9e5257c34e7.exe | jq
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