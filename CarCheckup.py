import obd
from obd import OBDStatus, commands
import inspect
from pprint import pprint
from pint import UnitRegistry as ureg
import argparse

class Obd_conn:
    def __init__(self, command, *args):
        try:
            self.conn = obd.OBD()
            if OBDStatus.NOT_CONNECTED:
                raise ConnectionError('cannot locate obd adaptor')
            elif OBDStatus.ELM_CONNECTED:
                raise ConnectionError('obd adaptor has been located however unable to connect to vehicle')
            
        except ImportError:
            raise ImportError('cound not find module or could not find name "OBD" within module')

        self.commands = {c for c in self.conn.supported_commands}
        exec_command = command
        self._func_factory(exec_command)


    def _func_factory(self, command):
        if command == 'connection_info':
            return self.connection_info()
        elif command == 'retrieve_errors':
            return self.retrieve_errors()
        elif command == 'engine_check':
            return self.engine_check()
        elif command == 'check_all':
            return self.check_all()
        elif command == 'trip_speed':
            return self.trip_speed()
        else:
            raise ValueError("the command '{}' does not exist".format(command))

    
    def all_commands(self):
        return self.commands


    def connection_info(self):
        """Displays the port name, protocol id and protocol name of the obd adapter currently in use
        
        
        Returns:
            Bool: checks whether the program is connected to the vehicle
        
        """
        if self.conn.is_connected():
            print("Port: {}".format(self.conn.port_name()))
            print("Protocol id: {}".format(self.conn.protocol_id()))
            print("Protocol name: {}".format(self.conn.protocol_name()))
            return True
        
        return False


    def retrieve_errors(self):
        """returns an array of all error codes from the vehicle"""

        dtc = [{k: v for k, v in c } for c in obd.commands.GET_DTC.response.value]
        for err, msg in dtc:
            print("err code: {} | message: {}".format(err, msg))


    def engine_check(self):
        try:
            e_check = obd.commands.GET_DTC.response.value
            if e_check.MIL:
                print('Check Engine light is on!')
                print("ignition type: {}".format(e_check.ignition_type))
            else:
                print("all's good :)")
        except:
            pass


    def check_all(self):
        for c in self.commands:
            response = self.conn.query(c)
            if not response.is_null():
                print("Command Name: {}".format(c))
                print("response value: {}".format(response.value))
                print("Return message: {}".format(response.message))
            else:
                print('could not return any values from the vehicle. Allresponse values were equal to none')


    def trip_speed(self, units='kph'):
        """returns the average speed of a trip from the time the vehichle engine starts"""
        count = 0
        speed_total = 0
        if self.conn.query(commands.ENGINE_LOAD).is_null():
            return 'could not retrieve non-null response from vehicle'
        while self.conn.query(commands.ENGINE_LOAD) <= 0:
            continue
        else:
            while self.conn.query(commands.ENGINE_LOAD) > 0:    
                speed_total += query(commands.SPEED)
                count += 1

        avg_speed = speed_total / count
        
        if units == 'mph':
            avg_speed = avg_speed * 0.621
        
        return avg_speed


    def close(self):
        self.conn.close()


def main():
    parser = argparse.ArgumentParser(description="Investigate errors represented by error codes retrieved from your cars computer via the obd port")
    parser.add_argument('-cmd', help="""
                                        Availiable commands:
                                        
                                            -connection_info
                                            -retrieve_errors
                                            -engine_check
                                            -check_all
                                            -trip_speed
                                            """, dest="command", type=str, required=True)

    # parser.set_defaults(func=Obd_conn.__init__)
    args = parser.parse_args()
    arg = args.command
    Obd_conn(arg)

if __name__ == '__main__':
    main()
