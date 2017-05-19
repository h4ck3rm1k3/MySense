#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Contact Teus Hagen webmaster@behouddeparel.nl to report improvements and bugs
# 
# Copyright (C) 2017, Behoud de Parel, Teus Hagen, the Netherlands
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# $Id: MyINFLUXPUB.py,v 1.6 2017/05/19 21:22:39 teus Exp teus $

# TO DO: write to file or cache
# reminder: InFlux is able to sync tables with other MySQL servers

""" Publish measurements to InFlux time series database
    Relies on Conf setting by main program
"""
modulename='$RCSfile: MyINFLUXPUB.py,v $'[10:-4]
__version__ = "0." + "$Revision: 1.6 $"[11:-2]

try:
    import MyLogger
    import sys
    from influxdb import InfluxDBClient
    from influxdb import exceptions
    import datetime
    from time import time
except ImportError as e:
    MyLogger.log("FATAL","One of the import modules not found: %s" % e)

# configurable options
__options__ = ['output','hostname','port','database','user','password','identification']

Conf = {
    'output': False,
    'hostname': 'localhost', # host InFlux server
    'user': None,        # user with insert permission of InFlux DB
    'password': None,    # DB credential secret to use InFlux DB
    'database': None,    # InFlux database/table name
    'port': 8086,        # default mysql port number
    'fd': None,          # have sent to db: current fd descriptor, 0 on IO error
    'omit' : ['version','intern_ip'],  # fields not archived
}

# ========================================================
# write data directly to a database
# ========================================================
# create table <ProjectID_Serial>, record columns,
#       registration Sensors table on the fly
def attributes(**t):
    global Conf
    Conf.update(t)

# connect to db and keep connection as long as possible
def db_connect(net):
    """ Connect to InFlux database and save filehandler """
    global Conf
    if not 'fd' in Conf.keys(): Conf['fd'] = None
    if not 'last' in Conf.keys():
        Conf['waiting'] = 5 * 30 ; Conf['last'] = 0 ; Conf['waitCnt'] = 0
    if (Conf['fd'] == None) or (not Conf['fd']):
        if (Conf['hostname'] != 'localhost') and ((not net['module']) or (not net['connected'])):
            MyLogger.log('ERROR',"Local access database %s / %s."  % (Conf['hostname'], Conf[database]))      
            Conf['output'] = False
            return False
        for M in ('user','password','hostname','database'):
            if (not M in Conf.keys()) or not Conf[M]:
                MyLogger.log('ERROR','Define InFlux details and credentials.')
                Conf['output'] = False
                return False
        if (Conf['fd'] != None) and (not Conf['fd']):
            if ('waiting' in Conf.keys()) and ((Conf['waiting']+Conf['last']) >= time()):
                raise IOError
                return False
        try:
            Conf['fd'] = InfluxDBClient(
                Conf['hostname'], Conf['port'],
                Conf['user'], Conf['password'],
                Conf['database'], timeout=2*60)
            all_dbs_list = Conf['fd'].get_list_database()
            if { 'name': Conf['database'] } not in all_dbs_list:
                try:
                    if not Conf['fd'].create_database(Conf['database']):
                        MyLogger.log("WARNING", "InFlux unable to create the database %s" % Conf['database'])
                        return False
                except:
                    raise IOError
                MyLogger.log("ATTENT", "Created InFlux db: {0}".format(Conf['database']))
            Conf['fd'].switch_database(Conf['database'])
            Conf['last'] = 0 ; Conf['waiting'] = 5 * 30 ; Conf['waitCnt'] = 0
            return True
        except IOError:
            Conf['last'] = time() ; Conf['fd'] = 0 ; Conf['waitCnt'] += 1
            if not (Conf['waitCnt'] % 5): Conf['waiting'] *= 2
            raise IOError
        except:
            Conf['output'] = False; del Conf['fd']
            MyLogger.log('ERROR',"InFlux Connection failure type: %s; value: %s" % (sys.exc_info()[0],sys.exc_info()[1]) )
            return False
    else:
        return Conf['output']

ErrorCnt = 0
def Influx_write(database, data, tags):
    ''' send telegram to InFlux server. Parameters came from reverse engineering
        of the http request
        tags are strings, data is int/float values
        measurement is type: info or data
        telegram structure: measurement,column=string,... column=int_float,...
    '''
    global Conf
    if (not 'type' in tags.keys()) or not len(tags['type']):
        MyLogger("ERROR","Influx: unknown type of data.")
        return True
    if (not len(data) ) or (not len(database)): return True
    data_values = []
    data_tags = [tags['type']]
    for strg in [tags,data]:
        for item in strg.keys():
            if (strg == tags) and (item == 'type'): continue
            value = strg[item]
            if type(value) is list:
                value = [ "{}".format(a) for a in value ]
                value = ','.join(value)
            if (type(value) is str) or (type(value) is unicode):
                value = '"{}"'.format(value.replace(',','\,'))
            if strg == tags:
                data_tags.append("{}={}".format(item,value))
            else:
                data_values.append("{}={}".format(item,value))
    data_line = ','.join(data_tags) + ' ' + ','.join(data_values)
    try:
        return Conf['fd'].request('write','POST',{'db':database,'precision':'s'},data_line,204)
    except exceptions.InfluxDBClientError as err:
        MyLogger("ERROR","Influx: error: {}".format(err))
    ErrorCnt += 1
    return False

# registrate the sensor to the Sensors table and update location/activity
def db_registrate(net,ident):
    """ create or update identification inf to Sensors table in database """
    global Conf
    if ("registrated" in Conf.keys()) and (Conf['registrated'] != None):
        return Conf['registrated']
    if len(ident['fields']) == 0:
        return False
    if (not 'database' in ident.keys()) or (ident[database] == None):
        Conf['database'] = ident['project']+'_'+ident['serial']
    if not db_connect(net):
        return False

    # next fails on non admin priv users
    tags = {'type':'info'}
    data = {}
    # the tags: type info or data, project, serial, label
    for item in ['label']:
        if (item in ident.keys()) and ident[item] != None:
           tags[item] = ident[item]
    # the fields: information about the sensor
    for item in ident.keys():
        if item in Conf['omit']: continue
        if type(ident[item]) is list:
            data[item] = ','.join(ident[item])
        else:
            data[item] = ident[item]
    # retention_policy = 1h, 90m, 12h, 7d, 4w, INF
    # data is sent as json dump as UDP to server
    if not Influx_write(Conf['database'], data, tags):
        raise IOError("InFlux connection/send problem")
    MyLogger.log('ATTENT',"New registration to InFlux Sensors series.")
    Conf['new'] = 1
    Conf["registrated"] = True
    return True

def publish(**args):
    """ add records to the database,
        on the first update table Sensors with ident info """
    global Conf, ErrorCnt
    if (not 'output' in Conf.keys()) or (not Conf['output']):
        return
    for key in ['data','internet','ident']:
        if not key in args.keys():
            MyLogger.log('FATAL',"Broker publish call missing argument %s." % key)

    # translate MySense field names into InFlux column field names
    # TO DO: get the transaltion table from the MySense.conf file
    def db_name(my_name):
        DBnames = {
        }
        if my_name in DBnames.keys(): return DBnames[my_name]
        return my_name

    if Conf['fd'] == None: Conf['registrated'] = None
    if not db_registrate(args['internet'],args['ident']):
        MyLogger.log('WARNING',"Unable to registrate the sensor.")
        return False
    if Conf['fd'] == None:
        return False
   
    fields = {}
    for item in args['data'].keys():
        if item in Conf['omit']: continue
        if not args['data'][item]: continue
        Nm = db_name(item)
        if type(args['data'][item]) is list:
            MyLogger.log('WARNING',"Influx: Found list for sensor %s." % item)
            for i in range(0,len(args['data'][item])):
                fields["%s_%d" % (Nm,i)] = args['data'][item][i]
        else:
            fields[Nm] = args['data'][item]
    tags = {'type': 'data', 'new': Conf['new']}
    for item in ['label','geolocation']:
        if (item in args['ident'].keys()) and args['ident'][item]:
            tags[item] = args['ident'][item]
            if item in fields.keys():
                tags[item] = fields[item]
                del fields[item]
    # keep data for 12 hours, indicate this is the first data sent, label data
    if not Influx_write(Conf['database'], fields, tags):
        MyLogger("ATTENT","Sending data to InFlux server failed")
        if ErrorCnt > 10:
            Conf['fd'] = None
            raise IOError("Influx server connection failure.")
        return False
    ErrorCnt = 0
    Conf['new'] = 0
    return True

# test main loop
if __name__ == '__main__':
    from time import sleep
    Conf['output'] = True
    Conf['hostname'] = 'lunar'         # host InFlux server
    Conf['user'] = 'ios'               # user with insert permission of InFlux DB
    Conf['password'] = 'acacadabra'    # DB credential secret to use InFlux DB
    net = { 'module': True, 'connected': True }
    try:
        import Output_test_data
    except:
        print("Please provide input test data: ident and data.")
        exit(1)

    for cnt in range(0,len(Output_test_data.data)):
        timings = time()
        try:
            publish(
                ident=Output_test_data.ident,
                data = Output_test_data.data[cnt],
                internet = net
            )
        except Exception as e:
            print("output channel error was raised as %s" % e)
            break
        timings = 30 - (time()-timings)
        if timings > 0:
            print("Sleep for %d seconds" % timings)
            sleep(timings)
