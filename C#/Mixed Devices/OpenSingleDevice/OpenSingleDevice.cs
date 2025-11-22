using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using NewFocus.PicomotorApp;
using Newport.DeviceIOLib;

namespace NewFocus.Picomotor
{
    class OpenSingleDevice
    {
        static void Main (string[] args)
        {
            Console.WriteLine ("Waiting for device discovery...");
            DeviceIOLib deviceIO = new DeviceIOLib (true);
            CmdLib8742 cmdLib = new CmdLib8742 (deviceIO);

            // Set up USB to only discover picomotors
            deviceIO.SetUSBProductID (0x4000);

            // Discover USB and Ethernet devices - delay 5 seconds
            deviceIO.DiscoverDevices (0x5, 5000);

            // Get the list of discovered devices
            string[] strDeviceKeys = deviceIO.GetDeviceKeys ();

            // If no devices were discovered
            if (strDeviceKeys == null)
            {
                Console.WriteLine ("No devices discovered.");
            }
            else
            {
                // Get the first device key in the list
                string strDeviceKey = deviceIO.GetFirstDeviceKey ();

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

            // Shut down all communication
            deviceIO.Shutdown ();
        }
    }
}
