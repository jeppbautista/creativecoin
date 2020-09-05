jarallax(document.querySelectorAll('.jarallax'));

jarallax(document.querySelectorAll('.jarallax-keep-img'), {
    keepImg: true,
});

$('.jarallax').jarallax({
    speed: 0.2
  });

document.addEventListener('DOMContentLoaded', function() {
  AOS.init();
});


$('.na').on('click', function(){
  alert("Not Yet available");
});

