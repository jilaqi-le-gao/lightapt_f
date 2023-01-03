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
// Guider line Renders
// ----------------------------------------------------------------

$(function () {

    var RAData = [];
    var DECData = [];

    var GuidingLineData = {
        datasets: [
            {
                label: 'RA',
                backgroundColor: 'rgba(60,141,188,0.9)',
                borderColor: 'rgba(0,0,255,0.8)',
                pointRadius: false,
                pointColor: '#3b8bba',
                pointStrokeColor: 'rgba(60,141,188,1)',
                pointHighlightFill: '#fff',
                pointHighlightStroke: 'rgba(60,141,188,1)',
                data: RAData
            },
            {
                label: 'DEC',
                backgroundColor: 'rgba(255,0 ,0, 1)',
                borderColor: 'rgba(255, 0, 0, 0.8)',
                pointRadius: true,
                pointColor: 'rgba(210, 214, 222, 1)',
                pointStrokeColor: '#c1c7d1',
                pointHighlightFill: '#fff',
                pointHighlightStroke: 'rgba(220,220,220,1)',
                data: DECData
            },
        ]
    }

    var GuidingLineOptions = {
        maintainAspectRatio: false,
        responsive: true,
        legend: {
            display: true
        },
        scales: {
            xAxes: [{
                gridLines: {
                    display: true,
                }
            }],
            yAxes: [{
                gridLines: {
                    display: true,
                }
            }]
        }
    }


    var guiding_line_canvas = $('#guiding_line').get(0).getContext('2d')
    var guiding_line_options = $.extend(true, {}, GuidingLineOptions)
    var guiding_line_data = $.extend(true, {}, GuidingLineData)
    guiding_line_data.datasets[0].fill = false;
    guiding_line_data.datasets[1].fill = false;
    guiding_line_options.datasetFill = false

    var guiding_chart = new Chart(guiding_line_canvas, {
        type: 'line',
        data: guiding_line_data,
        options: guiding_line_options
    })
});

// ----------------------------------------------------------------
// Scatter plot Render
// ----------------------------------------------------------------

$(function () {

    var ScatterPlotOptions = {
        type: 'polarArea',
        //data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
        }
    }

    var scatter_plot_canvas = $('#scatter_plot').get(0).getContext('2d')
    var scatter_plot_options = $.extend(true, {}, ScatterPlotOptions)
    //var scatter_plot_data = $.extend(true, {}, ScatterPlotData)

    var ScatterPlot = new Chart(scatter_plot_canvas, scatter_plot_options)
});

// ----------------------------------------------------------------
// BS-Stepper for server and device connections
// ----------------------------------------------------------------

// BS-Stepper Init
document.addEventListener('DOMContentLoaded', function () {
    window.stepper = new Stepper(document.querySelector('.bs-stepper'))
})

// ----------------------------------------------------------------
// Select2 Initialization
// ----------------------------------------------------------------

$('.select2').select2()