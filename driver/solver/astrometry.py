# coding=utf-8

"""

Copyright(c) 2022 Max Qian  <astroair.cn>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Library General Public
License version 3 as published by the Free Software Foundation.
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.
You should have received a copy of the GNU Library General Public License
along with this library; see the file COPYING.LIB.  If not, write to
the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301, USA.

"""

from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from json import dump
from driver.basicsolver import BasicSolver,SolverInfo

from yaml import (safe_load,safe_dump)
from utils.lightlog import lightlog

log = lightlog(__name__)

import gettext
_ = gettext.gettext

class astrometry(BasicSolver):
    """Astrometry solver class"""

    def __init__(self) -> None:
        self.info = SolverInfo()
        self.api_url = "https://nova.astrometry.net/api/"
        self.session = None

    def __del__(self) -> None:
        return super().__del__()

    def online_solver(self, params: dict) -> dict:
        """
            Online solver via Astrometry.net API
            Args:
                params (dict): dictionary of parameters
                    {
                        "api_key": string,
                        "api_key_id": string,
                        "img" : {
                            "filename": string,
                            "downsample": int,
                            "ra" : str,
                            "dec" : str
                            TODO: Add more parameters
                        }
                    }
            Return:
                {
                    "status": "success","error","warning","debug"
                    "message": "",
                    "params": {
                        "result" : str
                        "info" : SolverInfo object
                    }
                }
            Note : Before executing this function please check the internet connection
        """
        # Login before upload image
        def login(self, apikey):
            args = { 'apikey' : apikey }
            result = self.send_request('login', args)
            self.session = result.get('session')
    

    def send_request(self, service, args={}, file_args=None):
        '''
        service: string
        args: dict
        '''
        if self.session is not None:
            args.update({ 'session' : self.session })
        json = dump(args)
        url = self.apiurl + service
        # If we're sending a file, format a multipart/form-data
        if file_args is not None:
            import random
            boundary_key = ''.join([random.choice('0123456789') for i in range(19)])
            boundary = '===============%s==' % boundary_key
            headers = {'Content-Type':
                       'multipart/form-data; boundary="%s"' % boundary}
            data_pre = (
                '--' + boundary + '\n' +
                'Content-Type: text/plain\r\n' +
                'MIME-Version: 1.0\r\n' +
                'Content-disposition: form-data; name="request-json"\r\n' +
                '\r\n' +
                json + '\n' +
                '--' + boundary + '\n' +
                'Content-Type: application/octet-stream\r\n' +
                'MIME-Version: 1.0\r\n' +
                'Content-disposition: form-data; name="file"; filename="%s"' % file_args[0] +
                '\r\n' + '\r\n')
            data_post = (
                '\n' + '--' + boundary + '--\n')
            data = data_pre.encode() + file_args[1] + data_post.encode()

        else:
            # Else send x-www-form-encoded
            data = {'request-json': json}
            print('Sending form data:', data)
            data = urlencode(data)
            data = data.encode('utf-8')
            print('Sending data:', data)
            headers = {}

        request = Request(url=url, headers=headers, data=data)
        try:
            f = urlopen(request)
            print('Got reply HTTP status code:', f.status)
            txt = f.read()
            print('Got json:', txt)
            result = dump(txt)
            print('Got result:', result)
            stat = result.get('status')
            print('Got status:', stat)
            if stat == 'error':
                errstr = result.get('errormessage', '(none)')
            return result
        except HTTPError as e:
            print('HTTPError', e)
            txt = e.read()
            open('err.html', 'wb').write(txt)
            print('Wrote error text to err.html')