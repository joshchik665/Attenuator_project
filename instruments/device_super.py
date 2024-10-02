from pyvisa import ResourceManager

class InstrumentUtilty():
    def __init__(self,ip_address):
        rm = ResourceManager()
        
        try:
            # Adjust the VISA Resource string to fit your instrument
            ip_address = self.remove_leading_zeros(ip_address)
            self.my_instrument = rm.open_resource('TCPIP::'+ip_address+'::INSTR')
            self.idn = self.my_instrument.query('*IDN?')
            print('Hello I am: ' + self.idn) # Asks the FSW it's ID
            self.connected = True
            self.my_instrument.write('*RST')
        except ValueError:
            print('value error, IP address is most likely typed wrong')
            self.connected = False
        except Exception as ex:
            print('Error initializing the instrument session:\n' + ex.args[0])
            self.connected = False
        
        self.idns = {
            'Agilent Technologies,L4490A': 'Keysight_J7204B'
        }
        
        self.device_type = 'unknown'
        
        for key,value in self.idns.items():
            if self.idn.startswith(key):
                self.device_type = value
    
    
    def remove_leading_zeros(self, ip_address):
        parts = ip_address.split('.')
        
        parts = [str(int(part)) for part in parts]
        
        clean_ip_address = '.'.join(parts)
        
        return clean_ip_address


