var rz = function () {
    $('.container-token')
        .css('height', 'auto')
        .css('height', $('.container-token').height() + 'px');
};
$(window).resize(function () {
    rz();
});

rz();