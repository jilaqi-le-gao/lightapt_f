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
 lightapt.js

 Main javascript file for lightapt web client
 
 ChangeLog

 2022/11/25 Rewite all JavaScript code for the new client and server API

*/

// ----------------------------------------------------------------
// Connect
// ----------------------------------------------------------------

/*
 * Connect to the server | 连接服务器
 * Args : None
 * Return : None
 */
function connect(){
    // Get url and port from form submission
    var ip = document.getElementById("ipAddress"),
        url = extractHostname(ip.value);
    ip.value = url,tcpPort = getTcpPort();
    let ws_protocol = getWs_protocol();
    // If the hostname is localhost
    "localhost"===urlpart?(
        wsUri=ws_protocol+urlpart.toString()+":"+tcpPort,createWebSocket()
    // If the hostname is None
    ):""===urlpart?(
        wsUri=ws_protocol+"localhost:"+tcpPort,createWebSocket()
    ):(
        wsUri=ws_protocol+urlpart.toString()+":"+tcpPort,createWebSocket()
    ),
    // Save local storage to session just hostname and port
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
 Check if the SSL mode is chosen , But now still only supports ws mode
 */
checkParamWssSwitch=()=>{
    let tmpParam=getUrlParam("ssl"),
        checkBox=document.getElementById("wssCheck");
    checkBox.checked=1==tmpParam
}

/*
 Save local storage to session | 将端口和IP保存到session便于下次读取
 Args : ipaddress
 Returns : none
*/
function saveLocalStorage(ip){		//将获取的IP地址存储在本地
    ""!=ip&&localStorage.setItem("host",ip)
}

// ----------------------------------------------------------------
// Receive message
// ----------------------------------------------------------------

function onMessage(Event){		//接收JSON信息
    try{
        var JSONobj=JSON.parse(Event.data.replace(/\bNaN\b/g,"null"))		//拆分JSON
    }
    catch(e){
        errorFire(e,"Not a JSON format")		//返回错误信息
    }
    "Polling"!==JSONobj.Event&&readJson(JSONobj)		//如果JSON中的Event部位Polling，则自动跳转到readJson
}

/*
 * Read JSON data and call functions
*/
function readJson(msg){
    var num = 100;
    for(var a = 0;a < 13;a++)
        if(msg.Event == events[a]){
            num = a;
            break;
        }
    switch(num){		//处理对应事件
        case 0:
            VersionRec(msg);		//版本号
            break;
        case 1:		//Polling确认是否连接
            break;
        case 2:
            signalReceived(msg.Code);
            break;
        case 3:
            newFitReadyReceived(msg);		//新的Fits图像加载完成
            break;
        case 4:
            newJPGReadyReceived(msg);		//新的JPG图像加载完成
            break;
        case 5:break;		//关机
        case 6:
            remoteActionResultReceived(msg);		//获取命令类型并作出判断
            break;
        case 7:
            arrayElementDataReceived(msg);
            break;
        case 8:
            controlDataReceived(msg);		//控制信息接收
            break;
        case 9:
            shotRunningReceived(msg);		//拍摄情况接收
            break;
        case 10:
            logEventReceived(msg);		//日志事件接收
            break;
        case 11:
            autoFocusResultReceived(msg);		//自动对焦结果接收
            break;
        case 12:
            profileChangedReceived(msg);		//配置文件变化情况接收
            break;
        default:text="No value found"		//不属于任何事件，返回错误
    }"error"in msg&&errorFire(msg.error.message+" - id:"+msg.id)		//如果有错误信息则显示错误信息
}
