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

// ----------------------------------------------------------------
// Select2 Initialization
// ----------------------------------------------------------------

$('.select2').select2()

// ----------------------------------------------------------------
// Event Handling
// ----------------------------------------------------------------

// Try if the server had already been initialized
$.ajax({
    url: '/indiweb/start',
    type: 'POST',
    async: true,
    processData: false,
    data: JSON.stringify({try:"aaa"}),
    contentType: "application/json",
    success: function(data){
        if(data.status == 114115){
            console.log(data)
            indi_start_success(data)
        }
    }
});

function camera_restart(){
    // Camera Restart
    $("#camera_restart").addClass("disabled");
    $("#camera_disconnect").addClass("disabled");
    $.ajax({
        url: '/indiweb/restart',
        type: 'POST',
        async: true,
        processData: false,
        data: JSON.stringify({deivce:"camera"}),
        contentType: "application/json",
        success: function(data){
            if(data.status == 200){
                $("#camera_restart").removeClass("disabled");
                $("#camera_disconnect").removeClass("disabled");
            }else{
                $("#errorMessage").text(data.message);
                $("#centralModalDanger").modal("show")
            }
        }
    })
}

function camera_disconnect(){

}

function mount_restart(){

}

function mount_disconnect(){

}

function filterwheel_restart(){

}

function filterwheel_disconnect(){

}

function focuser_restart(){

}

function focuser_disconnect(){

}

function guider_restart(){

}

function guider_disconnect(){

}

function solver_restart(){

}

function solver_disconnect(){

}

function indi_start_success(data){
    // Event after INDI server is started successfully
    if(data.params.camera != null){
        $("#camera_restart").removeClass("disabled");
        $("#camera_disconnect").removeClass("disabled");
        document.getElementById("camera_restart").addEventListener("click", camera_restart)
        document.getElementById("camera_disconnect").addEventListener("click", camera_disconnect)
    }
    if(data.params.mount != null){
        $("#mount_restart").removeClass("disabled");
        $("#mount_disconnect").removeClass("disabled");
        document.getElementById("mount_restart").addEventListener("click", mount_restart)
        document.getElementById("mount_disconnect").addEventListener("click", mount_disconnect)
    }
    if(data.params.filterwheel!= null){
        $("#filterwheel_restart").removeClass("disabled");
        $("#filterwheel_disconnect").removeClass("disabled");
        document.getElementById("filterwheel_restart").addEventListener("click", filterwheel_restart)
        document.getElementById("filterwheel_disconnect").addEventListener("click", filterwheel_disconnect)
    }
    if(data.params.focuser!= null){
        $("#focuser_restart").removeClass("disabled");
        $("#focuser_disconnect").removeClass("disabled");
        document.getElementById("focuser_restart").addEventListener("click", focuser_restart)
        document.getElementById("focuser_disconnect").addEventListener("click", focuser_disconnect)
    }
    if(data.params.guider!= null){
        $("#guider_restart").removeClass("disabled");
        $("#guider_disconnect").removeClass("disabled");
        document.getElementById("guider_restart").addEventListener("click", guider_restart)
        document.getElementById("guider_disconnect").addEventListener("click", guider_disconnect)
    }
    if(data.params.solver!= null){
        $("#solver_restart").removeClass("disabled");
        $("#solver_disconnect").removeClass("disabled");
        document.getElementById("solver_restart").addEventListener("click", solver_restart)
        document.getElementById("solver_disconnect").addEventListener("click", solver_disconnect)
    }

    $("#start_device").addClass("disabled");

    document.getElementById("start_device").innerHTML='<i class="fas fa-link fa-spin mr-1"></i>已连接';
}

$("#start_device").on('click', function (e) {
    let camera = $("#camera_type").val(),
        mount = $("#mount_type").val(),
        focuser = $("#focuser_type").val(),
        guider = $("#guider_type").val(),
        filterwheel = $("#filterwheel_type").val(),
        solver = $("#solver_type").val();

    console.debug("Camera : " + camera)
    console.debug("Mount : " + mount)
    console.debug("Focuser : " + focuser)
    console.debug("Guider : " + guider)
    console.debug("Filterwheel : " + filterwheel)
    console.debug("Solver : " + solver)

    let r = {
        camera: camera != "none" ? "indi_" + camera + "_ccd" : null,
        mount: mount != "none" ? "indi_" + mount + "_telescope" : null,
        focuser: focuser != "none" ? "indi_" + focuser + "_focuser" : null,
        guider: guider != "none" ? guider : null,
        filterwheel: filterwheel != "none" ? "indi_" + filterwheel + "_filterwheel" : null,
        solver: solver != "none" ? solver : null
    }

    let flag = false
    for(key in r){
        if(r[key] != null){
            flag = true
        }
    }
    if(!flag){
        $("#errorMessage").text("没选择任何设备，你想启动个毛线！")
        $("#centralModalDanger").modal("show")
        return
    }

    $.ajax({
        url: '/indiweb/start',
        dataType: 'json',
        type: 'POST',
        async: true,
        processData: false,
        data: JSON.stringify(r),
        contentType: "application/json",
        success: function(data){
            if(data['status']==200){
                console.log(data)
                indi_start_success(data)
            }else{
                $("#errorMessage").text(data['message'])
                $("#centralModalDanger").modal("show")
                indi_start_success(data)
            }
        }
    })
});