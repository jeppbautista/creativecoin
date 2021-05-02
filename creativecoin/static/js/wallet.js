$(document).ready(function(){
    $("#sourceWallet").on('change', function(e){
        var idx = $("#sourceWallet").find(":selected").val()
        $("#balance").val(+$("#balance-"+idx).val())
    })
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
