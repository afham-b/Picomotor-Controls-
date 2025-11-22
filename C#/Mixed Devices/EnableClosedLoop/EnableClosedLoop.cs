using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using NewFocus.PicomotorApp;
using Newport.DeviceIOLib;

namespace NewFocus.Picomotor
{
    class EnableClosedLoop
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
                    int nMotor = 1;
                    int nPosition = 0;

                    // Set the current position to zero
                    bool bStatus = cmdLib.SetZeroPosition (strDeviceKey, nMotor);

                    if (!bStatus)
                    {
                        Console.WriteLine ("I/O Error:  Could not set the current position.");
                    }

                    // Get the current position
                    bStatus = cmdLib.GetPosition (strDeviceKey, nMotor, ref nPosition);

                    if (!bStatus)
                    {
                        Console.WriteLine ("I/O Error:  Could not get the current position.");
                    }
                    else
                    {
                        Console.WriteLine ("Start Position = {0}", nPosition);
                    }

                    string strInput;

                    // If the device is an 8743
                    if (cmdLib.GetModelSerial (strDeviceKey).Contains ("8743"))
                    {
                        // Get the closed-loop setting from the user and send it to the device
                        Console.WriteLine ("Enter 0 to disable or 1 to enable closed-loop: ");
                        strInput = Console.ReadLine ();
                        int nClosedLoop = Convert.ToInt32 (strInput);
                        int nDeviceAddress = cmdLib.GetMasterDeviceAddress (strDeviceKey);
                        cmdLib.SetCLEnabledSetting (strDeviceKey, nDeviceAddress, nMotor, nClosedLoop == 0 ? 0 : 1);
                    }
                    else
                    {
                        Console.WriteLine ("This is NOT a closed-loop device (8743-CL) - skipping Enable Closed-Loop command.");
                    }

                    Console.WriteLine ("Enter the relative steps to move (0 or Ctrl-C for no movement): ");
                    strInput = Console.ReadLine ();
                    int nSteps = Convert.ToInt32 (strInput);

                    if (nSteps != 0)
                    {
                        // Perform a relative move
                        bStatus = cmdLib.RelativeMove (strDeviceKey, nMotor, nSteps);

                        if (!bStatus)
                        {
                            Console.WriteLine ("I/O Error:  Could not perform relative move.");
                        }
                    }

                    bool bIsMotionDone = false;

                    while (bStatus && !bIsMotionDone)
                    {
                        // Check for any device error messages
                        string strErrMsg = string.Empty;
                        bStatus = cmdLib.GetErrorMsg (strDeviceKey, ref strErrMsg);

                        if (!bStatus)
                        {
                            Console.WriteLine ("I/O Error:  Could not get error status.");
                        }
                        else
                        {
                            string[] strTokens = strErrMsg.Split (new string[] { ", " }, StringSplitOptions.RemoveEmptyEntries);

                            // If the error message number is not zero
                            if (strTokens[0] != "0")
                            {
                                Console.WriteLine ("Device Error:  {0}", strErrMsg);
                                break;
                            }

                            // Get the motion done status
                            bStatus = cmdLib.GetMotionDone (strDeviceKey, nMotor, ref bIsMotionDone);

                            if (!bStatus)
                            {
                                Console.WriteLine ("I/O Error:  Could not get motion done status.");
                            }
                            else
                            {
                                // Get the current position
                                bStatus = cmdLib.GetPosition (strDeviceKey, nMotor, ref nPosition);

                                if (!bStatus)
                                {
                                    Console.WriteLine ("I/O Error:  Could not get the current position.");
                                }
                                else
                                {
                                    Console.WriteLine ("Position = {0}", nPosition);
                                }
                            }
                        }
                    }

                    // Close the device
                    cmdLib.Close (strDeviceKey);
                }
            }

            // Shut down device communication
            Console.WriteLine ("Shutting down.");
            cmdLib.Shutdown ();

            // Shut down all communication
            deviceIO.Shutdown ();
        }
    }
}
