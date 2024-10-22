//
// Copyright 2015-2021 by Garmin Ltd. or its subsidiaries.
// Subject to Garmin SDK License Agreement and Wearables
// Application Developer Agreement.
//

import Toybox.Application;
import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Sensor;
import Toybox.WatchUi;
import Toybox.System;
import Toybox.Time;




//! View that shows the heart rate graph and current heart rate
class SensorTester extends WatchUi.View {
    private var _hrGraph as LineGraph;
    private var _hrString as String;

    //! Constructor
    public function initialize() {
        View.initialize();
        Sensor.setEnabledSensors([Sensor.SENSOR_HEARTRATE] as Array<SensorType>);
        Sensor.enableSensorEvents(method(:onSnsr));
        _hrGraph = new $.LineGraph(20, 10, Graphics.COLOR_RED);

        _hrString = "---bpm";
    }

    //! Update the view
    //! @param dc Device context
    public function onUpdate(dc as Dc) as Void {
        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_BLACK);
        dc.clear();

        dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);

        dc.drawText(dc.getWidth() / 2, 90, Graphics.FONT_LARGE, _hrString, Graphics.TEXT_JUSTIFY_CENTER);

        _hrGraph.draw(dc, [0, 0] as Array<Number>, [dc.getWidth(), dc.getHeight()] as Array<Number>);
    }

    //! Handle sensor updates
    //! @param sensorInfo Updated sensor data
    public function onSnsr(sensorInfo as Info) as Void {
        var heartRate = sensorInfo.heartRate;

        if (heartRate != null) {
            _hrString = heartRate.toString() + "bpm";
            System.print("Heart rate: " + heartRate.toString() + "\n");

            var options = {
                :method => Communications.HTTP_REQUEST_METHOD_POST
            };

            var data = {
                "timestamp" => Time.now().value(),
                "heartRate" => heartRate
            };


            Communications.makeWebRequest(
                "https://jiranek-chochola.cz/die-experts/index.php",
                data,
                options,
                method(:onReceive)
            );

            // Add value to graph
            _hrGraph.addItem(heartRate);
        } else {
            _hrString = "---bpm";
        }

        WatchUi.requestUpdate();
    }

    //! Receive the data from the web request
    //! @param responseCode The server response code
    //! @param data Content from a successful request
    public function onReceive(responseCode as Number, data as Dictionary<String, Object?> or String or Null) as Void {
        if (responseCode == 200) {
            System.print("Data: " + data);
        } else {
             System.print("Error: " + responseCode.toString());
        }
    }
}

//! This app shows how to use sensors. It displays the current heart rate,
//! along with a time series graph of the heart rate from the last 20 seconds. 
class SensorTest extends Application.AppBase {

    //! Constructor
    public function initialize() {
        AppBase.initialize();
    }

    //! Handle app startup
    //! @param state Startup arguments
    public function onStart(state as Dictionary?) as Void {
    }

    //! Handle app shutdown
    //! @param state Shutdown arguments
    public function onStop(state as Dictionary?) as Void {
    }

    //! Return the initial view for the app
    //! @return Array [View]
    public function getInitialView() as Array<Views or InputDelegates>? {
        return [new $.SensorTester()] as Array<Views>;
    }
}
