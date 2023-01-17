# coding=utf-8

"""

Copyright(c) 2022-2023 Max Qian  <astroair.cn>

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

from flask import render_template,request,Flask
from flask_login import login_required

def create_search_template(app : Flask , csrf):
    """
        Create a search template
    """

    @app.route('/search/api/<target_id>',methods=['GET'])
    @app.route('/search/api/<target_id>/',methods=['GET'])
    @login_required
    def search_target(target_id : str):
        """
            Search a target by target id
            Args:
                target_id : str # Like 'm1' or 'M1'
            Returns:
        """