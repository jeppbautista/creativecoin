$(window).scroll(function(event){
    $(".div-init-launch").each(function(i, el){
        var el = $(el);
        if (el.visible(true)){
            console.log("FOOO");
        }
    });
});

// $(document).ready(function(){
//     var bar = new ProgressBar.Line('#bar1', {
//         strokeWidth: 2,
//         easing: 'easeInOut',
//         duration: 1000,
//         color: '#FFEA82',
//         trailColor: '#eee',
//         trailWidth: 1,
//         svgStyle: {width: '100%', height: '100%'}
//       });
      
//       bar.animate(1.0);  // Number from 0.0 to 1.0
// });

