/*
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

var ready=callback=>{
    "loading"!=document.readyState?callback():document.addEventListener("DOMContentLoaded",callback)
};

ready(()=>{
    InitialSetBtnInactive();
    InitialSetBtnActive();
    // Bind connect event with connectBtn 
    document.getElementById("connectBtn").addEventListener("click",connect)
});

var is_connect = false,
    is_initialed = false,
    is_focuser_connected = false,
    is_goto = false,
    is_sync = false,
    is_parking = false,
    is_home = false
    is_parked = false,
    is_homed = false

    var websocket,
    polling_interval

var version = ""

var RemoteEvent = {
    0 : "RemoteStartServer",
    1 : "RemoteStopServer",
    2 : "RemoteShutdownServer",
    3 : "RemoteRestartServer",
    4 : "RemoteDashboardSetup",
    5 : "RemoteConnect",
    6 : "RemoteDisconnect",
    7 : "RemoteReconnect",
    8 : "RemoteScanning",
    9 : "RemotePolling"
}

// ----------------------------------------------------------------
// Some buttons events
function InitialSetBtnInactive(){
    // Make all buttons to inactive when initialized
    $(".btn").addClass("disabled")
    $(".btn-tool").removeClass("disabled")
    $('#goto_seq').tooltip({title: "Go to Script Editor", animation: true}); 
    $('#clear_log').tooltip({title: "清除日志", animation: true}); 
}

function InitialSetBtnActive(){
    // Kepp connectBtn active after initialization
    $("#connectBtn").removeClass("disabled")
}

function SetBtnActive(btnId){
    // Make a button active
    $(btnId).removeClass("disabled")
}

function SetBtnInactive(btnId){
    // Make a button inactive
    $(btnId).addClass("disabled")
}

function SetStatusLedOn(ledId){
    document.getElementById(ledId).classList.add("ledgreen")
}

function SetStatusLedOff(ledId){
    document.getElementById(ledId).classList.remove("ledgreen")
}

// ----------------------------------------------------------------
// Tiny Logging System
function log(msg){
    $("#generalLogText").text(msg)
}
// ----------------------------------------------------------------

// ----------------------------------------------------------------
// Connect and Disconnect events
function connect(){
    try{
        if(is_connect){
            console.debug("Client had already connected , please do not connect again")
        }else{
            log("Trying to connect server ...")
            // Get IP from the form
            let host = document.getElementById("ipAddress").value
            if(host == ""){
                host = "127.0.0.1"
            }
            console.debug("Get host : " + host)
            // Check if the input is valid
            
            // Get port from the selector
            let portForm = document.getElementById("ipPort")
            let port = portForm.options[portForm.selectedIndex].value
            console.debug("Get port : " + port)

            // In the future , we need to support wss mode
            let ws_protocol = "ws://"

            let url = ws_protocol + host + ":" + port
            console.debug("client url : " + url)
            // Create a new websocket connection
            websocket = new WebSocket(url)
            websocket.onopen = function(event) {on_open(event)}
            websocket.onclose = function(event) {on_close(event)}
            websocket.onmessage = function(event) {on_message(event)}
            websocket.onerror = function(event) {on_error(event)}
            saveLocalStorage(url)
        }
    }
    catch(err){
        console.error("Error : " + err.message)
    }
}

function disconnect(){
    is_connect && websocket.close()
}

function on_open(event) {
    is_connect = true;
    console.debug("Establishing connection with server successfully")
    ChangeButtonStatus()
    SetStatusLedOn("connStatus")
    $("#lightapt").text("LightAPT服务器已连接")
    log("Established connection with server")
    stepper.next()
    document.getElementById("disconnectBtn").addEventListener("click",disconnect)
    document.getElementById("focuserConnectBtn").addEventListener("click",focuser_connect)
    SendRemoteDashboardSetup()
}

function on_close(event) {
    if(is_connect){
        is_connect = false;
        console.debug("Disconnecting from server successfully")
        SetStatusLedOff("connStatus")
        InitialSetBtnInactive()
        InitialSetBtnActive()
        ChangeButtonStatus()
        ChangeConnectButtonStatus()
        $("#lightapt").text("LightAPT服务器未连接")
        log("Disconnect from server")
    }
    
}

function on_message(event) {
    try{
        var message = JSON.parse(event.data.replace(/\bNaN\b/g,"null"))
    }
    catch(e){
        console.error("Not a valid JSON message : " + e)
    }
    "RemotePolling" !== message.event && parser_json(message)
}

function on_error(event) {
    console.debug("websocket error")
    log("Websocket error: ")
}

function on_send(message){
    // send message to server
    console.debug("send message : " + message)
    if(is_connect){
        websocket.send(message + "\r\n")
    }
}

function StartPollingInterval(){
    // Send a polling command to server to get the newest infomation
    // default delay is 5 seconds
    polling_interval = setInterval(SendRemotePolling,1000)
}

function saveLocalStorage(url){
    localStorage.setItem("host",url)
}

function parser_json(msg){
    // parse json message and execute functions
    let id = -1
    for(let i = 0 ; i <= 24 ; i++){
        if(msg.event == RemoteEvent[i]){
            id = i
            break
        }
    }
    switch(id){
        case 0:
            remote_start_server(msg)
            break
        case 1:
            remote_stop_server(msg)
            break
        case 2:
            remote_shutdown_server(msg)
            break
        case 3:
            remote_restart_server(msg)
            break
        case 4:
            remote_dashboard_setup(msg)
            break
        case 5:
            remote_connect(msg)
            break
        case 6:
            remote_disconnect(msg)
            break
        case 7:
            remote_reconnect(msg)
            break
        case 8:
            remote_scanning(msg)
            break
        case 9:
            remote_polling(msg)
            break
    }
}

function ChangeButtonStatus(){
    // Change button status when connectBtn is clicked
    is_connect ? (
        document.getElementById("connectBtn").classList.add("btn-success"),
        document.getElementById("connectBtn").innerHTML='<i class="fas fa-link fa-spin mr-1"></i>已连接',
        SetBtnActive("#disconnectBtn"),
		SetBtnActive(".btn")
    ):(
        document.getElementById("connectBtn").classList.remove("btn-success"),		//如果已经连接
		document.getElementById("connectBtn").innerHTML='<i class="fas fa-link mr-1"></i>连接',
		SetBtnInactive(".btn"),
		SetBtnActive("#connectBtn")
    )
}

function ChangeConnectButtonStatus(){
    // Change button status when connectBtn is clicked
    is_focuser_connected ? (
        document.getElementById("focuserConnectBtn").classList.add("btn-success"),
        document.getElementById("focuserConnectBtn").innerHTML='<i class="fas fa-link fa-spin mr-1"></i>已连接',
        SetBtnActive("#focuserDisconnectBtn"),
        document.getElementById("focuserDisconnectBtn").addEventListener("click", focuser_disconnect)
    ):(
        document.getElementById("focuserConnectBtn").classList.remove("btn-success"),		//如果已经连接
		document.getElementById("focuserConnectBtn").innerHTML='<i class="fas fa-link mr-1"></i>连接',
		SetBtnActive("#focuserConnectBtn"),
        SetBtnInactive("#focuserDisconnectBtn")
    )
}

// ----------------------------------------------------------------
// Button Event Handlers
function focuser_connect(){
    let host = document.getElementById("connectHost").value,
        port = document.getElementById("connectPort").value,
        name = document.getElementById("connectName").value,
        typeForm = document.getElementById("connectType"),
        type = typeForm.options[typeForm.selectedIndex].value
    
    host = (host != undefined && host != null && host != "") ? host : "127.0.0.1"
    port = (port != undefined && port != null && port != "") ? port : 11111
    name = (name != undefined && name != null && name != "") ? name : "focuser"
    type = (type != undefined) ? type : "ascom"

    console.debug("Trying to connect to focuser ...")
    console.debug(host + ":" + port + ":" + name + ":" + type)
    log("Trying to connect to focuser ...")
    let params = {
        host: host,
        port: port,
        name: name,
        type: type
    }
    SendRemoteConnect(params)
}

function focuser_disconnect(){
    if(!is_focuser_connected){
        console.log("focuser is not connected , please do not execute disconnect command")
    }
    SendRemoteDisconnect()
}

function focuser_reconnect(){
    if(!is_focuser_connected){
        console.log("focuser is not connected, please do not execute reconnect command")
    }
    SendRemoteReconnect()
}

function focuser_scanning(){
    if(!is_focuser_connected){
        console.log("focuser is not connected, please do not execute scanning command")
    }
    SendRemoteScanning()
}

// ----------------------------------------------------------------

// ----------------------------------------------------------------
// Recieve Remote Messages and Process them
function remote_start_server(message){

}

function remote_stop_server(message){

}

function remote_shutdown_server(message){

}

function remote_restart_server(message){

}

function remote_dashboard_setup(message){
    let status = message.status,
        msg = message.message,
        params = message.params
    console.debug("Recieved remote dashboard setup message: " + JSON.stringify(message))
    if(status == 0){
        console.debug("Remote dashboard setup successfully")
        version = params.version
        console.debug("Remote dashboard version: " + version)
        log("Remote dashboard version: " + version)
    }else{
        console.debug("Remote dashboard setup failed")
        console.debug(msg)
        log("Remote dashboard setup failed")
    }
}

// ----------------------------------------------------------------
// Send command to remote server
function GenerateUID(){
    // Create a random uid for the remote server
    var result="",i,j;
    for(j=0;j<32;j++)
        8!=j&&12!=j&&16!=j&&20!=j||(result+="-"),
        result+=i=Math.floor(16*Math.random()).toString(16).toUpperCase();
    return result
}

function generate_message(event,params){
    // generate the normal type message
    let res = {
        event: event,
        uid : GenerateUID(),
        params: params
    }
    return res
}

function SendRemoteStartServer(){

}

function SendRemoteStopServer(){

}

function SendRemoteShutdownServer(){

}

function SendRemoteRestartServer(){

}

function SendRemoteDashboardSetup(){
    // Send setup command to remote server
    let request = {
        event: "RemoteDashboardSetup",
        uid : GenerateUID(),
        params : {}
    }
    on_send(JSON.stringify(request))
}

function SendRemoteConnect(params){
    // Send camera connect command to remote server
    let request = {
        event : "RemoteConnect",
        uid : GenerateUID(),
        params : params
    }
    on_send(JSON.stringify(request))
}

function SendRemoteDisconnect(){
    // Send camera disconnect command to remote server
    let request = {
        event : "RemoteDisconnect",
        uid : GenerateUID(),
        params : {}
    }
    on_send(JSON.stringify(request))
}

function SendRemoteReconnect(){
    // Send camera reconnect command to remote server
    let request = {
        event : "RemoteReconnect",
        uid : GenerateUID(),
        params : {}
    }
    on_send(JSON.stringify(request))
}

function SendRemoteScanning(){
    // Send camera scanning command to remote server
    let request = {
        event : "RemoteScanning",
        uid : GenerateUID(),
        params : {}
    }
    on_send(JSON.stringify(request))
}

function SendRemotePolling(){
    let request = {
        event : "RemotePolling",
        uid : GenerateUID(),
        params : {}
    }
    on_send(JSON.stringify(request))
}

function SendRemoteGetConfiguration(params){
    // Send get configuration command to remote server
    let request = {
        event : "RemoteGetConfiguration",
        uid : GenerateUID(),
        params : params
    }
    on_send(JSON.stringify(request))
}

function SendRemoteSetConfiguration(params){
    // Send set configuration command to remote server
    let request = {
        event : "RemoteSetConfiguration",
        uid : GenerateUID(),
        params : params
    }
    on_send(JSON.stringify(request))
}

// ----------------------------------------------------------------
// BS-Stepper for server and device connections
// ----------------------------------------------------------------

// BS-Stepper Init
document.addEventListener('DOMContentLoaded', function () {
    window.stepper = new Stepper(document.querySelector('.bs-stepper'))
})
