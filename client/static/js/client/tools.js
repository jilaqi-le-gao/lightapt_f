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


function onError(message) {
    $("#errorMessage").text(message);
    $("#centralModalDanger").modal("show");
};

// ----------------------------------------------------------------
// Get time
// ----------------------------------------------------------------

document.getElementById("get_time").addEventListener("click", getTime)
document.getElementById("sync_time").addEventListener("click", syncTime)
document.getElementById("reset_time").addEventListener("click", resetTime)

function getTime() {
    let now = new Date();
    let year = now.getFullYear();
    let month = now.getMonth()+1;
    let day = now.getDate();
    let hour= now.getHours();
    let minute= now.getMinutes();
    let second= now.getSeconds();
    let time = year + ":" + month + ":" + day + "-" + hour + ":" + minute + ":" + second;
    console.log(time)
    $("#time").val(time)
    return time
}

function syncTime(){
    $.ajax({
        url: '/tools/api/time/' + getTime(),
        type: 'GET',
        async: true,
        processData: false,
        contentType: "application/json",
        success: function (data) {
            if(!data.error){
                console.log(data.message);
                $("#time_info_message").text("Info: " + data.message);
                $("#time_info").removeAttr("hidden")
            }
            else{
                onError(data.error);
                $("#time_error_message").text("Error: " + data.error);
                $("#time_error").removeAttr("hidden")
            }
        },
        error: function () {
            onError("Failed to send request to server");
        }
    })
}

function resetTime(){
    $("#time").val("")
}

// ----------------------------------------------------------------
// Get location via client gps
// ----------------------------------------------------------------

document.getElementById('get_location').addEventListener('click', getLocation)
document.getElementById('sync_location').addEventListener('click', syncLocation)
document.getElementById('reset_location').addEventListener('click', resetLocation)

function getLocation() {
    let options = {
        enableHighAccuracy: true,
        maximumAge: 1000
    }
    // Web browsers support GPS option
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(onLocationSuccess, onLocationError, options);

    } else {
        onError("Web browser does not support GPS function");
    }
}

function syncLocation() {
    $.ajax({
        url: '/tools/api/location/' + $('#lon').val() + '/' + $('#lat').val(),
        type: 'GET',
        async: true,
        processData: false,
        contentType: "application/json",
        success: function (data) {
            if(!data.error){
                console.log(data.message);
                $("#location_info_message").text("Info: " + data.message);
                $("#location_info").removeAttr("hidden")
            }
            else{
                onError(data.error);
                $("#location_error_message").text("Error: " + data.error);
                $("#location_error").removeAttr("hidden")
            }
        },
        error: function () {
            onError("Failed to send request to server");
        }
    })
}

function resetLocation() {
    $("#lon").val("");
    $("#lat").val("");
}

function onLocationSuccess(pos) {
    console.log("Lon:" + pos.coords.longitude + "Lat:" + pos.coords.latitude)
    $('#lon').val(pos.coords.longitude)
    $('#lat').val(pos.coords.latitude)
}

function onLocationError(error) {
    switch (error.code) {
        case 1:
            onError("Positioning function rejected")
            break;
        case 2:
            onError("Unable to obtain location information temporarily");
            break;
        case 3:
            onError("Get information timeout");
            break;
        case 4:
            onError("Unknown error");
            break;
    }
}


// ----------------------------------------------------------------
// Update the sotfwares
// ----------------------------------------------------------------



// ----------------------------------------------------------------
// Download the template file for astromical solver
// ----------------------------------------------------------------

$(() => {
    $("#solver").change(() => {
        console.log($('#solver').val());
        let solver = $('#solver').val();
        // If want to downlaad astrometry templates
        if(solver == "astrometry"){
            // First check whether the files had already downloaded
            $.ajax({
                url: '/tools/api/download/astrometry/already',
                type: 'GET',
                async: true,
                processData: false,
                contentType: "application/json",
                success: function (data) {
                    if(!data.error){
                        console.log(data.message);
                    }
                    else{
                        onError(data.error);
                    }
                },
                error: function () {
                    onError("Failed to send request to server");
                }
            })
        }
        else{
            // Same step as astrometry
            $.ajax({
                url: '/tools/api/download/astap/already',
                type: 'GET',
                async: true,
                processData: false,
                contentType: "application/json",
                success: function (data) {
                    if(!data.error){
                        console.log(data.message);
                    }
                    else{
                        onError(data.error);
                    }
                },
                error: function () {
                    onError("Failed to send request to server");
                }
            })
        }
    })
});
