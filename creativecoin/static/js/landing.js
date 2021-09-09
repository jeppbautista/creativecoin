$(document).ready(function(){
    var rz = function () {
        // height = $("#para-misVis").height() + $("#para-misVis").height()*0.3;
        // // height = $(window).height() + $(window).height()*0.55;
        // console.log(height);
        // $("#para-misVis").css("height", height + "px");
    };
    $(window).resize(function () {
        rz();
    });

    var countdown = function() {
        var countDownDate = new Date("Jan 31, 2050 00:00:00").getTime();
        var x = setInterval(function(){
            var now = new Date().getTime();
            var distance = countDownDate - now;

            var days = Math.floor(distance / (1000 * 60 * 60 * 24));
            var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((distance % (1000 * 60)) / 1000);

            $("#cd-days").html(days);
            $("#cd-hours").html(hours);
            $("#cd-minutes").html(minutes);
            $("#cd-seconds").html(seconds);
        }, 500);
    }
    countdown();
    rz();


});


