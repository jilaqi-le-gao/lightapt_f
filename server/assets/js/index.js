/*
 * Copyright(c) 2022 Max Qian  <astroair.cn>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 * 
 */

/*
 * index.js 
 * 
 *
*/

/*
 * connect | 连接
 * Args: none
 * Returns: none
 *
 */
function connect(){
    var ip = document.getElementById("ipAddress"),
        url = extractHostname(ip.value);
    ip.value = url,tcpPort = getTcpPort();
    let ws_protocol = getWs_protocol();
    "localhost"===urlpart?(wsUri=ws_protocol+urlpart.toString()+":"+tcpPort,createWebSocket()):""===urlpart?(wsUri=ws_protocol+"localhost:"+tcpPort,createWebSocket()):(wsUri=ws_protocol+urlpart.toString()+":"+tcpPort,createWebSocket()),
    saveLocalStorage(inputField.value)
}

/*
 * extractHostname | 分解主机名
 *
 * @param url
 * @returns: hostname
*/
function extractHostname(url){
    return hostname=(hostname=(hostname=url.indexOf("//")>-1?url.split("/")[2]:url.split("/")[0]).split(":")[0]).split("?")[0]
}

function getTcpPort(){
    let portSelect=document.getElementById("ipPort");
    return portSelect.options[portSelect.selectedIndex].value
}

/*
 Get websocket protoca
*/
getWs_protocol=()=>{
    let checkBox,wssProt;
    return document.getElementById("wssCheck").checked?"wss://":"ws://"
}

/*
 Save local storage to session | 将端口和IP保存到session便于下次读取
 Args : ipaddress
 Returns : none
*/
function saveLocalStorage(ip){		//将获取的IP地址存储在本地
    ""!=ip&&localStorage.setItem("host",ip)
}