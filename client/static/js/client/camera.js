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
    document.getElementById("remoteShotbtn")
});

var is_connect = false,
    is_initialed = false,
    is_camera_connected = false,
    is_filter_connected = false,
    is_exposure = false,
    is_sequence_exposure = false

var filter_list = []

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
    9 : "RemotePolling",
    10 : "RemoteStartExposure",
    11 : "RemoteAbortExposure",
    12 : "RemoteGetExposureStatus",
    13 : "RemoteGetExposureResult",
    14 : "RemoteStartSequenceExposure",
    15 : "RemoteAbortSequenceExposure",
    16 : "RemotePauseSequenceExposure",
    17 : "RemoteContinueSequenceExposure",
    18 : "RemoteGetSequenceExposureStatus",
    19 : "RemoteGetSequenceExposureResults",
    20 : "RemoteCooling",
    21 : "RemoteCoolingTo",
    22 : "RemoteGetCoolingStatus",
    23 : "RemoteGetConfiguration",
    24 : "RemoteSetConfiguration"
}

// ----------------------------------------------------------------
// Some buttons events
function InitialSetBtnInactive(){
    // Make all buttons to inactive when initialized
    $(".btn").addClass("disabled")
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
    document.getElementById("disconnectBtn").addEventListener("click",disconnect)
    document.getElementById("cameraConnectBtn").addEventListener("click",camera_connect)
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
        case 10:
            remote_start_exposure(msg)
            break
        case 11:
            remote_abort_exposure(msg)
            break
        case 12:
            remote_get_exposure_status(msg)
            break
    }
}

function ChangeButtonStatus(){
    // Change button status when connectBtn is clicked
    is_connect ? (
        document.getElementById("connectBtn").classList.add("btn-success"),
        document.getElementById("connectBtn").innerHTML='<i class="fas fa-link fa-spin mr-1"></i>已连接',
        SetBtnActive("#disconnectBtn"),
		SetBtnActive(".btn"),
        document.getElementById("remoteShotBtn").addEventListener("click",camera_start_exposure),
        document.getElementById("remoteShotAbortBtn").addEventListener("click",camera_abort_exposure)
    ):(
        document.getElementById("connectBtn").classList.remove("btn-success"),		//如果已经连接
		document.getElementById("connectBtn").innerHTML='<i class="fas fa-link mr-1"></i>连接',
		SetBtnInactive(".btn"),
		SetBtnActive("#connectBtn"),
        document.getElementById("remoteShotBtn").removeEventListener('click'),
        document.getElementById("remoteShotAbortBtn").removeEventListener('click')
    )
}

function ChangeConnectButtonStatus(){
    // Change button status when connectBtn is clicked
    is_camera_connected ? (
        document.getElementById("cameraConnectBtn").classList.add("btn-success"),
        document.getElementById("cameraConnectBtn").innerHTML='<i class="fas fa-link fa-spin mr-1"></i>已连接',
        SetBtnActive("#cameraDisconnectBtn"),
        document.getElementById("cameraDisconnectBtn").addEventListener("click", camera_disconnect)
    ):(
        document.getElementById("cameraConnectBtn").classList.remove("btn-success"),		//如果已经连接
		document.getElementById("cameraConnectBtn").innerHTML='<i class="fas fa-link mr-1"></i>连接',
		SetBtnActive("#cameraConnectBtn"),
        SetBtnInactive("#cameraDisconnectBtn")
    )
}

function ChangeShotButtonStatus(){
    // Change the status of the button when remoteShotBtn or remoteShotAbortBtn is clicked
    is_exposure ? (
        $("#remoteShotbtn").html('<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>拍摄中...').addClass("disabled")

    ):(
        $("#remoteShotbtn").html('<i class="fas fa-camera mr-2"></i>拍摄').removeClass("disabled")
    )
}

function ChangeSequenceShotButtonStatus(){

}
// ----------------------------------------------------------------

// ----------------------------------------------------------------
// Button Event Handlers
function camera_connect(){
    let host = document.getElementById("connectHost").value,
        port = document.getElementById("connectPort").value,
        name = document.getElementById("connectName").value,
        typeForm = document.getElementById("connectType"),
        type = typeForm.options[typeForm.selectedIndex].value
    
    host = (host != undefined && host != null && host != "") ? host : "127.0.0.1"
    port = (port != undefined && port != null && port != "") ? port : 11111
    name = (name != undefined && name != null && name != "") ? name : "camera"
    type = (type != undefined) ? type : "ascom"

    console.debug("Trying to connect to camera ...")
    console.debug(host + ":" + port + ":" + name + ":" + type)
    log("Trying to connect to camera ...")
    let params = {
        host: host,
        port: port,
        name: name,
        type: type
    }
    SendRemoteConnect(params)
}

function camera_disconnect(){
    if(!is_camera_connected){
        console.log("Camera is not connected , please do not execute disconnect command")
    }
    SendRemoteDisconnect()
}

function camera_reconnect(){
    if(!is_camera_connected){
        console.log("Camera is not connected, please do not execute reconnect command")
    }
    SendRemoteReconnect()
}

function camera_scanning(){
    if(!is_camera_connected){
        console.log("Camera is not connected, please do not execute scanning command")
    }
    SendRemoteScanning()
}

function camera_start_exposure(){
    // Check if camera had already started exposure
    if(is_exposure || is_sequence_exposure){
        console.log("Exposure had already started"),
        log("Exposure has already started")
        return
    }
    // Get basic exposure parameters
    let exposure = document.getElementById("exposure"),
        gain = document.getElementById("gain"),
        offset = document.getElementById("offset")
    // Get the filter parameters if available
    let filterFrom = document.getElementById("filter"),
        filter = filterFrom.options[filterFrom.selectedIndex].value
    // Get the binning mode 
    let binning = document.getElementById("binning"),
        binningMode = binning.options[binning.selectedIndex].value
    // Check if the parameters are valid , though this will be done by server too.
    if(exposure == undefined || exposure == null || exposure < 0 || exposure > 3600){
        console.log("Invalid exposure parameters")
        return
    }
    if(gain == undefined || gain == null || gain < 0 || gain > 100){
        console.log("Invalid gain parameters")
        return
    }
    if(offset == undefined || offset == null || offset < 0 || offset > 100){
        console.log("Invalid offset parameters")
        return
    }
    if(filter != undefined || filter != null){
        if(!is_filter_connected){
            console.log("Filter is not connected, please do not execute start_exposure command")
            return
        }
        if(!filter in filter_list){
            console.log("Invalid filter parameters")
            return
        }
    }
    if(binning == undefined || binning == null){
        binning = 1
    }else{
        if(! 1 <= binning <=8){
            console.log("Invalid binning parameters")
            return
        }
    }
    r = {
        _exposure: exposure,
        _gain: gain,
        _offset: offset,
        _filter: filter,
        _binning: binning
    }
    SendRemoteStartExposure(r)
}

function camera_abort_exposure(){
    if(!is_exposure){
        console.debug("Camera had no exposure process")
        log("Camera has no exposure process")
        return
    }
    SendRemoteAbortExposure()
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

function remote_connect(message){
    let status = message.status,
        msg = message.message,
        params = message.params
    console.debug("Recieved remote connect message: " + JSON.stringify(message))
    if(status == 0){
        console.debug("Remote camera connected successfully")
        log("Remote camera connected successfully")
        if(params.info != null){
            is_initialed = true
            is_camera_connected = true

            ChangeConnectButtonStatus()

            $("#cameraConnectBar").remove()
            $("#cameraConnectIpBar").remove()
            $("#cameraConnectHelp").remove()
            // Display basic camera information
            $("#cameraStatusBar").append(
                "<li class='list-group-item d-flex camera-panel-item '><div class='col-2 p-0 text-muted text-left'>名称</div><div class='col-4 text-center' id='cameraName'></div><div class='col-2 p-0 text-muted text-left' id=''>类型</div><div class='col-4 text-center' id='cameraType'></div></li>"
            )
            $("#cameraStatusBar").append(
                "<li class='list-group-item d-flex align-items-center justify-content-around camera-panel-item px-1'><div class='col-6 p-0 text-center text-muted'>简介</div><div class='col-6 info-data-item' id='cameraDescription'></div></li>"
            )
            $("#cameraStatusBar").append(
                "<li class='list-group-item d-flex camera-panel-item '><div class='col-2 p-0 text-muted text-left'>IP</div><div class='col-4 text-center' id='cameraIpAddress'></div><div class='col-2 p-0 text-muted text-left' id=''>API</div><div class='col-4 text-center' id='cameraAPIVersion'></div></li>"
            )
            $("#cameraName").text(params.info.name)
            $("#cameraType").text(params.info.type)
            $("#cameraDescription").text(params.info.description)
            $("#cameraIpAddress").text(params.info.network.ipaddress)
            $("#cameraAPIVersion").text(params.info.network.api_version)
            
            $("#cameraStatusBar").append(
                "<li class='list-group-item d-flex camera-panel-item '><div class='col-2 p-0 text-muted text-left'>曝光时长</div><div class='col-4 text-center' id='cameraExposure'></div><div class='col-2 p-0 text-muted text-left' id=''>完成进度</div><div class='col-4 text-center' id='cameraPercentComplete'></div></li>"
            )
            $("#cameraExposure").text(params.info.current.exposure)
            $("#cameraPercentComplete").text(params.info.current.percent_complete)
            // Display information depending on the camera supported
            // Display current binning mode
            if(params.info.ability.can_binning){
                $("#cameraStatusBar").append(
                    "<li class='list-group-item d-flex camera-panel-item '><div class='col-2 p-0 text-muted text-left'>BinX</div><div class='col-4 text-center' id='cameraBinX'></div><div class='col-2 p-0 text-muted text-left' id=''>BinY</div><div class='col-4 text-center' id='cameraBinY'></div></li>"
                )
                $("#cameraBinX").text(params.info.current.binning[0])
                $("#cameraBinY").text(params.info.current.binning[1])
            }
            // Display current gain and offset values
            if(params.info.ability.can_gain && params.info.ability.offset){
                $("#cameraStatusBar").append(
                    "<li class='list-group-item d-flex camera-panel-item '><div class='col-2 p-0 text-muted text-left'>增益</div><div class='col-4 text-center' id='cameraGain'></div><div class='col-2 p-0 text-muted text-left' id=''>偏置</div><div class='col-4 text-center' id='cameraOffset'></div></li>"
                )
                $("#cameraGain").text(params.info.current.gain)
                $("#cameraOffset").text(params.info.current.offset)
            }
            // Display current cooling status and temperature
            if(params.info.ability.can_cooling){
                $("#cameraStatusBar").append(
                    "<li class='list-group-item d-flex camera-panel-item '><div class='col-2 p-0 text-muted text-left'>制冷状态</div><div class='col-4 text-center' id='cameraCoolingStatus'></div><div class='col-2 p-0 text-muted text-left' id=''>温度</div><div class='col-4 text-center' id='cameraTemperature'></div></li>"
                )
                $("#cameraCoolingStatus").text(params.info.status.is_cooling ? "制冷中" : "未制冷")
                $("#cameraTemperature").text(params.info.current.temperature)
            }
            console.debug("Established connection with camera successfully")
            log("Established connection with camera successfully")
            StartPollingInterval()
        }else{
            console.debug("Couldn't find camera information in message")
        }
    }else{
        console.debug("Remote camera connected failed")
        console.debug(msg)
        log("Remote camera connected failed")
    }
}

function remote_disconnect(message){
    let status = message.status,
        msg = message.message
    console.debug("Recieved remote disconnect message: " + JSON.stringify(message))
    if(status != 0){
        console.debug("Remote camera disconnect failed")
        console.debug(msg)
        log("Remote camera disconnect failed")
    }else{
        console.debug("Remote camera disconnected successfully")
        log("Remote camera disconnected successfully")
        is_camera_connected = false
        ChangeConnectButtonStatus()
        // Clean the status bar
        $("#cameraStatusBar").empty()
        // Add back connection bar
        $("#cameraConnectOptions").append(
            "<div class='input-group d-flex' id='cameraConnectIpBar'><input class='form-control form-control-sm text-center text-white border-sx-blue m-1' id='connectHost' placeholder='主机'><input type='number' class='form-control form-control-sm text-center text-white border-sx-blue m-1' id='connectPort' placeholder='端口'></div><div class='input-group d-flex' id='cameraConnectBar'><input class='form-control form-control-sm text-center text-white border-sx-blue m-1' id='connectName' placeholder='名称'><select class='custom-select custom-select-sm text-center text-white border-sx-blue m-1 p-2' id='connectType'><option value='ascom' selected=''>ASCOM</option><option value='indi'>INDI</option><option value='zwoasi'>ZWOASI</option><option value='qhyccd'>QHYCCD</option></select></div><small id='cameraConnectHelp' class='form-text text-muted text-center'>如果是ASI或者QHY相机，则不用填写主机和端口</small>"
        )
    }
}

function remote_reconnect(message){
    let status = message.status
        msg = message.message
    console.debug("Recieved remote reconnect message: " + JSON.stringify(message))
    if(status == 0){
        console.debug("Remote camera reconnect successful")
        log("Remote camera reconnect successful")
        is_camera_connected = true
        ChangeConnectButtonStatus()
    }
    else{
        console.debug("Remote camera reconnect failed")
        console.debug(msg)
        log("Remote camera reconnect failed")
        is_camera_connected = false
    }
}

function remote_scanning(message){

}

function remote_polling(message){
    // Return information is BaiscCameraInfo not wscamera_info
    let info = message.params.info
    if(!is_initialed){
        
    }else{
        $("#cameraName").text(info.name)
        $("#cameraType").text(info.type)
        $("#cameraDescription").text(info.description)

    }
}

function remote_start_exposure(message){
    let status = message.status,
        msg = message.message
    console.debug("Recieved remote start exposure message: " + JSON.stringify(message))
    if(status == 0){
        console.debug("Remote camera start exposure successful")
        log("Remote camera start exposure successful")
        is_exposure = true
    }else{
        console.debug("Remote camera start exposure failed")
        console.debug(msg)
        log("Remote camera start exposure failed")
        is_exposure = false

    }
    ChangeShotButtonStatus()
}

function remote_abort_exposure(message){
    let status = message.status,
        msg = message.message
    console.debug("Recieved remote abort exposure message: " + JSON.stringify(message))
    if(status == 0){
        console.debug("Remote camera abort exposure successful")
        log("Remote camera abort exposure successful")
        is_exposure = false
    }
    else{
        console.debug("Remote camera abort exposure failed")
        console.debug(msg)
        log("Remote camera abort exposure failed")
    }
    ChangeShotButtonStatus()
}

function remote_get_exposure_status(message){
    let status = message.status,
        msg = message.message,
        params = message.params
    console.debug("Recieved remote get exposure status message: " + JSON.stringify(message))
    if(status == 0){
        console.debug("Remote camera get exposure status successful")
        log("Remote camera get exposure status successful")
    }
    else{
        console.debug("Remote camera get exposure status failed")
        console.debug(msg)
        log("Remote camera get exposure status failed")
    }
}

function remote_get_exposure_result(message){
    let status = message.status,
        msg = message.message,
        params = message.params
    console.debug("Recieved remote get exposure result message: " + JSON.stringify(message))
    if(status == 0){
        console.debug("Remote camera get exposure result successful")
        log("Remote camera get exposure result successful")
    }
    else{
        console.debug("Remote camera get exposure result failed")
        console.debug(msg)
        log("Remote camera get exposure result failed")
    }
}

function remote_start_sequence_exposure(message){
    let status = message.status,
        msg = message.message
    console.debug("Recieved remote start sequence exposure message: " + JSON.stringify(message))
    if(status == 0){
        console.debug("Remote camera start exposure successful")
        log("Remote camera start exposure successful")
        is_sequence_exposure = true
    }
    else{
        console.debug("Remote camera start exposure failed")
        console.debug(msg)
        log("Remote camera start exposure failed")
        is_sequence_exposure = false
    }
    ChangeSequenceShotButtonStatus()
}

function remote_abort_sequence_exposure(message){
    let status = message.status,
        msg = message.message
    console.debug("Recieved remote abort sequence exposure message: " + JSON.stringify(message))
    if(status == 0){
        console.debug("Remote camera abort exposure successful")
        log("Remote camera abort exposure successful")
        is_sequence_exposure = false
    }
    else{
        console.debug("Remote camera abort exposure failed")
        console.debug(msg)
        log("Remote camera abort exposure failed")
    }
    ChangeSequenceShotButtonStatus()
}

function remote_pause_sequence_exposure(message){
    let status = message.status,
        msg = message.message
    console.debug("Recieved remote pause sequence exposure message: " + JSON.stringify(message))
    if(status == 0){
        console.debug("Remote camera pause exposure successful")
        log("Remote camera pause exposure successful")
        is_sequence_exposure = false
    }
    else{
        console.debug("Remote camera pause exposure failed")
        console.debug(msg)
        log("Remote camera pause exposure failed")
    }
    ChangeSequenceShotButtonStatus()
}

function remote_continue_sequence_exposure(message){
    let status = message.status,
        msg = message.message
    console.debug("Recieved remote continue sequence exposure message: " + JSON.stringify(message))
    if(status == 0){
        console.debug("Remote camera continue exposure successful")
        log("Remote camera continue exposure successful")
        is_sequence_exposure = true
    }
    else{
        console.debug("Remote camera continue exposure failed")
        console.debug(msg)
        log("Remote camera continue exposure failed")
    }
}

function remote_get_sequence_exposure_status(message){

}

function remote_get_sequence_exposure_results(message){

}

function remote_cooling(message){

}

function remote_cooling_to(message){

}

function remote_get_cooling_status(message){

}

function remote_get_configuration(message){

}

function remote_set_configuration(message){

}

// ----------------------------------------------------------------

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

function SendRemoteStartExposure(params){
    // Send start exposure command to remote server
    let request = {
        event : "RemoteStartExposure",
        uid : GenerateUID(),
        params : params
    }
    on_send(JSON.stringify(request))
}

function SendRemoteAbortExposure(){
    // Send abort exposure command to remote server
    let request = {
        event : "RemoteAbortExposure",
        uid : GenerateUID(),
        params : {}
    }
    on_send(JSON.stringify(request))
}

function SendRemoteGetExposureStatus(){
    // Send get exposure status command to remote server
    let request = {
        event : "RemoteGetExposureStatus",
        uid : GenerateUID(),
        params : {}
    }
    on_send(JSON.stringify(request))
}

function SendRemoteGetExposureResult(){
    // Send get exposure result command to remote server
    let request = {
        event : "RemoteGetExposureResult",
        uid : GenerateUID(),
        params : {}
    }
    on_send(JSON.stringify(request))
}

function SendRemoteStartSequenceExposure(params){
    // Send start sequence exposure command to remote server
    let request = {
        event : "RemoteStartSequenceExposure",
        uid : GenerateUID(),
        params : params
    }
    on_send(JSON.stringify(request))
}

function SendRemoteAbortSequenceExposure(){
    // Send abort sequence exposure command to remote server
    let request = {
        event : "RemoteAbortSequenceExposure",
        uid : GenerateUID(),
        params : {}
    }
    on_send(JSON.stringify(request))
}

function SendRemotePauseSequenceExposure(){
    // Send pause sequence exposure command to remote server
    let request = {
        event : "RemotePauseSequenceExposure",
        uid : GenerateUID(),
        params : {}
    }
    on_send(JSON.stringify(request))
}

function SendRemoteContinueSequenceExposure(){
    // Send continue sequence exposure command to remote server
    let request = {
        event : "RemoteContinueSequenceExposure",
        uid : GenerateUID(),
        params : {}
    }
    on_send(JSON.stringify(request))
}

function SendRemoteGetSequenceExposureStatus(){
    // Send get sequence exposure status command to remote server
    let request = {
        event : "RemoteGetSequenceExposureStatus",
        uid : GenerateUID(),
        params : {}
    }
    on_send(JSON.stringify(request))
}

function SendRemoteGetSequenceExposureResults(){
    // Send get sequence exposure results command to remote server
    let request = {
        event : "RemoteGetSequenceExposureResults",
        uid : GenerateUID(),
        params : {}
    }
    on_send(JSON.stringify(request))
}

function SendRemoteCooling(params){
    // Send cooling command to remote server
    let request = {
        event : "RemoteCooling",
        uid : GenerateUID(),
        params : params
    }
    on_send(JSON.stringify(request))
}

function SendRemoteCoolingTo(params){
    // Send cooling to command to remote server
    let request = {
        event : "RemoteCoolingTo",
        uid : GenerateUID(),
        params : params
    }
    on_send(JSON.stringify(request))
}

function SendRemoteGetCoolingStatus(){
    // Send get cooling status command to remote server
    let request = {
        event : "RemoteGetCoolingStatus",
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