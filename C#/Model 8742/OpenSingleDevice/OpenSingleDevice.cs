using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using NewFocus.Picomotor;

namespace NewFocus.Picomotor
{
    class OpenSingleDevice
    {
        static void Main (string[] args)
        {
            Console.WriteLine ("Waiting for device discovery...");
            string strDeviceKey = string.Empty;
            CmdLib8742 cmdLib = new CmdLib8742 (true, 5000, ref strDeviceKey);
            Console.WriteLine ("First Device Key = {0}", strDeviceKey);

            // If no devices were discovered
            if (strDeviceKey == null)
            {
                Console.WriteLine ("No devices discovered.");
            }
            else
            {
                // If the device was opened
                if (cmdLib.Open (strDeviceKey))
                {
                    string strID = string.Empty;
                    cmdLib.GetIdentification (strDeviceKey, ref strID);
                    Console.WriteLine ("Device ID = '{0}'", strID);

                    // Close the device
                    cmdLib.Close (strDeviceKey);
                }
            }

            Console.WriteLine ("Shutting down.");
            cmdLib.Shutdown ();
        }
    }
}
