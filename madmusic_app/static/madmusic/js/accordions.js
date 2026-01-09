/**
 * Script para inicializar acordeones Bootstrap
 */

(function($) {
    'use strict';
    
    $(document).ready(function() {
        console.log('🎵 Inicializando acordeones...');
        
        // Verificar que Bootstrap collapse esté disponible
        if (typeof $.fn.collapse === 'undefined') {
            console.error('❌ Bootstrap collapse no está cargado');
            return;
        }
        
        // Inicializar todos los acordeones
        $('.panel-collapse').each(function() {
            var $collapse = $(this);
            console.log('📋 Acordeón encontrado:', $collapse.attr('id'));
        });
        
        // Agregar listeners para debug
        $('.panel-collapse')
            .on('show.bs.collapse', function () {
                console.log('✅ Abriendo acordeón:', $(this).attr('id'));
                var $heading = $(this).prev('.panel-heading');
                $heading.find('a').removeClass('collapsed');
            })
            .on('hide.bs.collapse', function () {
                console.log('⬇️ Cerrando acordeón:', $(this).attr('id'));
                var $heading = $(this).prev('.panel-heading');
                $heading.find('a').addClass('collapsed');
            })
            .on('shown.bs.collapse', function () {
                console.log('✨ Acordeón abierto:', $(this).attr('id'));
            })
            .on('hidden.bs.collapse', function () {
                console.log('💤 Acordeón cerrado:', $(this).attr('id'));
            });
        
        // Forzar que los enlaces de acordeón funcionen
        $('.panel-title > a').on('click', function(e) {
            e.preventDefault();
            var target = $(this).attr('href');
            console.log('🖱️ Click en acordeón, target:', target);
            
            if (!target || target === '#') {
                console.error('❌ Target no válido');
                return;
            }
            
            var $target = $(target);
            if ($target.length === 0) {
                console.error('❌ Elemento target no encontrado:', target);
                return;
            }
            
            console.log('✅ Toggle collapse para:', target);
            $target.collapse('toggle');
        });
        
        console.log('✅ Acordeones inicializados');
    });
})(jQuery);
