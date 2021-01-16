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

$("#receive-close").on("click", function(e){
    $("#receive-modal").modal('hide')
})

