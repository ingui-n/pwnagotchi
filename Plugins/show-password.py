import logging
import os
import re
from datetime import datetime

import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


class ShowPassword(plugins.Plugin):
    __author__ = 'ingui-n'
    __version__ = '1.0.0'
    __name__ = 'show-password'
    __description__ = 'Shows the password of currently accessible network'

    handshakes_dir = ''

    def __init__(self):
        self.networks = []
        self.network_index = 0
        self.countdown = datetime.now().timestamp()

    def on_loaded(self):
        ShowPassword.handshakes_dir = self.options.get('handshakes_dir', '/home/pi/handshakes')

    def on_ui_setup(self, ui):
        if ui.is_waveshare_v3():
            h_pos = (0, 95)
        else:
            h_pos = (0, 91)

        ui.add_element('show-password', LabeledValue(color=BLACK, label='', value='',
                                                     position=h_pos,
                                                     label_font=fonts.Bold, text_font=fonts.Small))

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('show-password')

    def on_wifi_update(self, agent, access_points):
        logging.info("[show-password]: Searching for passwords")

        self.networks = []

        for ap in access_points:
            if ap['hostname'] != '' and ap['hostname'] != '<hidden>':
                if any(obj.get('hostname') == ap['hostname'] for obj in self.networks):
                    continue

                logging.info(f'[show-password]: SSID: {ap["hostname"]}')
                root_dir = '/home/pi/handshakes'
                pattern = re.compile(r'^' + ap['hostname'] + r'_\w{12}\.pcap\.cracked$')

                for root, dirs, files in os.walk(root_dir):
                    for file in files:
                        if pattern.search(file):
                            full_path = os.path.join(root, file)
                            with open(full_path, 'r') as password_file:
                                password = password_file.read()
                            self.networks.append({'hostname': ap['hostname'], 'password': password})
                            logging.info("[show-password]: Find network: " + ap['hostname'] + " | " + password)

    def on_ui_update(self, ui):
        if len(self.networks) != 0 and self.networks[self.network_index]['hostname']:
            ui.set('show-password', self.networks[self.network_index]['hostname'] + "|" + self.networks[self.network_index]['password'])

            if self.countdown + 5 < datetime.now().timestamp():
                self.network_index += 1
                if self.network_index >= len(self.networks):
                    self.network_index = 0
                self.countdown = datetime.now().timestamp()
        else:
            self.network_index = 0
            ui.set('show-password', '')
