// -------------------- Login -------------------
$("#btn-login__create-account").on('click', function () {
    $('.div-login-form').hide();
    $('#login-form').trigger('reset');
    $('.div-signup-form').show();
    $(".alert-login-error").hide();
});

$("#btn-signup__cancel").on('click', function () {
    $('.div-signup-form').hide();
    $('#signup-form').trigger('reset');
    $('.div-login-form').show();
    $(".alert-signup-error").hide();
    $("#no-pad").css("height", "auto")
});

$(document).ready(function () {
    function param(name) {
        return (location.search.split(name + '=')[1] || '').split('&')[0];
    }

    var currURL = window.location.href;
    var last_action = param('last_action');
    var ref = param('ref');

    if (ref) {
        $("#btn-login__create-account").click();
    } else {
        ref = "MDAwMDE="
    }

    $("#referrer").val(ref);

    var ERROR_MESSAGE_LOOKUP = {
        "login_form_error": "Invalid  information provided",
        "pass_email_error": "Incorrect email and/or password",
        "signup_form_error": "Invalid information provided",
        "signup_email_exists": "Email already exists",
        "default_error": "Something went wrong",
        "na": "N/A"
    }

    var err = param('error');
    var error_message = ERROR_MESSAGE_LOOKUP[err];

    if (last_action == "signup") {
        $('#btn-login__create-account').trigger('click');
        $('#span-signup__alert > p').html(error_message);
        if (error_message){
            $(".alert-signup-error").show();
        }
    }
    else if (last_action == "login") {
        $("#span-login__alert > p").html(error_message);
        if (error_message){
            $(".alert-login-error").show();
        }
    }

    var next = param('next');
    if (next){
        next = decodeURIComponent(next);
        $("#redirect").val(next);
    }
});

$(function () {
    var rz = function () {
        $(".container-login")
            .css("height", "auto")
            .css("height", $(".container-login").height() + "px");
    };
    $(window).resize(function () {
        rz();
    });

    rz();

    $(document).ready(function () {
        $(".sidenav").sidenav({
            edge: "right",
        });

        $(".dropdown-trigger").dropdown({
            coverTrigger: false,
        });
    });

    particlesJS("particles-js", {
        particles: {
            number: { value: 80, density: { enable: true, value_area: 800 } },
            color: { value: "#c4a101" },
            shape: {
                type: "circle",
                stroke: { width: 0, color: "#000000" },
                polygon: { nb_sides: 5 },
                image: { src: "img/github.svg", width: 100, height: 100 },
            },
            opacity: {
                value: 0.5,
                random: false,
                anim: { enable: false, speed: 1, opacity_min: 0.1, sync: false },
            },
            size: {
                value: 3,
                random: true,
                anim: { enable: false, speed: 40, size_min: 0.1, sync: false },
            },
            line_linked: {
                enable: true,
                distance: 150,
                color: "#c4a101",
                opacity: 0.4,
                width: 1,
            },
            move: {
                enable: true,
                speed: 5,
                direction: "none",
                random: true,
                straight: false,
                out_mode: "out",
                bounce: false,
                attract: { enable: true, rotateX: 600, rotateY: 1200 },
            },
        },
        interactivity: {
            detect_on: "canvas",
            events: {
                onhover: { enable: true, mode: "grab" },
                onclick: { enable: true, mode: "push" },
                resize: true,
            },
            modes: {
                grab: { distance: 315, line_linked: { opacity: 1 } },
                bubble: {
                    distance: 400,
                    size: 40,
                    duration: 2,
                    opacity: 8,
                    speed: 3,
                },
                repulse: { distance: 200, duration: 0.4 },
                push: { particles_nb: 4 },
                remove: { particles_nb: 2 },
            },
        },
        retina_detect: true,
    });

    $(document).tooltip();

    //$('.particles-js-canvas-el').resize($('.container-login').height())
});


// -------------------- Signup -------------------
$(".toggle-password").on("click", function () {
    $(this).toggleClass("fa-eye fa-eye-slash");
    var input = $($(this).attr("toggle"));

    if (input.attr("type") == "password") {
        input.attr("type", "text");
    } else {
        input.attr("type", "password");
    }
});

$("#txt-signup__phone").bind("input", function (value) {
    this.value = this.value.replace(/[a-zA-Z]+/g, "");
});