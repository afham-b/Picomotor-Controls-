<?xml version='1.0'?>
<Project Type="Project" LVVersion="8008005">
   <Item Name="My Computer" Type="My Computer">
      <Property Name="CCSymbols" Type="Str">OS,Win;CPU,x86;</Property>
      <Property Name="server.app.propertiesEnabled" Type="Bool">true</Property>
      <Property Name="server.control.propertiesEnabled" Type="Bool">true</Property>
      <Property Name="server.tcp.enabled" Type="Bool">false</Property>
      <Property Name="server.tcp.port" Type="Int">0</Property>
      <Property Name="server.tcp.serviceName" Type="Str">My Computer/VI Server</Property>
      <Property Name="server.tcp.serviceName.default" Type="Str">My Computer/VI Server</Property>
      <Property Name="server.vi.callsEnabled" Type="Bool">true</Property>
      <Property Name="server.vi.propertiesEnabled" Type="Bool">true</Property>
      <Property Name="specify.custom.address" Type="Bool">false</Property>
      <Item Name="Command VIs" Type="Folder">
         <Item Name="AbortMotion.vi" Type="VI" URL="Command VIs/AbortMotion.vi"/>
         <Item Name="AbsoluteMove.vi" Type="VI" URL="Command VIs/AbsoluteMove.vi"/>
         <Item Name="GetAbsTargetPos.vi" Type="VI" URL="Command VIs/GetAbsTargetPos.vi"/>
         <Item Name="GetAcceleration.vi" Type="VI" URL="Command VIs/GetAcceleration.vi"/>
         <Item Name="GetCLDeadband.vi" Type="VI" URL="Command VIs/GetCLDeadband.vi"/>
         <Item Name="GetCLEnabledSetting.vi" Type="VI" URL="Command VIs/GetCLEnabledSetting.vi"/>
         <Item Name="GetCLHardwareStatus.vi" Type="VI" URL="Command VIs/GetCLHardwareStatus.vi"/>
         <Item Name="GetCLThreshold.vi" Type="VI" URL="Command VIs/GetCLThreshold.vi"/>
         <Item Name="GetCLUnits.vi" Type="VI" URL="Command VIs/GetCLUnits.vi"/>
         <Item Name="GetCLUpdateInterval.vi" Type="VI" URL="Command VIs/GetCLUpdateInterval.vi"/>
         <Item Name="GetDeviceAddress.vi" Type="VI" URL="Command VIs/GetDeviceAddress.vi"/>
         <Item Name="GetErrorMsg.vi" Type="VI" URL="Command VIs/GetErrorMsg.vi"/>
         <Item Name="GetErrorNum.vi" Type="VI" URL="Command VIs/GetErrorNum.vi"/>
         <Item Name="GetHostName.vi" Type="VI" URL="Command VIs/GetHostName.vi"/>
         <Item Name="GetIdentification.vi" Type="VI" URL="Command VIs/GetIdentification.vi"/>
         <Item Name="GetMotionDone.vi" Type="VI" URL="Command VIs/GetMotionDone.vi"/>
         <Item Name="GetMotorType.vi" Type="VI" URL="Command VIs/GetMotorType.vi"/>
         <Item Name="GetPosition.vi" Type="VI" URL="Command VIs/GetPosition.vi"/>
         <Item Name="GetRelativeSteps.vi" Type="VI" URL="Command VIs/GetRelativeSteps.vi"/>
         <Item Name="GetVelocity.vi" Type="VI" URL="Command VIs/GetVelocity.vi"/>
         <Item Name="JogNegative.vi" Type="VI" URL="Command VIs/JogNegative.vi"/>
         <Item Name="JogPositive.vi" Type="VI" URL="Command VIs/JogPositive.vi"/>
         <Item Name="MoveToHome.vi" Type="VI" URL="Command VIs/MoveToHome.vi"/>
         <Item Name="MoveToNextDirIndexNeg.vi" Type="VI" URL="Command VIs/MoveToNextDirIndexNeg.vi"/>
         <Item Name="MoveToNextDirIndexPos.vi" Type="VI" URL="Command VIs/MoveToNextDirIndexPos.vi"/>
         <Item Name="MoveToTravelLimitNeg.vi" Type="VI" URL="Command VIs/MoveToTravelLimitNeg.vi"/>
         <Item Name="MoveToTravelLimitPos.vi" Type="VI" URL="Command VIs/MoveToTravelLimitPos.vi"/>
         <Item Name="RelativeMove.vi" Type="VI" URL="Command VIs/RelativeMove.vi"/>
         <Item Name="SaveToMemory.vi" Type="VI" URL="Command VIs/SaveToMemory.vi"/>
         <Item Name="SetAcceleration.vi" Type="VI" URL="Command VIs/SetAcceleration.vi"/>
         <Item Name="SetCLDeadband.vi" Type="VI" URL="Command VIs/SetCLDeadband.vi"/>
         <Item Name="SetCLEnabledSetting.vi" Type="VI" URL="Command VIs/SetCLEnabledSetting.vi"/>
         <Item Name="SetCLHardwareStatus.vi" Type="VI" URL="Command VIs/SetCLHardwareStatus.vi"/>
         <Item Name="SetCLThreshold.vi" Type="VI" URL="Command VIs/SetCLThreshold.vi"/>
         <Item Name="SetCLUnits.vi" Type="VI" URL="Command VIs/SetCLUnits.vi"/>
         <Item Name="SetCLUpdateInterval.vi" Type="VI" URL="Command VIs/SetCLUpdateInterval.vi"/>
         <Item Name="SetDeviceAddress.vi" Type="VI" URL="Command VIs/SetDeviceAddress.vi"/>
         <Item Name="SetHostName.vi" Type="VI" URL="Command VIs/SetHostName.vi"/>
         <Item Name="SetMotorType.vi" Type="VI" URL="Command VIs/SetMotorType.vi"/>
         <Item Name="SetVelocity.vi" Type="VI" URL="Command VIs/SetVelocity.vi"/>
         <Item Name="SetZeroPosition.vi" Type="VI" URL="Command VIs/SetZeroPosition.vi"/>
         <Item Name="StopMotion.vi" Type="VI" URL="Command VIs/StopMotion.vi"/>
      </Item>
      <Item Name="Device VIs" Type="Folder">
         <Item Name="DeviceClose.vi" Type="VI" URL="Device VIs/DeviceClose.vi"/>
         <Item Name="DeviceOpen.vi" Type="VI" URL="Device VIs/DeviceOpen.vi"/>
         <Item Name="DeviceQuery.vi" Type="VI" URL="Device VIs/DeviceQuery.vi"/>
         <Item Name="DeviceRead.vi" Type="VI" URL="Device VIs/DeviceRead.vi"/>
         <Item Name="DeviceWrite.vi" Type="VI" URL="Device VIs/DeviceWrite.vi"/>
         <Item Name="GetDeviceAddresses.vi" Type="VI" URL="Device VIs/GetDeviceAddresses.vi"/>
         <Item Name="GetMasterDeviceAddress.vi" Type="VI" URL="Device VIs/GetMasterDeviceAddress.vi"/>
         <Item Name="GetModelSerial.vi" Type="VI" URL="Device VIs/GetModelSerial.vi"/>
         <Item Name="InitMultipleDevices.vi" Type="VI" URL="Device VIs/InitMultipleDevices.vi"/>
         <Item Name="InitSingleDevice.vi" Type="VI" URL="Device VIs/InitSingleDevice.vi"/>
         <Item Name="IsModel8743.vi" Type="VI" URL="Device VIs/IsModel8743.vi"/>
         <Item Name="LogFileWrite.vi" Type="VI" URL="Device VIs/LogFileWrite.vi"/>
         <Item Name="Shutdown.vi" Type="VI" URL="Device VIs/Shutdown.vi"/>
      </Item>
      <Item Name="Sample8743UI" Type="Folder">
         <Item Name="Sample8743UI.vi" Type="VI" URL="Sample8743UI/Sample8743UI.vi"/>
         <Item Name="Global Variables.vi" Type="VI" URL="Sample8743UI/Global Variables.vi"/>
         <Item Name="UIDisable.vi" Type="VI" URL="Sample8743UI/UIDisable.vi"/>
         <Item Name="GetDiscoveredDevices.vi" Type="VI" URL="Sample8743UI/GetDiscoveredDevices.vi"/>
         <Item Name="CreateControllerName.vi" Type="VI" URL="Sample8743UI/CreateControllerName.vi"/>
         <Item Name="UIEnable.vi" Type="VI" URL="Sample8743UI/UIEnable.vi"/>
         <Item Name="FillControllerCombo.vi" Type="VI" URL="Sample8743UI/FillControllerCombo.vi"/>
         <Item Name="OnTimeout.vi" Type="VI" URL="Sample8743UI/OnTimeout.vi"/>
         <Item Name="MotionCheck.vi" Type="VI" URL="Sample8743UI/MotionCheck.vi"/>
         <Item Name="DisplayPosition.vi" Type="VI" URL="Sample8743UI/DisplayPosition.vi"/>
         <Item Name="DisplayErrorsForMasterSlave.vi" Type="VI" URL="Sample8743UI/DisplayErrorsForMasterSlave.vi"/>
         <Item Name="DisplayErrorsForDevice.vi" Type="VI" URL="Sample8743UI/DisplayErrorsForDevice.vi"/>
         <Item Name="OnDeviceSelected.vi" Type="VI" URL="Sample8743UI/OnDeviceSelected.vi"/>
         <Item Name="UpdateUIForSelectedDevice.vi" Type="VI" URL="Sample8743UI/UpdateUIForSelectedDevice.vi"/>
         <Item Name="CloseDevice.vi" Type="VI" URL="Sample8743UI/CloseDevice.vi"/>
         <Item Name="OnGo.vi" Type="VI" URL="Sample8743UI/OnGo.vi"/>
         <Item Name="OnStopMotion.vi" Type="VI" URL="Sample8743UI/OnStopMotion.vi"/>
      </Item>
      <Item Name="SampleGetIDMultiple.vi" Type="VI" URL="SampleGetIDMultiple.vi"/>
      <Item Name="SampleGetIDSingle.vi" Type="VI" URL="SampleGetIDSingle.vi"/>
      <Item Name="SampleRelativeMove.vi" Type="VI" URL="SampleRelativeMove.vi"/>
      <Item Name="SampleGetPositionAllSlaves.vi" Type="VI" URL="SampleGetPositionAllSlaves.vi"/>
      <Item Name="AppendToOutput.vi" Type="VI" URL="AppendToOutput.vi"/>
      <Item Name="Dependencies" Type="Dependencies"/>
      <Item Name="Build Specifications" Type="Build"/>
   </Item>
</Project>
