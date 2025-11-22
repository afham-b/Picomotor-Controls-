using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using NewFocus.PicomotorApp;
using Newport.DeviceIOLib;

namespace NewFocus.Picomotor
{
    class GetPositionAllSlaves
    {
        static void Main (string[] args)
        {
            Console.WriteLine ("Waiting for device discovery...\r\n");
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
                // For each device key in the list
                for (int i = 0; i < strDeviceKeys.Length; i++)
                {
                    string strDeviceKey = strDeviceKeys[i];

                    // If the device was opened
                    if (cmdLib.Open (strDeviceKey))
                    {
                        // Get the device address and the model / serial of the master controller
                        int nDeviceAddress = cmdLib.GetMasterDeviceAddress (strDeviceKey);
                        string strModelSerial = cmdLib.GetModelSerial (strDeviceKey, nDeviceAddress);
                        Console.WriteLine ("Master Controller:  Device Key = '{0}', Address = {1}, Model / Serial = {2}", 
                            strDeviceKey, nDeviceAddress, strModelSerial);
                        cmdLib.WriteLog ("Master Controller:  Device Key = '{0}', Address = {1}, Model / Serial = {2}", 
                            strDeviceKey, nDeviceAddress, strModelSerial);

                        // Get the device addresses of the slaves (for this master controller)
                        int[] nDeviceAddressList = cmdLib.GetDeviceAddresses (strDeviceKey);

                        if (nDeviceAddressList == null)
                        {
                            Console.WriteLine ("     No Slave Controllers.");
                        }
                        else
                        {
                            // For each slave device address
                            for (int n = 0; n < nDeviceAddressList.Length; n++)
                            {
                                // Get the device address and the model / serial of the current slave controller
                                nDeviceAddress = nDeviceAddressList[n];
                                strModelSerial = cmdLib.GetModelSerial (strDeviceKey, nDeviceAddress);
                                Console.WriteLine ("     Slave Controller:  Device Key = '{0}', Address = {1}, Model / Serial = {2}",
                                    strDeviceKey, nDeviceAddress, strModelSerial);
                                cmdLib.WriteLog ("     Slave Controller:  Device Key = '{0}', Address = {1}, Model / Serial = {2}",
                                    strDeviceKey, nDeviceAddress, strModelSerial);

                                // Model 8742 has four motors
                                int nMotorMax = 4;

                                // Check the model type for 8743
                                if (strModelSerial.Contains ("8743"))
                                {
                                    // Model 8743 has two motors
                                    nMotorMax = 2;
                                }

                                // For each motor
                                for (int nMotor = 1; nMotor <= nMotorMax; nMotor++)
                                {
                                    int nPosition = 0;

                                    // Get the position of the current slave controller
                                    if (cmdLib.GetPosition (strDeviceKey, nDeviceAddress, nMotor, ref nPosition))
                                    {
                                        Console.WriteLine ("               Motor #{0}', Position = {1}", nMotor, nPosition);
                                        cmdLib.WriteLog ("               Motor #{0}', Position = {1}", nMotor, nPosition);
                                    }
                                    else
                                    {
                                        Console.WriteLine ("               Motor #{0}', GetPosition Error.", nMotor);
                                        cmdLib.WriteLog ("               Motor #{0}', GetPosition Error.", nMotor);
                                    }
                                }
                            }
                        }

                        // Close the device
                        cmdLib.Close (strDeviceKey);
                    }
                }
            }

            Console.WriteLine ("Shutting down.");
            cmdLib.Shutdown ();

            // Shut down all communication
            deviceIO.Shutdown ();
        }
    }
}
