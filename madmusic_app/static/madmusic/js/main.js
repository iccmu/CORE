// JavaScript para funcionalidades del sitio Madmusic

$(document).ready(function() {
    // Menú hover con animación suave
    $('.menu-item-has-children').hover(
        function() {
            $(this).find('.sub-menu').stop(true, true).fadeIn(200);
            $(this).addClass('active');
        },
        function() {
            $(this).find('.sub-menu').stop(true, true).fadeOut(200);
            $(this).removeClass('active');
        }
    );
    
    // Menú móvil toggle
    $('.menu_trigger').on('click', function(e) {
        e.preventDefault();
        $(this).toggleClass('active');
        $('#menu_principal_container').toggleClass('mobile-open');
    });
    
    // Búsqueda móvil toggle
    $('.search_trigger').on('click', function(e) {
        e.preventDefault();
        $(this).siblings('form').toggle();
    });
    
    // Slider de header (si existe)
    if ($('#header_image_slider li').length > 1) {
        let currentSlide = 0;
        const slides = $('#header_image_slider li');
        const totalSlides = slides.length;
        
        function nextSlide() {
            slides.eq(currentSlide).fadeOut(500);
            currentSlide = (currentSlide + 1) % totalSlides;
            slides.eq(currentSlide).fadeIn(500);
        }
        
        // Cambiar slide cada 5 segundos
        setInterval(nextSlide, 5000);
    }
});




