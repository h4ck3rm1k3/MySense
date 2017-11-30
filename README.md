<img src="images/MySense-logo.png" align=right width=100>

# MySense
Last update of the README on 2nd Sept 2017

## Description
Software Infrastructure or framework for managing environmental sensors and data aquisition

## Goal
Provide a generalised dynamic Open Source based infrastructure to allow:
* environmental measurements with sensors
* data acquisition
* dynamic transport of data to other data systems: e.g. databases, mosquitto, Influx,...
* data storage and archiving
* access for free visualisation
* free availability  of the data
* free availability of all software (GPLV4 license)

<div style='vertical-align: top; clear: both'>
<img src="images/MySense-kit-1.png" align=left height=200>
<img src="images/MySense-kit-2.png" height=200>
<br />MySense sensor kits examples
</figure>
</div>
<p>

## How to start MySense
* Create MySense user e.g. `ios` and login as this user.
* Install the software on e.g. the Raspberry Pi 3 on a new user e.g. `ios` in the directory e.g. `MySense`. Use `INSTALL.sh` to install all dependencies and startup scripts.
* Configure MySense.conf using MySense.conf.example as a lead.
* Test one by one the input and output scripts in the python debugger as standalone e.g. `pdb MySDS011.py`. Once this is tested, go to the next step.
* Run Mysense as follows `python MySense.py` and you will see all output on your screen.
* If you use a tiny display: start the display server: `python MyDisplayServer.py start`
* Start up MySense: `python MySense.py start`

If needed See the README files and documentation files in `docs` for more detailed info.

If you installed a led switch (controlled by `/usr/local/bin/poweroff`:
* Pressing the switch longer as 20 seconds will poweroff the Pi
* Pressing the switch longer as 10 seconds will reboot the Pi
* Pressing the switch 6 seconds will restart a search for wired or wifi internet connectivity.
* If the Pi is powered off a discoonect and connect of the adapter will boot the Pi.

Without internet connectivity the MySense software will not be started on a reboot.

The `@reboot /home/ios/MySense/MyStart.sh` in the ios crontab table will automatically start MySense on a reboot. Comment this out in the test phase.

# MySense box
## Sensor kit case

<div style='vertical-align: top; clear: both'>
<img src="images/MySense-2-kast.png" align=left height=100>
The sensor kit case is build from PVC roof gutter pieces: gutter end pieces for keeping the air in and the rain out, and overflow gutter box as casing.
The case has a poweroff button and small window to show a tiny display with current measurements. The senors are fixated on a Lego plate to allow flexibility of sensor changes.
</div>
See for a How To: README.case.md
<p>

# Software
## Scripts
All scripts are written in Python 2. Python 3 is supported but not tested well.
Scripts have been tested on Raspberry Pi (2 and 3) running Wheezy, Jessie and Stretch Debian based OS.
Scripts have a -h (help) option. With no arguments the script will be started in interactive mode. Arguments: *start*, *status*, *stop*.

### Support scripts
* MyLed.py: control the Pi with button to poweroff and put it in wifi WPA mode. Pi will set up a wifi access point `MySense` if no internet connectivity could be established via wifi or LAN.
* MyDisplayServer.py, a display service: messages received will be shown on a tiny Adafruit display.

### Main script
The main python script is MySense.py. It acts as intermediate beween input plugins and output channels. It uses `MySense.conf` (see MySense.conf.example) to configure itself.
The MySense configuration file defines all plugins available for the MySense.py command.

* input (modules) plugins: temperature, dust, etc. sensor device modules and brokers
* output (modules) channels: console output, (MySQL) database, (CSV/gspread) spreadsheets, and brokers (mosquitto, InFlux, ...).

Try `./MySense.py --help` to get an overview.

On the command line the option --input and --output plugins can be switched on (all other configured plugins are disabled).

#### operation phases
MySense starts with a configuring phase (options, arguments, reading configuration, loading modules), whereafter in the `readsensors()` routine it will first access the input modules to obtain measurement values, combine them into an internal buffer cache per output channel, and finaly tries per output channel to empty the queued records.

The output of sensor values to an output channel will always on startup to send an identification json info record.
Each configurable interval period of time MySense will send (input) measurements values to all configured output channels. For each output channel connected via internet MySense will keep a queue in the case the connection will be broken. If the queue is exceeding memory limits the oldest records in the queue will be deleted first.
If the configured *interval* time is reached it will redo the previous loop.

If switched on and configured an email with identification information will be sent to the configured user.
Make sure one obeys the Personally Identifiable Information ([PII]http://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-122.pdf) privacy rulings.

### Plugin configuration 
MySense.conf is the configuration/init file from which plugin or modules are imported into the MySense process. See the `MySense.conf.example` for all plugins (sections) and the plugin options.

For every plugin module there is an README.plugin with explanations of the input/output plugin.
The input from sensors is read asynchronous (in parallel) via the module MyTHREAD.py.
If needed it can be switched to read only in sync with the other input sensors.

A working example of MySense script in todays operation:
```
          remote access             |  INTERNET (wired/wifi, wifi-G3/4 mobile)
          syst.mgt.     webmin -----||_ wifi AP -- webmin/ssh system mgt
                    ssh tunnel -----|
            Remot3 (Weaved)IoT -----|
                                    |
                                    |    
    INPUT PLUGINs                   |        OUTPUT CHANNELS    GATEWAY/BROKER
                                  __|__
    DHT11/22-meteo ---GPIO---->| ///|\\\ |>- CSV                _____
    GPS-locator ------RS232--->|=MySense=|>- console           ///|\\\  
    RSSI-wifi signal-strength >||  Pi3  ||>- MYSQL           |=MySense=|>-gspread
    Dylos-dust -USB-- RS232--->||Stretch||>- Mosquitto pub-->|| Debian||>-MySQL
    Grove-loudness ---GPIO---->| \\\|/// |>- HTTP-Post       || Linux ||>-CSV
    EMS280 -meteo ----I2C----->|    |    |>- email info      | \\\|/// |>-console
    PPD42NS -dust-Arduino-USB->|    |    |>- InFlux publish  |         |>-InFlux pub
    Nova SDS011 -dust -USB --->|    |    |>- display SSD1306
    Plantower PMS7003 -USB --->|    |    |>- Google gspread (alpha, depricated)
    BME680 -meteo+gas--I2C --->|    |    |   (planned Dec 2017)
    Adafruit rain -------GPIO->|    |    |   (in develop Dec 2017)
    O3,NO2,CO,H2S -SPECK--USB->|    |    |   (beta test Dec 2017)
    NH3(Alpha)--SPECK-----USB->|    |    |   (planned Jan 2018)
    LoRaWan (planned) -------->|    |    |>- broker? (planned)
    Mosquitto sub ----server ->|    |    |>- LoRaWan (planned, TTN end of 2017)
    InFlux subscribe -server ->|    |    |>- Bluetooth (planned)
                                    |
                                    |>-raw measurement values -> InFlux server or file
                                           calibration
```

## Configuration
See `MySense.conf.example for an example of `MySense.conf`.

Use for configuration of plugins/outputchannels the `section` (plugin name in lowercase) and section options.
The option `input = True or False` and `output = T/F` will define resp input plugin and output channel
to be imported and to be switched on or off.
Input plugins as for gas and dust (particle counts) will have a configurable sample time (time to get vales) and interval time (time (interval minus sample) to wait before the next sample).
The MySense main loop has an own `interval` time within input plugin sensor values will be collected (sliding average from sample values) and push values to output channels.

## Interaction data format
Interaction with plugins and output channels is done in json datastructure:
Example of json to display a measurement on the console (and others):
```javascript
     { "time": UNIXtimeStamp,
        "temp": 23.2,
        "rh": 30.2,
        "pm": 234.2,
        "o3": None }
```

At the startup MySense.py will start with an identification record providing details of the version, the location if available, a unique identifier, sensor types and measurement unit, etc.
This information will define eg the first row of a spreadsheet or the database table with all sensor info (called Sensors).

Towards a broker the output will consist of an (updated e.g. GPS location) combination of the data json record and the infomration json record:
```javascript
    { "ident": id-record, "data": data-record }
```
See for an example the file: `testdata/Output_test_data.py`

The input sensor plugins provide (sliding window of a per plug definable buffer size)) averages in a per input plugin defined interval time in seconds. The output is done on a general interval period timing using the average time of input timings.

Typical input rate from a sensor is 60 seconds (can be tuned) and for brokers it is 60 minute interval (can be tuned).

## Brokers
MySense can act either *sensor manager* or as *input from broker manager* to a set (dynamic) of output channels. 

Available input plugins:
* Dust: Dylos DC1100 or 1700 via serial interface, Shinyei GPIO (e.g. Grove dust sensor)
* Temperature/humidity: Adafruit DHT11/22 or AM3202 and Grove variants
* RSSI (strength of wifi signal): via the platform
* Location: GPS (GPS Ultimate from Adafruit/Grove) via TTL serial interface

## Remote management
The Pi allows to install a wifi connectivity with internet as well a virtual wifi Access Point. A backdoor configuration is provided via direct access to `webmin` and `ssh` (Putty), as well via a proxy as *ssh tunneling* and/or using the proxy service of Weaved (`https://www.remot3.it/web/index.html`).

## Hardware Platform
Sensors have a hardware interface to I2C, GPIO: those sensors are tested on RaspBerry Pi (and Arduino Uno)
Sensors with USB serial are tested on Linux Debian platforms which run Python.

## Installation
See README.pi for installation of the Raspberry Pi platform.
MySense plugins: Use the shell file `INSTALL.sh [DHT GPS DB plugin ...]` to download all dependent modules.

The sensor plugins, and output modules can be tested in *standalone mode*, e.g. for BME280 Bosch chip, use `python MyBME280.py`. Or use the Python debugger `pdb` in stead. See the script for the use of sync and debug options at the end of the script to test.

## Documentation
See the REAME's and docs directory for descriptions how to prepair the HW, python software and Pi OS for the different modules.

`CONTENT.md` will give an overview of the files and short description.

## Operation status
See the various README/docs directory for the plugin's and modules for the status of operation, development status, or investigation.

Failures on internet connectivity and so retries of access is provided.

## Extensive test support
Use the following first if one uses MySense for the first time: test each sensor input or output channel one at a time first.
Use the Conf dictionary to set configuration for the test of the module.

The sensor plugin as well the output pugin channels *all* have a `__main__` test loop in the script.
This enables one to test each plugin (one at a time) in standalone modus: `pdb MyPLUGIN.py`.
Use for the sensor input plugins `Conf['sync']=False` (to disable multithreading) and switch debug on: `Conf['debug']=True`.
Set the python debugger `pdb` to break on `break getdata` (input plugin) or `break publish` for stepping through the script. Failures in configuration are shown in this way easily.

After you have tested the needed input/output modules: To test the central script `MySense.py` use first the Python debugger `pdb`. The main routine after the initiation and configuration phase is `sensorread`, in `pdb` use `break sensorread`. Continue to this break point and use `print Conf` to show you the configuration settings. Step to the first `getdata` call or `publish` call to go into the input or output module.
Note that the `getdata()` input routine may need some time in order to allow the module to collect measurement(s) from the sensor.

## Current development focus

<img src="images/SensorKit.png" width=300 align=right>
The MySense framework/infrastructure is operational as lab test model (alpha phase).

By default MySense uses a so called lightweight process (multithreaded) to allow sensor data to be collected asynchronously.
Input is tested with serial, I2C-bus and GPIO sensors (meteo,dust,geo,audio, (gas in September 2017).
The focus is to allow Grove based sensors (easier to plugin to the MySense system) and weather resistent cases for the system.

The gas sensor development (NO2, O3, NH3, CO) is just (Febr 2017) started, Aug 2017 alpha tests.

## Calibration
Calibration of dust counters like Shinyei, Nova SDS011 and Dylos is started in May/June 2017.
Outdoor correlation tests started Sept 2017.

Calibration of Alpha Sense gas sensors is a problematic area. Probably Sept 2017. First tests show Alpha Sense O3, CO2 are OK, NO2 not successfull, NH3 prosponed.

To facilitate measurements for calibration purposes all sensor plugins are optionaly (set `raw` option to `True` for the particular sensor in `MySense.conf`) able to output on file or to an InFlux DB server the *raw* measurements values, as follows:
```
    raw,sensor=<type> <field1>=<value1>,<field2>=<value2>,... <nano timestamp>
```
This is an InFlux type of telegram, where the UNIX timestamp is in nano seconds. Example for database BdP_02345pa0:
```
    raw,sensor=bme280 temp=25.4,rh=35.6,pha=1024 1496503325005000
    raw,sensor=dylos pm25=250,pm10=15 1496503325045000
```
E.g. download the *serie* for eg correlation calculation from this server or into a CVS file (`awk` maybe your friend in this).
Or use a file, say `MyMeasurements_BdP_02345pa0.influx`.
```shell
    # send the file to the InFluxdb server via e.g.
    curl -i -XPOST 'http://localhost:8086/write?db=BdP_02345pa0&u=myname&p=acacadabra' --data-binary @MyMeasurements_BdP_02345pa0.influx
```
InFlux query reference manual:
* https://docs.influxdata.com/influxdb/v1.2/query_language/

Using the Influx CLI (command line interface) one is able to convert the columnized output into whatever format, e.g. to CSV:
```
    influx --format csv | tee InFlux.csv
    >auth myname acacadabra
    >use db_name
    >show series
    >select * from raw order by time desc limit 1
    >select * from raw where time > now() - 2d and time < now() - 1d order by time desc
    >quit
```

After the correlation calculation set for the sensor the `calibration` option: e.g. `calibration=[[25.3,-0.5],[13.5,63.203,0.005]]` for here two fields with a linear regression: `<calibrated value> = 25.3 - 0.5 * <measured value>` for the first field values. The second field has a 2-order polynomial as calibration.

To avoid *outliers* the MySense input multi threading module will maintain a sliding average of a window using the buffersize and interval as window parameters. Python numpa is used to delete the outliers in this window. The parameters for this filtering technique are default set to a spread interval of 25% (minPerc MyThreading class parameter)) - 75% (maxPerc). Set the parameters to 0% and 100% to disable outlier filtering. Set busize to 1 to disable sliding average calculation of the measurements.

### Calibration tool
For calibration the Python tool `statistics/Calibration.py` has been developped. The script uses pyplot and is based on numpy (numeric analyses library). The calibration uses values from two or more database columns, or (XLSX) spreadsheets, or CSV files as input and provides a best fit polynomial (dflt order 1/linear), the R square and shows the scattered plot and best fit graph to visualize the difference between the sensors. Make sure to use a long period of measurements in a fluctuating environment (a fixed indoor temperature measurement comparison between two temp sensors does not make much sense).

### Test remarks and experience

#### meteo
The DHT meteo sensors show intermittant lots of read errors. The meteo sensor BME280 is current focus.

#### dust
The Shiney PPD42NS (tested 3 sensors) gave lots of null reading on low PM10 values. The sensor values are not stable enough in comparison with newer sensors from Nova and Plantower as well the bulky Dylos handhelt.

Due to airflow the sensors need to be cleaned periodically. The Plantower sensor is hard to clean as it cannot be opened.

Plantower dust sensor measures also PM0.3, PM0.5, PM1 and PM5.

Plantower and Nova dust sensors use USB bus. The values are privided in mass values. The conversion from particle count to mass is not made public.

#### gas
Tghe Alpha Sense gas sensors have a high cost level (ca 80 euro per gas). NH3 is hard to test and still planned. NO2 give too many errors in the field. The sensors have a very limited time.

#### GPS
The Grove GPS sensors is applied via USB bus connection and the standard Debian GPS deamon. The location is not precise enough. The wait is for the Galileo GPS sensors availability.

#### Raspberry Pi
The tests are done with the Raspberry Pi 3. With the GrovePi+ shield and the big V5/2.5A adapter it gets bulky. The new Raspberry Pi Zero V1.3 is half size, uses far less power and costs only 25% of the Pi3.
We expect the Zero might be applicable.

## Costs
There is no funding (costs and development time is above personal budget level).
Costs at start are high due to failures on tests of common sensors (Arduino is skipped due to too low level of functionality; Shiney and DHT sesnors failures, application of smaller adaptors, etc.).
Money is lacking for sensors research and travel expenses coverage to meet other initiatives.

July 2017: local government is asked to subsidy operational phase: distribution of sensors kits and maintenance.

## Licensing:
FSF GPLV4
Feedback of improvements, or extentions to the software are required.
* Copyright: Teus Hagen, ver. Behoud de Parel, the Netherlands, 2017

## References
A list of references for the documentation and/or code used in MySense.py:
* Open Data Stuttgart ESP8266 controller oriented: https://github.com/opendata-stuttgart
* MIT Clairity CEE Senior Capstone Project report V1 dd 15-05-14
* https://www.challenge.gov/challenge/smart-city-air-challenge/ Smart City Air Challenge (2016, USA GOV)
See also: https://developer.epa.gov/air-pollution/
* http://opensense.epfl.ch/wiki/index.php/OpenSense_2
* http://mysensors.org
* http://opensensors.io
* http://mydevices.org (Cayenne)
* https://waag.org/nl/project/urban-airq Waag Society Amsterdam Smart Citizens Lab Urban AirQ
* http://www.citi-sense.eu/ Citi-Sense EU project
* http://waag.org/nl/project/smart-citizen-kit Smart-Citizen-Kit Waag Society
* http://smartemission.ruhosting.nl/ Smart Emission, Maps 4 Society Nijmegen
* https://github.com/guyzmo/polluxnzcity Pollux NZcity, NZ
* https://github.com/HabitatMap/AirCastingAndroidClient AirCasting on Android Client
* https://mosquitto.org/ Mosquitto (MQTT) broker
* https://docs.influxdata.com/influxdb/v1.2/ documentation from InFluxData.com
* https://cdn.hackaday.io/files/21912937483008/Thomas_Portable_Air_Quality.pdf interesting overview of sensors
