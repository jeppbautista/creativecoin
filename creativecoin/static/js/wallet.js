$(document).ready(function(){
    $("#sourcewallet").on('change', function(e){
        var idx = $("#sourcewallet").find(":selected").val()
        $("#balance").val(+$("#balance-"+idx).val())
        validate_balance()
    })

    $("#amount").on("input", function(e){
        var amount = $("#amount").val()
        validate_balance();
    })

    var idx = $("#sourcewallet").find(":selected").val()
    $("#balance").val(+$("#balance-"+idx).val())
    validate_balance()

    function validate_balance(){
        var idx = $("#sourcewallet").find(":selected").val()
        var balance = parseFloat($("#balance-"+idx).val())
        var amount = parseFloat($("#amount").val())

        if (isNaN(amount)){
            amount = 0;
        }

        if (balance < amount) {
            $("#balance-error").html("Insufficient funds")
            $("#submit").prop("disabled", true)
        }
        else if (balance < 100 || amount < 100){
            $("#balance-error").html("The minimum transfer is 100 CCN")
            $("#submit").prop("disabled", true)
        }
        else {
           $("#balance-error").html("&nbsp;")
            $("#submit").prop("disabled", false)
        }
    }

})

$(document).ready(function() {
    function param(name){
        return (location.search.split(name + '=')[1] || '').split('&')[0];
    }

    var currURL = window.location.href;

    var ERROR_MESSAGE_LOOKUP = {
        "login_form_error": "Invalid  information provided",
        "pass_email_error": "Incorrect email and/or password",
        "send_form_amount": "Invalid amount. Transaction failed",
        "send_form_invalid_wallet": "Invalid wallet address. Transaction failed",
        "signup_form_error": "Invalid information provided",
        "signup_email_exists": "Email already exists",
        "default_error": "Something went wrong. Transaction failed",
        "na": "Transaction failed"
    }


    var err = param("error");
    var error_message = ERROR_MESSAGE_LOOKUP[err];

    var status = param("status")

    $("#span-wallet__alert > p").html(error_message);
    if (error_message){
        $(".alert-wallet-error").show();
    } else if (status) {
        $(".alert-wallet-success").show();
    }

})

$(".copy").on("click", function(e){
    e.preventDefault();
    var text = $("#ref-code").select();
    document.execCommand("copy");
});

$(".copy2").on("click", function(e){
    e.preventDefault();
    var text = $("#wallet-code").select();
    document.execCommand("copy");
});

$("#receive-btn").on("click", function(e){
    $("#receive-modal").modal({show: true})
})

$("#send-btn").on("click", function(e){
    $("#send-modal").modal({show: true})
})

$("#receive-close").on("click", function(e){
    $("#receive-modal").modal('hide')
})

$("#send-close").on("click", function(e){
    $("#send-modal").modal('hide')
})

$("#send-close2").on("click", function(e){
    $("#send-modal").modal('hide')
})
